import logging
from datetime import datetime
from typing import Dict
import grpc
from google.protobuf import timestamp_pb2
from concurrent import futures

from grpc_orchestrator import saga_pb2
from grpc_orchestrator import saga_pb2_grpc
from grpc_orchestrator.core.storage.memory import InMemoryStorage

from grpc_orchestrator.core.storage.base import SagaStorage
from grpc_orchestrator.core.models import SagaInstance

class GrpcOrchestratorTransaction(saga_pb2_grpc.SagaOrchestratorServiceServicer):
    def __init__(self, storage: SagaStorage):
        self.storage = storage
        self.channel_pool: Dict[str, grpc.Channel] = {}
        self.logger = logging.getLogger(__name__)
        
    def StartSagaTransaction(self, request: saga_pb2.StartSagaRequest, context):
        saga = SagaInstance(
            saga_id=request.saga_id,
            steps=list(request.steps),
            payload=request.payload
        )
        
        if not self.storage.save_saga(saga):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to save saga')
            return saga_pb2.StartSagaResponse()
            
        # Start async execution
        self._execute_saga_async(saga)
        
        return saga_pb2.StartSagaResponse(
            saga_id=saga.saga_id,
            status=saga.status
        )
    
    def GetSagaStatusTransaction(self, request: saga_pb2.GetSagaStatusRequest, context):
        saga = self.storage.get_saga(request.saga_id)
        
        if not saga:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Saga {request.saga_id} not found")
            return saga_pb2.GetSagaStatusResponse()
        
        # Convert datetime to protobuf Timestamp
        created_at = timestamp_pb2.Timestamp()
        created_at.FromDatetime(saga.created_at)
        
        updated_at = timestamp_pb2.Timestamp()
        updated_at.FromDatetime(saga.updated_at)
        
        return saga_pb2.GetSagaStatusResponse(
            saga_id=saga.saga_id,
            status=saga.status,
            current_step=saga.current_step,
            created_at=created_at,
            updated_at=updated_at,
            steps=saga.execution_history
        )
    
    def _execute_saga_async(self, saga: SagaInstance):
        """Execute saga steps asynchronously"""
        try:
            for step_idx, step in enumerate(saga.steps):
                # Update current step
                saga.current_step = step_idx
                saga.status = saga_pb2.SagaStatus.IN_PROGRESS
                self.storage.save_saga(saga)
                
                # Execute step
                if not self._execute_step(saga, step):
                    # Compensation needed
                    self._compensate(saga, step_idx)
                    return
                    
            # All steps completed successfully
            saga.status = saga_pb2.SagaStatus.COMPLETED
            self.storage.save_saga(saga)
            
        except Exception as e:
            self.logger.error(f"Saga execution failed: {e}")
            saga.status = saga_pb2.SagaStatus.FAILED
            self.storage.save_saga(saga)
    
    def _execute_step(self, saga: SagaInstance, step: saga_pb2.SagaStep) -> bool:
        """Execute a single saga step"""
        try:
            channel = self._get_channel(step.service_name)
            stub = saga_pb2_grpc.SagaParticipantStub(channel)
            
            request = saga_pb2.SagaParticipantRequest(
                saga_id=saga.saga_id,
                payload=saga.payload,
                headers={
                    "step-method": step.rpc_method,
                    "saga-current-step": str(saga.current_step)
                }
            )
            
            # Execute the step
            response = stub.Execute(
                request, 
                timeout=step.timeout_seconds
            )
            
            self._record_step_execution(
                saga.saga_id,
                step_number=saga.current_step,
                service_name=step.service_name,
                method_name=step.rpc_method,
                success=response.success,
                result_payload=response.result_payload,
                error_message=response.error_message
            )
            
            return response.success
            
        except grpc.RpcError as e:
            self._record_step_execution(
                saga.saga_id,
                step_number=saga.current_step,
                service_name=step.service_name,
                method_name=step.rpc_method,
                success=False,
                error_message=str(e)
            )
            return False
    
    def _compensate(self, saga: SagaInstance, failed_step_idx: int):
        """Execute compensation for all completed steps"""
        saga.status = saga_pb2.SagaStatus.COMPENSATING
        self.storage.save_saga(saga)
        
        try:
            # Compensate in reverse order
            for step_idx in range(failed_step_idx - 1, -1, -1):
                step = saga.steps[step_idx]
                if not step.compensation_method:
                    continue
                    
                if not self._execute_compensation(saga, step):
                    self.logger.error(f"Compensation failed for step {step_idx}")
                    
            saga.status = saga_pb2.SagaStatus.COMPENSATED
            
        except Exception as e:
            self.logger.error(f"Compensation failed: {e}")
            saga.status = saga_pb2.SagaStatus.FAILED
            
        finally:
            self.storage.save_saga(saga)
    
    def _execute_compensation(self, saga: SagaInstance, step: saga_pb2.SagaStep) -> bool:
        """Execute compensation for a single step"""
        try:
            channel = self._get_channel(step.service_name)
            stub = saga_pb2_grpc.SagaParticipantStub(channel)
            
            request = saga_pb2.SagaParticipantRequest(
                saga_id=saga.saga_id,
                payload=saga.payload,
                headers={
                    "compensation-method": step.compensation_method,
                    "saga-current-step": str(saga.current_step)
                }
            )
            
            response = stub.Compensate(request)
            
            self._record_step_execution(
                saga.saga_id,
                step_number=saga.current_step,
                service_name=step.service_name,
                method_name=step.compensation_method,
                success=response.success,
                error_message=response.error_message
            )
            
            return response.success
            
        except grpc.RpcError as e:
            self._record_step_execution(
                saga.saga_id,
                step_number=saga.current_step,
                service_name=step.service_name,
                method_name=step.compensation_method,
                success=False,
                error_message=str(e)
            )
            return False
    
    def _record_step_execution(self, saga_id: str, **kwargs):
        """Record step execution details"""
        execution_data = {
            **kwargs,
            'executed_at': datetime.now()
        }
        self.storage.record_step_execution(saga_id, execution_data)
    
    def _get_channel(self, service_name: str) -> grpc.Channel:
        """Get or create a gRPC channel for the service"""
        if service_name not in self.channel_pool:
            # For development, assume services are on localhost with different ports
            if ':' not in service_name:
                service_name = f'localhost:{service_name.split("_")[0][-4:]}'  # Convert 'inventory_service' to 'localhost:50052'
            
            self.channel_pool[service_name] = grpc.insecure_channel(service_name)
        return self.channel_pool[service_name]

def serve():
    """Start the orchestrator server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    storage = InMemoryStorage()
    saga_pb2_grpc.add_SagaOrchestratorServiceServicer_to_server(
        GrpcOrchestratorTransaction(storage), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Grpc Transaction Start at: [::]:50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()