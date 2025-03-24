from collections import namedtuple
from BNFError import BNFError
from Singleton import Singleton

Rule = namedtuple("Rule", ["lhs", "rhs"])

class Grammar(metaclass=Singleton):
    _rules: dict[str, list[list[str]]] = {}
    TAGS = ['{', '}', '+', '*', '?']
    OPTIONAL_TAGS = ['*', '?']
    REPETITION_TAGS = ['*', '+']

    def parse_file(self, filename: str) -> None:
        with open(filename, 'r') as file: 
            input = []
            for line_num, line in enumerate(file, start=1):               
                input.append(line)

            self._parse_from_string(input)

    @classmethod
    def _parse_grammar_line(cls, input: list[str], lhs = None) -> Rule:
        if len(input) >= 3 and input[1] == "::=":
            return Rule(input[0], input[2:])

        elif len(input) >= 1 and input[0] == '|':
            return Rule(lhs, input[1:])
        
        elif input:
            raise BNFError(BNFError.MSG_EMPTY_BNF)

    @classmethod 
    def _parse_from_string(cls, BNF: list[str]) -> None:
            cls.START_SYMBOL = BNF[0].split()[0]

            lhs = None
            for line in BNF:        
                substrs = line.split()
                if not substrs:
                    continue

                rule = cls._parse_grammar_line(substrs, lhs)
                if lhs != rule.lhs:
                    lhs = rule.lhs
                
                if lhs in cls._rules:
                    cls._rules[lhs].append(rule.rhs)
                else: 
                    cls._rules[lhs] = [rule.rhs]

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
            ((len(symbol)) > 1 and symbol[-1] in cls.OPTIONAL_TAGS) or 
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

    # used for testing and debugging
    @classmethod
    def get_rules(cls) -> str:
        result = ""
        for lhs, rhs in cls._rules.items():
            result += (lhs + " ::= ")
            for l in rhs:
                for s in l:
                    result += (s + " ")
                result += " | "

            result = result[:-2] + '\n'

        return result