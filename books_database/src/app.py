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


class Replica:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.replica_url = f'books_database_{replica_id}:50055'

    def __lt__(self, other):
        """Less than comparison for sorting."""
        return self.replica_id < other.replica_id


class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):

    def __init__(self, replica_id, replicas):
        self.replica_id = replica_id
        self.leader_replica_id = replicas[-1].replica_id
        self.is_leader = self.leader_replica_id == replica_id
        self.replicas = replicas


    def Read(self, request, context):
        logger.info("title=%s", request.title)
        # Extract book_id from the gRPC request
        title = request.title
        # Perform read operation
        book_info = books_database.BookInfo()
        # Create a response message
        response = books_database.BookInfo()
        response.title = book_info['title']
        response.stock = book_info['stock']
        response.version = book_info['version']
        logger.info("title=%s", response.title)
        return response

    def Write(self, request, context):
        logger.info("title=%s stock=%s version=%s", request.title, request.stock, request.version)
        # Extract book data from the gRPC request
        book_data = {
            'title': request.title,
            'stock': request.stock,
            'version': request.version
        }
        # Perform write operation
        # success = books_database.WriteResponse()
        # Create a response message
        response = books_database.WriteResponse()
        response.success = True
        logger.info("success=%s", response.success)
        return response

# Define the serve function to start the gRPC server
def serve(replica_id, replicas):
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the BooksDatabase service
    books_database_grpc.add_BooksDatabaseServiceServicer_to_server(BooksDatabaseService(replica_id, replicas), server)
    port = "50056"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info(f"Books Database Server started. Listening on port {port}.")
    # Keep the thread alive
    server.wait_for_termination()

# Entry point of the script
if __name__ == '__main__':
    replica_id = int(os.getenv('INSTANCE_ID'))
    max_number_of_replicas = int(os.getenv('MAX_NUMBER_OF_REPLICAS'))
    replicas = [Replica(replica_id=id) for id in range(max_number_of_replicas)]

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve(replica_id, replicas)