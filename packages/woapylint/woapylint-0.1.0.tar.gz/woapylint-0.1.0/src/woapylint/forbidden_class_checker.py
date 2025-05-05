from astroid import Name
from pylint.checkers import BaseChecker
import astroid

FORBIDDEN_CLASSES = {"ChatModel"}


class ForbiddenClassChecker(BaseChecker):

    name = "forbidden-class-checker"
    msgs = {
        "W9011": (
            "Forbidden class '%s' is used",
            "forbidden-class-used",
            "This class should not be used in the codebase.",
        ),
    }

    def visit_call(self, node: astroid.Call):
        try:
            func = node.func
            if isinstance(func, Name):
                class_name = func.name
                if class_name in FORBIDDEN_CLASSES:
                    self.add_message(
                        "forbidden-class-used", node=node, args=(class_name,)
                    )
        except AttributeError:
            return
