import sys
import os
import logging
import queue

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


class Order:
    def __init__(self, order_id, order_type, payload):
        self.order_id = order_id
        self.order_type = order_type
        self.payload = payload


class OrderQueueService(order_queue_grpc.OrderQueueServiceServicer):

    def __init__(self):
        self.orders = queue.PriorityQueue()

    def EnqueueOrder(self, request, context):
        logger.info("order_id=%s order_type=%s priority=%s", request.order_id, request.order_type, request.priority)

        order = Order(request.order_id, request.order_type, request.payload)

        priority = 10
        if request.priority is not None and request.priority > 0:
            priority = request.priority

        self.orders.put((priority, order))

        response = order_queue.EnqueueOrderResponse()
        response.order_id = request.order_id
        response.is_success = True
        return response

    def DequeueOrder(self, request, context):

        if self.orders.empty():
            # Handle the case where the queue is empty
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Order queue is empty')
            return order_queue.DequeueOrderResponse()

        _, order = self.orders.get()
        logger.info("Dequeue order_id=%s order_type=%s", order.order_id, order.order_type)

        response = order_queue.DequeueOrderResponse()
        response.order_id = order.order_id
        response.order_type = order.order_type
        response.payload = order.payload

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