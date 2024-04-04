import sys
import os
import logging

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, utils_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import grpc
from concurrent import futures


logger = logging.getLogger('suggestions')

class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer):


    def CalculateSuggestions(self, request, context):
        logger.info("device=%s browser=%s app_version=%s screen_resolution=%s referrer=%s device_language=%s",
                     request.device, request.browser, request.app_version, request.screen_resolution,
                     request.referrer, request.device_language)

        suggested_books = [
            suggestions.Book(book_id='1', title='Pattern Recognition and Machine Learning',
                             author='Christopher M. Bishop'),
            suggestions.Book(book_id='2', title='Deep Learning',
                             author='Ian Goodfellow, Yoshua Bengio, and Aaron Courville'),
            suggestions.Book(book_id='3', title='The Hundred-Page Machine Learning Book', author='Andriy Burkov')
        ]

        # Create the response object and populate it with the suggested books
        response = suggestions.CalculateSuggestionsResponse()
        response.suggested_books.extend(suggested_books)
        logger.info("suggested_books_size=%s", len(response.suggested_books))
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    suggestions_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    port = "50053"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info("Suggestions server started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()