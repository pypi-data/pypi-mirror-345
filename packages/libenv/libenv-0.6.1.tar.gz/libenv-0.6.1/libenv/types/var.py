from typing import Dict

from ..envtype import EnvType
from .. import cmd
from ..config import Config

class Var(EnvType):
    vars:    Dict[str, str] = {}
    append:  Dict[str, str] = {}
    prepend: Dict[str, str] = {}

    #def testScript(self) -> cmd.Script:
    #    """ TestScripts may return 3 different values,
    #        0 = success
    #        1 = not present (install needed)
    #        2 = present, but misconfigured/incompatible
    #    """
    #    return cmd.run("@ { exit 1 }")
    def installScript(self, config: Config) -> cmd.Script:
        #append  = "{k} = ${k}:{v}"
        #prepend = "{k} = {v}:${k}"
        # alternately, omit `:` if empty...
        append = "{{ ~ $#{k} 0 || {k}=$\"{k}:^({v}) }}; {{ ~ $#{k} 0 && {k}=({v}) }}; {k}=$\"{k}"
        prepend = "{{ ~ $#{k} 0 || {k}=({v})^:$\"{k} }}; {{ ~ $#{k} 0 && {k}=({v}) }}; {k}=$\"{k}"

        cmds = [f"{k} = ({v})" for k,v in self.vars.items()]
        cmds.extend([
             append.format(k=k, v=v)  for k,v in self.append.items()
                ])
        cmds.extend([
             prepend.format(k=k, v=v) for k,v in self.prepend.items()
                    ])
        return cmd.run(*cmds)

    def loadScript(self, config: Config) -> cmd.Script:
        return self.installScript(config)
