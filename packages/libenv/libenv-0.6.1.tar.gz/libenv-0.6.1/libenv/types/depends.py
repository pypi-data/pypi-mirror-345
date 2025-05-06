""" Recursively download and interpret (as inlined)
    environment specs from URL-s.

    We assume that all dependencies can be installed
    in parallel.  Each install gets run in a shell with
    the "load" step from all previous steps.

    After installing, the "load" steps from this block
    done in serial.

    TODO: re-implement cmd.Script class to describe this
    idea of parallel steps which take load-scripts as histories
    and create a "load then run make" script as their install
    process.

    This involves clever naming that will reveal common
    package dependencies (e.g. one subdir per dependency).
"""
from typing import Any, List
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

#from aurl import URL
from aurl import arun
from aurl.fetch import download_url

from .. import cmd
from ..config import Config
from ..envtype import EnvType, load_envfile

# TODO: force URL to refer to a git repo in the form,
# git+https://gitlab.com/frobnitzem/libenv.git
#
# then construct the download from
# git+https://gitlab.com/frobnitzem/libenv.git@<tag>:env.yaml
#
# i.e. repo = https://gitlab.com/frobnitzem/libenv.git
#      rev-parse = <tag>:env.yaml
async def fetch_env(config: Config, url: str) -> Any:
    with NamedTemporaryFile(mode="r", encoding="utf-8") as f:
        await download_url(f.name, url)
        return load_envfile(config, Path(f.name))

class Depends(EnvType):
    urls: List[str]

    def installScript(self, config: Config) -> cmd.Script:
        script = cmd.Script()
        for url in self.urls:
            specs = arun(fetch_env(config, url))
            for spec in specs:
                script.extend( spec.installScript(config) )
        return script
    def loadScript(self, config: Config) -> cmd.Script:
        script = cmd.Script()
        for url in self.urls:
            specs = arun(fetch_env(config, url))
            for spec in specs:
                script.extend( spec.loadScript(config) )
        return script
