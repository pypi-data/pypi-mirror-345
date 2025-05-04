"""
Parser for BARX IR.

This module provides a Pratt parser for parsing expressions into
an abstract syntax tree (AST) with static shape information.
"""

from enum import Enum
from typing import Dict, List, Union, Optional, Any, Tuple
import re

class TokenType(Enum):
    """Enum for token types in the parser."""
    NUMBER = 1
    IDENTIFIER = 2
    PLUS = 3
    MINUS = 4
    STAR = 5
    SLASH = 6
    LPAREN = 7
    RPAREN = 8
    LBRACKET = 9
    RBRACKET = 10
    COMMA = 11
    DOT = 12
    EQUALS = 13
    EOF = 14

class Token:
    """Token for the lexer and parser."""
    
    def __init__(self, token_type: TokenType, value: str, line: int, column: int):
        """
        Initialize a token.
        
        Args:
            token_type: Type of the token
            value: String value of the token
            line: Line number in source code
            column: Column number in source code
        """
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column
        
    def __repr__(self):
        return f"Token({self.token_type}, '{self.value}', {self.line}, {self.column})"

class Lexer:
    """
    Lexer for tokenizing input code.
    
    Converts source code into a stream of tokens for parsing.
    """
    
    def __init__(self, source: str):
        """
        Initialize the lexer.
        
        Args:
            source: Source code to tokenize
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
    def tokenize(self) -> List[Token]:
        """
        Tokenize the source code.
        
        Returns:
            List of tokens
        """
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            # Skip whitespace
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
                continue
                
            # Numbers
            if char.isdigit() or (char == '.' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit()):
                start = self.pos
                start_column = self.column
                
                # Find the end of the number
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
                    self.pos += 1
                    self.column += 1
                    
                value = self.source[start:self.pos]
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, start_column))
                continue
                
            # Identifiers
            if char.isalpha() or char == '_':
                start = self.pos
                start_column = self.column
                
                # Find the end of the identifier
                while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    self.pos += 1
                    self.column += 1
                    
                value = self.source[start:self.pos]
                self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line, start_column))
                continue
                
            # Single-character tokens
            token_type = None
            
            if char == '+':
                token_type = TokenType.PLUS
            elif char == '-':
                token_type = TokenType.MINUS
            elif char == '*':
                token_type = TokenType.STAR
            elif char == '/':
                token_type = TokenType.SLASH
            elif char == '(':
                token_type = TokenType.LPAREN
            elif char == ')':
                token_type = TokenType.RPAREN
            elif char == '[':
                token_type = TokenType.LBRACKET
            elif char == ']':
                token_type = TokenType.RBRACKET
            elif char == ',':
                token_type = TokenType.COMMA
            elif char == '.':
                token_type = TokenType.DOT
            elif char == '=':
                token_type = TokenType.EQUALS
                
            if token_type:
                self.tokens.append(Token(token_type, char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue
                
            # Unknown character
            raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
            
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        
        return self.tokens

class ASTNode:
    """Base class for AST nodes."""
    
    def __init__(self):
        self.shape = None
        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate the node in the given context.
        
        Args:
            context: Variable bindings for evaluation
            
        Returns:
            Result of evaluation
        """
        raise NotImplementedError("Subclasses must implement evaluate")

class NumberNode(ASTNode):
    """AST node for numeric literals."""
    
    def __init__(self, value: float):
        """
        Initialize a number node.
        
        Args:
            value: Numeric value
        """
        super().__init__()
        self.value = value
        self.shape = ()  # Scalar shape
        
    def evaluate(self, context: Dict[str, Any]) -> float:
        """
        Evaluate the number node.
        
        Args:
            context: Variable bindings (not used for literals)
            
        Returns:
            The numeric value
        """
        return self.value
        
    def __repr__(self):
        return f"NumberNode({self.value})"

class VariableNode(ASTNode):
    """AST node for variables."""
    
    def __init__(self, name: str):
        """
        Initialize a variable node.
        
        Args:
            name: Variable name
        """
        super().__init__()
        self.name = name
        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate the variable node.
        
        Args:
            context: Variable bindings
            
        Returns:
            The value bound to the variable name
        """
        if self.name not in context:
            raise NameError(f"Variable '{self.name}' not defined")
            
        return context[self.name]
        
    def __repr__(self):
        return f"VariableNode('{self.name}')"

class BinaryOpNode(ASTNode):
    """AST node for binary operations."""
    
    def __init__(self, op: TokenType, left: ASTNode, right: ASTNode):
        """
        Initialize a binary operation node.
        
        Args:
            op: Operation token type
            left: Left operand node
            right: Right operand node
        """
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate the binary operation.
        
        Args:
            context: Variable bindings
            
        Returns:
            Result of the binary operation
        """
        left_val = self.left.evaluate(context)
        right_val = self.right.evaluate(context)
        
        if self.op == TokenType.PLUS:
            return left_val + right_val
        elif self.op == TokenType.MINUS:
            return left_val - right_val
        elif self.op == TokenType.STAR:
            return left_val * right_val
        elif self.op == TokenType.SLASH:
            return left_val / right_val
        else:
            raise ValueError(f"Unsupported binary operator: {self.op}")
            
    def __repr__(self):
        return f"BinaryOpNode({self.op}, {self.left}, {self.right})"

class CallNode(ASTNode):
    """AST node for function calls."""
    
    def __init__(self, func: ASTNode, args: List[ASTNode]):
        """
        Initialize a function call node.
        
        Args:
            func: Function to call
            args: Arguments to pass to the function
        """
        super().__init__()
        self.func = func
        self.args = args
        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate the function call.
        
        Args:
            context: Variable bindings
            
        Returns:
            Result of the function call
        """
        func = self.func.evaluate(context)
        args = [arg.evaluate(context) for arg in self.args]
        
        if not callable(func):
            raise TypeError(f"Object is not callable: {func}")
            
        return func(*args)
        
    def __repr__(self):
        return f"CallNode({self.func}, {self.args})"

class Parser:
    """
    Pratt parser for expressions.
    
    Parses tokens into an abstract syntax tree.
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize the parser.
        
        Args:
            tokens: List of tokens to parse
        """
        self.tokens = tokens
        self.pos = 0
        
    def current(self) -> Token:
        """
        Get the current token.
        
        Returns:
            Current token
        """
        return self.tokens[self.pos]
        
    def peek(self, offset: int = 1) -> Token:
        """
        Peek at a token ahead of the current position.
        
        Args:
            offset: Number of tokens to look ahead
            
        Returns:
            Token at the peeked position
        """
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[pos]
        
    def advance(self) -> Token:
        """
        Advance to the next token.
        
        Returns:
            Previous token
        """
        token = self.current()
        self.pos += 1
        return token
        
    def consume(self, token_type: TokenType) -> Token:
        """
        Consume a token of the expected type.
        
        Args:
            token_type: Expected token type
            
        Returns:
            Consumed token
            
        Raises:
            SyntaxError: If the current token doesn't match the expected type
        """
        if self.current().token_type == token_type:
            return self.advance()
            
        raise SyntaxError(
            f"Expected {token_type}, got {self.current().token_type} at line {self.current().line}, column {self.current().column}"
        )
        
    def parse(self) -> ASTNode:
        """
        Parse the tokens into an AST.
        
        Returns:
            Root AST node
        """
        return self.parse_expression()
        
    def parse_expression(self, precedence: int = 0) -> ASTNode:
        """
        Parse an expression with the given precedence.
        
        Args:
            precedence: Minimum precedence to parse
            
        Returns:
            AST node for the expression
        """
        token = self.current()
        
        # Parse prefix expression
        if token.token_type == TokenType.NUMBER:
            self.advance()
            left = NumberNode(float(token.value))
        elif token.token_type == TokenType.IDENTIFIER:
            self.advance()
            
            # Check if this is a function call
            if self.current().token_type == TokenType.LPAREN:
                self.advance()  # Consume '('
                args = []
                
                # Parse arguments
                if self.current().token_type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    
                    while self.current().token_type == TokenType.COMMA:
                        self.advance()  # Consume ','
                        args.append(self.parse_expression())
                        
                self.consume(TokenType.RPAREN)
                left = CallNode(VariableNode(token.value), args)
            else:
                left = VariableNode(token.value)
        elif token.token_type == TokenType.LPAREN:
            self.advance()
            left = self.parse_expression()
            self.consume(TokenType.RPAREN)
        else:
            raise SyntaxError(
                f"Unexpected token: {token.token_type} at line {token.line}, column {token.column}"
            )
            
        # Parse infix expressions
        while self.current().token_type != TokenType.EOF:
            if self.current().token_type in (TokenType.PLUS, TokenType.MINUS) and 1 > precedence:
                op = self.advance().token_type
                right = self.parse_expression(1)
                left = BinaryOpNode(op, left, right)
            elif self.current().token_type in (TokenType.STAR, TokenType.SLASH) and 2 > precedence:
                op = self.advance().token_type
                right = self.parse_expression(2)
                left = BinaryOpNode(op, left, right)
            elif self.current().token_type == TokenType.DOT:
                self.advance()  # Consume '.'
                
                # Attribute access or method call
                if self.current().token_type == TokenType.IDENTIFIER:
                    attr_name = self.advance().value
                    
                    # Method call
                    if self.current().token_type == TokenType.LPAREN:
                        self.advance()  # Consume '('
                        args = []
                        
                        # Parse arguments
                        if self.current().token_type != TokenType.RPAREN:
                            args.append(self.parse_expression())
                            
                            while self.current().token_type == TokenType.COMMA:
                                self.advance()  # Consume ','
                                args.append(self.parse_expression())
                                
                        self.consume(TokenType.RPAREN)
                        
                        # Create a method call node
                        # For simplicity, we'll treat it as accessing an attribute then calling it
                        left = CallNode(
                            AttributeAccessNode(left, attr_name),  # This would need to be defined
                            args
                        )
                    else:
                        # Simple attribute access
                        left = AttributeAccessNode(left, attr_name)  # This would need to be defined
                else:
                    raise SyntaxError(
                        f"Expected identifier after '.', got {self.current().token_type} at line {self.current().line}, column {self.current().column}"
                    )
            else:
                break
                
        return left

# Additional classes that would be needed for a complete implementation
class AttributeAccessNode(ASTNode):
    """AST node for attribute access expressions."""
    
    def __init__(self, obj: ASTNode, attr: str):
        """
        Initialize an attribute access node.
        
        Args:
            obj: Object to access attribute from
            attr: Attribute name
        """
        super().__init__()
        self.obj = obj
        self.attr = attr
        
    def evaluate(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate the attribute access.
        
        Args:
            context: Variable bindings
            
        Returns:
            Value of the accessed attribute
        """
        obj = self.obj.evaluate(context)
        
        if not hasattr(obj, self.attr):
            raise AttributeError(f"'{type(obj).__name__}' object has no attribute '{self.attr}'")
            
        return getattr(obj, self.attr)
        
    def __repr__(self):
        return f"AttributeAccessNode({self.obj}, '{self.attr}')"
