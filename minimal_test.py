#!/usr/bin/env python3

from svrf_drc_parser import SVRFLexer

# Test lexer with problematic content
test_content = """NMOS_GATE = POLY AND ACTIVE"""

lexer = SVRFLexer(test_content)
tokens = lexer.tokenize()

print("Tokens:")
for token in tokens:
    print(f"  {token.type.value}: '{token.value}'")