from typing import MutableSequence, Any, Tuple


class ScatterAppend:
    @classmethod
    def make_n(cls, n: int):
        return cls(*tuple([] for _ in range(n)))

    def __init__(self, *refs: MutableSequence[Any]) -> None:
        self.refs = refs

    def __iadd__(self, others: Tuple[Any, ...]):
        for ref, o in zip(self.refs, others):
            ref.append(o)
        return self

    def __getitem__(self, i: int):
        return self.refs[i]

    def __repr__(self):
        return str([x for x in self.refs])

    def get(self, index: int) -> Tuple[Any, ...]:
        return tuple(x[index] for x in self.refs)

    def size(self, i=None):
        return tuple(len(x) for x in self.refs) if i is None else len(self.refs[i])
