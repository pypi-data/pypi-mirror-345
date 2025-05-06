import sys

from pygeai.cli.commands import Option
from pygeai.core.common.config import get_settings


def configure(option_list: list[str, str] = None):
    if not any(option_list):
        sys.stdout.write("# Configuring GEAI credentials...\n")
        alias = str(input("-> Select an alias (Leave empty to use 'default'): "))
        if not alias:
            alias = "default"

        api_key = str(input("-> Insert your GEAI API KEY (Leave empty to keep current value): "))
        if api_key:
            configure_api_key(api_key, alias)

        base_url = str(input("-> Insert your GEAI API BASE URL (Leave empty to keep current value): "))
        if base_url:
            configure_base_url(base_url, alias)

        eval_url = str(input("-> Insert your GEAI API EVAL URL (Leave empty to keep current value): "))
        if eval_url:
            configure_eval_url(eval_url, alias)

    else:
        for option_flag, option_arg in option_list:
            alias = "default"
            if option_flag.name == "alias":
                alias = option_arg
            if option_flag.name == "api_key":
                configure_api_key(api_key=option_arg, alias=alias)
            if option_flag.name == "base_url":
                configure_base_url(base_url=option_arg, alias=alias)
            if option_flag.name == "eval_url":
                configure_eval_url(eval_url=option_arg, alias=alias)


def configure_api_key(api_key: str, alias: str = "default"):
    settings = get_settings()
    settings.set_api_key(api_key, alias)
    sys.stdout.write(f"GEAI API KEY for alias '{alias}' saved successfully!\n")


def configure_base_url(base_url: str, alias: str = "default"):
    settings = get_settings()
    settings.set_base_url(base_url, alias)
    sys.stdout.write(f"GEAI API BASE URL for alias '{alias}' saved successfully!\n")


def configure_eval_url(eval_url: str, alias: str = "default"):
    settings = get_settings()
    settings.set_eval_url(eval_url, alias)
    sys.stdout.write(f"GEAI API EVAL URL for alias '{alias}' saved successfully!\n")


configuration_options = (
    Option(
        "api_key",
        ["--key", "-k"],
        "Set GEAI API KEY",
        True
    ),
    Option(
        "base_url",
        ["--url", "-u"],
        "Set GEAI API BASE URL",
        True
    ),
    Option(
        "eval_url",
        ["--eval-url", "--eu"],
        "Set GEAI API EVAL URL for the evaluation module",
        True
    ),
    Option(
        "alias",
        ["--alias", "-a"],
        "Set alias for settings section",
        True
    ),
)
