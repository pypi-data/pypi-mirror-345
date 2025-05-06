from ..envtype import EnvType
from .. import cmd
from ..config import Config

spack_root = "$prefix/share/spack"
spack_url = "https://github.com/spack/spack.git"
stutter = lambda x: f"{spack_root}/{x}/spack"
fix_csh_setenv = r"sed -n -e 's/^setenv \([^ ]*\) \(.*\);$/\1=''\2'';/p'"
spack_load = lambda x: "eval `{ %s load --csh %s | %s }" % (
                stutter("bin"), x, fix_csh_setenv)

setup_spack = [f"SPACK_ROOT = {spack_root}",
               "SPACK_USER_CACHE_PATH  = $SPACK_ROOT/.cache",
               "SPACK_USER_CONFIG_PATH = $SPACK_ROOT/.spack"]

class Spack(EnvType):
    specs: list[str]

    def installScript(self, config: Config) -> cmd.Script:
        cmds = [ f"[ -d {spack_root} ] || git clone {spack_url} {spack_root}"
               ] + setup_spack
        for spec in self.specs:
            cmds.append("{} install {}".format(
                    stutter("bin"), cmd.quote(spec)))
        return cmd.runonce(*cmds)
    def loadScript(self, config: Config) -> cmd.Script:
        cmds = [s for s in setup_spack]
        for spec in self.specs:
            cmds.append(spack_load(cmd.quote(spec)))
        return cmd.runonce(*cmds)
