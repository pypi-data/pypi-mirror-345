import ast


class Flake8DiffOnlyChecker:
    name = "flake8-diff-only"
    version = "0.1.6"

    def __init__(self, tree: ast.AST, filename: str):
        pass

    def run(self):  # type: ignore[no-untyped-def]
        return []
