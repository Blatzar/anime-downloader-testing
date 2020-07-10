#!/bin/env python3
import os
import sys
import click
import tempfile
import uuid
import subprocess
import json
import re 

tempdir = tempfile.gettempdir()

@click.command()
@click.argument('branch_url')

@click.option(
    '--branch', '-b', 'branch', metavar='FORMAT STRING', 
    help="branch name for the specified PR",
    default='master'
)

@click.option(
    '--download-dir','-d','download_dir', metavar='PATH',
    help="Specifiy the directory to download to",default=tempdir
)

@click.option(
    '--provider','-p','provider', metavar='FORMAT STRING',
    help="provider name to test",default=None
)

@click.option(
    '--show','-s','show', metavar='FORMAT STRING',
    help="show name to test",default="neverland"
)

@click.pass_context
def command(ctx, branch_url, branch, download_dir, provider, show):
    _uuid = uuid.uuid1()
    github_regex = r'(https:.*?anime-downloader/)(tree/([^/]*)|)'
    if re.search(github_regex,branch_url).group(3):
        branch = re.search(github_regex,branch_url).group(3)
        print(f'Branch updated to: "{branch}"')
    if re.search(github_regex,branch_url).group(1):
        branch_url = re.search(github_regex,branch_url).group(1)
        print(f'Branch url updated to: "{branch_url}"')
    path = f'{download_dir}/anime_downloader_{branch}_{_uuid}'
    pipe = '> /dev/null 2>&1'
    os.system(f'git clone -b {branch} {branch_url} {path}')
    os.system(f'virtualenv {path} {pipe} && source {path}/bin/activate {pipe} && cd {path} && python3 setup.py install')
    sys_path = sys.path[:]
    sys.path = json.loads(os.popen(f'{path}/bin/python3 -c "import sys;print(sys.path)"').read()[:-1].replace("'",'"'))
    from anime_downloader.sites import ALL_ANIME_SITES, get_anime_class
    sitenames = [v[1] for v in ALL_ANIME_SITES]
    from anime_downloader.config import Config
    provider = provider if provider else sitenames[-1]
    print(f"Provider: {provider}")
    provider_conf = Config._CONFIG['siteconfig'].get(provider)
    #print(f"Config: {provider_conf}")
    #if 'servers' in provider_conf:
    #    servers = provider_conf['servers']
    #    print(f'Servers detected, will run {len(servers)} times')
    os.system(f"konsole --hold -e \"{path}/bin/anime -ll DEBUG dl -u -c 1 '{show}' --provider {provider}\"")

if __name__ == '__main__':
    command()
