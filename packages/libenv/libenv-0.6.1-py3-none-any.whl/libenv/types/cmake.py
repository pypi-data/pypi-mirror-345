from typing import Dict, Optional, Tuple

from ..envtype import EnvType
from ..config import Config
from .. import cmd

class Cmake(EnvType):
    source: str # name of directory containing source
    cmake: Dict[str, str] = {} # "C_COMPILER: gcc" ~> "-D C_COMPILER=gcc"
    env: Dict[str, str] = {}
    pre_configure: Optional[str] = None
    post_configure: Optional[str] = None
    post_install: Optional[str] = None

    def installScript(self, config: Config) -> cmd.Script:
        src = cmd.quote(self.source)
        build = cmd.quote(f"_build")

        env = "".join(f"{k}={cmd.quote(v)} " for k, v in self.env.items())
        env1, setenv = cmd.expand_vars(self.env)
        env2, setopts = cmd.expand_vars(self.cmake, "-D")

        cmds = [ f"rm -fr {build}" ]
        if self.pre_configure:
            cmds.append(self.pre_configure)
        cmds.append(f"{env1} {env2} cmake -B {build} -S {src} -DCMAKE_INSTALL_PREFIX=$prefix {setopts}")
        if self.post_configure:
            cmds.append(self.post_configure)
        cmds.append( f"make -j{config.concurrency} -C {build} install" )
        if self.post_install:
            cmds.append(self.post_install)
        cmds.append( f"rm -fr {build} {src}" )
        return cmd.run(*cmds)

    def loadScript(self, config: Config) -> cmd.Script:
        return cmd.Script()
