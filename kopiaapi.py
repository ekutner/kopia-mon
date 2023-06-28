import json
import subprocess

class KopiaApi:

    def __init__(self, config_file:str):
        self._config_file = config_file

    def _kopia_command(self, args:list[str]):
        args.append(f"--config-file={self._config_file}")
        with subprocess.Popen(["kopia", *args], stdout=subprocess.PIPE) as proc:
            res = proc.stdout.read()
            return json.loads(res)

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
