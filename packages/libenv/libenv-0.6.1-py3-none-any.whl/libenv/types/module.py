from ..envtype import EnvType
from .. import cmd
from ..config import Config

class Module(EnvType):
    specs: list[str]
    unload: list[str] = []

    def installScript(self, config: Config) -> cmd.Script:
        # load the modules to ensure they are available to the
        # loadScript
        return cmd.run(*[f"module unload {cmd.quote(s)}" for s in self.unload]
                      ).extend(
               cmd.run(*[f"module load {cmd.quote(s)}" for s in self.specs])
                      )
    def loadScript(self, config: Config) -> cmd.Script:
        return cmd.run(*[f"module unload {cmd.quote(s)}" for s in self.unload]
                      ).extend(
               cmd.run(*[f"module load {cmd.quote(s)}" for s in self.specs])
                      )
