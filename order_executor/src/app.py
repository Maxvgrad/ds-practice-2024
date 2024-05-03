import sys
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import schedule
import threading
from enum import Enum
import json

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, utils_path)
import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, utils_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, utils_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc

import grpc
from concurrent import futures

logger = logging.getLogger('order_executor')

executor = ThreadPoolExecutor(max_workers=2)


class OutOfStockException(Exception):
    def __init__(self, title, message="Insufficient stock for the book"):
        self.title = title
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.title}"

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

    def __init__(self, replica_id, replicas, book_database_replica_urls):
        self.state = OrderExecutorState.NO_TOKEN
        self.replica_id = replica_id
        self.replicas = replicas
        self.start_liveness_check_scheduler()
        assert len(book_database_replica_urls) > 0
        self.book_database_replica_urls = book_database_replica_urls
        self.next_database_replica_url_index = 0


    def PassToken(self, request, context):
        logger.info("Request received.")

        if self.state == OrderExecutorState.HAS_TOKEN:
            logger.error("Replica has token already.")
            raise ValueError("Replica has token already.")

        self.state = OrderExecutorState.HAS_TOKEN

        executor.submit(self.execute, "token")

        response = order_executor.PassTokenResponse()
        # logger.info("suggested_books_size=%s", len(response.suggested_books))
        return response

    def GetStateToken(self, request, context):
        response = order_executor.GetStateTokenResponse()
        response.state = self.state.name
        return response

    def execute(self, token):
        if self.state != OrderExecutorState.HAS_TOKEN:
            logger.error("Replica no has token for process token.")
            raise ValueError("Replica no has token for process token")

        logger.info("Dequeue order for processing.")

        try:
            order = dequeue_order()
        except:
            logger.error("Unexpected error during order de-queuing.")
            order = None

        if order is not None:
            payment_channel = grpc.insecure_channel('payment:50057')
            payment_stub = payment_grpc.PaymentServiceStub(payment_channel)

            books_database_replica_url = self.get_next_book_database_replica_url()
            books_database_channel = grpc.insecure_channel(books_database_replica_url)
            books_database_stub = books_database_grpc.BooksDatabaseServiceStub(books_database_channel)
            self.process_order(order, books_database_stub, payment_stub)
        else:
            time.sleep(2)

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

    def process_order(self, order, books_database_stub, payment_stub):
        try:
            order_payload = json.loads(order.payload)
            items = order_payload["items"]
            for item in items:
                request = books_database.ReadRequest(title=item["name"])
                book_info = read_book_info(books_database_stub, request)
                book_info.stock -= int(item['quantity'])

                if book_info.stock < 0:
                    logger.error(f"Insufficient stock for the book: {book_info.title}.")
                    raise OutOfStockException(book_info.title)

                request = books_database.WriteRequest(title=book_info.title, stock=book_info.stock,
                                                      version=book_info.version)
                book_info = write_book_info(books_database_stub, request)

            payment_details = order_payload["creditCard"]
            request = payment.ExecutePaymentRequest(
                payment_details=payment.PaymentDetails(
                    number=payment_details.get("number", ""),
                    expiration_date=payment_details.get("expirationDate", ""),
                    cvv=payment_details.get("cvv", "")
                )
            )
            payment_response = execute_payment(payment_stub, request)
            logger.info(f"Payment executed payment_id={payment_response.payment_id}.")
        except OutOfStockException as e:
            logger.error(e)
        except Exception as e:
            logger.error("Error passing token.", e)
        except:
            logger.error("Unexpected error during payment execution.")

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
                executor.submit(self.execute, "token")

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
            logger.info(f"Replica has token. Skip liveness check.")
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

    def get_next_book_database_replica_url(self):
        self.next_database_replica_url_index = (self.next_database_replica_url_index + 1) % len(self.book_database_replica_urls)
        return self.book_database_replica_urls[self.next_database_replica_url_index]


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


def dequeue_order(retries=3, delay=2):
    with grpc.insecure_channel('order_queue:50054') as channel:
        stub = order_queue_grpc.OrderQueueServiceStub(channel)
        request = order_queue.DequeueOrderRequest()

        for attempt in range(retries):
            try:
                response = stub.DequeueOrder(request)
                return response
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    logger.info("Order queue is empty.")
                    return None
                else:
                    logger.error(f"Error dequeueing. Attempt {attempt + 1} of {retries}")
                    if attempt < retries - 1:  # Don't sleep after the last attempt
                        time.sleep(delay)
        logger.error("All retry attempts failed.")
        raise grpc.RpcError("All retry attempts failed.")


def execute_payment(stub, request):
    response = stub.ExecutePayment(request)
    return response


def read_book_info(stub, request):
    try:
        response = stub.Read(request)
        if not response.title:
            raise ValueError("Book not found.")
        return response
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logger.error(f"Book with title {request.title} not found.")
        else:
            logger.error(f"Failed to read book info for title {request.title}: {e.details()}")
        raise


def write_book_info(stub, request):
    try:
        response = stub.Write(request)
        return response
    except grpc.RpcError as e:
        logger.error(f"Failed to update book info for title {request.title}: {e.details()}")
        raise


def serve(replica_id, replicas, book_database_replica_urls):
    service_instance = OrderExecutorService(replica_id, replicas, book_database_replica_urls)
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
    book_database_replica_urls = [url.strip() for url in os.getenv('BOOK_DATABASE_REPLICA_URLS').split(',')]
    replicas = [Replica(replica_id=id) for id in range(max_number_of_replicas)]

    logging.basicConfig(level=logging.INFO,
                        format=f'%(asctime)s - %(name)s - [Replica ID: {replica_id}] - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve(replica_id, replicas, book_database_replica_urls)

