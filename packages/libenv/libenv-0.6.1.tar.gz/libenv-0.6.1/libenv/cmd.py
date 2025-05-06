from typing import Dict, Tuple

def quote(x: str) -> str:
    """quote - appropriate for rc shell
    """
    return "'" + x.replace("'", "''") + "'"

def expand_vars(env: Dict[str,str], prefix: str = "") -> Tuple[str,str]:
    """expand variables - create list variables that expand
    their values and then turn them into whitespace-separated data.

    Note: this destroys any list structure in the variables created.

    Returns: list-variable creation statements and their shell expansions.

    >>> expand_vars({'a': '-I $HOME -L /usr/lib', 'b': '$SHELL:$SHELL'}, "-D")
    ('a=(-I $HOME -L /usr/lib) b=($SHELL:$SHELL)', '-Da=$"a -Db=$"b')
    """
    stmts = []
    results = []
    for k, v in env.items():
        stmts.append(f"{k}=({v})") # shell expand variables
        results.append(f"{prefix}{k}=$\"{k}") # turn into a space-separated string
    return " ".join(stmts), " ".join(results)


class Cmd:
    def __init__(self, x, once):
        self.x = x
        self.once = once
    def __str__(self):
        return self.x

class Script:
    """ A script is modeled as a monoid (associative,
        with empty + addition rules),
        where append joins all commands together in-order.

        Commands marked "once" are only appended 
    """
    def __init__(self) -> None:
        self.cmds : list[Cmd] = []
        self.done : set[str] = set() # (invariant)= set(c.x for c in self.cmds)

    def _append(self, cmd : Cmd) -> None:
        "Internal, unguarded append of cmd."
        if len(cmd.x.strip()) == 0:
            return
        self.done.add( cmd.x )
        self.cmds.append( cmd )

    def run(self, cmd : Cmd) -> None:
        if cmd.once and cmd.x in self.done:
            return
        self._append(cmd)

    def extend(self, rhs : "Script") -> "Script":
        """ In-place update by extending self
            with the commands from the right-hand side.
            This is the monoid addition rule.
        """
        for c in rhs.cmds:
            if c.once and c.x in self.done:
                continue
            self._append(c)
        return self

    def __str__(self) -> str:
        if len(self.cmds) == 0:
            return ""
        return ";\n".join( map(str, self.cmds) ) + ";\n"

def run(*cmds : str) -> Script:
    S = Script()
    for cmd in cmds:
        S.run( Cmd(cmd, False) )
    return S

def runonce(*cmds : str) -> Script:
    S = Script()
    for cmd in cmds:
        S.run( Cmd(cmd, True) )
    return S
