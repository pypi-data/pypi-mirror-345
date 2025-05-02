from .tokens import TokenType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    # 更新 peek 方法以使用 lexer.peek_token
    def peek(self):
        return self.lexer.peek_token()

    def cite_statement(self):
        self.eat(TokenType.CITE)
        library_name = self.current_token.value
        self.eat(TokenType.ID)
        return {'type': 'CITE', 'name': library_name}

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.current_token.type
            self.eat(op)
            node = {
                'type': 'BIN_OP',
                'op': op,
                'left': node,
                'right': self.factor()
            }
        return node

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            if self.current_token.type == TokenType.EOF:
                # 抛出特定异常，供REPL捕获并提示继续输入
                raise EOFError(f"Expected {token_type}, but reached EOF")
            else:
                raise Exception(f"Expected {token_type}, got {self.current_token.type}")

    def primary(self):
        token = self.current_token
        if token.type == TokenType.ID and token.value == "enter":
            # 解析 enter() 为函数调用
            return self.enter_expression()
        # 处理整数
        elif token.type == TokenType.INT:
            self.eat(TokenType.INT)
            return {'type': 'INT', 'value': token.value}
        # 处理浮点数
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return {'type': 'FLOAT', 'value': token.value}
        # 处理字符串
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return {'type': 'STRING', 'value': token.value}
        # 处理布尔值
        elif token.type in (TokenType.TRUE, TokenType.FALSE):
            value = token.value
            self.eat(token.type)
            return {'type': 'BOOL', 'value': value}
        # 处理变量名
        elif token.type == TokenType.ID:
            var_name = token.value
            self.eat(TokenType.ID)
            return {'type': 'VAR', 'value': var_name}
        # 处理括号表达式：( ... )
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()  # 递归解析表达式
            self.eat(TokenType.RPAREN)
            return node
        # 处理列表字面量：[ ... ]
        elif token.type == TokenType.LBRACKET:
            return self.list_expr()
        # 处理 version()
        elif token.type == TokenType.VERSION:
            return self.version_call()
        else:
            raise Exception(f"Unexpected token: {token.type}")

    def factor(self):
        node = self.primary()  # 解析基础因子
        while True:
            # 处理成员访问
            if self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                member = self.current_token.value
                self.eat(TokenType.ID)
                node = {
                    'type': 'MEMBER_ACCESS',
                    'object': node,
                    'member': member
                }

            # 处理函数调用
            if self.current_token.type == TokenType.LPAREN:
                node = self.call(node)  # 解析函数调用参数并生成 CALL 节点

            # 处理索引访问
            if self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)  # 消费 [
                index = self.expr()  # 解析索引表达式
                self.eat(TokenType.RBRACKET)  # 消费 ]
                node = {
                    'type': 'INDEX_ACCESS',
                    'object': node,
                    'index': index
                }
            else:
                break  # 没有更多链式操作，退出循环
        return node

    def version_call(self):
        self.eat(TokenType.VERSION)  # 消费 'version'
        self.eat(TokenType.LPAREN)  # 消费 '('
        self.eat(TokenType.RPAREN)  # 消费 ')'
        return {'type': 'VERSION_CALL'}

    def call(self, node):
        self.eat(TokenType.LPAREN)  # 消费 '('
        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())  # 解析第一个参数
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)  # 消费 ','
                args.append(self.expr())  # 解析后续参数
        self.eat(TokenType.RPAREN)  # 消费 ')'
        return {
            'type': 'CALL',
            'func': node,
            'args': args
        }

    def parse(self):
        return self.statement()

    def statement(self):
        try:
            if self.current_token.type == TokenType.LET:
                return self.let_statement()
            elif self.current_token.type == TokenType.LPAREN:
                return self.loop_statement()
            elif self.current_token.type == TokenType.PRINT:
                return self.print_statement()
            elif self.current_token.type == TokenType.LET:
                return self.let_statement()
            elif self.current_token.type == TokenType.LPAREN:
                return self.loop_statement()
            elif self.current_token.type == TokenType.PRINT:
                return self.print_statement()
            elif self.current_token.type == TokenType.SAY:
                return self.say_statement()
            elif self.current_token.type == TokenType.ENDEND:
                return self.endend_statement()
            elif self.current_token.type == TokenType.ENTER:
                return self.enter_expression()
            elif self.current_token.type == TokenType.CITE:
                return self.cite_statement()
            elif self.current_token.type == TokenType.FUNC:
                return self.func_definition()
            elif self.current_token.type == TokenType.SHAPE:
                return self.shape_statement()
            elif self.current_token.type == TokenType.PUSH:
                return self.push_statement()
            elif self.current_token.type == TokenType.OUT:
                return self.out_statement()
            elif self.current_token.type == TokenType.THROW:
                return self.throw_statement()
            else:
                return self.expr()
        except EOFError:
            # 允许未闭合结构继续输入
            raise
        except Exception as e:
            raise Exception(f"Syntax error: {e}")

    def shape_statement(self):
        self.eat(TokenType.SHAPE)
        self.eat(TokenType.LPAREN)
        expr_node = self.expr()
        self.eat(TokenType.RPAREN)
        return {'type': 'SHAPE', 'expr': expr_node}

    def func_definition(self):
        raise Exception("Function definitions are temporarily disabled.")
        self.eat(TokenType.FUNC)
        self.eat(TokenType.LPAREN)
        params = []
        # 解析参数列表
        while self.current_token.type != TokenType.ARROW:
            param = self.current_token.value
            self.eat(TokenType.ID)
            params.append(param)
            if self.current_token.type == TokenType.AND:
                self.eat(TokenType.AND)
        self.eat(TokenType.ARROW)  # 消费 ->
        func_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)

        # 允许函数体在同一行或换行后缩进
        if self.current_token.type == TokenType.NEWLINE:
            self.eat(TokenType.NEWLINE)
            # 跳过空行
            while self.current_token.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
            # 必须缩进
            if self.current_token.type != TokenType.INDENT:
                raise Exception("Function body must be indented")
            self.eat(TokenType.INDENT)
        elif self.current_token.type == TokenType.INDENT:
            self.eat(TokenType.INDENT)
        else:
            pass  # 单行函数体，无需缩进

        # 解析函数体
        body = []
        while True:
            if self.current_token.type == TokenType.OUT:
                self.eat(TokenType.OUT)
                return_expr = self.expr()
                body.append({'type': 'RETURN', 'value': return_expr})
                break
            elif self.current_token.type in (TokenType.DEDENT, TokenType.EOF):
                break  # 函数体结束
            else:
                body.append(self.statement())

        if self.current_token.type == TokenType.DEDENT:
            self.eat(TokenType.DEDENT)

        return {
            'type': 'FUNC_DEF',
            'name': func_name,
            'params': params,
            'body': body
        }

    def func_call(self):
        args = []
        while self.current_token.type != TokenType.ARROW:
            args.append(self.expr())
            if self.current_token.type == TokenType.AND:
                self.eat(TokenType.AND)
        self.eat(TokenType.ARROW)
        func_name = self.current_token.value
        self.eat(TokenType.ID)
        return {
            'type': 'FUNC_CALL',
            'name': func_name,
            'args': args
        }

    def let_statement(self):
        self.eat(TokenType.LET)
        variables = []
        while True:
            if self.current_token.type == TokenType.ID:
                var_name = self.current_token.value
                self.eat(TokenType.ID)
                if self.current_token.type == TokenType.LBRACKET:
                    self.eat(TokenType.LBRACKET)
                    index = self.expr()
                    self.eat(TokenType.RBRACKET)
                    var_name = {'type': 'INDEX_ACCESS', 'object': var_name, 'index': index}
            else:
                raise Exception("Expected variable name")
            self.eat(TokenType.COLON)
            value = self.expr()
            variables.append((var_name, value))
            if self.current_token.type != TokenType.AND:
                break
            self.eat(TokenType.AND)
        return {'type': 'LET', 'vars': variables}

    def loop_statement(self):
        self.eat(TokenType.LPAREN)
        variables = []
        # 解析循环变量 (保持不变)
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            while self.current_token.type == TokenType.ID:
                variables.append(self.current_token.value)
                self.eat(TokenType.ID)
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
            self.eat(TokenType.RPAREN)
        else:
            variables.append(self.current_token.value)
            self.eat(TokenType.ID)

        self.eat(TokenType.ARROW)  # 消费 ->

        # --- 修改开始 ---
        # 解析范围或可迭代对象
        first_expr = self.expr()
        if self.current_token.type == TokenType.AND:
            # 解析为数值范围
            self.eat(TokenType.AND)
            second_expr = self.expr()
            iterable_source_node = {'type': 'RANGE', 'start': first_expr, 'end': second_expr}
        else:
            # 解析为可迭代对象源
            iterable_source_node = {'type': 'ITERABLE', 'source': first_expr}
        # --- 修改结束 ---

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.DOT)
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)

        body = self.statement() # 解析循环体 (保持不变)

        self.eat(TokenType.RPAREN)

        return {
            'type': 'FOR_LOOP',
            'vars': variables,
            'iterable_spec': iterable_source_node, # 更新字段名
            'body': body
        }

    def print_statement(self):
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr_node = self.expr()
        self.eat(TokenType.RPAREN)
        return {'type': 'PRINT', 'expr': expr_node}

    def expr(self):
        if self.current_token.type == TokenType.TABLE:
            return self.table_expr()
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.type
            self.eat(op)
            node = {
                'type': 'BIN_OP',
                'op': op,
                'left': node,
                'right': self.term()
            }
        return node

    def table_expr(self):
        self.eat(TokenType.TABLE)
        self.eat(TokenType.LPAREN)
        if self.current_token.type == TokenType.RPAREN:
            self.eat(TokenType.RPAREN)
            return {'type': 'LIST', 'value': []}  # 空列表
        elements = []
        while self.current_token.type != TokenType.RPAREN:
            elements.append(self.expr())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            elif self.current_token.type == TokenType.SEMI:
                self.eat(TokenType.SEMI)
                sublists = [{'type': 'LIST', 'value': elements}]
                elements = []
                while self.current_token.type != TokenType.RPAREN:
                    sublist = []
                    while self.current_token.type not in (TokenType.SEMI, TokenType.RPAREN):
                        sublist.append(self.expr())
                        if self.current_token.type == TokenType.COMMA:
                            self.eat(TokenType.COMMA)
                    sublists.append({'type': 'LIST', 'value': sublist})
                    if self.current_token.type == TokenType.SEMI:
                        self.eat(TokenType.SEMI)
                self.eat(TokenType.RPAREN)
                return {'type': 'TABLE', 'value': sublists}
        self.eat(TokenType.RPAREN)
        return {'type': 'LIST', 'value': elements}

    # 解析列表字面量
    def list_expr(self):
        self.eat(TokenType.LBRACKET)
        elements = []
        while self.current_token.type != TokenType.RBRACKET:
            elements.append(self.expr())
            if self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        self.eat(TokenType.RBRACKET)
        return {'type': 'LIST', 'elements': elements}

    def simple_expr(self):
        token = self.current_token
        if token.type == TokenType.INT:
            self.eat(TokenType.INT)
            return {'type': 'INT', 'value': token.value}
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return {'type': 'FLOAT', 'value': token.value}
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return {'type': 'STRING', 'value': token.value}
        elif token.type in (TokenType.TRUE, TokenType.FALSE):
            value = token.value
            self.eat(token.type)
            return {'type': 'BOOL', 'value': value}
        elif token.type == TokenType.ID:
            value = token.value
            self.eat(TokenType.ID)
            return {'type': 'VAR', 'value': value}
        else:
            raise Exception("Unexpected token")

    # 解析 enter()
    def enter_expression(self):
        self.eat(TokenType.ID)  # 消费 "enter"
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.RPAREN)
        return {'type': 'ENTER_CALL'}

    # 解析 say(expr)
    def say_statement(self):
        self.eat(TokenType.SAY)
        self.eat(TokenType.LPAREN)
        expr_node = self.expr()
        self.eat(TokenType.RPAREN)
        return {'type': 'SAY', 'expr': expr_node}

    # 解析 endend()
    def endend_statement(self):
        self.eat(TokenType.ENDEND)
        self.eat(TokenType.LPAREN)
        arg = None
        if self.current_token.type == TokenType.INT:
            arg = self.current_token.value
            self.eat(TokenType.INT)
        self.eat(TokenType.RPAREN)
        return {'type': 'ENDEND', 'arg': arg}

    def push_statement(self):
        self.eat(TokenType.PUSH)
        element = self.expr()
        self.eat(TokenType.ARROW)
        list_obj = self.expr()
        return {'type': 'PUSH', 'element': element, 'list': list_obj}

    def out_statement(self):
        self.eat(TokenType.OUT)
        all_same = False  # 默认值

        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            next_token_peek = self.peek() # 查看括号后的第一个 token

            # 检查是否为 True 或 False (关键字或ID)
            is_pos_true = self.current_token.type == TokenType.TRUE or \
                          (self.current_token.type == TokenType.ID and self.current_token.value == 'True')
            is_pos_false = self.current_token.type == TokenType.FALSE or \
                           (self.current_token.type == TokenType.ID and self.current_token.value == 'False')

            # 情况 1: out(True) 或 out(False)，后面必须是右括号
            if (is_pos_true or is_pos_false) and next_token_peek.type == TokenType.RPAREN:
                all_same = is_pos_true
                # 消耗掉 True/False (无论是 TokenType 还是 ID)
                self.eat(self.current_token.type)

            # 情况 2: out(all_same : True/False)
            elif self.current_token.type == TokenType.ID and self.current_token.value == 'all_same' and next_token_peek.type == TokenType.COLON:
                self.eat(TokenType.ID)      # 消耗 'all_same'
                self.eat(TokenType.COLON)   # 消耗 ':'

                # 现在检查冒号后面的 True 或 False
                is_kw_true = self.current_token.type == TokenType.TRUE or \
                             (self.current_token.type == TokenType.ID and self.current_token.value == 'True')
                is_kw_false = self.current_token.type == TokenType.FALSE or \
                              (self.current_token.type == TokenType.ID and self.current_token.value == 'False')

                if is_kw_true:
                    all_same = True
                    self.eat(self.current_token.type) # 消耗 True/False
                elif is_kw_false:
                    all_same = False
                    self.eat(self.current_token.type) # 消耗 True/False
                else:
                    raise Exception("Expected True or False after 'all_same:'")
                # 确认布尔值后面是右括号
                if self.current_token.type != TokenType.RPAREN:
                     raise Exception("Expected ')' after boolean value for 'all_same'")

            # 情况 3: 括号内语法无效
            else:
                raise Exception("Invalid syntax within out(). Expected out(True), out(False), out(all_same:True), or out(all_same:False)")

            self.eat(TokenType.RPAREN) # 消耗最后的右括号

        # 解析要移除的元素和目标列表 (这部分不变)
        element = self.expr()
        self.eat(TokenType.ARROW)
        list_obj = self.expr()
        return {'type': 'OUT', 'element': element, 'list': list_obj, 'all_same': all_same}

    def throw_statement(self):
        self.eat(TokenType.THROW)
        element = self.expr()
        self.eat(TokenType.ARROW)
        list_obj = self.expr()
        return {'type': 'THROW', 'element': element, 'list': list_obj}