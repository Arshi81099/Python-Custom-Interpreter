import sys
from typing import Any




def print_error(message):
    sys.stderr.write(f"{message}\n")

    
ENVIRONMENT = {}



class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal if self.literal is not None else 'null'}"



class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.had_error = False
        self.keywords = {
            "and": "AND",
            "class": "CLASS",
            "else": "ELSE",
            "false": "FALSE",
            "for": "FOR",
            "fun": "FUN",
            "if": "IF",
            "nil": "NIL",
            "or": "OR",
            "print": "PRINT",
            "return": "RETURN",
            "super": "SUPER",
            "this": "THIS",
            "true": "TRUE",
            "var": "VAR",
            "while": "WHILE",
        }

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def scan_token(self):
        c = self.advance()
        if c == "(":
            self.add_token("LEFT_PAREN")
        elif c == ")":
            self.add_token("RIGHT_PAREN")
        elif c == "{":
            self.add_token("LEFT_BRACE")
        elif c == "}":
            self.add_token("RIGHT_BRACE")
        elif c == ",":
            self.add_token("COMMA")
        elif c == ".":
            self.add_token("DOT")
        elif c == "-":
            self.add_token("MINUS")
        elif c == "+":
            self.add_token("PLUS")
        elif c == ";":
            self.add_token("SEMICOLON")
        elif c == "*":
            self.add_token("STAR")
        elif c == "!":
            if self.match("="):
                self.add_token("BANG_EQUAL")
            else:
                self.add_token("BANG")
        elif c == "=":
            if self.match("="):
                self.add_token("EQUAL_EQUAL")
            else:
                self.add_token("EQUAL")
        elif c == "<":
            if self.match("="):
                self.add_token("LESS_EQUAL")
            else:
                self.add_token("LESS")
        elif c == ">":
            if self.match("="):
                self.add_token("GREATER_EQUAL")
            else:
                self.add_token("GREATER")
        elif c == "/":
            if self.match("/"):
                # a comment goes until the end of the line
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token("SLASH")
        elif c == " ":
            pass
        elif c == "\r":
            pass
        elif c == "\t":
            pass
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == "_":
            self.identifier()
        else:
            self.error(self.line, f"Unexpected character: {c}")

    def error(self, line, message, where=""):
        self.had_error = True
        print_error(f"[line {line}] Error{where}: {message}")

    def identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.source[self.start : self.current]
        type = self.keywords.get(text)
        if type is None:
            self.add_token("IDENTIFIER")
        else:
            self.add_token(type)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        value = float(self.source[self.start : self.current])
        self.add_token("NUMBER", value)

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.error(self.line, "Unterminated string.")
            return
        self.advance()
        self.add_token("STRING", self.source[self.start + 1 : self.current - 1])

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def match(self, expected):
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def is_at_end(self):
        return self.current >= len(self.source)

    def add_token(self, type, literal=None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def scan(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens



class ExpressionVisitor:
    def visit_binary_expression(self, expression: "BinaryExpression"):
        raise NotImplementedError("Subclass must implement abstract method")

    def visit_literal_expression(self, expression: "LiteralExpression"):
        raise NotImplementedError("Subclass must implement abstract method")

    def visit_unary_expression(self, expression: "UnaryExpression"):
        raise NotImplementedError("Subclass must implement abstract method")

    def visit_grouping_expression(self, expression: "GroupingExpression"):
        raise NotImplementedError("Subclass must implement abstract method")

    def visit_variable_expression(self, expression: "VariableExpression"):
        raise NotImplementedError("Subclass must implement abstract method")


class Expression:
    def accept(self, visitor: "ExpressionVisitor"):
        raise NotImplementedError("Subclass must implement abstract method")


class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_binary_expression(self)


class AssignmentExpression(Expression):
    def __init__(self, name: Token, value: Expression):
        self.name = name
        self.value = value

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_assignment_expression(self)


class LiteralExpression(Expression):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_literal_expression(self)


class UnaryExpression(Expression):
    def __init__(self, operator: Token, right: Expression):
        self.operator = operator
        self.right = right

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_unary_expression(self)


class VariableExpression(Expression):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_variable_expression(self)


class GroupingExpression(Expression):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: "ExpressionVisitor"):
        return visitor.visit_grouping_expression(self)



class ExpressionPrinter(ExpressionVisitor):
    def visit_binary_expression(self, expression: BinaryExpression):
        return f"({expression.operator.lexeme} {expression.left.accept(self)} {expression.right.accept(self)})"

    def visit_literal_expression(self, expression: LiteralExpression):
        if expression.value is True:
            return "true"
        if expression.value is False:
            return "false"
        if expression.value is None:
            return "nil"
        return f"{expression.value}"

    def visit_unary_expression(self, expression: UnaryExpression):
        return f"({expression.operator.lexeme} {expression.right.accept(self)})"

    def visit_grouping_expression(self, expression: GroupingExpression):
        return f"(group {expression.expression.accept(self)})"

    def visit_variable_expression(self, expression: VariableExpression):
        return f"(variable {expression.name.lexeme})"

    def visit_assignment_expression(self, expression: AssignmentExpression):
        return f"(assignment {expression.name.lexeme} {expression.value.accept(self)})"

    def print(self, expression: Expression):
        return expression.accept(self)



class ExpressionEvaluator(ExpressionVisitor):
    def visit_binary_expression(self, expression: BinaryExpression):
        left = expression.left.accept(self)
        right = expression.right.accept(self)
        operator = expression.operator.lexeme
        if operator == "+":
            if type(left) != type(right):
                print_error(
                    f"[line {expression.operator.line}] Operands must be two numbers or two strings."
                )
                exit(70)
            if isinstance(left, (bool, type(None))) or isinstance(
                right, (bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left + right
        elif operator == "-":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left - right
        elif operator == "*":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left * right
        elif operator == "/":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            result = left / right
            return int(result) if result.is_integer() else result
        elif operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left > right
        elif operator == ">=":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left >= right
        elif operator == "<":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left < right
        elif operator == "<=":
            if isinstance(left, (str, bool, type(None))) or isinstance(
                right, (str, bool, type(None))
            ):
                print_error(
                    f"[line {expression.operator.line}] Operands must be numbers."
                )
                exit(70)
            return left <= right

    def visit_literal_expression(self, expression: LiteralExpression):
        if isinstance(expression.value, str):
            return expression.value
        if expression.value is None:
            return None
        if expression.value is True:
            return True
        if expression.value is False:
            return False
        if expression.value.is_integer():
            return int(expression.value)
        if isinstance(expression.value, float):
            return float(expression.value)
        return expression.value

    def visit_unary_expression(self, expression: UnaryExpression):
        right = expression.right.accept(self)
        operator = expression.operator.lexeme
        if operator == "-":
            if isinstance(right, (str, bool, type(None))):
                print_error(
                    f"[line {expression.operator.line}] Operand must be a number."
                )
                exit(70)
            if isinstance(right, int):
                return -right
            elif isinstance(right, float):
                return -right
            else:
                print_error(
                    f"[line {expression.operator.line}] Operand must be a number."
                )
                exit(70)
        elif operator == "!":
            return not right

    def visit_grouping_expression(self, expression: GroupingExpression):
        return expression.expression.accept(self)

    def visit_variable_expression(self, expression: VariableExpression):
        if expression.name.lexeme in ENVIRONMENT:
            return ENVIRONMENT[expression.name.lexeme]
        else:
            print_error(
                f"[line {expression.name.line}] Undefined variable '{expression.name.lexeme}'."
            )
            exit(70)

    def visit_assignment_expression(self, expression: AssignmentExpression):
        value = expression.value.accept(self)
        ENVIRONMENT[expression.name.lexeme] = value
        return value

    def evaluate(self, expression: Expression):
        return expression.accept(self)



class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        declarations = []
        while not self.is_at_end():
            declarations.append(self.declaration())
        return declarations

    def declaration(self):
        if self.match("VAR"):
            return self.variable_declaration()
        return self.statement()

    def variable_declaration(self):
        name = self.consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self.match("EQUAL"):
            initializer = self.expression()
        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return VariableDeclaration(name, initializer)

    def expression_statement(self):
        expression = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return ExpressionStatement(expression)

    def statement(self):
        if self.match("PRINT"):
            value = self.expression()
            self.consume("SEMICOLON", "Expect ';' after value.")
            return PrintStatement(value)
        if self.match("LEFT_BRACE"):
            block = self.block()
            self.consume("RIGHT_BRACE", "Expect '}' after block.")
            return block
        expression = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return ExpressionStatement(expression)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expression = self.equality()
        if self.match("EQUAL"):
            if isinstance(expression, VariableExpression):
                name = expression.name
                value = self.assignment()
                return AssignmentExpression(name, value)
            self.error(self.previous(), "Invalid assignment target.")
        return expression

    def equality(self):
        expression = self.comparison()
        while self.match("EQUAL_EQUAL") or self.match("BANG_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def comparison(self):
        expression = self.term()
        while (
            self.match("GREATER")
            or self.match("GREATER_EQUAL")
            or self.match("LESS")
            or self.match("LESS_EQUAL")
        ):
            operator = self.previous()
            right = self.term()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def term(self):
        expression = self.factor()
        while self.match("MINUS") or self.match("PLUS"):
            operator = self.previous()
            right = self.factor()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def factor(self):
        expression = self.unary()
        while self.match("STAR") or self.match("SLASH"):
            operator = self.previous()
            right = self.unary()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def unary(self):
        if self.match("BANG") or self.match("MINUS"):
            operator = self.previous()
            right = self.unary()
            return UnaryExpression(operator, right)
        return self.primary()

    def primary(self):
        if self.match("TRUE"):
            return LiteralExpression(True)
        if self.match("FALSE"):
            return LiteralExpression(False)
        if self.match("NIL"):
            return LiteralExpression(None)
        if self.match("THIS"):
            return LiteralExpression("this")
        if self.match("SUPER"):
            return LiteralExpression("super")
        if self.match("LEFT_PAREN"):
            expression = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return GroupingExpression(expression)
        if self.match("IDENTIFIER"):
            return VariableExpression(self.previous())
        if self.match("NUMBER"):
            return LiteralExpression(self.previous().literal)
        if self.match("STRING"):
            return LiteralExpression(self.previous().literal)
        self.error(self.previous(), "Expect expression.")


    def block(self):
        statements = []
        while not self.is_at_end() and not self.check("RIGHT_BRACE"):
            statements.append(self.declaration())
        return Block(statements)

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        self.error(self.peek(), message)

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == "EOF"

    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        return self.tokens[self.current]

    def match(self, type):
        if self.is_at_end() or self.peek().type != type:
            return False
        self.current += 1
        return True

    def error(self, token, message):
        print_error(f"[line {token.line}] Error at '{token.lexeme}': {message}")
        exit(65)

def print_result(result):
    if result is None:
        print("nil")
    elif result is True:
        print("true")
    elif result is False:
        print("false")
    elif isinstance(result, str):
        print(result)
    else:
        print(result)


class Statement:
    def accept(self, visitor: "Interpreter"):
        raise NotImplementedError("Subclass must implement abstract method")


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: "Interpreter"):
        return visitor.visit_expression_statement(self)


class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: "Interpreter"):
        return visitor.visit_print_statement(self)


class VariableDeclaration(Statement):
    def __init__(self, name: Token, initializer: Expression):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: "Interpreter"):
        return visitor.visit_variable_declaration(self)


class Block(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def accept(self, visitor: "Interpreter"):
        return visitor.visit_block(self)


class Interpreter:
    def __init__(self):
        self.evaluator = ExpressionEvaluator()

    def evaluate(self, expression: Expression):
        return self.evaluator.evaluate(expression)
        
    def visit_expression_statement(self, statement: ExpressionStatement):
        return self.evaluate(statement.expression)

    def visit_print_statement(self, statement: PrintStatement):
        value = self.evaluate(statement.expression)
        print_result(value)

    def visit_variable_declaration(self, statement: VariableDeclaration):
        value = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        ENVIRONMENT[statement.name.lexeme] = value

    def visit_block(self, statement: Block):
        self.execute_block(statement.statements)

    def execute_block(self, statements: list[Statement]):
        global ENVIRONMENT
        previous = ENVIRONMENT
        ENVIRONMENT = {**ENVIRONMENT}
        try:
            for statement in statements:
                statement.accept(self)
        finally:
            ENVIRONMENT = previous

    def interpret(self, statements: list[Statement]):
        for statement in statements:
            statement.accept(self)


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    with open(filename) as file:
        file_contents = file.read()
        if command == "tokenize":
            scanner = Scanner(file_contents)
            scanner.scan()
            for token in scanner.tokens:
                print(token)
            if scanner.had_error:
                exit(65)
            return

        if command == "parse":
            scanner = Scanner(file_contents)
            scanner.scan()
            if scanner.had_error:
                exit(65)
            tokens = scanner.tokens
            parser = Parser(tokens)
            expression = parser.expression()
            print(ExpressionPrinter().print(expression))
            return

        if command == "evaluate":
            scanner = Scanner(file_contents)
            scanner.scan()
            if scanner.had_error:
                exit(65)
            tokens = scanner.tokens
            parser = Parser(tokens)
            expression = parser.expression()
            print_result(ExpressionEvaluator().evaluate(expression))
            return

        if command == "run":
            scanner = Scanner(file_contents)
            scanner.scan()
            if scanner.had_error:
                exit(65)
            tokens = scanner.tokens
            parser = Parser(tokens)
            statements = parser.parse()
            interpreter = Interpreter()
            interpreter.interpret(statements)
            return

    print(f"Unknown command: {command}", file=sys.stderr)
    exit(1)


if __name__ == "__main__":
    main()