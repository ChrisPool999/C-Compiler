from Grammar import Grammar
from Item import Item
from Utils import Singleton, Rule

class State:
    _state_map = {}

    def print_state(self) -> None:
        for item in self._items:
            item.print_item()
        print("\n\n\n")

    # core represents the starting item set in a state, only item before closure
    def __init__(self, core: Item):
        if core in self._state_map:
            raise RuntimeError("State already exists. Shouldn't be intialized again")
        
        self._state_map[core] = self
        self._items = set([core])
        self.transitions = {}
        self.reductions = {}

        self._items |= core.closure()
        self._create_states()

    def _create_states(self):
        for item in self._items:

            if item.pos >= len(item.rhs):
                for value in item.lookahead:
                    self.reductions[value] = Rule(item.lhs, item.rhs) 
            else:            
                core = Item(Rule(item.lhs, item.rhs), item.lookahead, item.pos + 1)
                symbol = item.rhs[item.pos]

                if core in self._state_map:
                    self.transitions[symbol] = self._state_map[core]
                else:
                    self.transitions[symbol] = State(core)

class TableGenerator(metaclass=Singleton):

    @staticmethod
    def _get_augment_start() -> Item:
        lhs = "S'"
        rhs = [Grammar.START_SYMBOL]
        lookahead = set(["$"])
        
        return Item(Rule(lhs, rhs), lookahead)

    @staticmethod
    def print_states() -> None:
        i = 1
        for key in State._state_map:
            print(f"State {i}:")
            i += 1
            State._state_map[key].print_state()

    def __init__(self, file_name, output_file = None):
        self.Grammar = Grammar(file_name)

        start = self._get_augment_start()
        Grammar._rules[start.lhs] = [start.rhs] 
        start_state = State(start)

        self.print_states()

def main():
    table = TableGenerator("./PARSING/BNF_TEST.txt")
    pass

if __name__ == "__main__":
    main()

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list