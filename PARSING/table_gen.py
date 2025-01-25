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
    def _remove_tags(symbol: str) -> str:
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
    def _find_first(cls, symbol: str, seen: set = None) -> set[str]:
        """
            Finds any terminal symbols that can result from a symbol be expanded\n

            Parameters:\n
            symbol (str): The symbol you want to find the terminals of
            seen (set): Default Parameter. Avoid passing this argument outside the method. Used to avoid infinite expansions\n

            returns: \n 
            list[str]: strings representing terminal symbols
        """
        symbol = cls._remove_tags(symbol)        
        if seen is None: seen = set()

        if symbol in seen: return set()
        if cls._is_terminal(symbol): return set([symbol])

        seen.add(symbol)

        terminals = set()
        for RHS in cls._rules[symbol]:
            for s in RHS:
                terminals |= cls._find_first(s, seen)
                if not cls._is_optional(s): break

        return terminals

    @classmethod
    def _is_terminal(cls, symbol: str) -> bool:
        """
            Returns true if a symbol can no longer expand\n

            Parameters: symbol (str)

            Returns: bool
        """
        return symbol not in cls._rules 

    @classmethod
    def _is_optional(cls, symbol: str) -> bool:
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
    def _is_repetitive(symbol: str) -> bool:
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
    def _print_rules(cls) -> None:
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
    def __init__(self, lhs: str, rhs: str, dot_pos: int, lookahead: str):
        self.lhs = lhs
        self.rhs = rhs
        self.pos = dot_pos
        self.lookahead = lookahead 

    # LALR(1) parsing can merge states with differing look-aheads
    def _cmp(self, item):
        return (
            self.lhs == item.lhs and
            self.rhs == item.rhs and
            self.dot_pos == item.dot_pos
        )

    def _closure(self) -> list[Item]:
        """
            Performs closure on a given item set. Returns all rules where the current symbol is on the LHS
            and applies closure to any rules returned

            Parameters: no parameters

            Return: list[Item] Returns a list of item sets that are produced from closure
        """
    
        if Grammar._is_repetitive(self.RHS[self.pos]):
            pass
        pass

        # if optional?


        # if closure is optional, find closure of next...
        # STEPS
        # have: 
            # 1. base rule and look-ahead (Item)
            # 2. where we are at in the rule
        # bring all rules where the closure symbol appears on the LHS...
        # --passing along the lookahead, which is the follow() of the closure symbol
        # perform closure on all new rules until we run out of rules


        # _______________________________________________________________________________________________
        # optional...

        # decide between reducing/shifting? reduce x from nothing, or from a
        # A -> y . X? z
        # X -> . , z          
        # X -> . a, z          

        # repetitive...
        # A -> y . X* z, (some look-ahead)
        # X -> . X X , first(X)
        # X -> . , z  
        # X ..

        # one or more...
        # A -> y . X+ z
        # X -> . X X , first(X)
        # X -> . a , z

    def _find_follow(self, item: Item) -> set[str]:
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
        terminals = set()

        if Grammar._is_repetitive(item.rhs[item.pos]):
            terminals |= self._find_first(item.rhs[item.pos])

        if item.pos + 1 >= len(item.rhs):
            terminals |= item.lookahead
            return terminals

        terminals |= Grammar._find_first(item.rhs[item.pos + 1])

        if Grammar._is_optional(item.rhs[item.pos]):
            self._find_follow(item, item.pos + 1)

        return terminals

class State:

    def __init__(self):
        self._item_sets: list[Item] = []
        self.transitions: {str, State} = {}

    def _cmp_(self, state: State):
        for i in len(self._item_sets):
            item1 = self._item_sets[i]
            item2 = state._item_sets[i]
            
            if not item1.cmp(item2):
                return False
        return True

class TableGenerator:
    def __init__(self, BNF_file, output_file = None):
        self.Grammar(BNF_file)
        self._states: list[list[self.Item]] = [] 
        self._stack = ["$"]

def main():
    table = TableGenerator("PARSING/BNF.txt")
    table2 = TableGenerator("PARSING/BNF.txt")
    Grammar._print_rules()

if __name__ == "__main__":
    main()


    # OPTIONAL FIX:

    # if we have z, send it to a new state (what if we already have a state for that input...)
    # 1.)
    # A -> y . (X?)
    # A -> y .        (skipping x)  (follow() of A will become the look-ahead for y z .)
    # X -> . a        (expanding x) (needs z as a look-ahead to perform reduce)

    # decide between reducing/shifting? reduce x from nothing, or from a
    # 2.)
    # A -> y . (X?) z
    # X -> . , z        (skipping x)  (look-ahead should be follow() of A)
    # X -> . a          (expanding x) (look-ahead should be z or first() of z)

    # paths to different states should never share the same input (probably combine the states if they do)
    # look-ahead merely resolves shift/reduce
# __________________________________________________________________________________________________________________

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list