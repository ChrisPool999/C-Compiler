from __future__ import annotations
from Grammar import Grammar, Rule
from Item import Item
from Singleton import Singleton
from collections import deque 
from typing import Optional

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
        if len(self.items) != len(other.items):
            return False

        for i in range(len(self._items)):
            if self._items[i] != other.items[i]:
                return False

        return True

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
    state_list = []

    @property
    def items(self):
        return self._items

    def get_yellow_str_output(self, string: str) -> str:
        return f"\033[93m{string}\033[0m"

    def get_green_str_output(self, string: str) -> str:
        return "\033[92m{string}\033[0m"

    def __repr__(self) -> str:
        result = ""
        for item in self.core.items:
            result += self.get_yellow_str_output(str(item)) + "\n"
        
        for item in self._items:
            if item.pos >= len(item.rhs):
                result += self.get_green_str_output(str(item)) + "\n"
            else:
                result += (str(item) + "\n")
        
        return result

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

    @classmethod
    def make_graph(cls, root: State) -> dict[Core, State]:
        dq = deque([root])

        while dq:
            state = dq[0]

            for item in (state.core._items + state.items):
                if item.pos >= len(item.rhs):
                    state.add_reduction(item)          

            State.state_list.append(state)

            edges = state._get_edges()

            for edge, node in edges.items():
                core = Core(node)

                if hash(core) in State.state_map:
                    State.state_map[hash(core)]._merge_state(core)
                    state.edges[edge] = State.state_map[hash(core)]
                    continue
                
                new_state = State(core)
                State.state_map[hash(core)] = new_state
                dq.append(new_state)

                state.edges[edge] = new_state

            dq.popleft()

    def add_reduction(self, item) -> None:
        if item in self.reductions:
            raise RuntimeError(f"reduction already added. cycle issue? \n{self}")
        
        self.reductions[item] = item.lookahead

    def _get_edges(self) -> dict[str, Core]:
        edges = {}

        for item in (self.core._items + self._items):
                if item.pos >= len(item.rhs):
                    continue

                symbol = item.rhs[item.pos]
                next_item = Item(item.rule, item.lookahead, item.pos + 1)

                if symbol in edges:
                    edges[symbol].append(next_item)
                else:
                    edges[symbol] = [next_item]

        return edges

    def _merge_state(self, core: Core) -> None:
        if len(self.core.items) != len(core.items):
            raise RuntimeError("States should be identical length when merging")

        for i in range(len(self.core.items)):
            self.core.items[i].lookahead |= core.items[i].lookahead

class Generator(metaclass=Singleton):

    @staticmethod
    def _get_augment_start() -> Item:
        lhs = "S'"
        rhs = [Grammar.START_SYMBOL]
        lookahead = set(["$"])
        
        return Item(Rule(lhs, rhs), lookahead)

    @staticmethod
    def print_states() -> None:
        i = 0
        for state in State.state_list:
            print(f"State {i}:")
            i += 1
            print(state)

    @staticmethod
    def create_table() -> list[dict[str, Optional: Rule | int]]:
        table = []
        
        for state in State.state_list:

            row = {}
            for edge, node in state.edges.items():
                if edge in row:
                    raise RuntimeError(f"shift conflict for {edge} in state.. \n{state}")

                row[edge] = State.state_list.index(node)
            
            for item in state.reductions:
                for lookahead in item.lookahead:
                    if lookahead in row:
                        raise RuntimeError(f"reduce conflict for {lookahead} in state.. \n{state}")

                    row[lookahead] = item.rule 
            table.append(row)
        
        return table            

    def print_table(table: list[dict[str, Optional: Rule | int]]) -> None:
        for i in range(len(table)):
            row = table[i]
            
            print(f"State {i}")
            for symbol, cell in row.items():
                if isinstance(cell, Rule):
                    print(f"{symbol} --> {cell.lhs} ::= {" ".join(cell.rhs)}")

                elif isinstance(cell, int):
                    print(f"{symbol} --> S{cell}")

                else:
                    raise RuntimeError(f"cell in table not Rule or State number, type {type(cell)}")
            print("\n")

    @staticmethod
    def generate(file_name):
        grammar = Grammar()
        grammar.parse_file(file_name)

        start = Generator._get_augment_start()
        Grammar._rules[start.lhs] = [start.rhs] 

        State.make_graph(State(start))
        
        Generator.print_states()

        table = Generator.create_table()
        Generator.print_table(table)

if __name__ == "__main__":
    filename = "./PARSING/parse_tables/BNF3.txt"
    Generator.generate(filename)

# FEATURES
# 1. Generate Table (Create C++ file for use)
# 2. more tests
# 3. this thing...  ->  # <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list
# 4. REFACTOR

# BUGS
# 3. if multiple cores, wont merge lookaheads within item set
# 4. do tag tests work with this approach? idk...


# - cant have expansions that are all optional
# - what about when theres multiple tags per expansion eg S -> . A? B* C+
#                                                         S -> . A B* C+
#                                                         S -> . B* C+



    # def _find_follow(self, offset: int = 0) -> set[str]:
    #     """ 
    #         Finds the follow() of a symbol\n
    #         The follow() is the set of terminals that can appear after a symbol within a rule\n
    #         Includes any cases where the symbol may be optional, repetitive, or the last symbol in a rule\n

    #         Parameters:\n
    #         item (Item)\n
    #         offset (int) (Only intended for internal use) Offset shifts the progress position of rule forward. \n

    #         Returns:
    #         set[str]: returns a set of terminals symbols that could possibly follow a symbol in a rule
    #     """        
    #     pos = self.pos + offset
    #     if pos >= len(self.rhs): 
    #         return set()

    #     terminals = set()

    #     # if the current symbol can repeat, the next symbol could be a repetition
    #     curr_symbol = self.rhs[self.pos]
    #     # if Grammar.is_repetitive(curr_symbol):
    #     #     terminals |= Grammar.find_first(curr_symbol)

    #     # follow of the end symbol = follow of LHS/reduction = item's look-ahead
    #     if pos == len(self.rhs) - 1:
    #         terminals |= self.lookahead
    #         return terminals

    #     next_symbol = self.rhs[pos + 1]
    #     # if Grammar.is_optional(next_symbol):
    #     #     terminals |= self._find_follow(offset + 1)

    # def _get_optional_item_rule(self):
    #     if self.pos >= len(self.rhs):
    #         raise RuntimeError(f"This item has completed. No current symbol to modify\n {self}")
        
    #     item = copy.deepcopy(self)
    #     del item.rhs[self.pos]
    #     self.pos -= 1

    #     # if item.rhs == []:
    #     #     raise RuntimeError(f"Item expansion symbols shouldn't be all optional. " 
    #     #                        "Define the symbol as optional at the call site instead of globally\n"
    #     #                        f"{self}")

    #     item.lookahead = item._find_follow()

    #     return item                    

    # def _get_repetitive_item_rule(self):
    #     if self.pos >= len(self.rhs):
    #         raise RuntimeError(f"This item has completed. No current symbol to modify\n {self}")

    #     symbol = Grammar.remove_tags(self.rhs[self.pos])
    #     lookahead = Grammar.find_first(symbol)
    #     return Item(Rule(symbol, [symbol, symbol]), lookahead)

    # def _create_tag_sets(self) -> list[Item]:
    #     new_items = []
    #     symbol = self.rhs[self.pos]

    #     if Grammar.is_optional(symbol):
    #         optional_rule = self._get_optional_item_rule()
    #         new_items.append(optional_rule)

    #     if Grammar.is_repetitive(symbol):
    #         repetitive_rule = self._get_repetitive_item_rule()
    #         new_items.append(repetitive_rule)

    #     return new_items