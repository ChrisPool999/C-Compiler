from collections import namedtuple

class InputError(Exception):
    MSG_NO_LHS = "Missing Left-hand side (lhs) definition before expansion"
    MSG_BAD_FORMAT = "Invalid format, expected either " \
                         "'<symbol> ::= ...' or '| ...'"
    MSG_EMPTY_BNF = "The grammer file is empty"

    @staticmethod
    def MSG_item_OOB(lhs: str, rhs: str, pos: int):
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
    
Rule = namedtuple("Rule", ["lhs", "rhs"])