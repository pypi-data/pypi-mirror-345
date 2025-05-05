from pylint.checkers import BaseChecker
from astroid import nodes


class LongStringChecker(BaseChecker):

    name = "long-string-checker"
    priority = -1
    msgs = {
        "C9998": (
            "String literal too long (%d characters)",
            "long-string",
            "Used when a string literal exceeds max allowed length.",
        ),
    }

    options = (
        (
            "max-string-length",
            {
                "default": 120,
                "type": "int",
                "metavar": "<int>",
                "help": "Maximum allowed string literal length",
            },
        ),
    )

    def visit_const(self, node: nodes.Const):
        if isinstance(node.value, str):
            lines = node.value.split("\n")
            for line in lines:
                if len(line) > self.linter.config.max_string_length:
                    self.add_message("long-string", node=node, args=(len(node.value),))
