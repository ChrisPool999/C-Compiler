from __future__ import annotations
from collections import namedtuple

class InputError(Exception):
    def __init__(self, message: str, input_value: str = None) -> None:
        super().__init__(message)
        self.input_value = input_value

    def __str__(self) -> str:
        if self.input_value is not None:
            return f"{self.args[0]} (Invalid input: {self.input_value})"
        
        return self.args[0]

class Singleton(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

Rule = namedtuple("Rule", ["lhs", "expansions"])

class Grammar(metaclass=Singleton):
    _rules: dict[str, list[str]] = {}

    def __init__(self, filename: str) -> None:
        self._parse_grammar(filename)

    @classmethod
    def _parse_grammar(cls, filename: str) -> None:
        """
            parse_grammar() will parse a textfile into a set of grammar rules\n
            The format must be 'lhs ::= lhs' with any additional expansions
            following each on a seperate line with the structure '| rhs'\n
            Tags such as '+', '?' or '*' must be be immediately following the symbol

            Parameters: filename (str)

            Returns: None 
        """
        with open(filename, 'r') as file:
            lhs = None

            for line in file:        
                substrs: list[str] = line.split()

                # A valid grammar rule will always have 3 parts:  LSH ::= RHS
                if len(substrs) >= 3 and substrs[1] == "::=":
                    lhs = substrs[0]
                    expansion = substrs[2:]
                    cls._rules[lhs] = [expansion]

                # An empty RHS can be valid if it's not the only expansion
                elif len(substrs) >= 1 and substrs[0] == '|':
                    if not lhs:
                        raise InputError("No lhs has been defined prior to this expansion", substrs)
                    expansion = substrs[1:]
                    cls._rules[lhs].append(expansion)
                
                elif substrs:
                    raise InputError("Invalid input", substrs)

    @classmethod
    def _is_terminal(cls, symbol: str) -> bool:
        """
            Returns true if a symbol can no longer expand\n

            Parameters: symbol (str)

            Returns: bool
        """
        return symbol not in cls._rules 

    @classmethod
    def remove_tags(symbol: str) -> str:
        """ Removes punctuation, tags, and extra information from the base symbol \n
            E.g {<assignment-operator}* --> <assignment-operator>

            Parameter: symbol(str)
            Returns: str 
        """
        left: int = None
        right: int = None

        for i in range(len(symbol)):
            if symbol[i] == '<': left = i
            if (symbol[i] == '>'): right = i
        
        if left and right:  
            return symbol[left : right + 1]
        return symbol

    @classmethod
    def find_first(cls, symbol: str, seen: set = None) -> set[str]:
        """
            Finds any terminal symbols that can result from a symbol be expanded\n

            Parameters:\n
            symbol (str): The symbol you want to find the terminals of
            seen (set): Default Parameter. Avoid passing this argument outside the method. Used to avoid infinite expansions\n

            returns: \n 
            list[str]: strings representing terminal symbols
        """
        symbol = cls.remove_tags(symbol)        
        if seen is None: seen = set()

        if symbol in seen: return set()
        if cls._is_terminal(symbol): return set([symbol])

        seen.add(symbol)

        terminals = set()
        for RHS in cls._rules[symbol]:
            for s in RHS:
                terminals |= cls.find_first(s, seen)
                if not cls.is_optional(s): break

        return terminals

    @classmethod
    def is_optional(cls, symbol: str) -> bool:
        """
            Returns true if a symbol is optional, meaning it can be omitted\n
            e.g contains the tag '?' or '*'\n

            Parameter: symbol (str)

            Returns: bool
        """
        return (
            symbol[-1] in {"?", "*"} or 
            ("ε" in cls._rules.get(symbol, []))
        )

    @classmethod
    def is_repetitive(symbol: str) -> bool:
        """
            Returns true if a symbol can occur an arbitrary number of times\n
            e.g contains the tag '+' or '*'\n

            Parameters: symbol(str)

            returns: bool
        """
        return (
            "<" in symbol and ">" in symbol and
            (
                symbol[-1] == "+" or
                symbol[-1] == "*"
            )
        )

    @classmethod
    def print_rules(cls) -> None:
        """
            Prints out the grammar rules

            Parameters: None

            Returns: None
        """
        for lhs, expansions in cls._rules.items():
            print("\n" + lhs)
            for e in expansions:
                print("    " + str(e))

class Item:

    # dot position refers to the progress made in completing a grammer rule
    def __init__(self, lhs: str, rhs: list[str], dot_pos: int, lookahead: set[str]):
        self.lhs = lhs
        self.rhs = rhs
        self.pos = dot_pos
        self.lookahead = lookahead 

    @property
    def symbol(self):
        return self.rhs[self.pos]

    def _find_follow(self, offset: int = 0) -> set[str]:
        """ 
            Finds the follow() of a symbol\n
            The follow() is the set of terminals that can appear after a symbol within a rule\n
            Includes any cases where the symbol may be optional, repetitive, or the last symbol in a rule\n
            Look-ahead should be included within the item parameter in cases where there is no symbol to the right\n

            Parameters:
            item (Item): Item class expects ("rhs": str, "i": int, "Look-ahead": str)

            Returns:
            set[str]: returns a set of terminals symbols that could possibly follow a symbol in a rule
        """
        pos = self.pos + offset        
        if pos >= len(self.rhs):
            raise RuntimeError(f"'{self.lhs} ::= {self.rhs}': "
                               f"the dot position {pos} is out of bounds")

        terminals = set()

        if Grammar.is_repetitive(self.rhs[pos]):
            terminals |= self._find_first(self.rhs[pos])

        if pos + 1 >= len(self.rhs):
            terminals |= self.lookahead
            return terminals

        terminals |= Grammar.find_first(self.rhs[pos + 1])

        if Grammar.is_optional(self.rhs[pos + 1]):
            terminals |= self._find_follow(offset + 1)

        return terminals

    #TODO optimize duplicate work with cache
    def closure(self) -> list[Item]:
        """
            Performs closure on a given item set. Returns all rules where the current symbol is on the LHS
            and applies closure to any rules returned

            Parameters: no parameters

            Return: list[Item] Returns a list of item sets that are produced from closure
        """
        new_items: list[Item] = []
        symbol = self.rhs[self.pos]
        lookahead = self._find_follow()

        if Grammar.is_repetitive(symbol):
            tag = symbol[-1]
            new_items += Item(symbol, f"{symbol} {symbol}{tag}", 0, lookahead)
        
        if Grammar.is_optional(symbol):
            new_items += Item(symbol, [], 0, lookahead)

        for rhs in Grammar._rules[symbol]:
            new_items += Item(symbol, rhs, 0, lookahead)

        for item in new_items:
            new_items += self._closure(item)

        return new_items

class State:

    # core represents the intial starter item within a set prior to closure
    def __init__(self, core: Item):
        self._item_sets: list[Item] = [core]
        self.transitions: {str, State} = {}
        self.complete_rules: {str, Rule} = [] 

        self._item_sets += core._closure()
        self._create_states()

    def _lookup_state(self, item: Item) -> State:
        core_hash = str(item.lhs + item.rhs + item.pos)

        if core_hash in self.transitions:
            return self.transitions[core_hash]
        return None

    def _create_states(self):
        for item in self._item_sets:

            if item.pos >= len(item.rhs):
                for value in item.lookahead:
                    self.complete_rules[value] = Rule(lhs=item.lhs, expansions=item.rhs) 
            else:            
                core = Item(item.lhs, item.rhs, item.pos + 1, item.lookahead)
                symbol = item.rhs[item.pos]

                if self._lookup_state(core):
                    self.transitions[symbol] = self._lookup_state(core)
                else:
                    self.transitions[symbol] = State(core)

class TableGenerator(metaclass=Singleton):

    # states: dict[str, State] = {}
    # goto_table: list[list[]]

    def __init__(self, BNF_file, output_file = None):
        self.Grammar = Grammar(BNF_file)

def main():
    table = TableGenerator("PARSING/BNF.txt")

if __name__ == "__main__":
    main()

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list