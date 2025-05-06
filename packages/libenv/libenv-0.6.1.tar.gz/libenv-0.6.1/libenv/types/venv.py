from ..envtype import EnvType
from .. import cmd
from ..config import Config

class Venv(EnvType):
    python: str = "python3"
    system_site_packages: bool = False
    specs: list[str] = []

    def installScript(self, config: Config) -> cmd.Script:
        opts = ""
        if self.system_site_packages:
            opts = " --system-site-packages"
        python = cmd.quote(self.python)
        cmds = [ f"{python} -m venv --upgrade-deps" + opts + " $prefix",
                 "VIRTUAL_ENV=$prefix"
               ]
        for spec in self.specs:
            cmds.append("pip --cache-dir {} --no-input --require-virtualenv install {}".format(config.cache_dir/"pip", cmd.quote(spec)))
        return cmd.runonce(*cmds)

    def loadScript(self, config: Config) -> cmd.Script:
        return cmd.runonce("VIRTUAL_ENV=$prefix")
