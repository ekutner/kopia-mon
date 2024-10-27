import argparse
import logging
import yaml
import dateutil.parser
from pathlib import Path
from dateutil.tz import tzlocal
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

from kopiaapi import KopiaApi
from emailutil import Email
from repoinfo import RepoInfo
from status import Status

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-c", default="config.yaml", action="store", dest="config_file", help="path to the config file")
parser.add_argument("-v", default=False, action="store_true", dest="verbose", help="Output verbose log information to the console")
parser.add_argument("--no-send-email", default=True, action="store_false", dest="send_email", help="Write the report to stdout instead of sending it by email")
parser.add_argument("--set-exit-code", default=False, action="store_true", dest="set_exit_code", help="Sets non-standard exit codes, see the README for details")

args = parser.parse_args()

if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

def render(config:dict, data:list[dict]) -> str:
    templateFile:str = config.get("template", "report.template")
    if "." not in templateFile:
        templateFile += '.template'

    env = Environment(loader=FileSystemLoader('templates'), lstrip_blocks=True, trim_blocks=True)
    env.filters["to_date"] = lambda value: dateutil.parser.isoparse(value)
    template = env.get_template(templateFile)
    template.globals['now'] = datetime.now(tz=timezone.utc)
    template.globals['config'] = config
    return template.render(data=data)

if not Path(args.config_file).exists():
    logging.error("Config file doesn't exist at the specified path: %s", args.config_file)
    exit(1)

with open(args.config_file, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error("Invalid YAML syntax", exc_info=exc)
        exit(1)

if args.verbose:
    logging.info("Config file is loaded")

status = Status.load()
all_repos = []
error_count = 0
generate_report = False
for repo in config["repositories"]:
    logging.debug("Processing repo: %s", repo)
    repo_info = RepoInfo.create(repo, status.last_run)
    error_count += repo_info.error_count
    if repo_info.inactivity_error:
        error_count += 1
    generate_report = generate_report or repo_info.should_render

    all_repos.append(repo_info)

if generate_report:
    html = render(config, all_repos )
    if args.send_email:
        em = Email(config["email"])
        em.send(html, error_count>0)
    else:
        print(html)
status.last_run = datetime.now(tz=timezone.utc)
status.save()

if args.set_exit_code:
    if generate_report:
        if error_count>0:
            exit(6)
        else:
            exit(2)
