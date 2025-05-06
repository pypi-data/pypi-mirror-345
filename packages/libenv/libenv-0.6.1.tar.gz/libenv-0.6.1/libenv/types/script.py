from ..envtype import EnvType
from .. import cmd
from ..config import Config

class Script(EnvType):
    install: str
    load: str

    def installScript(self, config: Config) -> cmd.Script:
        return cmd.run( self.install )
    def loadScript(self, config: Config) -> cmd.Script:
        return cmd.run( self.load )
