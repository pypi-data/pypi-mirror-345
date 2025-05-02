from concurrent import futures
import json
import logging
from .... import saga_pb2
from .... import service_base


class ExampleService(service_base.GrpcSagaTransactionParticipantBase):
    def execute(self, request, context):
        method = request.headers.get("step-method")
        self.logger = logging.getLogger(__name__)
        try:
            if method == "RefundPayment":
                return self._refund_payment(request)
        except Exception as e:
            self.logger.error(f"Compensation failed: {e}")
            return saga_pb2.SagaParticipantResponse(success=False, error_message=str(e))
    def compensate(self, request, context):
        method = request.headers.get("compensation-method")
        try:
            if method == "ReleaseInventory":
                return self._release_inventory(request=request)
            elif method == "RefundPayment":
                return self._refund_payment(request=request)
            else:
                return saga_pb2.SagaParticipantResponse(
                    success=False, error_message=f"Unknown compensation {method}"
                )
        except Exception as e:
            self.logger.error(f"Compensation failed: {e}")
            return saga_pb2.SagaParticipantResponse(success=False, error_message=str(e))

    def _reserve_inventory(self, request):
        # Business logic here
        return saga_pb2.SagaParticipantResponse(success=True)

    def _process_payment(self, request):
        # Business logic here
        return saga_pb2.SagaParticipantResponse(success=True)

    def _release_inventory(self, request):
        # Compensation logic here
        return saga_pb2.SagaParticipantResponse(success=True)

    def _refund_payment(self, request):
        refund_data = {
            "transaction_id": "txn_12345",
            "amount": 100.00,
            "currency": "USD",
            "status": "refunded",
            "timestamp": "2023-07-20T12:00:00Z",
        }
        # Compensation logic here
        return saga_pb2.SagaParticipantResponse(
            success=True, result_payload=json.dumps(refund_data).encode("utf-8")
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service_base.run_participant_server(ExampleService(),port=50053)