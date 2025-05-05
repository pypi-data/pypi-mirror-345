"""
Ruff formatter.

Copyright 2024 Vlad Emelianov
"""

import json
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Sequence
from pathlib import Path

from mypy_boto3_builder.constants import LINE_LENGTH, SUPPORTED_PY_VERSIONS
from mypy_boto3_builder.logger import get_logger
from mypy_boto3_builder.utils.path import print_path


class RuffError(RuntimeError):
    """
    Ruff error.
    """


class RuffFormatter:
    """
    Ruff formatter.
    """

    def __init__(
        self,
        known_first_party: Sequence[str] = (),
        known_third_party: Sequence[str] = (),
    ) -> None:
        self.logger = get_logger()
        self._target_version = self._get_target_version()
        self._known_first_party = list(known_first_party)
        self._known_third_party = [i for i in known_third_party if i not in self._known_first_party]

    @staticmethod
    def _get_target_version() -> str:
        min_version = min(v for v in SUPPORTED_PY_VERSIONS if len(v) > 1)
        return f"py{min_version[0]}{min_version[1]}"

    def format_python(self, paths: Sequence[Path]) -> None:
        """
        Format python files with `ruff`.

        Arguments:
            path -- Target path.
        """
        self._sort_imports(paths)
        self._run_format(paths)

    def _get_config_cli(self) -> list[str]:
        overrides = [
            f'target-version = "{self._target_version}"',
            f"line-length = {LINE_LENGTH}",
            'format.quote-style = "double"',
            'format.line-ending = "lf"',
            f"lint.isort.known-first-party = {json.dumps(self._known_first_party)}",
            f"lint.isort.known-third-party = {json.dumps(self._known_third_party)}",
        ]
        result: list[str] = []
        for option in overrides:
            result.extend(["--config", option])

        return result

    def _run_check(self, paths: Sequence[Path], rules: Sequence[str]) -> None:
        cmd = (
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--target-version",
            self._target_version,
            *self._get_config_cli(),
            "--select",
            ",".join(rules),
            "--fix",
            "--isolated",
            *(path.as_posix() for path in paths),
        )
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.logger.warning(
                f"Ruff check failed for paths {[print_path(path) for path in paths]}",
            )
            self.logger.warning(" ".join(cmd))
            self.logger.warning(e.output.decode())
            raise RuffError(f"Ruff check failed with status {e.returncode}") from None

    def _sort_imports(self, paths: Sequence[Path]) -> None:
        """
        Sort imports.
        """
        self._run_check(paths, ("I",))

    def _run_format(self, paths: Sequence[Path]) -> None:
        """
        Format python code with `ruff`.
        """
        cmd = (
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--target-version",
            self._target_version,
            *self._get_config_cli(),
            "--isolated",
            *(path.as_posix() for path in paths),
        )
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.logger.warning(
                f"Ruff format failed for paths {[print_path(path) for path in paths]}",
            )
            self.logger.warning(" ".join(cmd))
            self.logger.warning(e.output.decode())
            raise RuffError(f"Ruff format failed: {e.output}, paths: {paths}") from None

    def format_strings(self, codes: Iterable[str]) -> list[str]:
        """
        Format python code as strings.
        """
        with tempfile.TemporaryDirectory() as dir_name:
            paths: list[Path] = []
            for index, code in enumerate(codes):
                file_path = Path(dir_name) / f"temp_{index}.py"
                file_path.write_text(code)
                paths.append(file_path)

            self._run_format(paths)
            return [path.read_text().rstrip("\n") for path in paths]

    def format_markdown(self, text: str) -> str:
        """
        Format python codeblocks in markdown.
        """
        blocks = text.split("\n```")
        format_blocks: list[str] = []
        format_block_indices: list[int] = []
        for index, block in enumerate(blocks):
            if block.startswith("python"):
                format_blocks.append(block)
                format_block_indices.append(index)

        if format_blocks:
            for index, formatted_block in enumerate(self.format_strings(format_blocks)):
                block_index = format_block_indices[index]
                blocks[block_index] = formatted_block
        return "\n```".join(blocks)


def format_python(code: str) -> str:
    """
    Format python code. Removes duplicated empty lines.
    """
    ruff_formatter = RuffFormatter()
    result = ruff_formatter.format_strings((code,))[0]
    clean_result: list[str] = []
    for line in result.splitlines():
        if not line and (not clean_result or not clean_result[-1]):
            continue
        clean_result.append(line)
    return "\n".join(clean_result)
