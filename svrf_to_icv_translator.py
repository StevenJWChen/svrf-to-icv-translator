#!/usr/bin/env python3
"""
SVRF to Synopsys ICV Translator
Translates Calibre SVRF DRC rules to Synopsys IC Validator (ICV) format
"""

import re
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from simple_svrf_parser import SVRFParser, Layer, DRCRule

@dataclass
class ICVRule:
    """ICV DRC Rule representation"""
    name: str
    description: str
    layer: str
    operation: str
    constraint: str
    value: float
    icv_syntax: str
    line_number: int = 0

class SVRFToICVTranslator:
    """Translator from SVRF to ICV format"""
    
    def __init__(self):
        self.svrf_parser = SVRFParser()
        self.icv_rules = []
        self.icv_layers = []
        self.technology = "Generic"
        self.process_node = "180nm"
        
        # SVRF to ICV syntax mappings
        self.rule_mappings = {
            'internal1': self.translate_internal1,
            'internal2': self.translate_internal2,
            'external1': self.translate_external1,
            'external': self.translate_external,
            'area': self.translate_area,
            'density': self.translate_density,
            'enclosure': self.translate_enclosure
        }
    
    def translate_file(self, svrf_file: str, output_file: str = None):
        """Translate SVRF file to ICV format"""
        # Parse SVRF file
        self.svrf_parser.parse_file(svrf_file)
        
        if self.svrf_parser.errors:
            print(f"Errors in SVRF parsing:")
            for error in self.svrf_parser.errors:
                print(f"  {error}")
            return False
        
        # Translate layers
        self.translate_layers()
        
        # Translate rules
        self.translate_rules()
        
        # Generate ICV output
        if output_file:
            self.write_icv_file(output_file)
        
        return True
    
    def translate_layers(self):
        """Translate SVRF layer definitions to ICV format"""
        for layer in self.svrf_parser.layers:
            if layer.gds_number is not None:
                # Primary layer
                icv_layer = f"LAYER {layer.name} = {layer.gds_number};"
            else:
                # Derived layer
                icv_expression = self.translate_layer_expression(layer.expression)
                icv_layer = f"LAYER {layer.name} = {icv_expression};"
            
            self.icv_layers.append(icv_layer)
    
    def translate_layer_expression(self, expression: str) -> str:
        """Translate SVRF layer expressions to ICV format"""
        if not expression:
            return ""
        
        # Basic translation mappings
        icv_expr = expression.replace(" AND ", " & ")
        icv_expr = icv_expr.replace(" OR ", " | ")
        icv_expr = icv_expr.replace(" NOT ", " ! ")
        
        return icv_expr
    
    def translate_rules(self):
        """Translate SVRF rules to ICV format"""
        for rule in self.svrf_parser.rules:
            if rule.rule_type in self.rule_mappings:
                icv_rule = self.rule_mappings[rule.rule_type](rule)
                if icv_rule:
                    self.icv_rules.append(icv_rule)
            else:
                print(f"Warning: Unsupported rule type '{rule.rule_type}' for rule {rule.name}")
    
    def translate_internal1(self, rule: DRCRule) -> ICVRule:
        """Translate INTERNAL1 (width) rules"""
        if rule.operator == '<':
            # Width rule: minimum width
            icv_syntax = f"width({rule.layer}) < {rule.value}"
            operation = "width check"
        else:
            icv_syntax = f"width({rule.layer}) {rule.operator} {rule.value}"
            operation = "width constraint"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation=operation,
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_internal2(self, rule: DRCRule) -> ICVRule:
        """Translate INTERNAL2 rules"""
        # INTERNAL2 is typically for length constraints
        icv_syntax = f"length({rule.layer}) {rule.operator} {rule.value}"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation="length check",
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_external1(self, rule: DRCRule) -> ICVRule:
        """Translate EXTERNAL1 (spacing) rules"""
        if rule.operator == '<':
            # Spacing rule: minimum spacing
            icv_syntax = f"space({rule.layer}) < {rule.value}"
            operation = "spacing check"
        else:
            icv_syntax = f"space({rule.layer}) {rule.operator} {rule.value}"
            operation = "spacing constraint"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation=operation,
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_external(self, rule: DRCRule) -> ICVRule:
        """Translate EXTERNAL (inter-layer spacing) rules"""
        # Extract second layer from description or rule name
        second_layer = self.extract_second_layer(rule.name, rule.description)
        
        if second_layer:
            icv_syntax = f"space({rule.layer}, {second_layer}) {rule.operator} {rule.value}"
            operation = "inter-layer spacing"
        else:
            icv_syntax = f"space({rule.layer}) {rule.operator} {rule.value}"
            operation = "spacing check"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation=operation,
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_area(self, rule: DRCRule) -> ICVRule:
        """Translate AREA rules"""
        icv_syntax = f"area({rule.layer}) {rule.operator} {rule.value}"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation="area check",
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_density(self, rule: DRCRule) -> ICVRule:
        """Translate DENSITY rules"""
        # ICV density syntax: density(layer, window_width, window_height) operator value
        window_info = [100, 100]  # Default window size
        
        if hasattr(rule, 'extra_params') and rule.extra_params:
            if isinstance(rule.extra_params, dict) and 'window' in rule.extra_params:
                window_info = rule.extra_params['window']
        
        if len(window_info) >= 2:
            icv_syntax = f"density({rule.layer}, {window_info[0]}, {window_info[1]}) {rule.operator} {rule.value}"
        else:
            icv_syntax = f"density({rule.layer}) {rule.operator} {rule.value}"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation="density check",
            constraint=f"{rule.operator} {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def translate_enclosure(self, rule: DRCRule) -> ICVRule:
        """Translate enclosure rules (NOT INSIDE BY)"""
        # Extract enclosing layer from rule name or description
        enclosing_layer = self.extract_enclosing_layer(rule.name, rule.description)
        
        if enclosing_layer:
            icv_syntax = f"enclosure({enclosing_layer}, {rule.layer}) >= {rule.value}"
            operation = "enclosure check"
        else:
            icv_syntax = f"enclosure({rule.layer}) >= {rule.value}"
            operation = "enclosure constraint"
        
        return ICVRule(
            name=rule.name,
            description=rule.description,
            layer=rule.layer,
            operation=operation,
            constraint=f">= {rule.value}",
            value=rule.value,
            icv_syntax=icv_syntax,
            line_number=rule.line_number
        )
    
    def extract_second_layer(self, rule_name: str, description: str) -> Optional[str]:
        """Extract second layer name from rule name or description"""
        # Common patterns: LAYER1_LAYER2_SPACE, "LAYER1 to LAYER2 spacing"
        patterns = [
            r'(\w+)_(\w+)_SPACE',
            r'(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+and\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, rule_name, re.IGNORECASE)
            if match:
                return match.group(2)
            
            if description:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    return match.group(2)
        
        return None
    
    def extract_enclosing_layer(self, rule_name: str, description: str) -> Optional[str]:
        """Extract enclosing layer name from rule name or description"""
        # Common patterns: VIA_ENCLOSED_METAL, "VIA enclosed by METAL"
        patterns = [
            r'\w+_ENCLOSED_(\w+)',
            r'enclosed\s+by\s+(\w+)',
            r'(\w+)\s+enclos',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, rule_name, re.IGNORECASE)
            if match:
                return match.group(1)
            
            if description:
                match = re.search(pattern, description, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    def write_icv_file(self, output_file: str):
        """Write translated rules to ICV format file"""
        with open(output_file, 'w') as f:
            # Write header
            f.write(f"// ICV DRC Rules translated from SVRF\n")
            f.write(f"// Technology: {self.technology}\n")
            f.write(f"// Process Node: {self.process_node}\n")
            f.write(f"// Generated by SVRF to ICV Translator\n")
            f.write(f"// Total Rules: {len(self.icv_rules)}\n")
            f.write(f"// Total Layers: {len(self.icv_layers)}\n\n")
            
            # Write run options
            f.write("// Run Options\n")
            f.write("run_options {\n")
            f.write("    layout_file = \"layout.gds\";\n")
            f.write("    output_dir = \"./icv_results\";\n")
            f.write("    temp_dir = \"./icv_temp\";\n")
            f.write("    report_file = \"drc_report.txt\";\n")
            f.write("    summary_file = \"drc_summary.txt\";\n")
            f.write("}\n\n")
            
            # Write layer definitions
            f.write("// Layer Definitions\n")
            for layer in self.icv_layers:
                f.write(f"{layer}\n")
            f.write("\n")
            
            # Write rules grouped by type
            rule_groups = {}
            for rule in self.icv_rules:
                if rule.operation not in rule_groups:
                    rule_groups[rule.operation] = []
                rule_groups[rule.operation].append(rule)
            
            for group_name, rules in rule_groups.items():
                f.write(f"// {group_name.title()} Rules\n")
                for rule in rules:
                    f.write(f"// Rule: {rule.name}\n")
                    if rule.description:
                        f.write(f"// Description: {rule.description}\n")
                    f.write(f"rule {rule.name.lower()} {{\n")
                    f.write(f"    check_rule = {rule.icv_syntax};\n")
                    f.write(f"    error_message = \"{rule.description or rule.name}\";\n")
                    f.write(f"}}\n\n")
    
    def print_translation_summary(self):
        """Print translation summary"""
        print(f"SVRF to ICV Translation Summary:")
        print(f"  Input SVRF Rules: {len(self.svrf_parser.rules)}")
        print(f"  Translated ICV Rules: {len(self.icv_rules)}")
        print(f"  Input SVRF Layers: {len(self.svrf_parser.layers)}")
        print(f"  Translated ICV Layers: {len(self.icv_layers)}")
        
        if self.svrf_parser.errors:
            print(f"  Parse Errors: {len(self.svrf_parser.errors)}")
        
        # Show rule type distribution
        rule_types = {}
        for rule in self.icv_rules:
            rule_types[rule.operation] = rule_types.get(rule.operation, 0) + 1
        
        print(f"\n  Rule Type Distribution:")
        for rule_type, count in sorted(rule_types.items()):
            print(f"    {rule_type}: {count}")
    
    def print_icv_rules(self, limit: int = 10):
        """Print sample ICV rules"""
        print(f"\nSample ICV Rules (showing first {limit}):")
        print("=" * 60)
        
        for i, rule in enumerate(self.icv_rules[:limit]):
            print(f"Rule {i+1}: {rule.name}")
            print(f"  Layer: {rule.layer}")
            print(f"  Operation: {rule.operation}")
            print(f"  ICV Syntax: {rule.icv_syntax}")
            if rule.description:
                print(f"  Description: {rule.description}")
            print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SVRF to ICV Translator")
    parser.add_argument("input", help="Input SVRF file")
    parser.add_argument("-o", "--output", help="Output ICV file")
    parser.add_argument("--summary", action="store_true", help="Show translation summary")
    parser.add_argument("--preview", type=int, default=0, help="Preview N translated rules")
    parser.add_argument("--technology", default="Generic", help="Technology name")
    parser.add_argument("--process", default="180nm", help="Process node")
    
    args = parser.parse_args()
    
    # Create translator
    translator = SVRFToICVTranslator()
    translator.technology = args.technology
    translator.process_node = args.process
    
    # Set default output filename if not provided
    if not args.output:
        input_path = Path(args.input)
        args.output = input_path.with_suffix('.icv').name
    
    print(f"Translating SVRF to ICV: {args.input} -> {args.output}")
    
    # Perform translation
    success = translator.translate_file(args.input, args.output)
    
    if success:
        print(f"Translation completed successfully!")
        print(f"Output written to: {args.output}")
        
        if args.summary:
            translator.print_translation_summary()
        
        if args.preview > 0:
            translator.print_icv_rules(args.preview)
    else:
        print("Translation failed due to errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()