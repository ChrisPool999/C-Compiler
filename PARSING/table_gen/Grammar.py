from Utils import Singleton, InputError

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