import sys
from itertools import islice
from collections import namedtuple

class InputError(Exception):
    def __init__(self, message: str, input_value: str = None) -> None:
        super().__init__(message)
        self.input_value = input_value

    def __str__(self) -> str:
        if self.input_value is not None:
            return f"{self.args[0]} (Invalid input: {self.input_value})"
        
        return self.args[0]

Rule = namedtuple("Rule", ["LHS", "expansions"])

class Grammer:

    def __init__(self, filename: str) -> None:
        self._rules: dict[list:str] = {}
        self._parse_grammer(filename)

    def _print_rules(self) -> None:
        print("\n")
        for LHS, expansions in self._rules.items():
            print(LHS)
            for e in expansions:
                print("    " + str(e))
            print("\n")

    def _parse_grammer(self, filename: str) -> None:
        with open(filename, 'r') as file:
            LHS = ""
            expansions = []

            lines:list[str] = file.readlines()
            for i in range(len(lines)):        
                symbols: list[str] = lines[i].split()

                if not symbols:
                    self._rules[LHS] = expansions
                    expansions = []
                    continue
                
                if symbols[1] == "::=":
                    LHS = symbols[0]
                    expansions.append(symbols[2 : len(symbols)])

                elif (symbols[0] == '|'):
                    expansions.append(symbols[1 : len(symbols)])
                
                else:
                    print(symbols + "\n")
                    raise InputError("Invalid input", symbols)
                
                if i == len(lines) - 1:
                    self._rules[LHS] = expansions

    def _remove_tags(self, symbol: str) -> str:
        """ Removes punctuation, tags, and extra information from the base symbol \n
            E.g {<assignment-operator}* --> <assignment-operator"""

        left: int = None
        right: int = None

        for i in range(len(symbol)):
            if symbol[i] == '<':
                left = i
            if (symbol[i] == '>'):
                right = i
        
        if left and right:
            return symbol[left : right + 1]
        return symbol

    def _is_terminal(self, symbol: str) -> bool:
        return symbol not in self._rules 

    def _is_optional(self, symbol: str) -> bool:
        return (
            symbol[-1] in {"?", "*"} or 
            ("ε" in self._rules.get(symbol, []))
        )

    def _is_repetitive(self, symbol: str) -> bool:
        return (
            "<" in symbol and 
            ">" in symbol and
            (
                symbol[-1] == "+" or
                symbol[-1] == "*"
            )
        )

    def _get_rule(self, index: int) -> Rule:
        if (index >= len(self._rules.items())):
            raise IndexError(f"Index {index} is out of bounds")
        
        l, r = list(self._rules.items())[index]
        return Rule(LHS=l, expansions=r)

class TableGenerator:
    Item = namedtuple("item", ["RHS", "i", "lookahead"])

    def __init__(self, BNF_file, output_file = None):
        self._grammer = Grammer(BNF_file)
        self._states: list[list[self.Item]] = [] 
        self._stack = ["$"]
        
        # start_rule = self._grammer._get_rule(0)
        # start_item = self.Item(rule=start_rule, lookahead=["$"])
        # self._create_state(start_item)

    def _create_state(self, start_item: Item) -> None:
        return 
        # items = [start_item]
        # self._closure()

    def _closure(self, item: Item, state_num: int) -> Item:
        # if closure is optional, find closure of next...
        return

    def _find_follow(self, item: Item) -> set[str]:
        terminals = set()

        if self._grammer._is_repetitive(item.RHS[item.i]):
            terminals |= self._find_first(item.RHS[item.i])

        if item.i + 1 >= len(item.RHS):
            terminals |= item.lookahead
            return terminals

        terminals |= self._find_first(item.RHS[item.i + 1])

        if self._grammer._is_optional(item.RHS[item.i]):
            self._find_follow(item, item.i + 1)

        return terminals

    # removing symbol at the top is important here 
    # we want the symbol to be tagless for the entire method
    # OTHER than when we call is_optional(), 
    # which works since the symbols (s) still has tags during the nested for loop
    def _find_first(self, symbol: str, seen: set = None) -> set[str]:
        """
            Finds the terminal symbols that can expand from a symbol\n
            Will automatically remove any tags from the symbol\n
            E.g {<specifier-qualifier>}* -> <specifier-qualifier> which is how the LHS is represented in the BNF\n

            Parameters:\n
            symbol (str): The symbol you want to find the terminals of
            seen (set): Default Parameter. Avoid passing this argument outside the method. Used to avoid infinite expansions\n

            returns:\n
            list[str]: strings representing terminal symbols
        """
        if seen is None: seen = set()
        symbol = self._grammer._remove_tags(symbol)

        if symbol in seen: return set()
        if self._grammer._is_terminal(symbol): return set([symbol])

        seen.add(symbol)
        terminals = set()

        for RHS in self._grammer._rules[symbol]:
            for s in RHS:
                terminals |= self._find_first(s, seen)
                if not self._grammer._is_optional(s): break

        return terminals

def main():
    table = TableGenerator("PARSING/BNF.txt")
    print(table._find_follow(table.Item(RHS=["{<external-declaration>}*"], i=0, lookahead=set("$"))))

if __name__ == "__main__":
    main()

#____________________________________________________________________________________________________________
# have to handle repetition, optionals, far right closures (just give previous look-ahead...)

#_____________________________________________________________________________________________________________
# if its an optional... we want to ALSO do the thing do the symbol after it
# if its a repetition... we want to ALSO do the thing as IF the next symbol was the closure 

# OPTIONAL CLOSURE
# . {<pointer>}? <direct-declarator>
# . <direct-declarator>

# REPETITION CLOSURE
# {<specifier-qualifier>}+ {<abstract-declarator>}?
# . {<specifier-qualifier>}+ {<abstract-declarator>}?
# look-ahead for <specifier-qualifier, sends it so the same state, eg . {<specifier-qualifier>}+ {<abstract-declarator>}?
# look-ahead for {<abstract-declarator>} or follow(LHS) sends it to 2 different states

#_________________________________________________________________________________________________________________________________________

# closure
#   - add all rules where the symbol appears on the LHS
#       - Need to include support for optionals
#       - Need to include support for repetitions 

# follow()
#   - get first() possible terminals AFTER the closure symbol
#       - Need to include support for optionals
#       - Need to include support for repetitions 
#       - need to include support for far-right symbols
# _____________________________________________________________________________________________________

# what happens if a closure is optional?
#   - perform closure on both the optional and the symbol after, assuming its non-terminal

# what happens if a closure if on the far right?
#   - the look-ahead will stay the same as the current rule, eg S -> a.X, $  lookahead = $

# what happens if a closure is repetitive?
#   we must consider both cases if closure symbol appears once or more

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list