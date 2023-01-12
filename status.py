import json
import os
import logging
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined, config
from datetime import datetime, timezone

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Status:
    last_run:datetime = datetime.min.replace(tzinfo=timezone.utc)

    @classmethod
    def load(cls):
        if os.path.exists("status.json"):
            with open("status.json", 'r') as file:
                try:
                    #j = json.load(file)
                    raw_json = file.read()
                    s = Status.from_json(raw_json)
                    return s
                except Exception as exc:
                    logging.debug(exc)
        return Status()

    def save(self):
        j = self.to_json(indent=2)
        with open("status.json", 'w') as file:
            file.write(j)
