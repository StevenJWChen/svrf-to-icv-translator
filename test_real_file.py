#!/usr/bin/env python3
"""Test with real SVRF file"""

from svrf_drc_parser import SVRFLexer, SVRFParser

# Read the example file
with open("example_drc_rules.svrf", "r") as f:
    content = f.read()

print(f"File content length: {len(content)} characters")
print(f"File lines: {content.count('\\n')} lines")

# Test lexer
print("Testing lexer...")
lexer = SVRFLexer(content)
tokens = lexer.tokenize()

print(f"Generated {len(tokens)} tokens")

# Test parser with safety limits
print("Testing parser...")
parser = SVRFParser(tokens)

step_count = 0
max_steps = 1000  # Safety limit

try:
    while parser.current_token and parser.current_token.type.value != "EOF" and step_count < max_steps:
        if step_count % 100 == 0:
            print(f"Step {step_count}: {parser.current_token.type.value} '{parser.current_token.value}'")
        
        old_pos = parser.pos
        
        parser.skip_newlines()
        parser.skip_comments()
        
        if not parser.current_token or parser.current_token.type.value == "EOF":
            break
        
        if parser.current_token.type.value == "INCLUDE":
            parser.parse_include()
        elif parser.current_token.type.value == "LAYER":
            parser.parse_layer_definition()
        elif parser.current_token.type.value == "LAYOUT":
            while (parser.current_token and 
                   parser.current_token.type.value not in ["NEWLINE", "EOF"]):
                parser.advance()
        elif parser.current_token.type.value == "IDENTIFIER":
            parser.parse_drc_rule()
        else:
            parser.advance()
        
        # Safety check
        if parser.pos == old_pos:
            print(f"No progress at step {step_count}, forcing advance")
            parser.advance()
        
        step_count += 1
    
    if step_count >= max_steps:
        print(f"Hit step limit ({max_steps})")
    else:
        print(f"Parsing completed in {step_count} steps")
    
    print(f"Layers found: {len(parser.layers)}")
    print(f"Rules found: {len(parser.rules)}")
    print(f"Includes found: {len(parser.includes)}")
    print(f"Errors: {len(parser.errors)}")
    
    if parser.layers:
        print("\\nFirst few layers:")
        for layer in parser.layers[:5]:
            print(f"  {layer.name}: {layer.gds_layer or layer.expression}")
    
    if parser.rules:
        print("\\nFirst few rules:")
        for rule in parser.rules[:5]:
            print(f"  {rule.name}: {rule.rule_type} {rule.layer} {rule.constraint} {rule.value}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()