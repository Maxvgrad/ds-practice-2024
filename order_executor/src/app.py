import sys
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import schedule
import threading
from enum import Enum

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, utils_path)
import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

import grpc
from concurrent import futures

logger = logging.getLogger('order_executor')

executor = ThreadPoolExecutor(max_workers=2)

class Replica:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.replica_url = f'order_executor_{replica_id}:50055'

    def __lt__(self, other):
        """Less than comparison for sorting."""
        return self.replica_id < other.replica_id


class OrderExecutorState(Enum):
    NO_TOKEN = 1
    HAS_TOKEN = 2
    PASSING_TOKEN = 3


class OrderExecutorService(order_executor_grpc.OrderExecutorServiceServicer):

    def __init__(self, replica_id, replicas):
        self.state = OrderExecutorState.NO_TOKEN
        self.replica_id = replica_id
        self.replicas = replicas
        self.start_liveness_check_scheduler()


    def PassToken(self, request, context):
        logger.info("Request received.")

        if self.state == OrderExecutorState.HAS_TOKEN:
            logger.error("Replica has token already.")
            raise ValueError("Replica has token already.")

        self.state = OrderExecutorState.HAS_TOKEN

        executor.submit(self.dequeue_order, "token")

        response = order_executor.PassTokenResponse()
        # logger.info("suggested_books_size=%s", len(response.suggested_books))
        return response

    def GetStateToken(self, request, context):
        response = order_executor.GetStateTokenResponse()
        response.state = self.state.name
        return response

    def dequeue_order(self, token):
        if self.state != OrderExecutorState.HAS_TOKEN:
            logger.error("Replica no has token for process token.")
            raise ValueError("Replica no has token for process token")

        logger.info("Dequeue order for process.")
        order = None # dequeue
        time.sleep(1)  # Wait before retrying

        if order is not None:
            # submit processing
            logger.info("Submit order for processing.")

        self.state = OrderExecutorState.PASSING_TOKEN
        request = order_executor.PassTokenRequest()
        next_replica = self.get_next_replica()
        logger.info(f"Passing token to next replica {next_replica.replica_id}.")

        try:
            pass_token(request, next_replica)
        except grpc.RpcError as e:
            logger.warning("Fail to pass token. Start re-election.", e)
        except Exception as e:
            logger.error("Error passing token.", e)
        except:
            logger.error("Unexpected error during passing token.")
        finally:
            self.state = OrderExecutorState.NO_TOKEN

    def get_next_replica(self):
        replicas = self.replicas
        for index, replica in enumerate(replicas):
            if replica.replica_id == self.replica_id:
                next_replica_index = (index + 1) % len(replicas)
                return replicas[next_replica_index]
        raise Exception(f"No next replica found with ID {replica_id}")

    def initialize_token_passing(self):
        if self.state == OrderExecutorState.NO_TOKEN and self.replica_id == 0:
            self.state = OrderExecutorState.HAS_TOKEN
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self.dequeue_order, "token")

    def start_liveness_check_scheduler(self):
        schedule.every(5).seconds.do(self.liveness_check)
        thread = threading.Thread(target=self.run_scheduler, daemon=True)
        thread.start()

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(2)

    def liveness_check(self):
        """Performs a liveness check on all replicas."""
        if self.state == OrderExecutorState.HAS_TOKEN:
            logger.info(f"Replica has token. Skip liveness check")
            return True

        for replica in self.replicas:
            if self.replica_id == replica.replica_id:
                logger.info(f"Skip own replica call for state.")
                continue

            try:
                with grpc.insecure_channel(replica.replica_url) as channel:
                    stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                    response = stub.GetStateToken(order_executor.GetStateTokenRequest())
                    logger.info(f"Replica {replica.replica_id} is alive with state {response.state}.")
            except Exception as e:
                logger.error(f"Failed to check liveness for replica {replica.replica_id}: {e}")

def pass_token(request, replica):
    max_retries = 3  # Maximum number of retries
    retry_delay = 1  # Delay between retries in seconds

    for attempt in range(max_retries):
        try:
            with grpc.insecure_channel(replica.replica_url) as channel:
                stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                response = stub.PassToken(request)
                return response  # Success, return response
        except grpc.RpcError as e:
            status_code = e.code()
            if status_code == grpc.StatusCode.UNAVAILABLE or status_code == grpc.StatusCode.INTERNAL:
                # Log the retry attempt and the reason
                logger.error(f"Retry {attempt + 1} for replica {replica.replica_id} due to {status_code.name}: {e.details()}")
                time.sleep(retry_delay)  # Wait before retrying
            else:
                # If the error is not retryable, re-raise the exception
                raise e
    # If we reach here, all retries have failed
    logger.error(f"Failed to pass token to replica {replica.replica_id} after {max_retries} attempts.")
    raise Exception(f"Failed to pass token to replica {replica.replica_id}.")


def serve(replica_id, replicas):
    service_instance = OrderExecutorService(replica_id, replicas)
    server = grpc.server(futures.ThreadPoolExecutor())
    order_executor_grpc.add_OrderExecutorServiceServicer_to_server(service_instance, server)

    port = "50055"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"OrderExecutor server started. Listening on port {port}.")

    if replica_id == 0:
        service_instance.initialize_token_passing()

    # Keep thread alive
    server.wait_for_termination()


if __name__ == '__main__':
    replica_id = int(os.getenv('INSTANCE_ID'))
    max_number_of_replicas = int(os.getenv('MAX_NUMBER_OF_REPLICAS'))
    replicas = [Replica(replica_id=id) for id in range(max_number_of_replicas)]

    logging.basicConfig(level=logging.INFO,
                        format=f'%(asctime)s - %(name)s - [Replica ID: {replica_id}] - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve(replica_id, replicas)

