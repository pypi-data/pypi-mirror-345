from ast import Dict
from datetime import datetime
from typing import Optional
import saga_pb2
from ...core.models import SagaInstance


class InMemoryStorage(SagaInstance):
    def __init__(self):
        self.sagas: Dict[str,SagaInstance] = {}
    
    def save_saga(self,saga: SagaInstance) -> bool:
        self.sagas[saga.saga_id] = saga
        return True
    def update_saga_status(self, saga_id: str, status: int) -> bool:
        if saga_id in self.sagas:
            self.sagas[saga_id].status = status
            self.sagas[saga_id].updated_at = datetime.now()
            return True
        return False
    def get_saga(self, saga_id: str) -> Optional[SagaInstance]:
        return self.sagas[saga_id]
    def record_step_execution(self, saga_id: str, step_execution: dict) -> bool:
        if saga_id not in self.sagas:
            return False
            
        step = saga_pb2.StepExecution(
            step_number=step_execution.get('step_number', 0),
            service_name=step_execution.get('service_name', ''),
            method_name=step_execution.get('method_name', ''),
            success=step_execution.get('success', False),
            result_payload=step_execution.get('result_payload', b''),
            error_message=step_execution.get('error_message', ''),
            executed_at=step_execution.get('executed_at')
        )
        
        self.sagas[saga_id].execution_history.append(step)
        return True