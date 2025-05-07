import subprocess

from flake8_diff_only.types import LineNumber


def get_changed_lines(filename: str) -> set[LineNumber]:
    """
    Получаем множество изменённых строк из git diff.
    """
    changed_lines: set[LineNumber] = set()

    diff_cmd = ["git", "diff", "--unified=0", "--no-color", "--cached", filename]
    try:
        output = subprocess.check_output(diff_cmd, stderr=subprocess.DEVNULL).decode()
    except subprocess.CalledProcessError:
        return changed_lines

    for line in output.splitlines():
        if line.startswith("@@"):
            # Парсим хедер ханка: @@ -old,+new @@
            try:
                new_section = line.split(" ")[2]
                start_line, length = _parse_diff_range(new_section)
                lines = set(range(start_line, start_line + length))
                changed_lines.update(lines)
            except Exception:
                continue
    return changed_lines


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
