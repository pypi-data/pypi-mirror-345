from pylint.checkers import BaseChecker
from astroid import nodes


class StringWhitespaceChecker(BaseChecker):

    name = "string-whitespace-checker"
    priority = -1
    msgs = {
        "C9997": (
            "String literal has leading or trailing whitespace or newline",
            "string-leading-trailing-space",
            "Avoid using string literals with extra space or newline at start/end.",
        ),
    }

    def visit_const(self, node: nodes.Const):
        if isinstance(node.value, str):
            val = node.value
            if val and (val != val.strip()):
                self.add_message("string-leading-trailing-space", node=node)
