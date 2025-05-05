from pylint.checkers import BaseChecker
from astroid import nodes


class ForbiddenStringChecker(BaseChecker):

    name = "forbidden-string-checker"
    msgs = {
        "C9996": (
            "Warning when u using field in your string '%s'",
            "forbidden-string",
            "Used field in your string",
        ),
    }

    def visit_const(self, node: nodes.Const):
        if isinstance(node.value, str):
            if "field" in node.value.lower():
                self.add_message("forbidden-string", node=node, args=(node.value,))
