from __future__ import annotations

import ast
import subprocess
from typing import ClassVar

FilePath = str
LineNumber = int


class Flake8DiffOnlyChecker:
    name = "flake8-diff-only"
    version = "0.1.3"

    _instance: ClassVar[Flake8DiffOnlyChecker | None] = None
    _diff_lines: ClassVar[dict[FilePath, set[LineNumber]]]

    def __new__(  # type: ignore[no-untyped-def]
        cls, *args, **kwargs
    ) -> Flake8DiffOnlyChecker:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._diff_lines = cls._load_git_diff()
        return cls._instance

    def __init__(self, tree: ast.AST, filename: str):
        self.filename = filename
        self.tree = tree

    def run(self):  # type: ignore[no-untyped-def]
        # Если файл не изменён — пропускаем
        if self.filename not in self._diff_lines:
            return

        # Получаем список изменённых строк
        changed_lines = Flake8DiffOnlyChecker._diff_lines[self.filename]

        # Получаем все ошибки от других плагинов
        for lineno, col_offset, message, checker in self._original_errors():
            if lineno in changed_lines:
                yield lineno, col_offset, message, checker

    def _original_errors(self) -> list:  # type: ignore[type-arg]
        """
        Заглушка: Этот метод не реализует собственную логику проверки.
        Он нужен только как перехватчик для других плагинов.
        Фактически, flake8 вызовет ВСЕ плагины, а наш просто отфильтрует их вывод.
        Поэтому мы не генерируем ошибок тут.
        """
        return []

    @classmethod
    def _load_git_diff(cls) -> dict[FilePath, set[LineNumber]]:
        """
        Получаем список изменённых строк из git diff.
        Возвращает словарь: { 'filename': set(linenos) }
        """
        diff_cmd = ["git", "diff", "--unified=0", "--no-color", "--cached"]
        try:
            output = subprocess.check_output(
                diff_cmd, stderr=subprocess.DEVNULL
            ).decode()
        except subprocess.CalledProcessError:
            return {}

        result: dict[FilePath, set[LineNumber]] = {}
        current_file: str | None = None

        for line in output.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("@@"):
                # Парсим хедер ханка: @@ -old,+new @@
                try:
                    new_section = line.split(" ")[2]
                    start_line, length = Flake8DiffOnlyChecker._parse_diff_range(
                        new_section
                    )
                    lines = set(range(start_line, start_line + length))
                    if current_file:
                        current_file_lines: set[LineNumber] = result.setdefault(
                            current_file, set()
                        )
                        current_file_lines.update(lines)
                except Exception:
                    continue
        return result

    @staticmethod
    def _parse_diff_range(range_str: str) -> tuple[LineNumber, int]:
        """
        Парсит формат вроде '+12,3' или '+45' → (start_line, length)
        """
        range_str = range_str.lstrip("+")
        if "," in range_str:
            start, length = map(int, range_str.split(","))
        else:
            start, length = int(range_str), 1
        return start, length
