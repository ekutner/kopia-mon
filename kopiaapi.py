from datetime import datetime, timezone
import json
import subprocess
import re
from dataclasses import dataclass


@dataclass
class SnapshotVerifyResult:
    blob_count: int
    processed_count: int
    errors: list[str]
    error_count: int
    timestamp: datetime = datetime.min.replace(tzinfo=timezone.utc)
    run_time: int = 0

@dataclass
class ContentVerifyResult:
    contents_count: int
    error_count: int
    errors: list[str]
    timestamp: datetime = datetime.min.replace(tzinfo=timezone.utc)
    run_time: int = 0

class KopiaApi:

    # Allow injecting a custom kopia command for testing
    def __init__(self, config_file:str, kopia_command=None):
        self._config_file = config_file
        self._kopia_command = kopia_command if kopia_command else self._kopia_command_default

    def _kopia_command_default(self, args:list[str], json_result=True):
        args.append(f"--config-file={self._config_file}")
        with subprocess.Popen(["kopia", *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
            res = proc.stdout.read().decode('utf-8')
            if json_result:
                return json.loads(res)
            return res

    def get_repo_status(self) -> dict:
        args = ["repo", "status", "--json"]
        status = self._kopia_command(args)
        return status

    def get_snapshot_list(self) -> list:
        args = ["snapshot", "list", "--json"]
        snapshots = self._kopia_command(args)
        return snapshots

    def get_show_obj(self, obj_id) -> dict:
        args = ["show", obj_id ]
        show = self._kopia_command(args)
        return show

    def snapshot_verify(self, percent:float=1, file_parallelism:int=10, parallel:int=10) -> SnapshotVerifyResult:
        args = ["snapshot", "verify", f"--verify-files-percent={str(percent)}", f"--file-parallelism={file_parallelism}", f"--parallel={parallel}"]
        run_start_time = datetime.now(tz=timezone.utc)
        verify_res = self._kopia_command(args, json_result=False)
        blob_count_regex = r"Listed (\d+) blobs"
        blob_count = re.search(blob_count_regex, verify_res).group(1)
        processed_count_regex = r"Finished processing (\d+) objects"
        processed_count = re.search(processed_count_regex, verify_res).group(1)
        errors = re.findall(r"ERROR (.*?)\n", verify_res, re.MULTILINE|re.IGNORECASE)
        return SnapshotVerifyResult(
            blob_count=int(blob_count),
            processed_count=int(processed_count),
            errors=errors,
            error_count=len(errors),
            timestamp=run_start_time,
            run_time=(datetime.now(tz=timezone.utc) - run_start_time).total_seconds()
        )
        # return SnapshotVerifyResult(
        #     blob_count=100482,
        #     processed_count=289957,
        #     errors=[
        #         "error processing eran@homepc:C:\\Users\\eran@2025-02-01 01:59:58 IST/AppData/Local/Google/DriveFS/Logs/drive_fs_232.txt: error reading object 5f0e8088163c1b71075bfa540ddacb95: unable to open object 5f0e8088163c1b71075bfa540ddacb95: unexpected content error: invalid checksum at p8dec91ff45a45091b370164a6a27dc89-s6ab50597524a9eca12b offset 8534285 length 36352/36352: decrypt: Error computing ECC: no shard data",
        #         "error reading object 5f0e8088163c1b71075bfa540ddacb95: unable to open object 5f0e8088163c1b71075bfa540ddacb95: unexpected content error: invalid checksum at p8dec91ff45a45091b370164a6a27dc89-s6ab50597524a9eca12b offset 8534285 length 36352/36352: decrypt: Error computing ECC: no shard data"
        #     ],
        #     error_count=0,
        #     timestamp=datetime.now(tz=timezone.utc),
        #     run_time=5000.0
        # )


    def content_verify(self, percent:float=1, parallel:int=10) -> ContentVerifyResult:
        args = ["content", "verify", f"--verify-files-percent={str(percent)}", f"--parallel={parallel}", "--json"]
        run_start_time = datetime.now(tz=timezone.utc)
        verify_res = self._kopia_command(args, json_result=False)
        error_regex = r"ERROR (?'error'.*)"
        errors = re.findall(error_regex, verify_res)

        summary_regex = r"Finished verifying (\d+) contents, found (\d+) errors"
        summary = re.search(summary_regex, verify_res)

        return ContentVerifyResult(
            contents_count=int(summary.group(1)),
            error_count=int(summary.group(2)),
            errors=errors,
            timestamp=datetime.now(tz=timezone.utc),
            run_time=(datetime.now(tz=timezone.utc) - run_start_time).total_seconds()
        )
