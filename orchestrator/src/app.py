import sys
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging.config import dictConfig
import uuid

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

# Import the transaction verification gRPC stubs
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

# Import the suggestions gRPC stubs
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, utils_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request, jsonify
from flask_cors import CORS

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app)


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Create a dictionary to store the vector clocks for each order
vector_clocks = {}

# Generate a unique OrderID
def generate_order_id():
    return int(datetime.now().timestamp())

def initialize_order(order_id, request_data):
    vector_clocks[order_id] = [0, 0, 0]

# Update the vector clock for the given order and service
def update_vector_clock(order_id, service_index):
    vector_clocks[order_id][service_index] += 1


def initialize_order_data(request_data):
    # Initialize vector clock for the order
    vector_clock = {'transaction-verification': 0, 'fraud-detection': 0, 'suggestions': 0}
    return {
        'order_data': request_data,
        'vector_clock': vector_clock
    }

def greet(name='you'):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.HelloServiceStub(channel)
        # Call the service through the stub object.
        response = stub.SayHello(fraud_detection.HelloRequest(name=name))
    return response.greeting


def detect_fraud(request, order_id):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.HelloServiceStub(channel)
        metadata = [('vector_clock', str(vector_clocks[order_id]))]
        # Call the service through the stub object.
        response = stub.DetectFraud(request['order_data'], metadata=metadata)
        update_vector_clock(order_id, 1)
        app.logger.info('Current Vector Clock for Fraud Detection: %s', vector_clocks[order_id])
    return response, request


def verify_transaction(request, order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        metadata = [('vector_clock', str(vector_clocks[order_id]))]
        response = stub.VerifyTransaction(request['order_data'], metadata=metadata)
        update_vector_clock(order_id, 0)
        app.logger.info('Current Vector Clock for Transaction Verification: %s', vector_clocks[order_id])
    return response, request


def calculate_suggestions(request, order_id):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        metadata = [('vector_clock', str(vector_clocks[order_id]))]
        # Call the service through the stub object.
        response = stub.CalculateSuggestions(request['order_data'], metadata=metadata)
        update_vector_clock(order_id, 2)
        app.logger.info('Current Vector Clock for Suggestions: %s', vector_clocks[order_id])
    return response, request
    
   
def convert_to_detect_fraud_request(json_data, order_id):
    return fraud_detection.DetectFraudRequest(
        order_id=order_id,
        user=fraud_detection.User(
            name=json_data['user']['name'],
            contact=json_data['user']['contact']
        ),
        creditCard=fraud_detection.CreditCard(
            number=json_data['creditCard']['number'],
            expirationDate=json_data['creditCard']['expirationDate'],
            cvv=json_data['creditCard']['cvv']
        ),
        userComment=json_data['userComment'],
        items=[fraud_detection.Item(name=item['name'], quantity=item['quantity']) for item in json_data['items']],
        discountCode=json_data['discountCode'],
        shippingMethod=json_data['shippingMethod'],
        giftMessage=json_data['giftMessage'],
        billingAddress=fraud_detection.Address(
            street=json_data['billingAddress']['street'],
            city=json_data['billingAddress']['city'],
            state=json_data['billingAddress']['state'],
            zip=json_data['billingAddress']['zip'],
            country=json_data['billingAddress']['country']
        ),
        giftWrapping=json_data['giftWrapping'],
        termsAndConditionsAccepted=json_data['termsAndConditionsAccepted'],
        notificationPreferences=json_data['notificationPreferences'],
        device=fraud_detection.Device(
            type=json_data['device']['type'],
            model=json_data['device']['model'],
            os=json_data['device']['os']
        ),
        browser=fraud_detection.Browser(
            name=json_data['browser']['name'],
            version=json_data['browser']['version']
        ),
        appVersion=json_data['appVersion'],
        screenResolution=json_data['screenResolution'],
        referrer=json_data['referrer'],
        deviceLanguage=json_data['deviceLanguage']
    )


def convert_to_verify_transaction_request(json_data, order_id):
    # Extract data from JSON and construct a TransactionRequest object
    transaction_request = transaction_verification.TransactionRequest()

    # Iterate over the JSON data and populate the fields of the TransactionRequest object
    for item_data in json_data['items']:
        item = transaction_request.items.add()
        item.name = item_data['name']
        item.quantity = item_data['quantity']
    
    transaction_request.order_id = order_id

    # user_id field
    transaction_request.user_id.user_id = json_data.get('user_id', '-1') # TODO: user_id is missing in request

    # shipping_address field
    transaction_request.shipping_address.street = json_data['billingAddress']['street']
    transaction_request.shipping_address.city = json_data['billingAddress']['city']
    transaction_request.shipping_address.state = json_data['billingAddress']['state']
    transaction_request.shipping_address.zip = json_data['billingAddress']['zip']
    transaction_request.shipping_address.country = json_data['billingAddress']['country']

    # payment_details field
    transaction_request.payment_details.number = json_data['creditCard']['number']
    transaction_request.payment_details.expiration_date = json_data['creditCard']['expirationDate']
    transaction_request.payment_details.cvv = json_data['creditCard']['cvv']

    return transaction_request


def convert_to_calculate_suggestions_request(json_data, order_id):
    # Create CalculateSuggestionsRequest and populate its fields from json_data
    request = suggestions.CalculateSuggestionsRequest(
        order_id = order_id,
        user=suggestions.User(
            name=json_data['user']['name'],
            contact=json_data['user']['contact']
        ),
        credit_card=suggestions.CreditCard(
            number=json_data['creditCard']['number'],
            expiration_date=json_data['creditCard']['expirationDate'],
            cvv=json_data['creditCard']['cvv']
        ),
        user_comment=json_data['userComment'],
        items=[suggestions.Item(name=item['name'], quantity=item['quantity']) for item in json_data['items']],
        discount_code=json_data['discountCode'],
        shipping_method=json_data['shippingMethod'],
        gift_message=json_data['giftMessage'],
        billing_address=suggestions.Address(
            street=json_data['billingAddress']['street'],
            city=json_data['billingAddress']['city'],
            state=json_data['billingAddress']['state'],
            zip=json_data['billingAddress']['zip'],
            country=json_data['billingAddress']['country']
        ),
        gift_wrapping=json_data['giftWrapping'],
        terms_and_conditions_accepted=json_data['termsAndConditionsAccepted'],
        notification_preferences=json_data['notificationPreferences'],
        device=suggestions.Device(
            type=json_data['device']['type'],
            model=json_data['device']['model'],
            os=json_data['device']['os']
        ),
        browser=suggestions.Browser(
            name=json_data['browser']['name'],
            version=json_data['browser']['version']
        ),
        app_version=json_data['appVersion'],
        screen_resolution=json_data['screenResolution'],
        referrer=json_data['referrer'],
        device_language=json_data['deviceLanguage']
    )

    return request


# Define a GET endpoint.
@app.route('/', methods=['GET'])
def index():
    """
    Responds with 'Hello, [name]' when a GET request is made to '/' endpoint.
    """
    # Test the fraud-detection gRPC service.
    response = greet(name='orchestrator')
    # Return the response.
    return response


@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    request_data = request.json
    order_id = generate_order_id()
    initialize_order(order_id, request_data)
    app.logger.info(
        'device=type=%s, model=%s, os=%s, browser=name=%s, version=%s, appVersion=%s, screenResolution=%s, '
        'referrer=%s, deviceLanguage=%s',
        request_data['device']['type'],
        request_data['device']['model'],
        request_data['device']['os'],
        request_data['browser']['name'],
        request_data['browser']['version'],
        request_data['appVersion'],
        request_data['screenResolution'],
        request_data['referrer'],
        request_data['deviceLanguage']
        )
    order_data = initialize_order_data(request_data)

    with ThreadPoolExecutor(max_workers=3) as executor:
        verify_transaction_future = executor.submit(verify_transaction,
                                                    convert_to_verify_transaction_request(request_data), order_data)
        update_vector_clock(order_id, 0)
        detect_fraud_future = executor.submit(detect_fraud, convert_to_detect_fraud_request(request_data), order_data)
        update_vector_clock(order_id, 1)
        calculate_suggestions_future = executor.submit(calculate_suggestions,
                                                       convert_to_calculate_suggestions_request(request_data), order_data)
        update_vector_clock(order_id, 2)

        verify_transaction_result = verify_transaction_future.result()
        detect_fraud_result = detect_fraud_future.result()
        calculate_suggestions_result = calculate_suggestions_future.result()

    if not verify_transaction_result.is_valid:
        app.logger.info('Transaction invalid. message=%s', verify_transaction_result.message)
        return jsonify(
            {'error': f'Transaction unverified. Message {verify_transaction_result.message}. '
                      f'Please check your transaction details and try again.'}), 400

    if detect_fraud_result.isFraud:
        app.logger.info('Fraud is detected. reason=%s', detect_fraud_result.reason)
        return jsonify(
            {'error': 'Your payment cannot be processed. Please contact customer support for further assistance.'}), 400

    app.logger.info('Suggested books size=%s', len(calculate_suggestions_result.suggested_books))
    suggested_books_list = [
        {'bookId': book.book_id, 'title': book.title, 'author': book.author}
        for book in calculate_suggestions_result.suggested_books
    ]
    response_data = {
        'orderId': int(datetime.now().timestamp()),
        'status': 'Order Approved',
        'suggestedBooks': suggested_books_list
    }
    return jsonify(response_data)


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
