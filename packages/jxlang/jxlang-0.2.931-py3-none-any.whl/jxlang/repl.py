from .interpreter import Interpreter
from .exceptions import ExitREPL
from .lexer import Lexer
from .parser import Parser
from .tokens import TokenType


def repl():
    print("JxLang MI (输入 endend() 退出，输入 version() 查看版本)")
    interpreter = Interpreter()
    while True:
        text_lines = []
        prompt = "jxlang> "  # 每次新语句开始时重置提示符
        while True:
            try:
                line = input(prompt).strip().replace('\r', '')
                if not line and not text_lines: # 完全空行，且不是多行输入中间的空行
                    continue
                text_lines.append(line)
                full_text = "\n".join(text_lines)

                # --- 新增检查：预扫描 Token ---
                temp_lexer = Lexer(full_text)
                has_meaningful_token = False
                while True:
                    token = temp_lexer.get_next_token()
                    # 我们认为除了 NEWLINE 和 EOF 之外的都是有意义的 Token
                    # （注释已经被 lexer 内部跳过，不会生成 Token）
                    if token.type not in (TokenType.NEWLINE, TokenType.EOF):
                        has_meaningful_token = True
                        break
                    if token.type == TokenType.EOF:
                        break
                # --- 检查结束 ---

                # 如果只有换行或EOF，并且不是在多行输入过程中，则认为输入无效/空，重新提示
                if not has_meaningful_token and prompt == "jxlang> ":
                     text_lines = [] # 清空，避免影响下次输入
                     raise EOFError("Comment only or empty line") # 用 EOFError 触发重新提示

                # 如果有有意义的Token，或者在多行输入中，尝试解析
                lexer = Lexer(full_text) # 重新创建 Lexer 供 Parser 使用
                parser = Parser(lexer)
                tree = parser.parse()
                # 如果解析成功，跳出内层循环，执行代码
                break
            except EOFError: # 捕获由 parser 抛出的 EOFError (需要更多输入) 或我们自己抛出的
                if prompt == "jxlang> ": # 如果是初次提示符下的EOF (比如只有注释行)
                    # 清空 text_lines 准备接收新输入，但不改变提示符，直接 continue 外层循环
                    text_lines = []
                    continue # 继续外层 while True 循环，获取新输入
                else:
                    # 如果是 ... 提示符下的 EOF，说明是需要继续输入的多行模式
                    prompt = "    ... "
            except Exception as e:
                print(f"Syntax Error: {e}")
                text_lines = [] # 清空错误的输入
                # 不改变提示符，直接 break 内层循环，然后 continue 外层循环获取新输入
                break

        # 如果 text_lines 为空 (因为语法错误或只有注释被清空)，则跳过执行
        if not text_lines:
            continue

        # 执行解析后的代码
        try:
            result = interpreter.visit(tree)
            if result is not None:
                if isinstance(result, dict) and result.get('type') == 'JX_LIST':
                    print(result['data'])
                else:
                    print(result)
        except ExitREPL as e:
            print(f"Exiting with code {e.code}")
            break
        except Exception as e:
            print(f"Runtime Error: {e}")

def run_jl_file():
    import sys
    if len(sys.argv) < 2:
        print("Usage: jlr <filename.jl>")
        return

    filename = sys.argv[1]
    if not filename.endswith('.jl'):
        print("Error: The file must have a .jl extension.")
        return

    try:
        print(f"Reading file: {filename}")  # 调试信息
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()

        print("File content loaded. Starting parsing...")  # 调试信息
        interpreter = Interpreter()
        lexer = Lexer(code)
        parser = Parser(lexer)
        tree = parser.parse()

        print("Parsing completed. Executing code...")  # 调试信息
        result = interpreter.visit(tree)

        print("Execution completed.")  # 调试信息
        if result is not None:
            if isinstance(result, dict) and result.get('type') == 'JX_LIST':
                print(result['data'])
            else:
                print(result)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except Exception as e:
        print(f"Error: {e}")