# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from utils.pb.transaction_verification import transaction_verification_pb2 as utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2


class TransactionVerificationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.VerifyTransaction = channel.unary_unary(
                '/transaction.verification.TransactionVerificationService/VerifyTransaction',
                request_serializer=utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionRequest.SerializeToString,
                response_deserializer=utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionResponse.FromString,
                )


class TransactionVerificationServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def VerifyTransaction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionVerificationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'VerifyTransaction': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyTransaction,
                    request_deserializer=utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionRequest.FromString,
                    response_serializer=utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'transaction.verification.TransactionVerificationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TransactionVerificationService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def VerifyTransaction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction.verification.TransactionVerificationService/VerifyTransaction',
            utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionRequest.SerializeToString,
            utils_dot_pb_dot_transaction__verification_dot_transaction__verification__pb2.TransactionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
