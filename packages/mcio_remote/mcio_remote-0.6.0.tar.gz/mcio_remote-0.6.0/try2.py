import sys
from collections import defaultdict
from typing import Any

import mcio_remote as mcio
from mcio_remote.envs import minerl_env


def run() -> None:
    opts = mcio.types.RunOptions.for_connect()
    env = minerl_env.MinerlEnv(opts, render_mode="human")

    setup_commands = [
        # "time set 0t",  # Just after sunrise
        # "teleport @s ~ ~ ~ -90 0",  # face East
    ]
    print("RESET")
    observation, info = env.reset(options={"commands": setup_commands})
    print(env.health)
    env.render()
    print("RESET DONE")

    action: dict[str, Any] = defaultdict(int)
    action["camera"] = [0, 1]

    terminated = False
    for i in range(25):
        # input(f"{i}> ")
        observation, reward, terminated, truncated, info = env.step(action)
        # print(env.health)
        env.render()
    print("Terminated")
    # env.step(action)

    env.close()


def setup() -> None:
    ctrl = mcio.controller.ControllerSync()

    setup_commands = [
        "time set 0t",  # Just after sunrise
        "teleport @s ~ ~ ~ -90 0",  # face East
    ]
    pkt = mcio.network.ActionPacket(commands=setup_commands)
    ctrl.send_action(pkt)
    obs = ctrl.recv_observation()
    print(f"RESET: curr={obs.cursor_pos}")

    null_pkt = mcio.network.ActionPacket()
    for i in range(25):
        ctrl.send_action(null_pkt)
        obs = ctrl.recv_observation()
        print(f"{i}: curr={obs.cursor_pos}")

    ctrl.close()


def reset_test() -> None:
    opts = mcio.types.RunOptions.for_connect(width=100, height=100)
    env = minerl_env.MinerlEnv(opts, render_mode="human")
    setup_commands = [
        "kill @e[type=!player]",
        "summon minecraft:pillager ~2 ~2 ~2",
        # "time set 0t",  # Just after sunrise
        # "teleport @s ~ ~ ~ -90 0",  # face East
    ]
    print("RESET")
    observation, info = env.reset(options={"commands": setup_commands})
    print(env.health)
    env.render()
    print("RESET DONE")

    action: dict[str, Any] = defaultdict(int)
    action["camera"] = [0, 1]

    while not env.terminated:
        observation, reward, terminated, truncated, info = env.step(action)
        # print(env.health)
        env.render()

    print("Terminated")

    print("RESET 2")
    observation, info = env.reset()
    print(env.health)
    env.render()
    print("RESET 2 DONE")
    while not env.terminated:
        observation, reward, terminated, truncated, info = env.step(action)
        # print(env.health)
        env.render()

    env.close()


def asynk() -> None:
    opts = mcio.types.RunOptions(mcio_mode=mcio.types.MCioMode.ASYNC)
    env = minerl_env.MinerlEnv(opts, render_mode="human")
    setup_commands = [
        "kill @e[type=!player]",
        "summon minecraft:pillager ~2 ~2 ~2",
        # "time set 0t",  # Just after sunrise
        # "teleport @s ~ ~ ~ -90 0",  # face East
    ]
    print("RESET")
    observation, info = env.reset(options={"commands": setup_commands})
    print(env.health)
    env.render()
    print("RESET DONE")

    action: dict[str, Any] = defaultdict(int)
    action["camera"] = [0, 0]

    while not env.terminated:
        observation, reward, terminated, truncated, info = env.step(action)
        # print(env.health)
        env.render()

    print("Terminated")

    print("RESET 2")
    observation, info = env.reset()
    print(env.health)
    env.render()
    print("RESET 2 DONE")
    while not env.terminated:
        observation, reward, terminated, truncated, info = env.step(action)
        # print(env.health)
        env.render()

    env.close()


if __name__ == "__main__":
    mcio.util.logging_init()

    if len(sys.argv) != 2:
        print("Usage: python script.py <function_name>")
        print(
            "Available commands:",
            ", ".join(
                fn
                for fn in globals()
                if callable(globals()[fn]) and not fn.startswith("_")
            ),
        )
        sys.exit(1)

    cmd = sys.argv[1]
    fn = globals().get(cmd)
    if not callable(fn):
        print(f"No such command: {cmd}")
        sys.exit(1)

    fn()
