import sys
import os
import logging
import random

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, utils_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

import grpc
from concurrent import futures
from datetime import datetime

logger = logging.getLogger('payment')


class PaymentService(payment_grpc.PaymentServiceServicer):

    def ExecutePayment(self, request, context):
        logger.info("payment_details.number=%s", obfuscate_string(request.payment_details.number))
        response = payment.ExecutePaymentResponse()
        response.payment_id = int(datetime.now().timestamp())
        return response


def obfuscate_string(s):
    if len(s) <= 4:
        return '*' * len(s)
    else:
        return s[:-4] + '****'


def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    payment_grpc.add_PaymentServiceServicer_to_server(PaymentService(), server)
    port = "50057"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"Payment server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()