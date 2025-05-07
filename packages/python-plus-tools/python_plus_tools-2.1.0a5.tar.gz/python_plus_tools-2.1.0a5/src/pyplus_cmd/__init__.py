from os import makedirs
from pathlib import Path
from site import getsitepackages

from toml import load, dump

global_config_path = Path.home() / "appdata" / "xystudio" / "pyplus" / "config.toml"
local_config_path = Path.cwd() / ".xystudio" / "pyplus" / "config.toml"
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
    getsitepackages()[1] + "\\pyplus\\data\\config\\config_help.toml",
    "r",
    encoding="utf-8",
) as f:
    config_help = load(f)

with open(
    getsitepackages()[1] + "\\pyplus\\data\\config\\alias.toml", "r", encoding="utf-8"
) as f:
    lang_alias = load(f)

with open(
    getsitepackages()[1] + "\\pyplus\\data\\config\\doc_help.toml",
    "r",
    encoding="utf-8",
) as f:
    doc_help = load(f)


def get_update(namespace, version):
    """get the version update doc."""
    try:
        open_dict = updates["release"][namespace]["update_info"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["release"][namespace]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        out_obj = open_dict.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_version_update_time(namespace, version):
    """Get the version update time."""
    try:
        open_dict = updates["release"][namespace]["update_time"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["release"][namespace]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_version(namespace):
    """Get the version."""
    return updates["release"][namespace]["version"]


def get_pre_version():
    """Get the pre version."""
    return updates["pre-release"]["version"]


def get_pre_update(version):
    """Get the pre-release version update doc."""
    try:
        open_dict = updates["pre-release"]["update_info"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == ALL:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["pre-release"]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        out_obj = open_dict.get(
            WILL, "This version is not found. Maybe it is not recorded."
        )
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )

    print(out_obj)
    return out_obj


def get_pre_version_update_time(version):
    """Get the pre-release version update time."""
    try:
        open_dict = updates["pre-release"]["update_time"]
    except KeyError:
        raise ValueError("This namespace not found.")

    if version == NEW:
        out_obj = open_dict
    elif version == NEW:
        out_obj = open_dict.get(
            updates["pre-release"]["version"],
            "This version is not found. Maybe it is not recorded.",
        )
    elif version == WILL:
        raise ValueError("`get_version_update_time` cannot get will update time.")
    else:
        out_obj = open_dict.get(
            str(version), "This version is not found. Maybe it is not recorded."
        )
    print(out_obj)
    return out_obj

def open_doc(doc_name, lang="en"):
    from markdown import markdown
    from os import remove
    from webbrowser import open as op
    from time import sleep

    doc_html_path = Path.cwd() / ".xystudio" / "pyplus" / "cache" / "doc.html"
    doc_name = doc_name.lower()

    for key, values in lang_alias.items():
        if lang.lower() in values:
            lang = key
    lang = lang.lower()

    makedirs(doc_html_path.parent, exist_ok=True)

    if doc_name == "index":
        op(getsitepackages()[1] + f"\\pyplus\\data\\docs\\web\\{lang}\\index.html")
    else:
        with open(
            getsitepackages()[1]
            + f"\\pyplus\\data\\docs\\markdown\\{lang}\\{doc_name}.md",
            "r",
            encoding="utf-8",
        ) as f:
            html = markdown(f.read())

        with open(doc_html_path, "w", encoding="utf-8") as f:
            f.write(html)

        op(doc_html_path)
        sleep(1)
        remove(doc_html_path)


def get_doc_help(doc_name=ALL):
    print()
    if doc_name == ALL:
        for doc_namespace, doc_des in doc_help.items():
            print(f"{doc_namespace} : {doc_des}")
    else:
        print(f"{doc_name}: {doc_help.get(doc_name, 'Not found.')}")


def get_alias(lang=ALL):
    print()
    match_alias = None
    for k, v in lang_alias.items():
        if lang.lower() in v:
            match_alias = k
            break

    if lang == ALL:
        for k, v in lang_alias.items():
            print(f"alias {k} -> {', '.join(v)}")
    elif match_alias is not None:
        print(f"alias {match_alias} -> {lang}")
    else:
        print(f"alias {lang} -> {', '.join(lang_alias.get(lang, ["Not found."]))}")


def config(config_name, value, config_type=first_used_config):
    global local_config, global_config, union_config

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


def get_config(config_name):
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
        print(
            "\nWhen you set config,you need use 'pyplus config set local name.config value'"
        )
    else:
        print("*" * 22 + "-" * 8 + config_type + "- " * 8 + "*" * 22)
        try:
            for doc_name, doc_des in config_help[config_type].items():
                print(f"{doc_name} : {doc_des}")
        except KeyError:
            print("This document is not found.")
        else:
            print(
                "When you set config,you need use 'pyplus config set local name.config value'"
            )


def open_doc(doc_name, lang="en"):
    from markdown import markdown
    from os import remove
    from webbrowser import open as op
    from time import sleep

    doc_html_path = Path.cwd() / ".xystudio" / "pyplus" / "cache" / "doc.html"
    doc_name = doc_name.lower()

    for key, values in lang_alias.items():
        if lang.lower() in values:
            lang = key
    lang = lang.lower()

    makedirs(doc_html_path.parent, exist_ok=True)

    if doc_name == "index":
        op(getsitepackages()[1] + f"\\pyplus\\data\\docs\\web\\{lang}\\index.html")
    else:
        with open(
            getsitepackages()[1]
            + f"\\pyplus\\data\\docs\\markdown\\{lang}\\{doc_name}.md",
            "r",
            encoding="utf-8",
        ) as f:
            html = markdown(f.read())

        with open(doc_html_path, "w", encoding="utf-8") as f:
            f.write(html)

        op(doc_html_path)
        sleep(1)
        remove(doc_html_path)


def remove_config(config_name, config_type=first_used_config):
    global local_config, global_config, union_config

    if config_type == LOCAL:
        del local_config[config_name]
        with open(local_config_path, "w", encoding="utf-8") as f:
            dump(local_config, f)
    elif config_type == GLOBAL:
        del global_config[config_name]
        with open(global_config_path, "w", encoding="utf-8") as f:
            dump(global_config, f)
    else:
        raise ValueError("This config type not found.")

    del union_config[config_name]
    return union_config


__version__ = get_version("main")


def shell():
    print("starting shell...")

    from pyplus import tools, science
    import decorators
    from img_fit import latex2text as latex

    from pyplus.tools import (
        colors,
        dec,
        database_convert,
        formula,
        geohash,
        # password,
        permission,
        pydebugger,
        stack,
        tag,
        type,
        update,
        web,
        variables,
        pycppio,
    )

    from argparse import Namespace

    # from . import () # deprecated moudle

    def wait(operator: bool):
        """
        Please use it in subprocess.
        """
        while operator:
            pass

    print(f'python-plus-tools {get_version("main")} ({get_pre_version()})')
    print("type exit to exit the shell.")
    while True:
        try:
            code = input("pyplus >>> ")
            if code == "exit" or code == "quit" or code == "exit()" or code == "quit()":
                break
            exec(code)
        except KeyboardInterrupt:
            print("^C\nKeyboardInterrupt")
            break
        except EOFError:
            break
        except Exception as e:
            print(e)


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
    subparsers = parser.add_subparsers(dest="command", required=False)

    config_cmd = subparsers.add_parser(
        "config",
        help="Set the config.Usage 'pyplus config get' to get all config.",
    )
    config_namespace = config_cmd.add_subparsers(dest="config_command", required=True)
    set_cmd = config_namespace.add_parser("set", help="Set the config")
    set_namespace = set_cmd.add_subparsers(dest="set_namespace", required=True)
    local_config_cmd = set_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    global_config_cmd = set_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    local_config_cmd.add_argument("setting", help="Config setting.")
    local_config_cmd.add_argument("value", help="Config value.")

    global_config_cmd.add_argument("setting", help="Config setting.")
    global_config_cmd.add_argument("value", help="Config value.")

    get_conf = config_namespace.add_parser("get", help="Get the config.")
    get_conf.add_argument(
        "-l",
        "--local",
        action=localAction,
        nargs="?",
        help="Get the local config in your project.Local config in './.xystudio/pyplus/config.toml'",
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

    get_conf_help = config_namespace.add_parser("get_help", help="Get the config help.")
    get_conf_help.add_argument(
        "-d",
        "--document_description",
        nargs="?",
        help="get one document description.",
        default=ALL,
    )
    remove_cmd = config_namespace.add_parser("remove", help="Remove the config")
    remove_namespace = remove_cmd.add_subparsers(dest="remove_namespace", required=True)
    local_config_cmd = remove_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    global_config_cmd = remove_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    local_config_cmd.add_argument("setting", help="Config setting.")
    global_config_cmd.add_argument("setting", help="Config setting.")

    doc_command = subparsers.add_parser("document", help="Document name.")

    doc_namespace = doc_command.add_subparsers(dest="doc_namespace", required=True)
    open_doc_command = doc_namespace.add_parser("open", help="Open the document.")
    get_help_command = doc_namespace.add_parser(
        "get_help", help="Get the document help."
    )
    open_doc_command.add_argument("doc_name", help="Document name.")
    open_doc_command.add_argument(
        "-l", "--lang", help="Document language.", nargs="?", default="en"
    )
    get_help_command.add_argument(
        "-d",
        "--document_description",
        nargs="?",
        help="get one document description.",
        default=ALL,
    )

    update_command = subparsers.add_parser("update", help="Get the update.")

    update_namespace = update_command.add_subparsers(
        dest="update_namespace", required=True
    )

    release_update = update_namespace.add_parser(
        "release", help="Get the release update."
    )
    pre_update = update_namespace.add_parser("pre", help="Get the pre-release update.")

    release_update_namespace = release_update.add_subparsers(
        dest="release_namespace", required=True
    )
    pre_update_namespace = pre_update.add_subparsers(dest="pre", required=True)

    release_update_namespace.add_parser(
        "version", help="Get a release version."
    ).add_argument(
        "namespace", help="A release version namespace."
    )

    news = release_update_namespace.add_parser(
        "news", help="Get the news."
    )
    news.add_argument(
        "namespace", help="A release version namespace.", nargs="?"
    )
    news.add_argument(
        "version", help="release version.", nargs="?"
    )

    time = release_update_namespace.add_parser(
        "time", help="Get the time."
    )
    time.add_argument(
        "namespace", help="A release version namespace.", nargs="?"
    )
    time.add_argument(
        "version", help="release version.", nargs="?"
    )

    pre_update_namespace.add_parser(
        "version", help="Get a pre-release version."
    )

    news = pre_update_namespace.add_parser(
        "news", help="Get the pre-release news."
    )
    news.add_argument(
        "version", help="pre-release version.", nargs="?"
    )

    time = pre_update_namespace.add_parser(
        "time", help="Get the pre-release time."
    )
    time.add_argument(
        "version", help="pre-release version.", nargs="?"
    )

    shell_command = subparsers.add_parser("shell", help="run pyplus code.")

    shell_command.add_subparsers(dest="shell_namespace", required=False)

    parser.add_argument("-v", "--version", help="Get the version.", action="store_true")

    get_alias_command = subparsers.add_parser("get_ailas", help="Get the alias.")

    get_alias_command.add_argument(
        "-l", "--lang", help="Document language.", nargs="?", default=ALL
    )

    args = parser.parse_args()

    if args.command == "config":
        if args.config_command == "set":
            if args.value.lower() == "true":
                value = True
            elif args.value.lower() == "false":
                value = False
            else:
                value = args.value
            print("Run code again to set the config.")
            config(args.setting, value, args.set_namespace)
        elif args.config_command == "get_help":
            get_config_help(args.document_description)
        elif args.config_command == "get":
            if hasattr(args, "_local"):
                print(local_config)
            if hasattr(args, "_global"):
                print(global_config)
            if hasattr(args, "_all"):
                print(union_config)
        elif args.config_command == "remove":
            remove_config(args.setting, args.remove_namespace)
    elif args.version:
        print("Version : pyplus pre:", get_pre_version())
        print("Version : pyplus :", get_version("main"))
    elif args.command == "document":
        if args.doc_namespace == "open":
            open_doc(args.doc_name, args.lang)
        elif args.doc_namespace == "get_help":
            get_doc_help(args.document_description)
    elif args.command == "update":
        if args.update_namespace == "release":
            if args.release_namespace == "version":
                print(get_version(args.namespace))
            elif args.release_namespace == "news":
                print(get_update(args.namespace, args.version))
            elif args.release_namespace == "time":
                print(get_version_update_time(args.namespace, args.version))
        elif args.update_namespace == "pre":
            if args.pre == "version":
                print(get_pre_version())
            elif args.pre == "news":
                print(get_pre_update(args.version))
            elif args.pre == "time":
                print(get_pre_version_update_time(args.version))
    elif args.command == "shell":
        shell()
    elif args.command == "get_ailas":
        get_alias(args.lang)
    else:
        print("Command not found.Press 'pyplus -h' to get help.")


def config_cmd():
    import os
    import sys

    os.system(f"pyplus config {" ".join(sys.argv[1:])}")


def doc_cmd():
    import os
    import sys

    os.system(f"pyplus document {" ".join(sys.argv[1:])}")


def update_cmd():
    import os
    import sys

    os.system(f"pyplus update {" ".join(sys.argv[1:])}")


if __name__ == "__main__":
    main()
