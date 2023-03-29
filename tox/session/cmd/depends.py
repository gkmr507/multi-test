from __future__ import annotations

from typing import cast

from tox.config.cli.parser import ToxParser
from tox.plugin import impl
from tox.session.cmd.run.common import env_run_create_flags, run_order
from tox.session.state import State
from tox.tox_env.runner import RunToxEnv


@impl
def tox_add_option(parser: ToxParser) -> None:
    our = parser.add_command(
        "depends",
        ["de"],
        "visualize tox environment dependencies",
        depends,
    )
    env_run_create_flags(our, mode="depends")


def depends(state: State) -> int:
    to_run_list = list(state.envs.iter(only_active=False))
    order, todo = run_order(state, to_run_list)
    print(f"Execution order: {', '.join(order)}")

    deps: dict[str, list[str]] = {k: [o for o in order if o in v] for k, v in todo.items()}
    deps["ALL"] = to_run_list

    def _handle(at: int, env: str) -> None:
        print("   " * at, end="")
        print(env, end="")
        if env != "ALL":
            run_env = cast(RunToxEnv, state.envs[env])
            packager_list: list[str] = []
            try:
                for pkg_env in run_env.package_envs:
                    packager_list.append(pkg_env.name)
            except Exception as exception:
                packager_list.append(f"... ({exception})")
            names = " | ".join(packager_list)
            if names:
                print(f" ~ {names}", end="")
        print("")
        at += 1
        for dep in deps[env]:
            _handle(at, dep)

    _handle(0, "ALL")
    return 0
