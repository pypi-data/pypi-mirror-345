import base64
import json
import uuid
import grpc
from grpc_orchestrator import  saga_pb2
from grpc_orchestrator import saga_pb2_grpc
from google.protobuf.json_format import MessageToDict

from grpc_orchestrator.core.connection.grpc_connection import GrpcConnection
from grpc_orchestrator.utils.pretty import prettify_saga_response


class GrpcOrchestratorClient:
    def __init__(self, orchestrator_host='localhost', orchestrator_port=50051):
        self.orchestrator_address = f"{orchestrator_host}:{orchestrator_port}"
    def start_transaction(self, transaction_id: str, steps: list, payload: dict={}) -> dict:
        """Start a new grpc transaction with explicit service ports"""
        try:
            saga_steps = []
            for step in steps:
                print(step['port'])
                saga_steps.append(saga_pb2.SagaStep(
                    service_name=f"localhost:{step['port']}",  # Explicit port
                    rpc_method=step['rpc_method'],
                    compensation_method=step['compensation_method'],
                    timeout_seconds=step.get('timeout_seconds', 5)
                ))
            with GrpcConnection(self.orchestrator_address) as connect:
                stub = connect.get_stub("SagaOrchestratorService",saga_pb2_grpc.SagaOrchestratorServiceStub)
                response = stub.StartSagaTransaction(saga_pb2.StartSagaRequest(
                    saga_id=transaction_id,
                    steps=saga_steps,
                    payload=str(payload).encode()
                ))
                return MessageToDict(response)
        except grpc.RpcError as e:
            print(f"Error starting transaction: {e.code()}: {e.details()}")
            return None

    def get_transaction_status(self, transaction_id: str) -> dict:
        try:
            with GrpcConnection(grpc_server_add=self.orchestrator_address) as connect:
                stub = connect.get_stub("SagaOrchestratorService",saga_pb2_grpc.SagaOrchestratorServiceStub)
                response = stub.GetSagaStatusTransaction(
                    saga_pb2.GetSagaStatusRequest(saga_id=transaction_id)
                )
                
                response_dict = MessageToDict(response)

                if 'steps' in response_dict:
                    for step in response_dict['steps']:
                        if 'resultPayload' in step:
                            try:
                                raw = base64.b64decode(step['resultPayload'])
                                step['resultPayload'] = json.loads(raw.decode('utf-8'))
                            except Exception as e:
                                raise e
                return response_dict
        except grpc.RpcError as e:
            print(f"Error getting status: {e.code()}: {e.details()}")
            return None
if __name__ == '__main__':
    client = GrpcOrchestratorClient()
    steps = [
        {
            'port': 50053,
            'rpc_method': 'process_order',
            'compensation_method': 'rollback_order',
            'timeout_seconds': 5
        },
        #  {
        #     'port': 50052,
        #     'rpc_method': 'ReserveInventory',
        #     'compensation_method': 'ReleaseInventory',
        #     'timeout_seconds': 5
        # }
    ]
    transaction_id=uuid.uuid4()
    response = client.start_transaction(
        transaction_id="order_123",
        steps=steps,
    )
    status = client.get_transaction_status(transaction_id="order_123")
    
    print("Receive status:: ", status)