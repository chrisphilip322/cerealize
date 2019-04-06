import abc
import ast
import dataclasses
from typing import Optional, Callable


@dataclasses.dataclass
class Context:
    attr: Optional[str]
    parent: object
    parent_context: Optional['Context']
    item: Optional[object]


class BaseCerealizer(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, value: object, context: Optional[Context]) -> object:
        pass

    @abc.abstractmethod
    def dump(self, value: object, context: Optional[Context]) -> object:
        pass


class RawCerealizer(BaseCerealizer):
    def load(self, value: object, context: Optional[Context]) -> object:
        return value

    def dump(self, value: object, context: Optional[Context]) -> object:
        return value

    def compile_load(self, context: Optional[Context]) -> ast.AST:
        pass


class ListCerealizer(BaseCerealizer):
    def __init__(self, sub: BaseCerealizer) -> None:
        self._sub = sub

    def load(self, value: object, context: Optional[Context]) -> object:
        assert isinstance(value, list)
        return [
            self._sub.load(v, Context(None, value, context, index))
            for index, v in enumerate(value)
        ]

    def dump(self, value: object, context: Optional[Context]) -> object:
        assert isinstance(value, list)
        return [
            self._sub.dump(v, Context(None, value, context, index))
            for index, v in enumerate(value)
        ]


class SchemaCerealizer(BaseCerealizer):
    def __init__(self) -> None:
        self._members = {
            k: v
            for k, v in vars(type(self)).items()
            if isinstance(v, BaseCerealizer)
        }
        self.klass = getattr(self, 'klass')

    def load(self, value: object, context: Optional[Context]) -> object:
        assert isinstance(value, dict)
        return self.klass(**{
            k: v.load(value[k], Context(k, value, context, None))
            for k, v in self._members.items()
        })

    def dump(self, value: object, context: Optional[Context]) -> object:
        assert isinstance(value, self.klass)
        return {
            k: v.dump(getattr(value, k), Context(k, value, context, None))
            for k, v in self._members.items()
        }


class OptionalCerealizer(BaseCerealizer):
    def __init__(self, sub: BaseCerealizer) -> None:
        self._sub = sub

    def load(self, value: object, context: Optional[Context]) -> object:
        if value is None:
            return None
        else:
            return self._sub.load(value, context)

    def dump(self, value: object, context: Optional[Context]) -> object:
        if value is None:
            return None
        else:
            return self._sub.dump(value, context)


class DeferredCerealizer(BaseCerealizer):
    def __init__(self, sub_factory: Callable[[], BaseCerealizer]) -> None:
        self._sub_factory = sub_factory
        self.__sub = None

    @property
    def _sub(self):
        if self.__sub is None:
            self.__sub = self._sub_factory()
        return self.__sub

    def load(self, value: object, context: Optional[Context]) -> object:
        return self._sub.load(value, context)

    def dump(self, value: object, context: Optional[Context]) -> object:
        return self._sub.dump(value, context)
