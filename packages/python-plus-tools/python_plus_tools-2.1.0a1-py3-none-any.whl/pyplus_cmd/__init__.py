"""
The python Plus - Pyplus
================
the python's plus library.\n
"""

from os import makedirs, getenv
from pathlib import Path
from site import getsitepackages

from sys import version_info
from toml import load, dump

global_config_path = Path(getenv("appdata"), "xystudio", "pyplus", "config.toml")
local_config_path = Path(".xystudio", "pyplus", "config.toml").absolute()
global_config = {}
local_config = {}
union_config = {}

LOCAL = "local"
GLOBAL = "global"

ALL = "all"
NEW = "news"
WILL = "will"

makedirs(global_config_path.parent, exist_ok=True)

if not global_config_path.exists():
    global_config_path.touch()
else:
    with open(global_config_path, "r", encoding="utf-8") as f:
        global_config = load(f)

if global_config.get("library", {"autoCreateLocalConfig": True}).get(
    "autoCreateLocalConfig", True
):
    makedirs(local_config_path.parent, exist_ok=True)
    if not (local_config_path.exists()):
        local_config_path.touch()

try:
    with open(local_config_path, "r", encoding="utf-8") as f:
        local_config = load(f)
except FileNotFoundError:
    pass

first_used_config = global_config.get("library", {"firstUsedConfig": "local"}).get(
    "firstUsedConfig", "local"
)

if first_used_config == "local":
    union_config = global_config | local_config
else:
    union_config = local_config | global_config

with open(
    getsitepackages()[1] + "\\pyplus\\data\\config\\update.toml", "r", encoding="utf-8"
) as f:
    updates = load(f)

with open(
    getsitepackages()[1] + "\\pyplus\\data\\config\\get_config.toml",
    "r",
    encoding="utf-8",
) as f:
    config_help = load(f)


def get_version(namespace: str) -> str:
    """Get the version."""
    return updates["release"][namespace]["version"]


def get_pre_version() -> str:
    """Get the pre version."""
    return updates["pre-release"]["version"]


def open_doc(doc_name: str):
    raise NotImplementedError("Document is not completed.")


def config(config_name: str, value, config_type=first_used_config):
    global local_config, global_config

    if config_type == LOCAL:
        makedirs(local_config_path.parent, exist_ok=True)
        if not (local_config_path.exists()):
            local_config_path.touch()

        config_split = config_name.split(".", 1)
        config_char_1 = config_split[0]
        try:
            config_char_2 = config_split[1]
        except IndexError:
            raise ValueError("config name must use 'a.b'.")

        with open(local_config_path, "w+", encoding="utf-8") as f:
            config = load(f) | {config_char_1: {config_char_2: value}}
            local_config |= config
            dump(config, f)
    elif config_type == GLOBAL:
        config_split = config_name.split(".")
        config_char_1 = config_split[0]
        try:
            config_char_2 = config_split[1]
        except IndexError:
            raise ValueError("config name must use 'a.b'.")

        with open(global_config_path, "w+", encoding="utf-8") as f:
            config = load(f) | {config_char_1: {config_char_2: value}}
            global_config |= config
            dump(config, f)
    else:
        raise ValueError("This config type not found.")
    union_config |= config


def get_config(config_name: str):
    try:
        config_split = config_name.split(".")
        config_char_1 = config_split[0]
        try:
            config_char_2 = config_split[1]
            return union_config[config_char_1][config_char_2]
        except IndexError:
            raise ValueError("config name must use two texts, example : 'a.b'.")
    except KeyError:
        return None


def get_config_help(config_type=ALL):
    if config_type == ALL:
        for config_t, config_docs in config_help.items():
            print("*" * 22 + "-" * 8 + config_t + "-" * 8 + "*" * 22)
            for doc_name, doc_des in config_docs.items():
                print()
                print(f"{doc_name} : {doc_des}")
            print(f"\n{'-'*30}\n")
        print("\nWhen you set config,you need use 'paragraph name.config name'")
    else:
        print("*" * 22 + "-" * 8 + config_type + "- " * 8 + "*" * 22)
        try:
            for doc_name, doc_des in config_help[config_type].items():
                print(f"{doc_name} : {doc_des}")
        except KeyError:
            print("This document is not found.")
        else:
            print("When you set config,you need use 'paragraph name.config name'")


__version__ = get_version("main")


def main() -> None:
    import argparse

    class globalAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_global", values)

    class allAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_all", values)

    class localAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_local", values)

    parser = argparse.ArgumentParser(description="imgfit commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_cmd = subparsers.add_parser(
        "config",
        help="Set the config setting.Usage 'pyplus get_config' to get all config.",
    )
    config_namespace = config_cmd.add_subparsers(dest="namespace", required=True)
    config_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    config_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )
    config_cmd.add_argument("setting", help="Config setting.")
    config_cmd.add_argument("value", help="Config value.")

    subparsers.add_parser("version", help="Get the pyplus version.")

    get_conf_help = subparsers.add_parser(
        "get_config_help", help="Get the config help."
    )
    get_conf_help.add_argument(
        "-d",
        "--document_description",
        nargs="?",
        help="get one document description.",
        default=ALL,
    )

    get_conf = subparsers.add_parser("get_config", help="Get the config.")
    get_conf.add_argument(
        "-l", "--local", nargs="?", action=localAction, help="Output the local config."
    )
    get_conf.add_argument(
        "-g",
        "--global",
        action=globalAction,
        nargs="?",
        help="Output the global config.",
    )
    get_conf.add_argument(
        "-a", "--all", nargs="?", action=allAction, help="Output all the config."
    )

    args = parser.parse_args()

    if args.command == "config":
        if args.value.lower() == "true":
            value = True
        elif args.value.lower() == "false":
            value = False
        else:
            value = args.value
        print("Run code again to set the config.")
        config(args.setting, value, args.namespace)
    elif args.command == "version":
        print("Version : pyplus pre:", get_pre_version)
        print("Version : pyplus :", get_version())
    elif args.command == "get_config_help":
        get_config_help(args.document_description)
    elif args.command == "get_config":
        if hasattr(args, "_local"):
            print(local_config)
        if hasattr(args, "_global"):
            print(global_config)
        if hasattr(args, "_all"):
            print(union_config)


del getsitepackages, Path, getenv, version_info

if __name__ == "__main__":
    main()
