import flake8.checker

from flake8_diff_only.utils import get_changed_lines

_original_run_checks = flake8.checker.FileChecker.run_checks


def _patched_run_checks(self) -> tuple[str, list, list] | None:  # type: ignore
    if not hasattr(self, "_changed_lines"):
        self._changed_lines = get_changed_lines(self.filename)

    results = _original_run_checks(self)
    if results is None or not self._changed_lines:
        return None

    self.filename, self.results, self.statistics = results
    self.results = list(filter(lambda r: r[1] in self._changed_lines, self.results))

    return self.filename, self.results, self.statistics


flake8.checker.FileChecker.run_checks = _patched_run_checks
