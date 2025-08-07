# SVRF DRC Tools - Complete Usage Guide

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Command Line Usage](#command-line-usage)
- [Python API Usage](#python-api-usage)
- [Workflow Examples](#workflow-examples)
- [Integration Scenarios](#integration-scenarios)
- [Best Practices](#best-practices)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- No additional dependencies required

### Installation
```bash
# Download the tools
wget https://example.com/svrf-tools.zip
unzip svrf-tools.zip
cd svrf-tools/

# Or clone from repository
git clone https://github.com/example/svrf-tools.git
cd svrf-tools/
```

### Verify Installation
```bash
# Test parser
python simple_svrf_parser.py --help

# Test translator
python svrf_to_icv_translator.py --help

# Run demos
python demo_parser.py
python demo_translator.py
```

## 💻 Command Line Usage

### 1. SVRF Parser (`simple_svrf_parser.py`)

#### Basic Usage
```bash
# Parse SVRF file and show summary
python simple_svrf_parser.py rules.svrf

# Example output:
# SVRF Parsing Results:
#   Layers: 13
#   Rules: 28  
#   Includes: 2
#   Errors: 0
```

#### Detailed Analysis
```bash
# Full analysis with statistics
python simple_svrf_parser.py rules.svrf --analyze --stats

# Show layer information
python simple_svrf_parser.py rules.svrf --layers

# Show all rules
python simple_svrf_parser.py rules.svrf --rules

# Filter by rule type
python simple_svrf_parser.py rules.svrf --rules spacing
python simple_svrf_parser.py rules.svrf --rules width
```

#### Common Options
| Option | Description | Example |
|--------|-------------|---------|
| `--layers` | Show layer details | `--layers` |
| `--rules` | Show rule details | `--rules` |
| `--filter TYPE` | Filter rules by type | `--filter spacing` |
| `--analyze` | Perform detailed analysis | `--analyze` |
| `--stats` | Show statistics only | `--stats` |

### 2. SVRF to ICV Translator (`svrf_to_icv_translator.py`)

#### Basic Translation
```bash
# Translate SVRF to ICV (auto-generate output filename)
python svrf_to_icv_translator.py rules.svrf

# Translate with custom output filename
python svrf_to_icv_translator.py rules.svrf -o my_rules.icv
```

#### Advanced Translation
```bash
# Translation with summary and preview
python svrf_to_icv_translator.py rules.svrf --summary --preview 10

# Technology-specific translation
python svrf_to_icv_translator.py rules.svrf \
    --technology "TSMC 28nm" \
    --process "28nm" \
    -o tsmc28_rules.icv

# Full analysis
python svrf_to_icv_translator.py rules.svrf \
    --summary --preview 20 \
    --technology "Custom Tech" \
    --process "65nm"
```

#### Translation Options
| Option | Description | Example |
|--------|-------------|---------|
| `-o FILE` | Output file | `-o output.icv` |
| `--summary` | Show translation summary | `--summary` |
| `--preview N` | Preview N translated rules | `--preview 10` |
| `--technology NAME` | Technology name | `--technology "TSMC 28nm"` |
| `--process NODE` | Process node | `--process "28nm"` |

## 🐍 Python API Usage

### 1. Basic Parsing

```python
from simple_svrf_parser import SVRFParser

# Create parser instance
parser = SVRFParser()

# Parse file
parser.parse_file("rules.svrf")

# Check for errors
if parser.errors:
    print("Parse errors found:")
    for error in parser.errors:
        print(f"  {error}")
else:
    print(f"Successfully parsed {len(parser.rules)} rules")

# Access parsed data
print(f"Layers: {len(parser.layers)}")
print(f"Rules: {len(parser.rules)}")
print(f"Includes: {len(parser.includes)}")
```

### 2. Advanced Analysis

```python
from simple_svrf_parser import SVRFParser, SVRFAnalyzer

# Parse and analyze
parser = SVRFParser()
parser.parse_file("rules.svrf")

analyzer = SVRFAnalyzer(parser)

# Get statistics
layer_stats = analyzer.get_layer_stats()
rule_stats = analyzer.get_rule_stats()

print(f"Primary layers: {layer_stats['primary_layers']}")
print(f"Derived layers: {layer_stats['derived_layers']}")
print(f"Rule types: {rule_stats['rule_types']}")

# Find specific rule types
spacing_rules = analyzer.get_spacing_rules()
width_rules = analyzer.get_width_rules()

print(f"Spacing rules: {len(spacing_rules)}")
print(f"Width rules: {len(width_rules)}")

# Check for issues
issues = analyzer.find_potential_issues()
if issues:
    print("Potential issues:")
    for issue in issues:
        print(f"  - {issue}")
```

### 3. Rule Translation

```python
from svrf_to_icv_translator import SVRFToICVTranslator

# Create translator
translator = SVRFToICVTranslator()

# Set technology parameters
translator.technology = "TSMC 28nm"
translator.process_node = "28nm"

# Translate file
success = translator.translate_file("input.svrf", "output.icv")

if success:
    # Show results
    translator.print_translation_summary()
    translator.print_icv_rules(10)  # Show first 10 rules
    
    # Access translated data
    print(f"Translated {len(translator.icv_rules)} rules")
    print(f"Translated {len(translator.icv_layers)} layers")
else:
    print("Translation failed")
```

### 4. Custom Processing

```python
def process_ruleset(svrf_file):
    """Custom processing function"""
    
    # Parse SVRF
    parser = SVRFParser()
    parser.parse_file(svrf_file)
    
    if parser.errors:
        return {'success': False, 'errors': parser.errors}
    
    # Analyze rules
    analyzer = SVRFAnalyzer(parser)
    
    # Get restrictive rules (< 0.15)
    restrictive_rules = [
        r for r in parser.rules 
        if r.value < 0.15 and r.operator == '<'
    ]
    
    # Get layer coverage
    layer_coverage = len(analyzer.get_rule_stats()['covered_layers'])
    
    # Translate to ICV
    translator = SVRFToICVTranslator()
    translator.technology = "Generic"
    icv_file = svrf_file.replace('.svrf', '.icv')
    translation_success = translator.translate_file(svrf_file, icv_file)
    
    return {
        'success': True,
        'layers': len(parser.layers),
        'rules': len(parser.rules),
        'restrictive_rules': len(restrictive_rules),
        'layer_coverage': layer_coverage,
        'translation_success': translation_success,
        'icv_file': icv_file if translation_success else None
    }

# Usage
result = process_ruleset("my_rules.svrf")
print(f"Processing result: {result}")
```

## 🔄 Workflow Examples

### 1. Basic Validation Workflow

```bash
#!/bin/bash
# validate_ruleset.sh

SVRF_FILE="$1"

echo "Validating SVRF ruleset: $SVRF_FILE"

# Step 1: Parse and check for errors
echo "Step 1: Parsing..."
python simple_svrf_parser.py "$SVRF_FILE" --stats > parse_results.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Parse failed"
    exit 1
fi

# Step 2: Check for potential issues
echo "Step 2: Analyzing..."
python simple_svrf_parser.py "$SVRF_FILE" --analyze > analysis_results.txt

# Step 3: Test translation
echo "Step 3: Testing translation..."
python svrf_to_icv_translator.py "$SVRF_FILE" --summary > translation_results.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Translation failed"
    exit 1
fi

echo "Validation completed successfully"
```

### 2. Multi-Technology Processing

```python
#!/usr/bin/env python3
# process_technologies.py

import os
import json
from pathlib import Path
from svrf_to_icv_translator import SVRFToICVTranslator

def process_technology_rulesets(config_file):
    """Process multiple technology rulesets"""
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    results = []
    
    for tech_config in config['technologies']:
        print(f"Processing {tech_config['name']}...")
        
        # Create translator for this technology
        translator = SVRFToICVTranslator()
        translator.technology = tech_config['name']
        translator.process_node = tech_config['process_node']
        
        # Process each ruleset
        for ruleset in tech_config['rulesets']:
            input_file = ruleset['svrf_file']
            output_file = ruleset['icv_file']
            
            print(f"  Translating {input_file} -> {output_file}")
            
            success = translator.translate_file(input_file, output_file)
            
            result = {
                'technology': tech_config['name'],
                'process_node': tech_config['process_node'],
                'input_file': input_file,
                'output_file': output_file,
                'success': success,
                'rule_count': len(translator.icv_rules) if success else 0,
                'layer_count': len(translator.icv_layers) if success else 0
            }
            results.append(result)
    
    return results

# Example configuration file (technologies.json):
"""
{
    "technologies": [
        {
            "name": "TSMC 28nm",
            "process_node": "28nm", 
            "rulesets": [
                {"svrf_file": "tsmc28_core.svrf", "icv_file": "tsmc28_core.icv"},
                {"svrf_file": "tsmc28_io.svrf", "icv_file": "tsmc28_io.icv"}
            ]
        },
        {
            "name": "GlobalFoundries 22nm",
            "process_node": "22nm",
            "rulesets": [
                {"svrf_file": "gf22_core.svrf", "icv_file": "gf22_core.icv"}
            ]
        }
    ]
}
"""

if __name__ == "__main__":
    results = process_technology_rulesets("technologies.json")
    
    # Print summary
    print("\nProcessing Summary:")
    for result in results:
        status = "SUCCESS" if result['success'] else "FAILED"
        print(f"  {result['technology']}: {result['input_file']} -> {status}")
```

### 3. Batch Processing Script

```bash
#!/bin/bash
# batch_process.sh

# Process all SVRF files in directory
SVRF_DIR="./svrf_rules"
ICV_DIR="./icv_rules"
LOG_FILE="batch_process.log"

# Create output directory
mkdir -p "$ICV_DIR"

# Initialize log
echo "Batch processing started: $(date)" > "$LOG_FILE"

# Process each SVRF file
for svrf_file in "$SVRF_DIR"/*.svrf; do
    if [ -f "$svrf_file" ]; then
        filename=$(basename "$svrf_file" .svrf)
        icv_file="$ICV_DIR/${filename}.icv"
        
        echo "Processing: $svrf_file" | tee -a "$LOG_FILE"
        
        # Parse and validate
        python simple_svrf_parser.py "$svrf_file" --stats 2>&1 | tee -a "$LOG_FILE"
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            # Translate
            python svrf_to_icv_translator.py "$svrf_file" -o "$icv_file" --summary 2>&1 | tee -a "$LOG_FILE"
            
            if [ ${PIPESTATUS[0]} -eq 0 ]; then
                echo "SUCCESS: $filename" | tee -a "$LOG_FILE"
            else
                echo "TRANSLATION FAILED: $filename" | tee -a "$LOG_FILE"
            fi
        else
            echo "PARSE FAILED: $filename" | tee -a "$LOG_FILE"
        fi
        
        echo "---" >> "$LOG_FILE"
    fi
done

echo "Batch processing completed: $(date)" | tee -a "$LOG_FILE"
```

## 🔧 Integration Scenarios

### 1. CAD Flow Integration

```python
# cad_flow_integration.py

import subprocess
import tempfile
import os
from pathlib import Path

class CADFlowIntegration:
    def __init__(self, work_dir):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
    
    def validate_drc_rules(self, svrf_file):
        """Validate DRC rules before using in CAD flow"""
        
        # Parse rules
        cmd = ["python", "simple_svrf_parser.py", svrf_file, "--analyze"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, f"Parse failed: {result.stderr}"
        
        # Check for critical issues
        output = result.stdout
        if "Errors:" in output and not "Errors: 0" in output:
            return False, "Parse errors found"
        
        return True, "Validation passed"
    
    def convert_to_icv(self, svrf_file, technology):
        """Convert SVRF to ICV for Synopsys tools"""
        
        icv_file = self.work_dir / f"{Path(svrf_file).stem}.icv"
        
        cmd = [
            "python", "svrf_to_icv_translator.py",
            svrf_file,
            "-o", str(icv_file),
            "--technology", technology
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, str(icv_file)
        else:
            return False, result.stderr
    
    def run_drc_check(self, layout_file, rules_file, tool="icv"):
        """Run DRC check with converted rules"""
        
        if tool == "icv":
            # Run IC Validator DRC
            cmd = [
                "icv", "-dp", "8",
                "-i", layout_file,
                "-runset", rules_file,
                "-o", str(self.work_dir / "drc_results")
            ]
        else:
            # Run Calibre DRC (original SVRF)
            cmd = [
                "calibre", "-drc", "-hier",
                "-runset", rules_file,
                layout_file
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout

# Usage example
def main():
    cad = CADFlowIntegration("./work")
    
    # Validate rules
    valid, msg = cad.validate_drc_rules("design_rules.svrf")
    if not valid:
        print(f"Rule validation failed: {msg}")
        return
    
    # Convert to ICV
    success, icv_file = cad.convert_to_icv("design_rules.svrf", "TSMC 28nm")
    if not success:
        print(f"Conversion failed: {icv_file}")
        return
    
    # Run DRC
    success, output = cad.run_drc_check("layout.gds", icv_file, "icv")
    if success:
        print("DRC check passed")
    else:
        print("DRC check failed")

if __name__ == "__main__":
    main()
```

### 2. Web Service Integration

```python
# web_service.py (Flask example)

from flask import Flask, request, jsonify, send_file
import tempfile
import os
from pathlib import Path
from svrf_to_icv_translator import SVRFToICVTranslator
from simple_svrf_parser import SVRFParser

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def parse_svrf():
    """Parse SVRF content and return analysis"""
    
    try:
        # Get SVRF content from request
        svrf_content = request.json.get('svrf_content', '')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svrf', delete=False) as f:
            f.write(svrf_content)
            temp_file = f.name
        
        # Parse SVRF
        parser = SVRFParser()
        parser.parse_file(temp_file)
        
        # Clean up
        os.unlink(temp_file)
        
        # Return results
        stats = parser.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'layers': [{'name': l.name, 'gds_number': l.gds_number, 'expression': l.expression} for l in parser.layers],
            'rules': [{'name': r.name, 'type': r.rule_type, 'layer': r.layer, 'value': r.value} for r in parser.rules[:10]],  # First 10 rules
            'errors': parser.errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/translate', methods=['POST'])
def translate_to_icv():
    """Translate SVRF to ICV format"""
    
    try:
        # Get parameters
        svrf_content = request.json.get('svrf_content', '')
        technology = request.json.get('technology', 'Generic')
        process_node = request.json.get('process_node', '180nm')
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svrf', delete=False) as f:
            f.write(svrf_content)
            svrf_file = f.name
        
        icv_file = svrf_file.replace('.svrf', '.icv')
        
        # Translate
        translator = SVRFToICVTranslator()
        translator.technology = technology
        translator.process_node = process_node
        
        success = translator.translate_file(svrf_file, icv_file)
        
        if success:
            # Read ICV content
            with open(icv_file, 'r') as f:
                icv_content = f.read()
            
            # Clean up
            os.unlink(svrf_file)
            os.unlink(icv_file)
            
            return jsonify({
                'success': True,
                'icv_content': icv_content,
                'statistics': {
                    'rules_translated': len(translator.icv_rules),
                    'layers_translated': len(translator.icv_layers)
                }
            })
        else:
            os.unlink(svrf_file)
            return jsonify({'success': False, 'error': 'Translation failed'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

## ✅ Best Practices

### 1. File Organization

```
project/
├── svrf_rules/           # Original SVRF files
│   ├── core_rules.svrf
│   ├── io_rules.svrf
│   └── custom_rules.svrf
├── icv_rules/            # Translated ICV files
│   ├── core_rules.icv
│   ├── io_rules.icv
│   └── custom_rules.icv
├── scripts/              # Processing scripts
│   ├── validate_rules.py
│   └── batch_convert.sh
└── logs/                 # Processing logs
    ├── parse_results.log
    └── translation.log
```

### 2. Error Handling Strategy

```python
def robust_processing(svrf_file):
    """Example of robust error handling"""
    
    errors = []
    warnings = []
    
    try:
        # Step 1: Pre-validation
        if not Path(svrf_file).exists():
            errors.append(f"File not found: {svrf_file}")
            return {'success': False, 'errors': errors}
        
        # Step 2: Parse with error collection
        parser = SVRFParser()
        try:
            parser.parse_file(svrf_file)
            errors.extend(parser.errors)
        except Exception as e:
            errors.append(f"Parse exception: {str(e)}")
        
        # Step 3: Validate parsed data
        if len(parser.rules) == 0:
            warnings.append("No rules found in file")
        
        if len(parser.layers) == 0:
            warnings.append("No layers found in file")
        
        # Step 4: Translation with fallback
        translator = SVRFToICVTranslator()
        icv_file = svrf_file.replace('.svrf', '.icv')
        
        try:
            success = translator.translate_file(svrf_file, icv_file)
            if not success:
                errors.append("Translation failed")
        except Exception as e:
            errors.append(f"Translation exception: {str(e)}")
            success = False
        
        # Return comprehensive results
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'statistics': {
                'rules_parsed': len(parser.rules),
                'layers_parsed': len(parser.layers),
                'rules_translated': len(translator.icv_rules) if success else 0
            }
        }
        
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return {'success': False, 'errors': errors}
```

### 3. Performance Optimization

```python
def optimize_large_file_processing(svrf_file):
    """Optimized processing for large files"""
    
    # Check file size
    file_size = Path(svrf_file).stat().st_size
    
    if file_size > 10 * 1024 * 1024:  # > 10MB
        print(f"Large file detected ({file_size/1024/1024:.1f} MB)")
        
        # Use streaming approach for very large files
        return process_large_file_streaming(svrf_file)
    else:
        # Standard processing
        return process_standard(svrf_file)

def process_large_file_streaming(svrf_file):
    """Stream processing for large files"""
    
    parser = SVRFParser()
    
    # Process in chunks
    with open(svrf_file, 'r') as f:
        chunk_lines = []
        chunk_size = 1000  # Process 1000 lines at a time
        
        for i, line in enumerate(f):
            chunk_lines.append(line)
            
            if len(chunk_lines) >= chunk_size:
                parser.parse_lines(chunk_lines)
                chunk_lines = []
                
                # Progress indication
                if i % 10000 == 0:
                    print(f"Processed {i} lines...")
        
        # Process remaining lines
        if chunk_lines:
            parser.parse_lines(chunk_lines)
    
    return parser
```

### 4. Validation Checklist

```python
def comprehensive_validation(svrf_file):
    """Comprehensive validation checklist"""
    
    validation_results = {
        'file_checks': {},
        'syntax_checks': {},
        'semantic_checks': {},
        'translation_checks': {}
    }
    
    # File-level checks
    path = Path(svrf_file)
    validation_results['file_checks'] = {
        'exists': path.exists(),
        'readable': path.is_file() and os.access(path, os.R_OK),
        'size_mb': path.stat().st_size / (1024*1024) if path.exists() else 0,
        'encoding_ok': check_file_encoding(svrf_file)
    }
    
    # Syntax checks
    parser = SVRFParser()
    parser.parse_file(svrf_file)
    
    validation_results['syntax_checks'] = {
        'parse_errors': len(parser.errors),
        'rules_found': len(parser.rules),
        'layers_found': len(parser.layers),
        'includes_found': len(parser.includes)
    }
    
    # Semantic checks
    semantic_issues = []
    
    # Check for unrealistic values
    for rule in parser.rules:
        if rule.rule_type in ['internal1', 'external1'] and rule.value > 100:
            semantic_issues.append(f"Unusually large value in {rule.name}: {rule.value}")
        if rule.value < 0:
            semantic_issues.append(f"Negative value in {rule.name}: {rule.value}")
    
    # Check layer references
    layer_names = {l.name for l in parser.layers}
    for rule in parser.rules:
        if rule.layer and rule.layer not in layer_names:
            semantic_issues.append(f"Unknown layer '{rule.layer}' in rule {rule.name}")
    
    validation_results['semantic_checks'] = {
        'issues_found': len(semantic_issues),
        'issues': semantic_issues
    }
    
    # Translation checks
    translator = SVRFToICVTranslator()
    icv_file = svrf_file.replace('.svrf', '.icv')
    translation_success = translator.translate_file(svrf_file, icv_file)
    
    validation_results['translation_checks'] = {
        'translation_success': translation_success,
        'rules_translated': len(translator.icv_rules) if translation_success else 0,
        'unsupported_rules': len(parser.rules) - len(translator.icv_rules) if translation_success else len(parser.rules)
    }
    
    return validation_results

def check_file_encoding(filename):
    """Check if file has valid encoding"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError:
        try:
            with open(filename, 'r', encoding='latin-1') as f:
                f.read()
            return 'latin-1'
        except UnicodeDecodeError:
            return False
```

## 🔧 Advanced Features

### 1. Custom Rule Processors

```python
class CustomRuleProcessor:
    """Custom rule processing for special requirements"""
    
    def __init__(self):
        self.custom_patterns = []
        self.post_processors = []
    
    def add_custom_pattern(self, pattern, processor_func):
        """Add custom rule pattern"""
        self.custom_patterns.append((pattern, processor_func))
    
    def add_post_processor(self, processor_func):
        """Add post-processing function"""
        self.post_processors.append(processor_func)
    
    def process_rules(self, parser):
        """Process rules with custom logic"""
        
        # Apply custom patterns
        for rule in parser.rules:
            for pattern, processor_func in self.custom_patterns:
                if re.match(pattern, rule.name):
                    processor_func(rule)
        
        # Apply post-processors
        for processor_func in self.post_processors:
            processor_func(parser.rules)
        
        return parser.rules

# Example usage
def metal_layer_processor(rule):
    """Special processing for metal layer rules"""
    if 'METAL' in rule.layer or 'M' in rule.layer:
        # Adjust values for metal layers
        if rule.rule_type == 'internal1' and rule.value < 0.1:
            print(f"Warning: Very tight width rule for metal layer: {rule.name}")

def density_post_processor(rules):
    """Post-process density rules"""
    density_rules = [r for r in rules if r.rule_type == 'density']
    if len(density_rules) == 0:
        print("Warning: No density rules found")

# Usage
processor = CustomRuleProcessor()
processor.add_custom_pattern(r'.*METAL.*', metal_layer_processor)
processor.add_post_processor(density_post_processor)

parser = SVRFParser()
parser.parse_file("rules.svrf")
processed_rules = processor.process_rules(parser)
```

### 2. Configuration-Driven Processing

```python
import yaml

class ConfigurableProcessor:
    """Configuration-driven rule processing"""
    
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def process_with_config(self, svrf_file):
        """Process SVRF file according to configuration"""
        
        # Parse file
        parser = SVRFParser()
        parser.parse_file(svrf_file)
        
        # Apply configuration-based filtering
        if 'rule_filters' in self.config:
            parser.rules = self.apply_rule_filters(parser.rules)
        
        # Apply value adjustments
        if 'value_adjustments' in self.config:
            self.apply_value_adjustments(parser.rules)
        
        # Translate with configured settings
        translator = SVRFToICVTranslator()
        translator.technology = self.config.get('technology', 'Generic')
        translator.process_node = self.config.get('process_node', '180nm')
        
        # Configure translation options
        if 'translation_options' in self.config:
            self.configure_translator(translator)
        
        output_file = self.config.get('output_file', svrf_file.replace('.svrf', '.icv'))
        success = translator.translate_file(svrf_file, output_file)
        
        return success, parser, translator
    
    def apply_rule_filters(self, rules):
        """Apply rule filters from configuration"""
        filtered_rules = []
        
        for rule in rules:
            include_rule = True
            
            # Check exclusion patterns
            for pattern in self.config['rule_filters'].get('exclude_patterns', []):
                if re.match(pattern, rule.name):
                    include_rule = False
                    break
            
            # Check minimum values
            min_values = self.config['rule_filters'].get('minimum_values', {})
            if rule.rule_type in min_values:
                if rule.value < min_values[rule.rule_type]:
                    include_rule = False
            
            if include_rule:
                filtered_rules.append(rule)
        
        return filtered_rules
    
    def apply_value_adjustments(self, rules):
        """Apply value adjustments from configuration"""
        adjustments = self.config['value_adjustments']
        
        for rule in rules:
            if rule.rule_type in adjustments:
                adjustment = adjustments[rule.rule_type]
                if adjustment['type'] == 'multiply':
                    rule.value *= adjustment['factor']
                elif adjustment['type'] == 'add':
                    rule.value += adjustment['value']

# Example configuration file (config.yaml):
"""
technology: "TSMC 28nm"
process_node: "28nm"
output_file: "processed_rules.icv"

rule_filters:
  exclude_patterns:
    - ".*DEBUG.*"
    - ".*TEST.*"
  minimum_values:
    internal1: 0.05
    external1: 0.05

value_adjustments:
  internal1:
    type: "multiply"
    factor: 1.1
  external1:
    type: "add"
    value: 0.01

translation_options:
  include_comments: true
  group_by_layer: true
"""
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Parser Hangs or Takes Too Long

**Symptoms**: Parser doesn't complete, high CPU usage
**Causes**: Malformed SVRF syntax, infinite loops in parsing
**Solutions**:
```bash
# Check for syntax issues
grep -n '[{}]' your_file.svrf | head -20

# Check brace balance
grep -o '[{}]' your_file.svrf | sort | uniq -c

# Use timeout for testing
timeout 30s python simple_svrf_parser.py your_file.svrf
```

#### 2. Translation Produces Incorrect Results

**Symptoms**: Rules not translated correctly, syntax errors in ICV
**Debugging**:
```python
# Debug specific rule translation
parser = SVRFParser()
parser.parse_file("rules.svrf")

# Check specific rule
for rule in parser.rules:
    if rule.name == "PROBLEMATIC_RULE":
        print(f"Rule type: {rule.rule_type}")
        print(f"Layer: {rule.layer}")
        print(f"Value: {rule.value}")
        print(f"Operator: {rule.operator}")
```

#### 3. Memory Issues with Large Files

**Symptoms**: Out of memory errors, slow processing
**Solutions**:
```python
# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Process in smaller chunks
def process_large_file_chunked(filename, chunk_size=1000):
    parser = SVRFParser()
    
    with open(filename, 'r') as f:
        lines = []
        for i, line in enumerate(f):
            lines.append(line)
            
            if len(lines) >= chunk_size:
                parser.parse_lines(lines)
                lines = []
                
                # Clear processed data periodically if needed
                if i % 10000 == 0:
                    print(f"Processed {i} lines")
        
        if lines:
            parser.parse_lines(lines)
    
    return parser
```

#### 4. Encoding Issues

**Symptoms**: Unicode errors, garbled text
**Solutions**:
```python
# Try different encodings
encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']

def read_with_fallback_encoding(filename):
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Successfully read with {encoding} encoding")
            return content
        except UnicodeDecodeError:
            continue
    
    raise ValueError("Could not read file with any encoding")
```

### Debug Mode

```python
# Enable debug mode for detailed logging
import logging

logging.basicConfig(level=logging.DEBUG)

def debug_parsing(svrf_file):
    """Parse with debug information"""
    
    print(f"Parsing file: {svrf_file}")
    print(f"File size: {Path(svrf_file).stat().st_size} bytes")
    
    parser = SVRFParser()
    
    # Add debug output to parser methods
    original_parse_drc_rule = parser.parse_drc_rule
    
    def debug_parse_drc_rule(lines, start_idx, line_num):
        print(f"Parsing rule at line {line_num}")
        result = original_parse_drc_rule(lines, start_idx, line_num)
        print(f"Rule parsing completed, next index: {result}")
        return result
    
    parser.parse_drc_rule = debug_parse_drc_rule
    
    # Parse with debug info
    parser.parse_file(svrf_file)
    
    print(f"Parsing completed:")
    print(f"  Layers: {len(parser.layers)}")
    print(f"  Rules: {len(parser.rules)}")
    print(f"  Errors: {len(parser.errors)}")
    
    return parser
```

This comprehensive usage guide provides all the information needed to effectively use the SVRF DRC parser and ICV translator tools in various scenarios and environments.