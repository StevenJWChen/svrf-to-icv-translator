#!/usr/bin/env python3
"""Debug script for SVRF parser"""

from svrf_drc_parser import SVRFLexer, SVRFParser

# Test with a simple SVRF snippet
test_content = """
// Simple test
LAYER M1 100
LAYER M2 200

M1_WIDTH { @ "M1 width rule"
    INTERNAL1 M1 < 0.25
}
"""

print("Testing lexer...")
lexer = SVRFLexer(test_content)
tokens = lexer.tokenize()

print(f"Generated {len(tokens)} tokens:")
for i, token in enumerate(tokens[:20]):  # Show first 20 tokens
    print(f"  {i}: {token.type.value} = '{token.value}' (line {token.line})")

print("\nTesting parser...")
parser = SVRFParser(tokens)

# Debug: check parser state
print(f"Initial token: {parser.current_token}")
print(f"Token count: {len(parser.tokens)}")

# Try parsing one step at a time
step_count = 0
max_steps = 50

try:
    while parser.current_token and parser.current_token.type.value != "EOF" and step_count < max_steps:
        print(f"Step {step_count}: Current token = {parser.current_token.type.value} '{parser.current_token.value}'")
        
        old_pos = parser.pos
        
        parser.skip_newlines()
        parser.skip_comments()
        
        if not parser.current_token or parser.current_token.type.value == "EOF":
            break
        
        if parser.current_token.type.value == "LAYER":
            print("  Parsing layer definition...")
            parser.parse_layer_definition()
        elif parser.current_token.type.value == "IDENTIFIER":
            print("  Parsing DRC rule...")
            parser.parse_drc_rule()
        else:
            print("  Advancing...")
            parser.advance()
        
        # Safety check - ensure we made progress
        if parser.pos == old_pos:
            print(f"  WARNING: No progress made at position {parser.pos}")
            parser.advance()
        
        step_count += 1
    
    print(f"Finished parsing in {step_count} steps")
    print(f"Final layers: {len(parser.layers)}")
    print(f"Final rules: {len(parser.rules)}")
    
except Exception as e:
    print(f"Error during parsing: {e}")
    import traceback
    traceback.print_exc()