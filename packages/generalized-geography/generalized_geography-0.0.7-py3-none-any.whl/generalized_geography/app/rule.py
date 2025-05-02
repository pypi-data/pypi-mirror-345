from typing import Callable, List


class Rule:
    first_index: int
    last_index: int
    change_rule: Callable[[str], List[str]]
    name: str

    def __init__(self,  first_index: int, last_index: int, change_rule, name: str = None):
        self.first_index = first_index
        self.last_index = last_index
        self.change_rule = change_rule
        self.name = name
