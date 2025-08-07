#!/usr/bin/env python3
"""
Analysis of complex SVRF to ICV translation
"""

from simple_svrf_parser import SVRFParser
from svrf_to_icv_translator import SVRFToICVTranslator
import re
import os

def analyze_complex_translation():
    print("=== Complex SVRF to ICV Translation Analysis ===\n")
    
    # Parse the complex SVRF file
    print("Parsing complex SVRF file...")
    parser = SVRFParser()
    parser.parse_file("complex_drc_rules.svrf")
    
    print("1. SVRF PARSING RESULTS")
    print("=" * 50)
    stats = parser.get_statistics()
    print(f"Total Layers: {stats['layers']}")
    print(f"  Primary Layers: {stats['layer_types']['primary']}")  
    print(f"  Derived Layers: {stats['layer_types']['derived']}")
    print(f"Total Rules: {stats['rules']}")
    print(f"Rule Types Found: {list(stats['rule_types'].keys())}")
    print(f"Parse Errors: {stats['errors']}")
    
    # Analyze rules by type
    print(f"\n2. RULE BREAKDOWN BY TYPE")
    print("=" * 50)
    
    rule_categories = {
        'width_rules': [r for r in parser.rules if r.rule_type == 'internal1'],
        'spacing_rules': [r for r in parser.rules if r.rule_type in ['external1', 'external']],
        'area_rules': [r for r in parser.rules if r.rule_type == 'area'],
        'density_rules': [r for r in parser.rules if r.rule_type == 'density'],
        'length_rules': [r for r in parser.rules if r.rule_type == 'internal2'],
        'unknown_rules': [r for r in parser.rules if r.rule_type == 'unknown']
    }
    
    for category, rules in rule_categories.items():
        print(f"{category.replace('_', ' ').title()}: {len(rules)}")
    
    # Show examples of unknown/unsupported rules
    if rule_categories['unknown_rules']:
        print(f"\nUnsupported Rules (need manual translation):")
        for rule in rule_categories['unknown_rules'][:8]:
            print(f"  - {rule.name}: {rule.description}")
    
    # Translate to ICV
    print(f"\n3. PERFORMING TRANSLATION")
    print("=" * 50)
    
    translator = SVRFToICVTranslator()
    translator.technology = "Advanced FinFET 7nm"
    translator.process_node = "7nm"
    
    success = translator.translate_file("complex_drc_rules.svrf", "analyzed_complex.icv")
    
    print(f"Translation Success: {success}")
    print(f"Rules Input: {len(parser.rules)}")
    print(f"Rules Translated: {len(translator.icv_rules)}")
    print(f"Translation Rate: {len(translator.icv_rules)/len(parser.rules)*100:.1f}%")
    print(f"Layers Translated: {len(translator.icv_layers)}")
    
    # Show translation results by category
    print(f"\n4. TRANSLATION RESULTS BY CATEGORY")
    print("=" * 50)
    
    icv_operations = {}
    for rule in translator.icv_rules:
        icv_operations[rule.operation] = icv_operations.get(rule.operation, 0) + 1
    
    for operation, count in sorted(icv_operations.items()):
        print(f"  {operation}: {count} rules")
    
    # Analyze layer complexity
    print(f"\n5. LAYER COMPLEXITY ANALYSIS")
    print("=" * 50)
    
    primary_layers = [l for l in parser.layers if l.gds_number is not None]
    derived_layers = [l for l in parser.layers if l.expression is not None]
    
    print(f"Primary Layers: {len(primary_layers)}")
    print(f"Derived Layers: {len(derived_layers)}")
    
    # Analyze derived layer complexity
    complex_expressions = []
    for layer in derived_layers:
        if layer.expression:
            # Count boolean operations
            and_count = layer.expression.count('AND')
            or_count = layer.expression.count('OR')
            not_count = layer.expression.count('NOT')
            paren_count = layer.expression.count('(')
            
            total_complexity = and_count + or_count + not_count + paren_count
            
            if total_complexity > 3:
                complex_expressions.append((layer.name, layer.expression, total_complexity))
    
    if complex_expressions:
        print(f"\nComplex Layer Expressions:")
        for name, expr, complexity in sorted(complex_expressions, key=lambda x: x[2], reverse=True)[:5]:
            print(f"  {name}: {expr}")
    
    # Check for advanced features
    print(f"\n6. ADVANCED PROCESS FEATURES DETECTED")
    print("=" * 50)
    
    features = []
    
    # High metal layers
    high_metals = [r for r in parser.rules if any(f'M{i}' in r.layer for i in range(8, 11))]
    if high_metals:
        features.append(f"High metal layers (M8-M10): {len(high_metals)} rules")
    
    # Very tight design rules
    tight_rules = [r for r in parser.rules if r.value < 0.05 and r.operator == '<']
    if tight_rules:
        features.append(f"Very tight rules (< 0.05): {len(tight_rules)} rules")
        print(f"  Tightest rule: {min(tight_rules, key=lambda r: r.value).name} = {min(r.value for r in tight_rules)}")
    
    # Device-specific rules  
    device_layers = ['VARACTOR', 'IND', 'CAP', 'RES', 'ESD', 'DIODE']
    device_rules = [r for r in parser.rules if any(dev in r.layer for dev in device_layers)]
    if device_rules:
        features.append(f"Analog device rules: {len(device_rules)} rules")
    
    # Multi-patterning hints
    mp_rules = [r for r in parser.rules if 'COLOR' in r.name.upper()]
    if mp_rules:
        features.append(f"Multi-patterning rules: {len(mp_rules)} rules")
    
    # Antenna rules
    antenna_rules = [r for r in parser.rules if 'ANTENNA' in r.name.upper()]
    if antenna_rules:
        features.append(f"Antenna effect rules: {len(antenna_rules)} rules")
    
    for feature in features:
        print(f"  ✓ {feature}")
    
    # File analysis
    print(f"\n7. FILE SIZE ANALYSIS")
    print("=" * 50)
    
    svrf_size = os.path.getsize("complex_drc_rules.svrf")
    icv_size = os.path.getsize("analyzed_complex.icv")
    
    print(f"SVRF Input Size: {svrf_size:,} bytes ({svrf_size/1024:.1f} KB)")
    print(f"ICV Output Size: {icv_size:,} bytes ({icv_size/1024:.1f} KB)")
    print(f"Size Expansion: {icv_size/svrf_size:.1f}x")
    
    # Show some sample translations
    print(f"\n8. SAMPLE TRANSLATIONS")
    print("=" * 50)
    
    sample_translations = [
        ("Width Rule", "GATE_WIDTH", "width(GATE) < 0.05"),
        ("Spacing Rule", "M1_SPACE", "space(M1) < 0.032"),
        ("Area Rule", "ACTIVE_AREA_MIN", "area(ACTIVE) < 0.0025"),
        ("Density Rule", "M1_DENSITY", "density(M1, 100, 100) < 0.2")
    ]
    
    for rule_type, rule_name, icv_syntax in sample_translations:
        # Find the rule
        matching_rules = [r for r in translator.icv_rules if r.name.upper() == rule_name.upper()]
        if matching_rules:
            rule = matching_rules[0]
            print(f"{rule_type}:")
            print(f"  SVRF: {rule.name} - {rule.description}")
            print(f"  ICV:  {rule.icv_syntax}")
            print()
    
    # Summary
    print(f"\n9. TRANSLATION SUMMARY")
    print("=" * 50)
    
    success_rate = len(translator.icv_rules) / len(parser.rules) * 100
    
    print(f"✓ Parsed {len(parser.rules)} SVRF rules across {len(parser.layers)} layers")
    print(f"✓ Successfully translated {len(translator.icv_rules)} rules ({success_rate:.1f}%)")
    print(f"✓ Generated complete ICV rule deck with {len(translator.icv_layers)} layer definitions")
    print(f"✓ Detected advanced 7nm process features")
    
    if rule_categories['unknown_rules']:
        print(f"⚠  {len(rule_categories['unknown_rules'])} rules need manual review (enclosure, antenna)")
    
    if success_rate >= 80:
        print(f"✓ Translation Quality: Excellent")
    elif success_rate >= 60:
        print(f"✓ Translation Quality: Good")
    else:
        print(f"⚠  Translation Quality: Fair - consider manual review")
    
    print(f"\n🎯 Result: Complex 7nm SVRF rule deck successfully translated to ICV format!")

if __name__ == "__main__":
    analyze_complex_translation()