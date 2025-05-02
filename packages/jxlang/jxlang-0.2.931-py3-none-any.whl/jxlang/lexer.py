# ---------- 词法分析器 (Lexer) ----------
from .tokens import TokenType, Token

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
        self.indent_stack = [0]  # 缩进栈
        self.keywords = {
            'let': TokenType.LET,
            'table': TokenType.TABLE,
            'for': TokenType.FOR,
            'print': TokenType.PRINT,
            'say': TokenType.SAY,
            'endend': TokenType.ENDEND,
            'true': TokenType.TRUE,       # 小写 true
            'false': TokenType.FALSE,     # 小写 false
            'cite': TokenType.CITE,
            'version': TokenType.VERSION,
            'func': TokenType.FUNC,
            'out': TokenType.OUT,
            'shape': TokenType.SHAPE,
            'push': TokenType.PUSH,
            'throw': TokenType.THROW
        }

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        else:
            return None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def id(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return self.keywords.get(result, TokenType.ID), result

    def handle_indent(self):
        spaces = 0
        # 仅允许空格作为缩进，拒绝制表符
        while self.current_char == ' ':
            spaces += 1
            self.advance()
        # 如果检测到非空格字符（如Tab），抛出异常
        if self.current_char == '\t':
            raise Exception("Tab characters are not allowed for indentation.")
        # 生成 INDENT/DEDENT Token
        if spaces > self.indent_stack[-1]:
            self.indent_stack.append(spaces)
            return Token(TokenType.INDENT)
        elif spaces < self.indent_stack[-1]:
            self.indent_stack.pop()
            return Token(TokenType.DEDENT)

    def get_next_token(self):
        while self.current_char:
            # 处理注释
            if self.current_char == '#':
                while self.current_char and self.current_char != '\n':
                    self.advance()
                continue  # 继续处理下一个 Token

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INT, self.integer())

            if self.current_char.isalpha() or self.current_char == '_':
                token_type, value = self.id()
                return Token(token_type, value)

            # 处理数字（整数或浮点数）
            if self.current_char.isdigit() or (self.current_char == '.' and self.peek() and self.peek().isdigit()):
                # 处理整数部分
                integer_part = 0
                if self.current_char.isdigit():
                    integer_part = self.integer()  # 读取整数部分（如 123）

                # 处理浮点数的小数部分（如 .456 或 123.456）
                if self.current_char == '.' and self.peek() and self.peek().isdigit():
                    self.advance()  # 吃掉 '.'
                    fraction_part = self.integer()  # 读取小数部分（如 456）
                    return Token(TokenType.FLOAT, float(f"{integer_part}.{fraction_part}"))
                else:
                    return Token(TokenType.INT, integer_part)  # 纯整数

            # 处理点号 .
            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT)

            # 处理字符串（支持单引号和双引号）
            if self.current_char in ('"', "'"):
                quote_char = self.current_char
                self.advance()  # 跳过引号
                value = ''
                while self.current_char and self.current_char != quote_char:
                    # 处理转义字符
                    if self.current_char == '\\':
                        self.advance()
                        if self.current_char == 'n':
                            value += '\n'
                        elif self.current_char == 't':
                            value += '\t'
                        elif self.current_char == '\\':
                            value += '\\'
                        elif self.current_char == quote_char:
                            value += quote_char
                        else:
                            value += '\\' + self.current_char
                    else:
                        value += self.current_char
                    self.advance()
                if not self.current_char:
                    raise Exception("Unclosed string literal")
                self.advance()  # 跳过结束引号
                return Token(TokenType.STRING, value)

            # 处理布尔值
            if self.current_char.isalpha():
                token_type, value = self.id()
                if token_type in (TokenType.TRUE, TokenType.FALSE):
                    return Token(token_type, value == 'true')
                else:
                    return Token(token_type, value)

            if self.current_char in ('\n', '\r'):
                # 处理 \r\n 组合
                if self.current_char == '\r' and self.peek() == '\n':
                    self.advance()  # 跳过 \r
                self.advance()  # 跳过 \n
                # 计算缩进空格数
                spaces = 0
                while self.current_char == ' ':
                    spaces += 1
                    self.advance()
                # 生成 INDENT/DEDENT 或 NEWLINE
                if spaces > 0:
                    if spaces > self.indent_stack[-1]:
                        self.indent_stack.append(spaces)
                        return Token(TokenType.INDENT)
                    elif spaces < self.indent_stack[-1]:
                        self.indent_stack.pop()
                        return Token(TokenType.DEDENT)
                    else:
                        return Token(TokenType.NEWLINE)
                else:
                    # 在函数定义时，允许空行
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        return Token(TokenType.NEWLINE)
                    else:
                        return Token(TokenType.NEWLINE)

            # 处理运算符
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS)
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '>':  # 处理 ->
                    self.advance()
                    return Token(TokenType.ARROW)
                else:
                    return Token(TokenType.MINUS)  # 单独减号
            elif self.current_char == '*':
                self.advance()
                return Token(TokenType.MUL)
            elif self.current_char == '/':
                self.advance()
                return Token(TokenType.DIV)
            elif self.current_char == '%':
                self.advance()
                return Token(TokenType.MOD)

            # 处理列表的方括号
            if self.current_char == '[':
                self.advance()
                return Token(TokenType.LBRACKET)
            elif self.current_char == ']':
                self.advance()
                return Token(TokenType.RBRACKET)

            # 处理符号
            if self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON)
            elif self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMI)
            elif self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA)
            elif self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN)
            elif self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN)
            elif self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    return Token(TokenType.ARROW)
                else:
                    raise Exception("Invalid token '->'")
            elif self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token(TokenType.AND)
                else:
                    raise Exception("Invalid token '&&'")
            elif self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT)
            else:
                raise Exception(f"Invalid character: {self.current_char}")

        return Token(TokenType.EOF)

    # 新增 peek_token 方法
    def peek_token(self):
        # 保存当前状态
        original_pos = self.pos
        original_current_char = self.current_char
        # 注意：缩进状态的保存/恢复对于简单的 token peek 可能不是必需的，
        # 但如果 peek 跨越换行符，则可能需要处理
        # original_indent_stack = self.indent_stack[:]

        token = None
        try:
            # 获取下一个 token
            token = self.get_next_token()
        finally:
            # 恢复状态
            self.pos = original_pos
            self.current_char = original_current_char
            # self.indent_stack = original_indent_stack
        return token