#!/usr/bin/env python3
"""
Demo script for SVRF to ICV Translator
"""

from svrf_to_icv_translator import SVRFToICVTranslator
from pathlib import Path

def demo_translator():
    print("=== SVRF to ICV Translator Demo ===\n")
    
    # Create translator
    translator = SVRFToICVTranslator()
    translator.technology = "Example 180nm"
    translator.process_node = "180nm"
    
    # Translate the example file
    input_file = "example_drc_rules.svrf"
    output_file = "demo_output.icv"
    
    print(f"Translating: {input_file} -> {output_file}")
    success = translator.translate_file(input_file, output_file)
    
    if not success:
        print("Translation failed!")
        return
    
    print("Translation completed successfully!\n")
    
    # Show detailed summary
    print("1. TRANSLATION SUMMARY")
    print("=" * 50)
    translator.print_translation_summary()
    
    # Show sample translations by type
    print("\n2. SAMPLE TRANSLATIONS BY RULE TYPE")
    print("=" * 50)
    
    rule_samples = {}
    for rule in translator.icv_rules:
        if rule.operation not in rule_samples:
            rule_samples[rule.operation] = rule
    
    for rule_type, sample_rule in sorted(rule_samples.items()):
        print(f"\n{rule_type.upper()}:")
        print(f"  Rule Name: {sample_rule.name}")
        print(f"  SVRF Original: {sample_rule.layer} {sample_rule.constraint}")
        print(f"  ICV Translation: {sample_rule.icv_syntax}")
        print(f"  Description: {sample_rule.description}")
    
    # Show layer translations
    print("\n\n3. LAYER TRANSLATIONS")
    print("=" * 50)
    
    print("Primary Layers (GDS):")
    for i, layer_def in enumerate(translator.icv_layers):
        if "=" in layer_def and layer_def.split("=")[1].strip().rstrip(";").isdigit():
            print(f"  {layer_def}")
            if i >= 4:  # Show first 5
                break
    
    print("\nDerived Layers (Boolean):")
    for i, layer_def in enumerate(translator.icv_layers):
        if "=" in layer_def and not layer_def.split("=")[1].strip().rstrip(";").isdigit():
            print(f"  {layer_def}")
            if i >= 3:  # Show first 4
                break
    
    # Show syntax comparison
    print("\n\n4. SYNTAX COMPARISON EXAMPLES")
    print("=" * 50)
    
    comparisons = [
        {
            "type": "Width Rule",
            "svrf": "INTERNAL1 M1 < 0.25",
            "icv": "width(M1) < 0.25"
        },
        {
            "type": "Spacing Rule", 
            "svrf": "EXTERNAL1 M1 < 0.25",
            "icv": "space(M1) < 0.25"
        },
        {
            "type": "Area Rule",
            "svrf": "AREA M1 < 0.1", 
            "icv": "area(M1) < 0.1"
        },
        {
            "type": "Enclosure Rule",
            "svrf": "VIA1 NOT INSIDE M1 BY == 0.05",
            "icv": "enclosure(M1, VIA1) >= 0.05"
        },
        {
            "type": "Layer Expression",
            "svrf": "NMOS_GATE = POLY AND ACTIVE",
            "icv": "LAYER NMOS_GATE = POLY & ACTIVE;"
        }
    ]
    
    for comp in comparisons:
        print(f"\n{comp['type']}:")
        print(f"  SVRF:  {comp['svrf']}")
        print(f"  ICV:   {comp['icv']}")
    
    # Show file statistics
    print(f"\n\n5. OUTPUT FILE ANALYSIS")
    print("=" * 50)
    
    output_path = Path(output_file)
    if output_path.exists():
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        comment_lines = len([l for l in lines if l.strip().startswith('//')])
        rule_lines = len([l for l in lines if 'rule ' in l])
        layer_lines = len([l for l in lines if l.startswith('LAYER ')])
        
        print(f"Output File: {output_file}")
        print(f"  Total Lines: {total_lines}")
        print(f"  Comment Lines: {comment_lines}")
        print(f"  Rule Definitions: {rule_lines}")
        print(f"  Layer Definitions: {layer_lines}")
        print(f"  File Size: {output_path.stat().st_size} bytes")
    
    print(f"\n\n6. KEY TRANSLATION FEATURES")
    print("=" * 50)
    print("✓ Complete SVRF rule parsing")
    print("✓ Layer definition translation (GDS + derived)")
    print("✓ All major DRC rule types supported")
    print("✓ Proper ICV syntax generation") 
    print("✓ Rule grouping by operation type")
    print("✓ Error message preservation")
    print("✓ Configurable run options")
    print("✓ Technology and process node support")
    
    print(f"\n\nTranslation completed! Check '{output_file}' for full ICV rules.")

if __name__ == "__main__":
    demo_translator()