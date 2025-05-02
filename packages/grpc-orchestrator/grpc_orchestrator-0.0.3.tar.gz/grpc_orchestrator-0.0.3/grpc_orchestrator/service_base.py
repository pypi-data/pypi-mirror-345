from concurrent import futures

import grpc
from . import saga_pb2_grpc
from . import saga_pb2
class GrpcSagaTransactionParticipantBase(saga_pb2_grpc.SagaParticipantServicer):
    def Execute(self, request, context)-> saga_pb2.SagaParticipantResponse:
        try:
            return self.execute(request,context)
        except Exception as e:
            return saga_pb2.SagaParticipantResponse(
                success=False,
                error_message=str(e)
            )
    def Compensate(self, request, context) -> saga_pb2.SagaParticipantResponse:
        try:
            return self.compensate(request=request,context=context)
        except Exception as e:
            return saga_pb2.SagaParticipantResponse(
                success=False,
                error_message=str(e)
            )
    def execute(self,request,context) -> saga_pb2.SagaParticipantResponse:
        raise NotImplementedError
    def compensate(self,request,context) -> saga_pb2.SagaParticipantResponse:
        raise NotImplementedError


def run_participant_server(service: GrpcSagaTransactionParticipantBase, port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    saga_pb2_grpc.add_SagaParticipantServicer_to_server(service, server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"Service running on port {port}")
    server.start()
    server.wait_for_termination()