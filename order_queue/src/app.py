import sys
import os
import logging
import queue

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import grpc
from concurrent import futures

from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

resource = Resource(attributes={
    SERVICE_NAME: "order_queue"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://observability:4317"))
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("order_queue.tracer")

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://observability:4317")
)
provider = MeterProvider(metric_readers=[metric_reader])

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("order_queue.meter")

order_queue_counter = meter.create_up_down_counter(
    name="order.queue",
    description="The number of the orders in the queue")


logger = logging.getLogger('order_queue')


class Order:
    def __init__(self, order_id, order_type, payload):
        self.order_id = order_id
        self.order_type = order_type
        self.payload = payload

    def __lt__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id < other.order_id

    def __eq__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id and self.order_type == other.order_type and self.payload == other.payload

    def __repr__(self):
        return f"Order(order_id={self.order_id}, order_type={self.order_type}, payload={self.payload})"



class OrderQueueService(order_queue_grpc.OrderQueueServiceServicer):

    def __init__(self):
        self.orders = queue.PriorityQueue()

    def EnqueueOrder(self, request, context):
        metadata = dict(context.invocation_metadata())
        traceparent = metadata.get('traceparent')
        carrier = {"traceparent": traceparent}
        logger.info(carrier)
        ctx = TraceContextTextMapPropagator().extract(carrier)

        with tracer.start_as_current_span("EnqueueOrder", context=ctx):

            logger.info("order_id=%s order_type=%s priority=%s", request.order_id, request.order_type, request.priority)

            order = Order(request.order_id, request.order_type, request.payload)

            priority = 10
            if request.priority is not None and request.priority > 0:
                priority = request.priority

            self.orders.put((priority, order))

            response = order_queue.EnqueueOrderResponse()
            response.order_id = request.order_id
            response.is_success = True
            order_queue_counter.add(1)
            return response

    def DequeueOrder(self, request, context):

        if self.orders.empty():
            # Handle the case where the queue is empty
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Order queue is empty')
            return order_queue.DequeueOrderResponse()

        _, order = self.orders.get()
        logger.info("Dequeue order_id=%s order_type=%s", order.order_id, order.order_type)

        response = order_queue.DequeueOrderResponse()
        response.order_id = order.order_id
        response.order_type = order.order_type
        response.payload = order.payload
        order_queue_counter.add(-1)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    order_queue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    server.start()
    logger.info(f"Order queue server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='a',
                        encoding='utf-8'
                        )
    serve()