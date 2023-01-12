import argparse
import logging
import yaml
import dateutil.parser
from dateutil.tz import tzlocal
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

from kopiaapi import KopiaApi
from emailutil import Email
from repoinfo import RepoInfo
from status import Status

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-c", default="config.yaml", action="store", dest="config_file", help="path to the config file")
args= parser.parse_known_args()


def render(config:any, data:any) -> None:
    templateFile:str = config.get("template", "report.template")
    if "." not in templateFile:
        templateFile += '.template'

    env = Environment(loader=FileSystemLoader('templates'), lstrip_blocks=True, trim_blocks=True)
    env.filters["to_date"] = lambda value: dateutil.parser.isoparse(value)
    template = env.get_template(templateFile)
    template.globals['now'] = datetime.now(tz=timezone.utc)
    template.globals['config'] = config
    return template.render(data=data)

with open(args.config_file, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.debug(exc)
        exit(1)

status = Status.load()
all_repos = []
error_count = 0
send_email = False
for repo in config["repositories"]:
    repo_info = RepoInfo.create(repo, status.last_run)
    error_count += repo_info.error_count
    if repo_info.inactivity_error:
        error_count += 1
    send_email = send_email or repo_info.should_render

    all_repos.append(repo_info)

if send_email:
    html = render(config, all_repos )
    #print(html)
    em = Email(config["email"])
    em.send(html, error_count>0)

status.last_run = datetime.now(tz=timezone.utc)
status.save()
