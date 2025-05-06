import dataclasses
from datetime import datetime


@dataclasses.dataclass
class File:
    path: str
    contents: str
    git_history: str
    chars: int
    tokens: int
    last_author: str
    last_modified: datetime


@dataclasses.dataclass
class FileSize:
    path: str
    bytes: float
    last_modified: datetime
