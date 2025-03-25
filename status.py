import os
import logging
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined, config
from datetime import datetime, timezone
from repoinfo import RepoInfo

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Status:
    repos:dict[str, RepoInfo] = field(default_factory=lambda: dict())
    last_run:datetime = datetime.min.replace(tzinfo=timezone.utc)
    # last_snapshot_verify:datetime = datetime.min.replace(tzinfo=timezone.utc)
    # last_snapshot_verify_errors:int = 0
    # last_content_verify:datetime = datetime.min.replace(tzinfo=timezone.utc)
    # last_content_verify_errors:int = 0

    @classmethod
    def load(cls):
        if os.path.exists("status.json"):
            with open("status.json", 'r', encoding="utf-8") as file:
                try:
                    #j = json.load(file)
                    raw_json = file.read()
                    s = Status.from_json(raw_json)
                    return s
                except Exception as exc:
                    logging.error("Exception when loading status file - report this only if it repeats", exc_info=exc)
        return Status()

    def save(self):
        j = self.to_json(indent=2)
        with open("status.json", 'w') as file:
            file.write(j)
