#!/usr/bin/env python3
"""
SVRF DRC Parser
A comprehensive parser for Calibre SVRF (Standard Verification Rule Format) DRC rules
"""

import re
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class TokenType(Enum):
    # Literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER" 
    STRING = "STRING"
    
    # Keywords
    LAYER = "LAYER"
    INCLUDE = "INCLUDE"
    LAYOUT = "LAYOUT"
    SYSTEM = "SYSTEM"
    GDSII = "GDSII"
    
    # Layer operations
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    INSIDE = "INSIDE"
    BY = "BY"
    
    # DRC operations
    INTERNAL1 = "INTERNAL1"
    INTERNAL2 = "INTERNAL2"  
    EXTERNAL = "EXTERNAL"
    EXTERNAL1 = "EXTERNAL1"
    AREA = "AREA"
    DENSITY = "DENSITY"
    WINDOW = "WINDOW"
    SINGULAR = "SINGULAR"
    
    # Operators
    LT = "<"
    GT = ">"
    EQ = "=="
    ASSIGN = "="
    
    # Delimiters
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    COMMA = ","
    SEMICOLON = ";"
    AT = "@"
    
    # Special
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

@dataclass
class LayerDefinition:
    name: str
    gds_layer: Optional[int] = None
    expression: Optional[str] = None
    line: int = 0

@dataclass
class DRCRule:
    name: str
    description: str
    rule_type: str
    layer: str
    constraint: str
    value: float
    line: int
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParseResult:
    layers: List[LayerDefinition]
    rules: List[DRCRule] 
    includes: List[str]
    errors: List[str]
    warnings: List[str]

class SVRFLexer:
    """Tokenizer for SVRF files"""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        
        # Keywords mapping
        self.keywords = {
            'LAYER': TokenType.LAYER,
            'INCLUDE': TokenType.INCLUDE,
            'LAYOUT': TokenType.LAYOUT,
            'SYSTEM': TokenType.SYSTEM,
            'GDSII': TokenType.GDSII,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
            'INSIDE': TokenType.INSIDE,
            'BY': TokenType.BY,
            'INTERNAL1': TokenType.INTERNAL1,
            'INTERNAL2': TokenType.INTERNAL2,
            'EXTERNAL': TokenType.EXTERNAL,
            'EXTERNAL1': TokenType.EXTERNAL1,
            'AREA': TokenType.AREA,
            'DENSITY': TokenType.DENSITY,
            'WINDOW': TokenType.WINDOW,
            'SINGULAR': TokenType.SINGULAR,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def advance(self):
        if self.pos < len(self.text) and self.text[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_comment(self) -> Token:
        start_line, start_col = self.line, self.column
        comment = ""
        
        if self.current_char() == '/' and self.peek_char() == '/':
            self.advance()  # Skip first /
            self.advance()  # Skip second /
            
            while self.current_char() and self.current_char() != '\n':
                comment += self.current_char()
                self.advance()
                
        return Token(TokenType.COMMENT, comment.strip(), start_line, start_col)
    
    def read_string(self) -> Token:
        start_line, start_col = self.line, self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    value += self.current_char()
                    self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
            
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            value += self.current_char()
            self.advance()
            
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ""
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_')):
            value += self.current_char()
            self.advance()
            
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
                
            char = self.current_char()
            
            # Comments
            if char == '/' and self.peek_char() == '/':
                tokens.append(self.read_comment())
                continue
            
            # Newlines
            if char == '\n':
                tokens.append(Token(TokenType.NEWLINE, char, self.line, self.column))
                self.advance()
                continue
            
            # Strings
            if char in '"\'':
                tokens.append(self.read_string())
                continue
            
            # Numbers
            if char.isdigit() or (char == '.' and self.peek_char() and self.peek_char().isdigit()):
                tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                tokens.append(self.read_identifier())
                continue
            
            # Two-character operators
            if char == '=' and self.peek_char() == '=':
                tokens.append(Token(TokenType.EQ, "==", self.line, self.column))
                self.advance()
                self.advance()
                continue
            
            # Single-character tokens
            single_char_tokens = {
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '@': TokenType.AT,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '=': TokenType.ASSIGN,
            }
            
            if char in single_char_tokens:
                tokens.append(Token(single_char_tokens[char], char, self.line, self.column))
                self.advance()
                continue
            
            # Unknown character - skip it
            self.advance()
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

class SVRFParser:
    """Parser for SVRF DRC rules"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
        
        self.layers = []
        self.rules = []
        self.includes = []
        self.errors = []
        self.warnings = []
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> bool:
        if self.current_token and self.current_token.type == token_type:
            self.advance()
            return True
        self.errors.append(f"Expected {token_type} at line {self.current_token.line if self.current_token else 'EOF'}")
        return False
    
    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def skip_comments(self):
        while self.current_token and self.current_token.type == TokenType.COMMENT:
            self.advance()
    
    def parse_include(self):
        self.advance()  # Skip INCLUDE
        if self.current_token and self.current_token.type == TokenType.STRING:
            self.includes.append(self.current_token.value)
            self.advance()
    
    def parse_layer_definition(self):
        layer_line = self.current_token.line
        self.advance()  # Skip LAYER
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            self.errors.append(f"Expected layer name at line {layer_line}")
            return
            
        layer_name = self.current_token.value
        self.advance()
        
        # Check for GDS layer number or expression
        if self.current_token and self.current_token.type == TokenType.NUMBER:
            gds_layer = int(float(self.current_token.value))
            self.layers.append(LayerDefinition(layer_name, gds_layer=gds_layer, line=layer_line))
            self.advance()
        elif self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()  # Skip =
            expression = self.parse_layer_expression()
            self.layers.append(LayerDefinition(layer_name, expression=expression, line=layer_line))
    
    def parse_layer_expression(self) -> str:
        expression_parts = []
        
        while (self.current_token and 
               self.current_token.type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.LBRACE]):
            expression_parts.append(self.current_token.value)
            self.advance()
            
        return " ".join(expression_parts)
    
    def parse_derived_layer(self):
        """Parse derived layer definitions like: NMOS_GATE = POLY AND ACTIVE"""
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            return
            
        layer_name = self.current_token.value
        layer_line = self.current_token.line
        self.advance()
        
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()  # Skip =
            expression = self.parse_layer_expression()
            self.layers.append(LayerDefinition(layer_name, expression=expression, line=layer_line))
    
    def parse_drc_rule(self):
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            self.advance()  # Skip invalid token
            return
            
        rule_name = self.current_token.value
        rule_line = self.current_token.line
        self.advance()
        
        if not self.current_token or self.current_token.type != TokenType.LBRACE:
            # Not a rule definition, skip this identifier
            return
            
        self.advance()  # Skip {
        self.skip_newlines()
        self.skip_comments()
        
        # Parse rule description
        description = ""
        if self.current_token and self.current_token.type == TokenType.AT:
            self.advance()  # Skip @
            if self.current_token and self.current_token.type == TokenType.STRING:
                description = self.current_token.value
                self.advance()
        
        self.skip_newlines()
        
        # Parse rule body
        rule_type = ""
        layer = ""
        constraint = ""
        value = 0.0
        additional_params = {}
        
        if self.current_token:
            rule_type = self.current_token.value
            self.advance()
            
            # Parse based on rule type
            if rule_type in ["INTERNAL1", "INTERNAL2", "EXTERNAL", "EXTERNAL1"]:
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    layer = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type in [TokenType.LT, TokenType.GT, TokenType.EQ]:
                    constraint = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type == TokenType.NUMBER:
                    value = float(self.current_token.value)
                    self.advance()
                    
                # Check for additional parameters
                while (self.current_token and 
                       self.current_token.type not in [TokenType.RBRACE, TokenType.NEWLINE]):
                    if self.current_token.type == TokenType.IDENTIFIER:
                        param_name = self.current_token.value
                        additional_params[param_name] = True
                        self.advance()
            
            elif rule_type == "AREA":
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    layer = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type in [TokenType.LT, TokenType.GT]:
                    constraint = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type == TokenType.NUMBER:
                    value = float(self.current_token.value)
                    self.advance()
            
            elif rule_type == "DENSITY":
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    layer = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type == TokenType.WINDOW:
                    self.advance()
                    # Parse window dimensions
                    window_params = []
                    while (self.current_token and 
                           self.current_token.type == TokenType.NUMBER and
                           len(window_params) < 2):
                        window_params.append(float(self.current_token.value))
                        self.advance()
                    additional_params["window"] = window_params
                    
                if self.current_token and self.current_token.type in [TokenType.LT, TokenType.GT]:
                    constraint = self.current_token.value
                    self.advance()
                    
                if self.current_token and self.current_token.type == TokenType.NUMBER:
                    value = float(self.current_token.value)
                    self.advance()
        
        # Skip to closing brace
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            self.advance()
            
        if self.current_token and self.current_token.type == TokenType.RBRACE:
            self.advance()
            
        self.rules.append(DRCRule(
            name=rule_name,
            description=description,
            rule_type=rule_type,
            layer=layer,
            constraint=constraint,
            value=value,
            line=rule_line,
            additional_params=additional_params
        ))
    
    def parse(self) -> ParseResult:
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            self.skip_comments()
            
            if not self.current_token or self.current_token.type == TokenType.EOF:
                break
            
            if self.current_token.type == TokenType.INCLUDE:
                self.parse_include()
            elif self.current_token.type == TokenType.LAYER:
                self.parse_layer_definition()
            elif self.current_token.type == TokenType.LAYOUT:
                # Skip layout system declaration
                while (self.current_token and 
                       self.current_token.type not in [TokenType.NEWLINE, TokenType.EOF]):
                    self.advance()
            elif self.current_token.type == TokenType.IDENTIFIER:
                # Check if this is a layer assignment or DRC rule
                next_token = self.peek()
                if next_token and next_token.type == TokenType.ASSIGN:
                    # This is a derived layer definition like: NMOS_GATE = POLY AND ACTIVE
                    self.parse_derived_layer()
                elif next_token and next_token.type == TokenType.LBRACE:
                    # This is a DRC rule
                    self.parse_drc_rule()
                else:
                    # Skip unknown identifier
                    self.advance()
            else:
                self.advance()
                
        return ParseResult(
            layers=self.layers,
            rules=self.rules,
            includes=self.includes,
            errors=self.errors,
            warnings=self.warnings
        )

class SVRFAnalyzer:
    """Analyzer for SVRF DRC rules"""
    
    def __init__(self, parse_result: ParseResult):
        self.result = parse_result
    
    def get_layer_stats(self) -> Dict[str, Any]:
        primary_layers = [l for l in self.result.layers if l.gds_layer is not None]
        derived_layers = [l for l in self.result.layers if l.expression is not None]
        
        return {
            "total_layers": len(self.result.layers),
            "primary_layers": len(primary_layers),
            "derived_layers": len(derived_layers),
            "layer_names": [l.name for l in self.result.layers]
        }
    
    def get_rule_stats(self) -> Dict[str, Any]:
        rule_types = {}
        layers_with_rules = set()
        
        for rule in self.result.rules:
            rule_types[rule.rule_type] = rule_types.get(rule.rule_type, 0) + 1
            if rule.layer:
                layers_with_rules.add(rule.layer)
        
        return {
            "total_rules": len(self.result.rules),
            "rule_types": rule_types,
            "layers_with_rules": len(layers_with_rules),
            "covered_layers": sorted(layers_with_rules)
        }
    
    def get_spacing_rules(self) -> List[DRCRule]:
        return [r for r in self.result.rules if "SPACE" in r.name.upper() or r.rule_type == "EXTERNAL1"]
    
    def get_width_rules(self) -> List[DRCRule]:
        return [r for r in self.result.rules if "WIDTH" in r.name.upper() or r.rule_type == "INTERNAL1"]
    
    def find_potential_issues(self) -> List[str]:
        issues = []
        
        # Check for layers without rules
        layer_names = {l.name for l in self.result.layers}
        rules_layers = {r.layer for r in self.result.rules if r.layer}
        unused_layers = layer_names - rules_layers
        
        if unused_layers:
            issues.append(f"Layers without rules: {', '.join(sorted(unused_layers))}")
        
        # Check for very restrictive rules
        restrictive_rules = [r for r in self.result.rules if r.value < 0.1 and r.constraint == "<"]
        if restrictive_rules:
            issues.append(f"Very restrictive rules (< 0.1): {len(restrictive_rules)} rules")
        
        return issues

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SVRF DRC Rule Parser")
    parser.add_argument("file", help="SVRF file to parse")
    parser.add_argument("--analyze", action="store_true", help="Perform detailed analysis")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--rules", choices=["all", "spacing", "width"], default="all",
                       help="Show specific rule types")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            content = f.read()
        
        # Tokenize
        lexer = SVRFLexer(content)
        tokens = lexer.tokenize()
        
        # Parse
        parser = SVRFParser(tokens)
        result = parser.parse()
        
        # Display results
        print(f"Parsing completed for: {args.file}")
        print(f"Errors: {len(result.errors)}")
        if result.errors:
            for error in result.errors:
                print(f"  ERROR: {error}")
        
        print(f"Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"  WARNING: {warning}")
        
        if args.stats or args.analyze:
            analyzer = SVRFAnalyzer(result)
            
            layer_stats = analyzer.get_layer_stats()
            rule_stats = analyzer.get_rule_stats()
            
            print(f"\nLayer Statistics:")
            print(f"  Total layers: {layer_stats['total_layers']}")
            print(f"  Primary layers: {layer_stats['primary_layers']}")
            print(f"  Derived layers: {layer_stats['derived_layers']}")
            
            print(f"\nRule Statistics:")
            print(f"  Total rules: {rule_stats['total_rules']}")
            print(f"  Rule types: {rule_stats['rule_types']}")
            print(f"  Layers with rules: {rule_stats['layers_with_rules']}")
            
        if args.analyze:
            issues = analyzer.find_potential_issues()
            if issues:
                print(f"\nPotential Issues:")
                for issue in issues:
                    print(f"  - {issue}")
        
        if args.rules != "all":
            analyzer = SVRFAnalyzer(result)
            if args.rules == "spacing":
                rules = analyzer.get_spacing_rules()
                print(f"\nSpacing Rules ({len(rules)}):")
            elif args.rules == "width":
                rules = analyzer.get_width_rules()
                print(f"\nWidth Rules ({len(rules)}):")
            
            for rule in rules:
                print(f"  {rule.name}: {rule.layer} {rule.constraint} {rule.value}")
                if rule.description:
                    print(f"    Description: {rule.description}")
        
        if not args.stats and not args.analyze and args.rules == "all":
            print(f"\nFound {len(result.layers)} layers and {len(result.rules)} rules")
            
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()