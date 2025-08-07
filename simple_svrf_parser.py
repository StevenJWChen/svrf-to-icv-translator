#!/usr/bin/env python3
"""
Simplified SVRF DRC Parser
A streamlined parser for SVRF DRC rules with better error handling
"""

import re
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Layer:
    name: str
    gds_number: Optional[int] = None
    expression: Optional[str] = None
    line_number: int = 0

@dataclass
class DRCRule:
    name: str
    description: str
    rule_type: str
    layer: str
    operator: str
    value: float
    line_number: int = 0
    extra_params: List[str] = None

class SVRFParser:
    def __init__(self):
        self.layers = []
        self.rules = []
        self.includes = []
        self.errors = []
    
    def parse_file(self, filename: str):
        """Parse SVRF file"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.errors.append(f"File not found: {filename}")
            return
        
        self.parse_lines(lines)
    
    def parse_lines(self, lines: List[str]):
        """Parse lines of SVRF content"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            line_num = i + 1
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                i += 1
                continue
            
            try:
                # INCLUDE statements
                if line.startswith('INCLUDE'):
                    self.parse_include(line, line_num)
                
                # LAYOUT statements
                elif line.startswith('LAYOUT'):
                    pass  # Skip layout declarations
                
                # Layer definitions
                elif line.startswith('LAYER'):
                    self.parse_layer_definition(line, line_num)
                
                # Derived layer assignments (LAYER_NAME = expression)
                elif '=' in line and not line.startswith('    ') and '{' not in line:
                    self.parse_derived_layer(line, line_num)
                
                # DRC rules (identifier followed by {)
                elif '{' in line or (i + 1 < len(lines) and '{' in lines[i + 1]):
                    i = self.parse_drc_rule(lines, i, line_num)
                
            except Exception as e:
                self.errors.append(f"Error parsing line {line_num}: {e}")
            
            i += 1
    
    def parse_include(self, line: str, line_num: int):
        """Parse INCLUDE statement"""
        match = re.search(r'INCLUDE\s+"([^"]+)"', line)
        if match:
            self.includes.append(match.group(1))
    
    def parse_layer_definition(self, line: str, line_num: int):
        """Parse LAYER definition"""
        parts = line.split()
        if len(parts) >= 3 and parts[0] == 'LAYER':
            layer_name = parts[1]
            gds_number = int(parts[2])
            self.layers.append(Layer(layer_name, gds_number=gds_number, line_number=line_num))
    
    def parse_derived_layer(self, line: str, line_num: int):
        """Parse derived layer assignment"""
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                layer_name = parts[0].strip()
                expression = parts[1].strip()
                self.layers.append(Layer(layer_name, expression=expression, line_number=line_num))
    
    def parse_drc_rule(self, lines: List[str], start_idx: int, line_num: int):
        """Parse DRC rule block"""
        line = lines[start_idx].strip()
        
        # Handle case where rule name and { are on same line or separate lines
        if '{' in line:
            rule_name = line.split('{')[0].strip()
            start_brace_line = start_idx
        else:
            rule_name = line.strip()
            start_brace_line = start_idx + 1
        
        # Find the complete rule block
        rule_lines = []
        brace_count = 0
        i = start_idx
        found_opening_brace = False
        
        while i < len(lines):
            current_line = lines[i].strip()
            if current_line:  # Skip empty lines
                rule_lines.append(current_line)
            
            # Count braces to find end of rule
            open_braces = current_line.count('{')
            close_braces = current_line.count('}')
            
            if open_braces > 0:
                found_opening_brace = True
            
            brace_count += open_braces - close_braces
            
            # If we found the opening brace and count is back to 0, we're done
            if found_opening_brace and brace_count == 0:
                break
            
            i += 1
        
        # Parse rule content
        rule_content = ' '.join(rule_lines)
        self.extract_rule_details(rule_name, rule_content, line_num)
        
        return i  # Return the last processed line index
    
    def extract_rule_details(self, rule_name: str, content: str, line_num: int):
        """Extract details from rule content"""
        
        # Extract description
        description = ""
        desc_match = re.search(r'@\s*"([^"]+)"', content)
        if desc_match:
            description = desc_match.group(1)
        
        # Common DRC rule patterns
        patterns = [
            # INTERNAL1 layer < value
            (r'(INTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'width/area'),
            # INTERNAL2 layer < value
            (r'(INTERNAL2)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'width/length'),
            # EXTERNAL1 layer < value  
            (r'(EXTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'spacing'),
            # EXTERNAL layer1 layer2 < value
            (r'(EXTERNAL)\s+(\w+)\s+\w+\s*(<|>|==)\s*([\d.]+)', 'spacing'),
            # layer NOT INSIDE layer BY == value
            (r'(\w+)\s+NOT\s+INSIDE\s+(\w+)\s+BY\s+==\s*([\d.]+)', 'enclosure'),
            # AREA layer < value
            (r'(AREA)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'area'),
            # DENSITY layer WINDOW x y < value
            (r'(DENSITY)\s+(\w+)\s+WINDOW\s+[\d.]+\s+[\d.]+\s*(<|>|==)\s*([\d.]+)', 'density'),
        ]
        
        rule_type = "unknown"
        layer = ""
        operator = ""
        value = 0.0
        extra_params = []
        
        for pattern, rule_category in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if rule_category == 'enclosure':
                    rule_type = "enclosure"
                    layer = match.group(1)
                    value = float(match.group(3))
                    operator = "=="
                else:
                    rule_type = match.group(1).lower()
                    layer = match.group(2) if len(match.groups()) > 1 else ""
                    operator = match.group(3) if len(match.groups()) > 2 else ""
                    value = float(match.group(4)) if len(match.groups()) > 3 else 0.0
                
                # Check for SINGULAR parameter
                if 'SINGULAR' in content:
                    extra_params.append('SINGULAR')
                
                break
        
        self.rules.append(DRCRule(
            name=rule_name,
            description=description,
            rule_type=rule_type,
            layer=layer,
            operator=operator,
            value=value,
            line_number=line_num,
            extra_params=extra_params
        ))
    
    def get_statistics(self):
        """Get parsing statistics"""
        layer_types = {}
        rule_types = {}
        
        for layer in self.layers:
            if layer.gds_number is not None:
                layer_types['primary'] = layer_types.get('primary', 0) + 1
            else:
                layer_types['derived'] = layer_types.get('derived', 0) + 1
        
        for rule in self.rules:
            rule_types[rule.rule_type] = rule_types.get(rule.rule_type, 0) + 1
        
        return {
            'layers': len(self.layers),
            'layer_types': layer_types,
            'rules': len(self.rules),
            'rule_types': rule_types,
            'includes': len(self.includes),
            'errors': len(self.errors)
        }
    
    def print_results(self):
        """Print parsing results"""
        stats = self.get_statistics()
        
        print(f"SVRF Parsing Results:")
        print(f"  Layers: {stats['layers']}")
        print(f"    Primary: {stats['layer_types'].get('primary', 0)}")
        print(f"    Derived: {stats['layer_types'].get('derived', 0)}")
        print(f"  Rules: {stats['rules']}")
        print(f"  Includes: {stats['includes']}")
        print(f"  Errors: {stats['errors']}")
        
        if self.errors:
            print(f"\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if stats['rule_types']:
            print(f"\nRule Types:")
            for rule_type, count in sorted(stats['rule_types'].items()):
                print(f"  {rule_type}: {count}")
    
    def print_layers(self):
        """Print layer information"""
        if not self.layers:
            return
            
        print(f"\nLayers ({len(self.layers)}):")
        for layer in self.layers:
            if layer.gds_number is not None:
                print(f"  {layer.name}: GDS {layer.gds_number}")
            else:
                print(f"  {layer.name}: {layer.expression}")
    
    def print_rules(self, rule_filter=None):
        """Print rule information"""
        if not self.rules:
            return
            
        filtered_rules = self.rules
        if rule_filter:
            filtered_rules = [r for r in self.rules if rule_filter.lower() in r.rule_type.lower()]
        
        print(f"\nRules ({len(filtered_rules)}):")
        for rule in filtered_rules:
            print(f"  {rule.name} (line {rule.line_number}):")
            print(f"    Type: {rule.rule_type}")
            print(f"    Layer: {rule.layer}")
            print(f"    Constraint: {rule.operator} {rule.value}")
            if rule.description:
                print(f"    Description: {rule.description}")
            if rule.extra_params:
                print(f"    Parameters: {', '.join(rule.extra_params)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple SVRF DRC Parser")
    parser.add_argument("file", help="SVRF file to parse")
    parser.add_argument("--layers", action="store_true", help="Show layer details")
    parser.add_argument("--rules", action="store_true", help="Show rule details")
    parser.add_argument("--filter", help="Filter rules by type")
    
    args = parser.parse_args()
    
    svrf_parser = SVRFParser()
    svrf_parser.parse_file(args.file)
    svrf_parser.print_results()
    
    if args.layers:
        svrf_parser.print_layers()
    
    if args.rules:
        svrf_parser.print_rules(args.filter)

if __name__ == "__main__":
    main()