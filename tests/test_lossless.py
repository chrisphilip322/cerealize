import dataclasses
from typing import Optional

import cerealize as c


@dataclasses.dataclass
class Foo:
    a: int
    b: str
    d: list
    f: Optional['Foo']


class FooCerealizer(c.SchemaCerealizer):
    klass = Foo
    a = c.RawCerealizer()
    b = c.RawCerealizer()
    d = c.ListCerealizer(c.RawCerealizer())
    f = c.OptionalCerealizer(c.DeferredCerealizer(lambda: FooCerealizer()))


f = Foo(1, 'b', [1, 2], Foo(2, 'c', [5, 6], None))
fc = FooCerealizer()
print(fc.load(fc.dump(f, None), None))
