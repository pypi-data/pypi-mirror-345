from typing import Dict, Callable

from cyanprintsdk.domain.core.deterministic import IDeterminism


class StatelessDeterminism(IDeterminism):
    def __init__(self, states: Dict[str, str]):
        self.states = states

    def get(self, key: str, origin: Callable[[], str]) -> str:
        if self.states is None:
            raise RuntimeError("States dictionary is null")

        state = self.states.get(key)

        if state is not None:
            return state

        val = origin()
        self.states[key] = val
        return val
