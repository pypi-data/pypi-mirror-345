from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from .. import saga_pb2

@dataclass
class SagaInstance:
    saga_id: str
    steps: List[saga_pb2.SagaStep]
    current_step: int = 0
    status: saga_pb2.SagaStatus = saga_pb2.SagaStatus.STARTED
    payload: bytes = b''
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    execution_history: List[saga_pb2.StepExecution] = None

    def __post_init__(self):
        if self.execution_history is None:
            self.execution_history = []