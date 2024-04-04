import sys
import os
import logging
import grpc
from concurrent import futures
from datetime import datetime

# Import gRPC stubs
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc



logger = logging.getLogger('transaction_verification')


def verify_transaction(transaction_data):
    if not transaction_data.get('items'):
        return False, "No items in the transaction"

    if not all(transaction_data.get(field) for field in ['user_id', 'shipping_address', 'payment_details']):
        return False, "Missing user data"

    is_valid, reason = validate_card(
        card_number=transaction_data['payment_details'].number,
        expiration_date=transaction_data['payment_details'].expiration_date,
        cvv=transaction_data['payment_details'].cvv
    )
    return is_valid, reason


class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer):

    def VerifyTransaction(self, request, context):
        logger.info("user_id=%s", request.user_id)
        # Extract transaction data from the gRPC request
        transaction_data = {
            'items': request.items,
            'user_id': request.user_id,
            'shipping_address': request.shipping_address,
            'payment_details': request.payment_details
        }
        # Perform transaction verification
        is_valid, message = verify_transaction(transaction_data)
        # Create a response message
        response = transaction_verification.TransactionResponse()
        response.is_valid = is_valid
        response.message = message
        logger.info("is_valid=%s", response.is_valid)
        return response


def luhn_checksum(card_number):
    """Check if the card number passes the Luhn algorithm."""
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10 == 0


def validate_card(card_number, expiration_date, cvv):
    """Validate credit card details."""
    if not (isinstance(card_number, str) and card_number.isdigit() and len(card_number) == 16 and luhn_checksum(card_number)):
        return False, "Invalid card number."

    try:
        exp_date = datetime.strptime(expiration_date, "%m/%y")
        if exp_date < datetime.now():
            return False, "Card expired."
    except ValueError:
        return False, "Invalid expiration date format."

    if not (isinstance(cvv, str) and cvv.isdigit() and len(cvv) in [3, 4]):
        return False, "Invalid CVV."

    return True, "Card details valid."


# Define the serve function to start the gRPC server
def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the TransactionVerification service
    transaction_verification_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Transaction Verification Server started. Listening on port 50052.")
    # Keep the thread alive
    server.wait_for_termination()

# Entry point of the script
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()