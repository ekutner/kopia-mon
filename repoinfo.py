
from collections import namedtuple
import glob
import os
import platform
import typing
import dateutil.parser
from typing import Self
from dataclasses import dataclass, field
from datetime import datetime, timezone
from kopiaapi import KopiaApi

@dataclass
class FileInfo:
    path:str = None
    time:datetime = None

@dataclass
class RepoInfo:
    config:dict
    status:dict = None
    snapshots:list[dict] = field(default_factory=lambda: list())
    last_snapshot:datetime = datetime.min.replace(tzinfo=timezone.utc)
    error_count:int = 0
    inactivity_error:bool = False
    sources:list[dict] = field(default_factory=lambda: list())
    last_modified_file:FileInfo = None
    should_render:bool = False
    hosts:set[str] = field(default_factory=lambda: set())

    def _update_last_modified_file(self) -> None:
        hostname = platform.node().lower()

        for source in self.sources:
            if source["host"] == hostname:
                files = glob.iglob(f"{source['path']}{os.sep}**", recursive=True)
                file_path = max(files, key=os.path.getmtime)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
                if self.last_modified_file.time is None or self.last_modified_file.time < file_time:
                    self.last_modified_file.path = file_path
                    self.last_modified_file.time = file_time

    def _update(self) -> Self:
        if len(self.snapshots) == 0 and (datetime.now(tz=timezone.utc) - self.last_snapshot).total_seconds() > self.config["inactivity_days"]*3600*24:
            self.inactivity_error = True
            if self.config["validate_inactivity"]:
                self.last_modified_file = FileInfo() #{ "path": None, "time": None }
                self._update_last_modified_file()
                if self.last_modified_file.time < self.last_snapshot:
                    self.inactivity_error = False

        if (not self.config["errors_only"]) or self.error_count>0 or self.inactivity_error:
            self.should_render = True
        return self

    @classmethod
    def create(cls, repo_conf:dict, min_time=None) -> Self:
        repo = RepoInfo(config=repo_conf)

        kopia = KopiaApi(repo_conf["config-file"])

        repo.status = kopia.get_repo_status()
        snapshots = kopia.get_snapshot_list()
        for snapshot in snapshots:
            source = snapshot["source"]
            if not any(s["host"]==source["host"] and s["path"]==source["path"] for s in repo.sources ):
                repo.sources.append(source)
            repo.hosts.add(f"{source['host']}@{source['host']}")
            start_time = dateutil.parser.isoparse(snapshot["startTime"])
            if start_time > repo.last_snapshot:
                repo.last_snapshot = start_time
            if min_time is None or start_time > min_time :
                if snapshot["stats"]["errorCount"] > 0:
                    repo.error_count += 1
                    show = kopia.get_show_obj(snapshot["rootEntry"]["obj"])
                    errors = show["summary"]["errors"]
                    snapshot["errors"] = errors
                repo.snapshots.append(snapshot)

        return repo._update()


