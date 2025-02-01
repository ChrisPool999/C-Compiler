from __future__ import annotations
from collections import namedtuple

# TODO ISSUES TO SOLVE
# give only tag characters

# Grammar that is not LALR
#   - Ambigious grammar (look-ahead conflict)
#   - Left recursive (infinite recursion, in SOME cases)

class InputError(Exception):
    MSG_NO_LHS = "Missing Left-hand side (lhs) definition before expansion"
    MSG_BAD_FORMAT = "Invalid format, expected either " \
                         "'<symbol> ::= ...' or '| ...'"
    MSG_EMPTY_BNF = "The grammer file is empty"

    @classmethod
    def MSG_item_OOB(self, lhs: str, rhs: str, pos: int):
        return f"Rule '{lhs} ::= {rhs}': " \
               f"the dot position {pos} is out of bounds"

    def __init__(self, message: str, line_num:str, input_value:str) -> None:
        super().__init__(message)
        self.input_value = input_value
        self.line_num = line_num

    def __str__(self) -> str:
        line_text = f'{self.input_value.lstrip().rstrip()}'
        return f"Line number {self.line_num}: {self.args[0]} -> {line_text})"

class Singleton(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

class Grammar(metaclass=Singleton):
    _rules: dict[str, list[str]] = {}
    TAGS = ['{', '}', '+', '*', '?']
    OPTIONAL_TAGS = ['*', '?']
    REPETITION_TAGS = ['*', '+']

    def __init__(self, filename: str) -> None:
        self._parse_grammar(filename)

    @classmethod
    def _get_start_symbol(cls, file) -> str:
        first_line = file.readline().split()
        file.seek(0)

        if first_line:
            return first_line[0]
        
        raise InputError(InputError.MSG_EMPTY_BNF) 

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
            cls.START_SYMBOL = cls._get_start_symbol(file)                            

            lhs = None
            for line_num, line in enumerate(file, start=1):        
                substrs: list[str] = line.split()

                # A valid grammar rule will always have 3 parts:  LSH ::= RHS
                if len(substrs) >= 3 and substrs[1] == "::=":
                    lhs = substrs[0]
                    rhs = substrs[2:]
                    cls._rules[lhs] = [rhs]

                # An empty RHS can be valid if its not the first rule
                elif len(substrs) >= 1 and substrs[0] == '|':
                    if not lhs:
                        raise InputError(InputError.MSG_NO_LHS, line_num, line)
                    rhs = substrs[1:]
                    cls._rules[lhs].append(rhs)
                
                elif substrs:
                    raise InputError(InputError.MSG_BAD_FORMAT, line_num, line)

    @classmethod
    def is_terminal(cls, symbol: str) -> bool:
        """
            Returns true if a symbol can no longer expand\n

            Parameters: symbol (str)

            Returns: bool
        """
        symbol = cls.remove_tags(symbol)
        return symbol not in cls._rules 

    @classmethod
    def remove_tags(cls, symbol: str) -> str:
        """ Removes punctuation, tags, and extra information from the base symbol \n
            E.g {<assignment-operator}* --> <assignment-operator>

            Parameter: symbol(str)
            Returns: str 
        """
        if len(symbol) <= 2:
            return symbol

        left:int = 0
        right:int = len(symbol) - 1

        while left < len(symbol) and symbol[left] in cls.TAGS:
            left += 1
        while right >= 0 and symbol[right] in cls.TAGS:
            right -= 1

        if right < left:
            raise RuntimeError(f"symbol '{symbol}' contains only tag characters")
        
        return symbol[left : right + 1]

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
        if cls.is_terminal(symbol): return set([symbol])

        seen.add(symbol)

        terminals = set()
        # first terminal can be from any rule
        for RHS in cls._rules[symbol]:
            for s in RHS:
                terminals |= cls.find_first(s, seen)
                # if optional, next symbol terminals are valid
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
            (len(symbol) > 1 and symbol[-1] in cls.OPTIONAL_TAGS) or 
            ("ε" in cls._rules.get(symbol, []))
        )

    @classmethod
    def is_repetitive(cls, symbol: str) -> bool:
        """
            Returns true if a symbol can occur an arbitrary number of times\n
            e.g contains the tag '+' or '*'\n

            Parameters: symbol(str)

            returns: bool
        """
        return len(symbol) > 1 and symbol[-1] in cls.REPETITION_TAGS

    @classmethod
    def print_rules(cls) -> None:
        """
            Prints out the grammar rules

            Parameters: None

            Returns: None
        """
        for lhs, rhs in cls._rules.items():
            print("\n" + lhs)
            for symbol in rhs:
                print("    " + str(symbol))

Rule = namedtuple("Rule", ["lhs", "rhs"])

class Item:

    @property
    def lhs(self):
        return self.rule.lhs

    @property
    def rhs(self):
        return self.rule.rhs

    # dot position refers to the progress made in completing a grammer rule
    def __init__(self, rule: Rule, lookahead: set[str] = set(), pos: int = 0):
        if not isinstance(rule, Rule):
            raise TypeError(f"rule must be a Rule type, it's a {type(rule)} rule -> {rule}")

        if not isinstance(rule.rhs, list):
            raise TypeError(f"RHS must be a list, it's a {type(rule.rhs)} RHS -> {rule.rhs}")
        
        if not isinstance(lookahead, set):
            raise TypeError(f"lookahead must be a list, it's a {type(lookahead)} lookahead -> {lookahead}")        

        self.rule = rule
        self.lookahead = lookahead 
        self.pos = pos

    def __eq__(self, other: Item) -> bool:
        if not isinstance(other, Item):
            raise RuntimeError(f"Trying to compare a class of Item with a {type(other)}")

        # look-ahead can be different in LALR(1)
        return (
            self.lhs == other.lhs and   
            self.rhs == other.rhs and 
            self.pos == other.pos 
        )   

    def __hash__(self):
        string = self.lhs
        for s in self.rhs:
            string += s
        string += str(self.pos)
        return hash(string) 

    def print_item(self) -> None:
        expansion = " "
        for i in range(len(self.rhs)):
            if i == self.pos:
                expansion += " . "
            expansion += self.rhs[i] + " "
        if (self.pos >= len(self.rhs)):
            expansion += " . "

        lookahead_list = ""
        for terminal in self.lookahead:
            lookahead_list += terminal + " "

        print(self.lhs + " ::= " + expansion + "\n" + lookahead_list)

    def _find_follow(self, _offset: int = 0) -> set[str]:
        """ 

            Finds the follow() of a symbol\n
            The follow() is the set of terminals that can appear after a symbol within a rule\n
            Includes any cases where the symbol may be optional, repetitive, or the last symbol in a rule\n

            Parameters:\n
            item (Item)\n
            offset (int) (Only intended for internal use) Offset shifts the progress position of rule forward. \n

            Returns:
            set[str]: returns a set of terminals symbols that could possibly follow a symbol in a rule
        """        
        pos = self.pos + _offset
        if pos >= len(self.rhs): 
            raise IndexError(InputError.MSG_item_OOB(self.lhs, self.rhs, pos))

        terminals = set()

        # if the current symbol can repeat, the repeat would follow the current
        curr_symbol = self.rhs[pos]
        if Grammar.is_repetitive(curr_symbol):
            terminals |= Grammar.find_first(curr_symbol)

        # follow of the end symbol = follow of LHS/reduction = item's look-ahead
        if pos == len(self.rhs) - 1:
            terminals |= self.lookahead
            return terminals

        next_symbol = self.rhs[pos + 1]
        if Grammar.is_optional(next_symbol):
            terminals |= self._find_follow(_offset + 1)

        terminals |= Grammar.find_first(next_symbol)
        return terminals

    #TODO optimize duplicate work with cache
    def closure(self, seen = None) -> set[Item]:
        """

            Performs closure on a given item set. Returns all rules where the current symbol is on the LHS
            and applies closure to any rules returned

            Parameters: no parameters

            Return: list[Item] Returns a list of item sets that are produced from closure
        """    
        if not seen:
            seen = set()

        if self.lhs in seen:
            return set()
        seen.add(self)
        
        if len(self.rhs) == 0 or self.pos >= len(self.rhs) or Grammar.is_terminal(self.rhs[self.pos]):
            return set()
    
        new_items = set()

        symbol = self.rhs[self.pos]
        lookahead = self._find_follow()
       
        # symbol needs to be able to repeat any number of times
        if Grammar.is_repetitive(symbol):
            new_items.add(Item(Rule(symbol, [symbol, symbol]), lookahead))
        
        # empty set = Can produce optional symbols with no input 
        if Grammar.is_optional(symbol):
            new_items.add(Item(Rule(symbol, []), lookahead))

        lhs = Grammar.remove_tags(symbol)
        for rhs in Grammar._rules[lhs]:
            new_items.add(Item(Rule(symbol, rhs), lookahead))

        while new_items - seen:
            item = (new_items - seen).pop()
            new_items |= item.closure(seen)

        return new_items

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
    table = TableGenerator("PARSING/BNF_TEST.txt")

if __name__ == "__main__":
    main()

# <parameter-list> , ...    -> can optionally append a comma seperated list of parameter-list