import sys
import os
import logging
import grpc
from concurrent import futures
import uuid
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
        self.replica_url = f'books_database_{replica_id}:50056'

    def __lt__(self, other):
        """Less than comparison for sorting."""
        return self.replica_id < other.replica_id


class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):

    def __init__(self, replica_id, replicas):
        self.replica_id = replica_id
        self.primary_replica_id = replicas[-1].replica_id
        self.primary_replica = replicas[-1]
        self.is_primary = self.primary_replica_id == replica_id
        self.replicas = replicas
        self.storage = {}
        self.transactions = {}

    def Read(self, request, context):
        logger.info("title=%s action=READ", request.title)
        title = request.title
        if title in self.storage:
            book_info = self.storage[title]
            return books_database.BookInfo(
                title=book_info['title'], stock=book_info['stock'], version=book_info['version'])
        else:
            # initialize stock for missing title. Initial stock is out of scope of the task.
            # We simply assign stock 2 to missing title
            self.storage[request.title] = {'title': request.title, 'stock': 2, 'version': 0}
            book_info = self.storage[title]
            sync_request = books_database.WriteRequest(
                title=book_info['title'], stock=book_info['stock'], version=book_info['version'])
            acks = self.propagate_to_replicas(sync_request)
            assert all(acks)  # Ensure all replicas acknowledged
            return books_database.BookInfo(
                title=book_info['title'], stock=book_info['stock'], version=book_info['version'])

    def Write(self, request, context):
        logger.info("title=%s stock=%s version=%s action=WRITE", request.title, request.stock, request.version)

        metadata = dict(context.invocation_metadata())
        transaction_id = metadata.get('transaction-id')

        if transaction_id is not None:
            logger.info("title=%s stock=%s version=%s transaction_id=%s action=WRITE",
                        request.title, request.stock, request.version, transaction_id)

            if transaction_id in self.transactions:
                transaction = self.transactions[transaction_id]

                if 'titles' not in transaction:
                    transaction['titles'] = []
                logger.info("title=%s stock=%s version=%s transaction_id=%s action=WRITE",
                            request.title, request.stock, request.version, transaction_id)

                transaction['titles'].append(request.title)
                transaction[request.title] = {'title': request.title, 'stock': request.stock, 'version': request.version}
                return books_database.WriteResponse(success=True)
            else:
                logger.error("transaction missing transaction_id=%s",transaction_id)

        return self.perform_write(request)

    def perform_write(self, request):
        if not self.is_primary:
            # Forward the write request to the primary
            return self.forward_write_to_primary(request)
        else:
            # Execute write at primary
            self.storage[request.title] = {'title': request.title, 'stock': request.stock, 'version': request.version}
            # Propagate to backups and wait for acknowledgments
            acks = self.propagate_to_replicas(request)
            success = all(acks)  # Ensure all replicas acknowledged
            return books_database.WriteResponse(success=success)

    def find_primary(self, book_info):
        # Primary replica is constant. It can be updated to runtime calculation of replica.
        return self.primary_replica

    def forward_write_to_primary(self, request):
        # Communicate with the primary server using gRPC
        channel = grpc.insecure_channel(self.primary_replica.replica_url)
        client = books_database_grpc.BooksDatabaseServiceStub(channel)
        return client.Write(request)

    def propagate_to_replicas(self, request):
        acknowledgments = []
        for replica in self.replicas:
            if replica.replica_id != self.replica_id:  # Do not send to self
                with grpc.insecure_channel(replica.replica_url) as channel:
                    client = books_database_grpc.BooksDatabaseServiceStub(channel)
                    try:
                        response = client.SyncWrite(request)
                        acknowledgments.append(response.success)
                    except grpc.RpcError as e:
                        logger.error(f"Replication failed for {replica.replica_url}: {e}")
                        acknowledgments.append(False)
        return acknowledgments

    def SyncWrite(self, request, context):
        logger.info("title=%s stock=%s version=%s action=SYNC_WRITE", request.title, request.stock, request.version)
        self.storage[request.title] = {'title': request.title, 'stock': request.stock, 'version': request.version}
        return books_database.WriteResponse(success=True)

    def OpenTransaction(self, request, context):
        logger.info("action=OPEN")
        transaction_id = get_transaction_id()
        self.transactions[transaction_id] = {
            "state": 'INIT'
        }
        response = books_database.OpenTransactionResponse()
        response.transaction_id = transaction_id
        return response

    def InitTwoPhaseCommit(self, request, context):
        logger.info("transaction_id=%s action=INIT_TWO_PHASE_COMMIT", request.transaction_id)
        transaction = self.transactions[request.transaction_id]
        logger.info("transaction_id=%s state=%s", request.transaction_id, transaction['state'])
        response = books_database.InitTwoPhaseCommitResponse()
        if transaction['state'] == 'INIT':
            transaction['state'] = 'READY'
            response.status = 'VOTE_COMMIT'
        else:
            transaction['state'] = 'ABORT'
            response.status = 'VOTE_ABORT'
        logger.info("transaction_id=%s state=%s action=INIT_TWO_PHASE_COMMIT", request.transaction_id, transaction['state'])
        return response

    def AbortTwoPhaseCommit(self, request, context):
        logger.info("transaction_id=%s action=ABORT", request.transaction_id)
        del self.transactions[request.transaction_id]
        return books_database.AbortTwoPhaseCommitResponse(status='ABORT')

    def CommitTwoPhaseCommit(self, request, context):
        logger.info("transaction_id=%s action=COMMIT", request.transaction_id)
        transaction = self.transactions[request.transaction_id]
        for title in transaction['titles']:
            logger.info("transaction_id=%s title=%s", request.transaction_id, title)

            book_info = transaction[title]
            write_request = books_database.WriteRequest(
                title=book_info['title'], stock=book_info['stock'], version=book_info['version'])
            self.perform_write(write_request)
        return books_database.CommitTwoPhaseCommitResponse(status='COMMIT')


def get_transaction_id():
    return str(uuid.uuid4())

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