import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

Engine = Literal["sass"]
logger = logging.getLogger(__file__)


class StylesheetCompiler(ABC):
    def __init__(self, source: Path, output: Path):
        self.source = source
        self.output = output

    @abstractmethod
    def compile(self, verbose: bool = False) -> Path | None:
        ...

class SassCompiler(StylesheetCompiler):
    def compile(self, verbose: bool = False) -> Path | None:
        from command_runner import command_runner

        command = f"sass -s compressed {self.source.resolve()} {self.output.resolve()}"
        command_runner(command, live_output=verbose)


# noinspection PyShadowingBuiltins
# noinspection PyCallingNonCallable
def compile(source: Path, output: Path, compiler: StylesheetCompiler = SassCompiler, verbose: bool = False):
    compiler(source, output).compile(verbose=verbose)
