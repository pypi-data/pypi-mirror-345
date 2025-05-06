from typing import Dict, Optional, List

from ..envtype import EnvType
from ..config import Config
from .. import cmd

class Autotools(EnvType):
    source: str # name of directory containing source
    env: Dict[str, str] = {}
    configure: List[str] = []
    pre_configure: Optional[str] = None
    post_configure: Optional[str] = None
    post_install: Optional[str] = None

    def installScript(self, config: Config) -> cmd.Script:
        src = cmd.quote(self.source)
        env1, env2 = cmd.expand_vars(self.env)
        args = " ".join(map(cmd.quote, self.configure))
        cmds = []
        if self.pre_configure:
            cmds.append(self.pre_configure)
        cmds.append(f"cd {src}")
        cmds.append(f"{env1} {env2} ./configure --prefix=$prefix {args}")
        if self.post_configure:
            cmds.append(self.post_configure)
        cmds.extend([
                 f"{env1} {env2} make -j{config.concurrency} install",
                  "cd ..",
                 f"rm -fr {src}",
               ])
        if self.post_install:
            cmds.append(self.post_install)
        return cmd.run(*cmds)
    def loadScript(self, config: Config) -> cmd.Script:
        return cmd.Script()
