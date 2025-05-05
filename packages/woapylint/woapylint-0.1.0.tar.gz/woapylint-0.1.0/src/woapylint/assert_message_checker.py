from astroid import Assert
from pylint.checkers import BaseChecker


class AssertMessageChecker(BaseChecker):
    name = "assert-message-checker"
    msgs = {
        "C1001": (
            "Assert statement should have a message",
            "assert-message-missing",
            "You should provide a message in assert statements to describe the failure reason.",
        ),
    }

    def visit_assert(self, node: Assert):
        if node.fail is None:
            self.add_message("assert-message-missing", node=node)
