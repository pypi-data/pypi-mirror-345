import json
from datetime import datetime

def prettify_saga_response(response):
    # Convert protobuf/dict to structured format
    formatted = {
        "transaction_id": response.get('sagaId'),
        "status": response.get('status'),
        "timestamps": {
            "createdAt": response.get('createdAt'),
            "updatedAt": response.get('updatedAt'),
            "completedAt": response.get('steps', [{}])[-1].get('executedAt')
        },
        "steps": [],
        "summary": {
            "totalSteps": len(response.get('steps', [])),
            "successful": 0,
            "failed": 0,
            "compensated": 1 if "COMPENSAT" in response.get('status', '') else 0
        }
    }

    for step in response.get('steps', []):
        step_data = {
            "service": step.get('serviceName', '').split(':')[0].capitalize() + " Service",
            "endpoint": step.get('serviceName', ''),
            "operation": {
                "method": step.get('methodName', ''),
                "status": "SUCCESS" if step.get('success') else "FAILED",
                "executedAt": step.get('executedAt', '')
            }
        }

        if step.get('success'):
            formatted["summary"]["successful"] += 1
            if 'resultPayload' in step:
                step_data["result"] = step['resultPayload']
        else:
            formatted["summary"]["failed"] += 1

        formatted["steps"].append(step_data)
    
    return json.dumps(formatted, indent=2, ensure_ascii=False)