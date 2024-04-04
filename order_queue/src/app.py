import sys
import os
import logging

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import grpc
from concurrent import futures

logger = logging.getLogger('order_queue')

class OrderQueueService(order_queue_grpc.OrderQueueServiceServicer):

    def EnqueueOrder(self, request, context):
        logger.info("order_id=%s order_type=%s", request.order_id, request.order_type)
        response = order_queue.EnqueueOrderResponse()
        response.order_id = request.order_id
        response.is_success = True
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    order_queue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"Order queue server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()