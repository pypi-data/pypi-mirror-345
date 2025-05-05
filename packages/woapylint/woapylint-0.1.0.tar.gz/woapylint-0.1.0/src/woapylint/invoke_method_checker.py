from astroid import Call
from pylint.checkers import BaseChecker
import astroid


class InvokeMethodChecker(BaseChecker):
    name = "check-invoke"
    msgs = {
        "W9001": (
            "Prefer using 'ainvoke' instead of 'invoke'",
            "use-ainvoke-method",
            "Recommended to use 'ainvoke' over 'invoke' in the class.",
        ),
    }

    def visit_call(self, node: Call):
        if not isinstance(node.func, astroid.Attribute):
            return

        method_name = node.func.attrname
        if method_name != "invoke":
            return

        try:
            inferred = next(node.func.expr.infer())
            if isinstance(inferred, astroid.Instance) or isinstance(
                inferred, astroid.ClassDef
            ):
                self.add_message("use-ainvoke-method", node=node)
        except (astroid.InferenceError, StopIteration):
            pass
