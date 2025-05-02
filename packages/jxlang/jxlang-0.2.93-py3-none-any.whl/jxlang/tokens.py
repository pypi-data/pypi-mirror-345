from enum import Enum


class TokenType(Enum):
    MUL = 'MUL'            # *
    PLUS = 'PLUS'          # +
    DIV = 'DIV'            # /
    MINUS = 'MINUS'        # -
    MOD = 'MOD'            # %
    LET = 'LET'            # let
    TABLE = 'TABLE'        # table
    ID = 'ID'              # 变量名
    INT = 'INT'            # 整数
    COLON = 'COLON'        # :
    SEMI = 'SEMI'          # ;
    COMMA = 'COMMA'        # ,
    LPAREN = 'LPAREN'      # (
    RPAREN = 'RPAREN'      # )
    ARROW = 'ARROW'        # ->
    AND = 'AND'            # &&
    DOT = 'DOT'            # .
    FOR = 'FOR'            # for
    PRINT = 'PRINT'        # print
    EOF = 'EOF'
    ENTER = 'ENTER'        # enter()
    SAY = 'SAY'            # say()
    ENDEND = 'ENDEND'      # endend()
    FLOAT = 'FLOAT'        # 浮点数
    STRING = 'STRING'      # 字符串
    TRUE = 'TRUE'          # true
    FALSE = 'FALSE'        # false
    LBRACKET = 'LBRACKET'  # [
    RBRACKET = 'RBRACKET'  # ]
    CITE = 'CITE'          # 导入库
    VERSION = 'VERSION'    # 版本号
    FUNC = 'FUNC'          # func
    OUT = 'OUT'            # out
    INDENT = 'INDENT'      # 缩进
    DEDENT = 'DEDENT'      # 取消缩进
    NEWLINE = 'NEWLINE'    # 换行符
    SHAPE = 'SHAPE'        # shape()
    PUSH = 'PUSH'          # push
    THROW = 'THROW'        # throw

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"