#!/usr/bin/env python3
"""
Demo script for SVRF DRC Parser capabilities
"""

from simple_svrf_parser import SVRFParser

def demo_parser():
    print("=== SVRF DRC Parser Demo ===\n")
    
    # Parse the example file
    parser = SVRFParser()
    parser.parse_file("example_drc_rules.svrf")
    
    # Show basic statistics
    print("1. PARSING STATISTICS")
    print("=" * 50)
    parser.print_results()
    
    # Show layers
    print("\n\n2. LAYER DEFINITIONS")
    print("=" * 50)
    parser.print_layers()
    
    # Show different rule types
    print("\n\n3. SPACING RULES")
    print("=" * 50)
    parser.print_rules("external")
    
    print("\n\n4. WIDTH/SIZE RULES")
    print("=" * 50)  
    parser.print_rules("internal")
    
    print("\n\n5. ENCLOSURE RULES")
    print("=" * 50)
    parser.print_rules("enclosure")
    
    # Show analysis capabilities
    print("\n\n6. ANALYSIS CAPABILITIES")
    print("=" * 50)
    stats = parser.get_statistics()
    
    print("Layer Coverage Analysis:")
    layer_names = {layer.name for layer in parser.layers if layer.gds_number is not None}
    rule_layers = {rule.layer for rule in parser.rules if rule.layer}
    
    covered_layers = layer_names.intersection(rule_layers)
    uncovered_layers = layer_names - rule_layers
    
    print(f"  Layers with rules: {len(covered_layers)}/{len(layer_names)}")
    print(f"  Covered: {sorted(covered_layers)}")
    if uncovered_layers:
        print(f"  Not covered: {sorted(uncovered_layers)}")
    
    print(f"\nRule Distribution:")
    for rule_type, count in sorted(stats['rule_types'].items()):
        print(f"  {rule_type.capitalize()}: {count}")
    
    print(f"\nStrictest Rules (< 0.2):")
    strict_rules = [r for r in parser.rules if r.value < 0.2 and r.operator == '<']
    for rule in strict_rules[:5]:
        print(f"  {rule.name}: {rule.layer} < {rule.value}")

if __name__ == "__main__":
    demo_parser()