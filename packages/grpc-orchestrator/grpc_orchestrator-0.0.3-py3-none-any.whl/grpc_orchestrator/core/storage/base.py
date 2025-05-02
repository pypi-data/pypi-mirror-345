from abc import ABC, abstractmethod
from ..models import SagaInstance
from typing import Optional

class SagaStorage(ABC):
    @abstractmethod
    def save_saga(self, saga: SagaInstance) -> bool:
        pass
        
    @abstractmethod
    def update_saga_status(self, saga_id: str, status: int) -> bool:
        pass
        
    @abstractmethod
    def get_saga(self, saga_id: str) -> Optional[SagaInstance]:
        pass
        
    @abstractmethod
    def record_step_execution(self, saga_id: str, step_execution: dict) -> bool:
        pass