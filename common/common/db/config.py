from dataclasses import dataclass
from typing import Dict


class Config(object):
    def to_dict(self) -> Dict:
        return self.__dict__.copy()


@dataclass
class ArangoCredentials(Config):
    username: str
    password: str


@dataclass
class ArangoConfig(Config):
    db_name: str
    hostname: str
    port: int
    credentials: ArangoCredentials
