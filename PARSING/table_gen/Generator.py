from __future__ import annotations
from Grammar import Grammar
from Item import Item
from Singleton import Singleton
from Grammar import Rule

class Core:
    def __init__(self, items: Item | list[Item]):
        self._init = True

        if isinstance(items, list):
            self._items = items
        elif isinstance(items, Item):
            self._items = [items]
        else:
            raise RuntimeError(f"Core should only be type list[Item] or Item, its {type(items)}")

    @property
    def items(self):
        return tuple(self._items)

    def __hash__(self) -> str:
        string = hash(tuple(Item.get_rule_with_pos(item) for item in self._items))
        return hash(string)        

    def __eq__(self, other: Core) -> bool:
        return len(self.items) < len(other.items)

    def add(self, item: Item) -> None:
        if not self._init:
            raise RuntimeError("Core list shouldnt be altered after completion")
        self._items.append(item)

    def finish_init(self) -> None:
        self._init = False

    def __repr__(self) -> str:
        for item in self._items:
            return Item.get_rule_with_pos(item)

class State:
    state_map: dict[Core, State] = {}

    @property
    def items(self):
        return self._items

    def print_state(self) -> None:
        for item in self.core.items:
            item.print_item()
        print()
        for item in self._items:
            item.print_item()
        print()

    def __init__(self, items: Item | Core):
        if isinstance(items, Core):
            self.core = items
        else:
            self.core = Core(items)

        if hash(self.core) in State.state_map:
            raise RuntimeError("State already exists. Shouldn't be intialized again")

        self._items = []
        self.edges = {}
        self.reductions = {}
        State.state_map[hash(self.core)] = self

        for item in self.core.items:
            self._items += item.closure()           

    def is_reduction_ambiguity(self, new_lookahead: set[str]) -> bool:
        for item, old_lookahead in self.reductions.items():
            if len(new_lookahead | old_lookahead) != 0:
                return False

        return True

    def add_reduction(self, item) -> None:
        if item in self.reductions:
            raise RuntimeError("error adding reduction. reduction already valid. Something else wrong with program?")
        
        self.reductions[item] = item.lookahead

        if self.is_reduction_ambiguity(item.lookahead):
            raise RuntimeError("reduction/reduction ambiguity. Multiple reductions with same lookahead")

    def _create_edges(self) -> dict[str, Core]:
        edges = {}

        for item in (self.core._items + self._items):
            if item.pos >= len(item.rhs):
                self.add_reduction(item)
            else:            
                symbol = item.rhs[item.pos]
                new_item = Item(item.rule, item.lookahead, item.pos + 1)

                if symbol not in edges:
                    edges[symbol] = Core(new_item)

                else:
                    core = edges[symbol]
                    core.add(new_item)

        self._connect_states(edges) 

    def _merge_state(self, core: Core) -> None:
        if len(self.core.items) != len(core.items):
            raise RuntimeError("States should be identical length when merging")

        for i in range(len(self.core.items)):
            self.core.items[i].lookahead |= core.items[i].lookahead

    def _connect_states(self, edges: dict[str, Core]):
        for symbol, core in edges.items():
            if hash(core) in State.state_map:
                State.state_map[hash(core)]._merge_state(core)
                continue

            state = State(core)
            self.edges[symbol] = state
            state._create_edges() 

class Generator(metaclass=Singleton):

    @staticmethod
    def _get_augment_start() -> Item:
        lhs = "S'"
        rhs = [Grammar.START_SYMBOL]
        lookahead = set(["$"])
        
        return Item(Rule(lhs, rhs), lookahead)

    @staticmethod
    def print_states() -> None:
        i = 1
        for key in State.state_map:
            print(f"State {i}:")
            i += 1
            State.state_map[key].print_state()

    @staticmethod
    def generate(file_name):
        grammar = Grammar(file_name)

        start = Generator._get_augment_start()
        Grammar._rules[start.lhs] = [start.rhs] 
        start_state = State(start)
        start_state._create_edges()

        Generator.print_states()

if __name__ == "__main__":
    Generator.generate("./PARSING/BNF_TEST.txt")

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list