import sys
import os

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

def greet(name='you'):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.HelloServiceStub(channel)
        # Call the service through the stub object.
        response = stub.SayHello(fraud_detection.HelloRequest(name=name))
    return response.greeting

def detect_fraud(request):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.HelloServiceStub(channel)
        # Call the service through the stub object.
        response = stub.DetectFraud(request)
    return response

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

# Function to convert JSON data to gRPC request for transaction verification
def convert_to_verify_transaction_request(json_data):
    # Extract data from JSON and construct a TransactionRequest object
    transaction_request = transaction_verification.TransactionRequest()

    # Iterate over the JSON data and populate the fields of the TransactionRequest object
    for item_data in json_data['items']:
        item = transaction_request.items.add()
        item.name = item_data['name']
        item.quantity = item_data['quantity']

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

# Function to call the transaction verification gRPC service
def verify_transaction(request):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        response = stub.VerifyTransaction(request)
    return response


def calculate_suggestions(request):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        # Call the service through the stub object.
        response = stub.CalculateSuggestions(request)
    return response

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
    # Print request object data
    print("Request Data:", request.json)
    
    detect_fraud_request = convert_to_detect_fraud_request(request.json)
    
    try:
        detect_fraud_response = detect_fraud(detect_fraud_request)
    except grpc.RpcError as e:
        print(f"RPC failed with code {e.code()}: {e.details()}")
        return jsonify({'error': 'Failed to perform fraud detection'}), 500

    print(f"Fraud detection response isFraud: {detect_fraud_response.isFraud}, reason: {detect_fraud_response.reason}")

    calculate_suggestions_request = convert_to_calculate_suggestions_request(request.json)

    try:
        calculate_suggestions_response = calculate_suggestions(calculate_suggestions_request)
    except grpc.RpcError as e:
        print(f"RPC failed with code {e.code()}: {e.details()}")
        return jsonify({'error': 'Failed to perform fraud detection'}), 500

    print(f"Calculate suggestions response: {calculate_suggestions_response}")

    verify_transaction_request = convert_to_verify_transaction_request(request.json)
    
    try:
        # Call the transaction verification gRPC service
        verify_transaction_response = verify_transaction(verify_transaction_request)
    except grpc.RpcError as e:
        # Handle gRPC errors, such as connection issues
        print(f"RPC failed with code {e.code()}: {e.details()}")
        return jsonify({'error': 'Failed to perform transaction verification'}), 500
    
    print(f"Transaction verification response: {verify_transaction_response.is_valid}, reason: {verify_transaction_response.message}")
    
    # Process verification response and handle checkout accordingly
    if verify_transaction_response.is_valid:

        suggested_books_list = [
            {'bookId': book.book_id, 'title': book.title, 'author': book.author}
            for book in calculate_suggestions_response.suggested_books
        ]

        order_status_response = {
            'orderId': '12345',
            'status': 'Order Approved',
            'suggestedBooks': suggested_books_list
        }
        #response_data = {'message': 'Checkout processed successfully'}
    else:
        # If transaction is invalid, handle accordingly
        #handle_invalid_transaction() # Could implement something different?
        # Dummy response for now
        order_status_response = {'error': 'Invalid transaction'}

    return order_status_response


def convert_to_detect_fraud_request(json_data):
    return fraud_detection.DetectFraudRequest(
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


def convert_to_calculate_suggestions_request(json_data):
    # Create CalculateSuggestionsRequest and populate its fields from json_data
    request = suggestions.CalculateSuggestionsRequest(
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


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
