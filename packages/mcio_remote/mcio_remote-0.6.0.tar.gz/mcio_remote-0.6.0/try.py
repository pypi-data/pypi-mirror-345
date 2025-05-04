import sys
from collections import defaultdict
from typing import Any

import mcio_remote as mcio
from mcio_remote.envs import minerl_env


def run2() -> None:
    opts = mcio.types.RunOptions.for_connect()
    env = minerl_env.MinerlEnv(opts, render_mode="human")
    setup_commands = []
    print("RESET")
    observation, info = env.reset(options={"commands": setup_commands})
    print(env.health)
    env.render()
    print("RESET DONE")

    action: dict[str, Any] = defaultdict(int)
    action["camera"] = [0, 0]

    terminated = False
    i = 0
    while not terminated:
        # input(f"{i}> ")
        i += 1
        observation, reward, terminated, truncated, info = env.step(action)
        print(env.health)
        env.render()
    print("Terminated")
    # env.step(action)

    env.close()


def run1() -> None:
    opts = mcio.types.RunOptions.for_connect()
    env = minerl_env.MinerlEnv(opts, render_mode="human")
    setup_commands = [
        "time set 0t",  # Just after sunrise
        "teleport @s ~ ~ ~ -90 0",  # face East
        "kill @e[type=!player]",
        "summon minecraft:pillager ~2 ~2 ~2",
    ]
    print("RESET")
    observation, info = env.reset(options={"commands": setup_commands})
    print(env.health)
    env.render()
    print("SKIP")
    env.skip_steps(25)  # Give time for the commands to complete
    print("SKIP DONE")
    env.render()

    action: dict[str, Any] = defaultdict(int)
    action["camera"] = [0, 1]

    terminated = False
    while not terminated:
        observation, reward, terminated, truncated, info = env.step(action)
        print(env.health)
        env.render()
    print("Terminated")
    env.step(action)

    env.close()


if __name__ == "__main__":

    mcio.util.logging_init()

    if len(sys.argv) != 2:
        print("Need cmd")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "run1":
        run1()
    elif cmd == "run2":
        run2()
