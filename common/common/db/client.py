 
from typing import Dict, Iterable
from arango.client import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ServerConnectionError
from common.db.config import ArangoConfig, ArangoCredentials
import logging

from common.db.exception import ArangoConnectionError

logger = logging.getLogger()
SYSTEM_DB = "_system"


def connect_to_db(client: ArangoClient,
                  config: ArangoConfig) -> StandardDatabase:
    return client.db(**config.credentials.to_dict(),
                     name=SYSTEM_DB,
                     verify=True)


def initialize_db(client: ArangoClient,
                  config: ArangoConfig) -> None:
    try:
        db: StandardDatabase = connect_to_db(client=client,
                                             config=config)
        db.create_database(config.db_name)
        return
    except ServerConnectionError:
        raise ArangoConnectionError("Arango client has bad credentials.")


class ArangoConnectionClient(object):
    def __init__(self, db: StandardDatabase):
        self._db: StandardDatabase = db

    @classmethod
    def build(cls, config: ArangoConfig):
        client: ArangoClient = ArangoClient(hosts=f"http://{config.hostname}:{config.port}")
        try:
            db: StandardDatabase = connect_to_db(client=client, config=config)
            return cls(db=db)
        except ServerConnectionError:
            initialize_db(client=client, config=config)
            return cls.build(config=config)
        

    def add_documents(document: Iterable[Dict]) -> None:
        return