# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import order_executor_pb2 as order__executor__pb2


class OrderExecutorServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PassToken = channel.unary_unary(
                '/order.executor.OrderExecutorService/PassToken',
                request_serializer=order__executor__pb2.PassTokenRequest.SerializeToString,
                response_deserializer=order__executor__pb2.PassTokenResponse.FromString,
                )
        self.GetStateToken = channel.unary_unary(
                '/order.executor.OrderExecutorService/GetStateToken',
                request_serializer=order__executor__pb2.GetStateTokenRequest.SerializeToString,
                response_deserializer=order__executor__pb2.GetStateTokenResponse.FromString,
                )


class OrderExecutorServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def PassToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStateToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderExecutorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PassToken': grpc.unary_unary_rpc_method_handler(
                    servicer.PassToken,
                    request_deserializer=order__executor__pb2.PassTokenRequest.FromString,
                    response_serializer=order__executor__pb2.PassTokenResponse.SerializeToString,
            ),
            'GetStateToken': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStateToken,
                    request_deserializer=order__executor__pb2.GetStateTokenRequest.FromString,
                    response_serializer=order__executor__pb2.GetStateTokenResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'order.executor.OrderExecutorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OrderExecutorService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def PassToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order.executor.OrderExecutorService/PassToken',
            order__executor__pb2.PassTokenRequest.SerializeToString,
            order__executor__pb2.PassTokenResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetStateToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order.executor.OrderExecutorService/GetStateToken',
            order__executor__pb2.GetStateTokenRequest.SerializeToString,
            order__executor__pb2.GetStateTokenResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
