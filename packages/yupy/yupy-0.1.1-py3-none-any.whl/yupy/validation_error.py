from dataclasses import dataclass, field
from typing import Generator, Any, List, Optional, Union, Callable, TypeAlias

__all__ = (
    'ErrorMessage',
    'ValidationError',
    'Constraint',
)

ErrorMessage: TypeAlias = Union[str, Callable[[Any | List[Any]], str]]


@dataclass
class Constraint:
    type: Optional[str]
    args: Any
    message: ErrorMessage = field(repr=False)

    @property
    def format_message(self) -> str:
        if callable(self.message):
            return self.message(self.args)
        return self.message


class ValidationError(ValueError):
    def __init__(
            self, constraint: Constraint, path: str = "", errors: Optional[List['Self']] = None, *args
    ) -> None:
        # self.path: str = re.sub(r"^\.", "", path)
        self.path = path
        self.constraint: Constraint = constraint
        self._errors: List['Self'] = errors or []
        super().__init__(self.path, self.constraint, self._errors, *args)

    def __str__(self) -> str:
        return f"(path={repr(self.path)}, constraint={self.constraint}, message={repr(self.constraint.format_message)})"

    def __repr__(self) -> str:
        return "ValidationError%s" % self.__str__()

    @property
    def errors(self) -> Generator['Self', None, None]:
        yield self
        for error in self._errors:
            yield from error.errors

    @property
    def message(self) -> str:
        return f"{repr(self.path)}: {self.constraint.format_message}"

    @property
    def messages(self) -> Generator[str, None, None]:
        for e in self.errors:
            yield e.message
