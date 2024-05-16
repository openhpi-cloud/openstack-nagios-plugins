# pylint: disable=missing-docstring

import re
from argparse import SUPPRESS, Action, ArgumentParser
from typing import Any, Type

ICINGA_ARGUMENTS_IGNORE = (
    "--help",
    "--print-command-definition",
    "--verbose",
)

ICINGA_ARGUMENT_ALIAS = {
    "timeout": "openstack_request_timeout",
    "insecure": "openstack_insecure",
    "check-timeout": "openstack_timeout",
}


ICINGA_ESCAPE = str.maketrans(
    {
        '"': r"\"",
        "\\": r"\\",
        "\t": r"\t",
        "\n": r"\n",
        "\r": r"\r",
        "\b": r"\b",
        "\f": r"\f",
    }
)


def command_definition_action(resource_class: Type):
    class PrintCommentDefinition(Action):
        def __init__(self, option_strings, **_kwargs):
            super().__init__(
                option_strings=option_strings,
                dest=SUPPRESS,
                default=SUPPRESS,
                nargs=0,
                help=SUPPRESS,
            )

        def __call__(self, parser, namespace, values, option_string=None):
            print(generate_command_definition(resource_class, parser))
            parser.exit()

    return PrintCommentDefinition


def generate_command_definition(resource_class: Type, parser: ArgumentParser):
    check_name = re.sub(
        r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])",
        "-",
        resource_class.__name__,
    ).lower()
    check_path = f"/usr/lib/nagios/plugins/check_{check_name.replace('-', '_')}"
    arg_prefix = check_name.replace("-", "_")

    lines = [
        f'object CheckCommand "{check_name}" {{',
        f'    command = [ "{check_path}" ]',
    ]

    arguments: dict[str, Any] = {}

    for action in parser._actions:  # pylint: disable=protected-access
        if action.help == SUPPRESS:
            continue

        for cmd in action.option_strings:
            if not cmd.startswith("--") or cmd in ICINGA_ARGUMENTS_IGNORE:
                continue

            name = cmd[2:]
            value = None

            if name in ICINGA_ARGUMENT_ALIAS:
                value = ICINGA_ARGUMENT_ALIAS[name].format(prefix=arg_prefix)
            elif name.startswith("os"):
                value = f"$openstack_{name[3:]}$"
            else:
                value = f"${arg_prefix}_{name}$"

            arguments[cmd] = {
                "value": value.replace("-", "_"),
                "description": action.help,
            }

            if action.required:
                arguments[cmd]["required"] = True

    if arguments:
        lines.append("    arguments += {")
        for name, argument in arguments.items():
            lines.append(f'        "{name}" = {{')
            for key, value in argument.items():
                lines.append(f"            {key} = {escape_value(value)}")
            lines.append("        }")

        lines.append("    }")

    lines.append("}")

    return "\n".join(lines) + "\n"


def escape_value(val: Any):
    if isinstance(val, str):
        return '"' + str(val).translate(ICINGA_ESCAPE) + '"'
    else:
        return val
