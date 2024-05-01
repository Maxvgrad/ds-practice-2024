import sys
import os
import logging
import grpc
from concurrent import futures
# Import gRPC stubs
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, utils_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc
logger = logging.getLogger('books_database')

class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):
    def Read(self, request, context):
        logger.info("book_id=%s", request.book_id)
        # Extract book_id from the gRPC request
        book_id = request.book_id
        # Perform read operation
        book_info = read_book(book_id)
        # Create a response message
        response = books_database.BookInfo()
        response.book_id = book_info['book_id']
        response.title = book_info['title']
        response.author = book_info['author']
        logger.info("title=%s", response.title)
        return response

    def Write(self, request, context):
        logger.info("book_id=%s", request.book_id)
        # Extract book data from the gRPC request
        book_data = {
            'book_id': request.book_id,
            'title': request.title,
            'author': request.author
        }
        # Perform write operation
        success = write_book(book_data)
        # Create a response message
        response = books_database.WriteResponse()
        response.success = success
        logger.info("success=%s", response.success)
        return response

# Define the serve function to start the gRPC server
def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the BooksDatabase service
    books_database_grpc.add_BooksDatabaseServiceServicer_to_server(BooksDatabaseService(), server)
    # Listen on port 50053
    port = "50056"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Books Database Server started. Listening on port 50053.")
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