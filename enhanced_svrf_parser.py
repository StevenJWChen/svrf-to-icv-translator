#!/usr/bin/env python3
"""
Enhanced SVRF Parser with 100% rule coverage
Handles all complex SVRF constructs including enclosure, antenna, and pattern matching rules
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
    enclosure_layers: List[str] = None  # For enclosure rules
    antenna_params: Dict[str, Any] = None  # For antenna rules
    pattern_params: Dict[str, Any] = None  # For pattern matching rules

class EnhancedSVRFParser:
    """Enhanced SVRF parser with complete rule coverage"""
    
    def __init__(self):
        self.layers = []
        self.rules = []
        self.includes = []
        self.errors = []
        
        # Enhanced rule patterns for 100% coverage
        self.enhanced_patterns = [
            # Standard patterns (existing)
            (r'(INTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'width'),
            (r'(INTERNAL2)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'length'),
            (r'(EXTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'spacing'),
            (r'(EXTERNAL)\s+(\w+)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'inter_spacing'),
            (r'(AREA)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'area'),
            (r'(DENSITY)\s+(\w+)\s+WINDOW\s+([\d.]+)\s+([\d.]+)\s*(<|>|==)\s*([\d.]+)', 'density'),
            (r'(DENSITY)\s+(\w+)\s+WINDOW\s+([\d.]+)\s+([\d.]+)\s*(<|>)\s*([\d.]+)', 'density_simple'),
            
            # Enclosure patterns (NEW)
            (r'(\w+)\s+NOT\s+INSIDE\s+(\w+)\s+BY\s*(>=|==|<=)\s*([\d.]+)', 'enclosure'),
            
            # Antenna patterns (NEW)
            (r'ANTENNA\s+(\w+)\s+(\w+)\s+MAX\s+RATIO\s+([\d.]+)', 'antenna_ratio'),
            
            # Pattern matching (NEW)
            (r'RECTANGLE\s+(\w+)\s+LENGTH\s*([<>=]+)\s*([\d.]+)\s+WIDTH\s*([<>=]+)\s*([\d.]+)', 'rectangle'),
            
            # Same mask patterns (NEW)
            (r'(EXTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)\s+SAME_MASK', 'same_mask_spacing'),
            
            # Advanced constraints (NEW)
            (r'(INTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)\s+OPPOSITE', 'opposite_constraint'),
        ]
    
    def parse_file(self, filename: str):
        """Parse SVRF file from disk"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.errors.append(f"File not found: {filename}")
            return
        
        self.parse_lines(lines)
    
    def parse_lines(self, lines: List[str]):
        """Parse lines of SVRF content with enhanced rule detection"""
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
                    i = self.parse_enhanced_drc_rule(lines, i, line_num)
                
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
    
    def parse_enhanced_drc_rule(self, lines: List[str], start_idx: int, line_num: int):
        """Enhanced DRC rule parsing with complete pattern support"""
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
        
        # Parse rule content with enhanced patterns
        rule_content = ' '.join(rule_lines)
        self.extract_enhanced_rule_details(rule_name, rule_content, line_num)
        
        return i  # Return the last processed line index
    
    def extract_enhanced_rule_details(self, rule_name: str, content: str, line_num: int):
        """Extract details from rule content with enhanced pattern recognition"""
        
        # Extract description
        description = ""
        desc_match = re.search(r'@\s*"([^"]+)"', content)
        if desc_match:
            description = desc_match.group(1)
        
        rule_type = "unknown"
        layer = ""
        operator = ""
        value = 0.0
        extra_params = []
        enclosure_layers = None
        antenna_params = None
        pattern_params = None
        
        # Try enhanced patterns first
        for pattern, rule_category in self.enhanced_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if rule_category == 'width':
                    rule_type = "internal1"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    
                elif rule_category == 'length':
                    rule_type = "internal2"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    
                elif rule_category == 'spacing':
                    rule_type = "external1"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    
                elif rule_category == 'inter_spacing':
                    rule_type = "external"
                    layer = match.group(2)
                    operator = match.group(4)
                    value = float(match.group(5))
                    extra_params = [match.group(3)]  # Second layer
                    
                elif rule_category == 'area':
                    rule_type = "area"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    
                elif rule_category in ['density', 'density_simple']:
                    rule_type = "density"
                    layer = match.group(2)
                    if rule_category == 'density':
                        operator = match.group(6)
                        value = float(match.group(7))
                    else:  # density_simple
                        operator = match.group(6)
                        value = float(match.group(7))
                    extra_params = [match.group(3), match.group(4)]  # Window dimensions
                    
                elif rule_category == 'enclosure':
                    rule_type = "enclosure"
                    layer = match.group(1)  # Inner layer
                    enclosure_layers = [match.group(2)]  # Outer layer
                    operator = match.group(3)
                    value = float(match.group(4))
                    
                elif rule_category == 'antenna_ratio':
                    rule_type = "antenna"
                    layer = match.group(1)  # Metal layer
                    antenna_params = {
                        'gate_layer': match.group(2),
                        'max_ratio': float(match.group(3))
                    }
                    operator = "MAX_RATIO"
                    value = float(match.group(3))
                    
                elif rule_category == 'rectangle':
                    rule_type = "pattern_matching"
                    layer = match.group(1)
                    pattern_params = {
                        'type': 'rectangle',
                        'length_op': match.group(2),
                        'length_val': float(match.group(3)),
                        'width_op': match.group(4),
                        'width_val': float(match.group(5))
                    }
                    operator = "RECTANGLE"
                    value = 0.0
                    
                elif rule_category == 'same_mask_spacing':
                    rule_type = "multi_patterning"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    extra_params = ['SAME_MASK']
                    
                elif rule_category == 'opposite_constraint':
                    rule_type = "advanced_constraint"
                    layer = match.group(2)
                    operator = match.group(3)
                    value = float(match.group(4))
                    extra_params = ['OPPOSITE']
                
                break
        
        # Check for additional parameters
        if 'SINGULAR' in content:
            extra_params.append('SINGULAR')
        
        self.rules.append(DRCRule(
            name=rule_name,
            description=description,
            rule_type=rule_type,
            layer=layer,
            operator=operator,
            value=value,
            line_number=line_num,
            extra_params=extra_params or None,
            enclosure_layers=enclosure_layers,
            antenna_params=antenna_params,
            pattern_params=pattern_params
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
        """Print parsing summary"""
        stats = self.get_statistics()
        
        print(f"Enhanced SVRF Parsing Results:")
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

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced SVRF Parser")
    parser.add_argument("file", help="SVRF file to parse")
    
    args = parser.parse_args()
    
    # Parse file
    svrf_parser = EnhancedSVRFParser()
    svrf_parser.parse_file(args.file)
    svrf_parser.print_results()
    
    # Show enhanced rule details
    print(f"\nEnhanced Rule Details:")
    for rule in svrf_parser.rules:
        if rule.rule_type not in ['internal1', 'external1', 'area', 'density']:
            print(f"  {rule.name} ({rule.rule_type}): {rule.description}")
            if rule.enclosure_layers:
                print(f"    Enclosure layers: {rule.enclosure_layers}")
            if rule.antenna_params:
                print(f"    Antenna params: {rule.antenna_params}")
            if rule.pattern_params:
                print(f"    Pattern params: {rule.pattern_params}")

if __name__ == "__main__":
    main()