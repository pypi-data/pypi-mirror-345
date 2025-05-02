import psycopg2
from ...core.models import SagaInstance
from ...core.storage.base import SagaStorage


class Postgrestorage(SagaStorage):
    def __init__(self, dsn: str):
        self.conn = psycopg2.connect(dsn)

    def save_saga(self, saga: SagaInstance):
        with self.conn.cursor() as cur:
            cur.execute(query="")
        self.conn.commit()
        return True
