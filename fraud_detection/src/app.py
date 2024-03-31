import sys
import os
import logging

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures

# Import Vector Clock Handler
from vector_clock import VectorClockHandler

logger = logging.getLogger('fraud_detection')

# Create a class to define the server functions, derived from
# fraud_detection_pb2_grpc.HelloServiceServicer
class HelloService(fraud_detection_grpc.HelloServiceServicer):
    def __init__(self, vector_clock_handler):
        self.vector_clock_handler = vector_clock_handler

    # Create an RPC function to say hello
    def SayHello(self, request, context):
        # Create a HelloResponse object
        response = fraud_detection.HelloResponse()
        # Set the greeting field of the response object
        response.greeting = "Hello, " + request.name
        # Print the greeting message
        logger.info("Response greeting: %s", response.greeting)
        # Return the response object
        return response

    def DetectFraud(self, request, context):
        logger.info("device=%s browser=%s appVersion=%s screenResolution=%s referrer=%s deviceLanguage=%s",
                     request.device, request.browser, request.appVersion, request.screenResolution,
                     request.referrer, request.deviceLanguage)
        # Increment vector clock
        self.vector_clock_handler.update_clock(request.orderId, 'fraud-detection')
        response = fraud_detection.DetectFraudResponse()
        response.isFraud = False
        response.reason = "No fraud"
        logger.info("isFraud=%s", response.isFraud)
        return response


def serve():
    # Initialize vector clock handler
    vector_clock_handler = VectorClockHandler()
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    fraud_detection_grpc.add_HelloServiceServicer_to_server(HelloService(vector_clock_handler), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()
