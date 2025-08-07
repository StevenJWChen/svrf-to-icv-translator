# SVRF DRC Parser and ICV Translator - Technical Reference

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Parser Implementation](#parser-implementation)
- [Translation Algorithm](#translation-algorithm)
- [Data Structures](#data-structures)
- [Rule Type Mappings](#rule-type-mappings)
- [Error Handling](#error-handling)
- [Performance Analysis](#performance-analysis)
- [Extension Points](#extension-points)

## 🏗 Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SVRF File     │───▶│  SVRF Parser    │───▶│   Data Model    │
│  (.svrf)        │    │                 │    │ (Layers/Rules)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ICV File      │◀───│ ICV Translator  │◀───│   Analyzer      │
│  (.icv)         │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Design Patterns Used

1. **Parser Pattern**: Line-by-line parsing with state tracking
2. **Strategy Pattern**: Different translation strategies for rule types
3. **Factory Pattern**: Rule object creation based on type
4. **Observer Pattern**: Error collection and reporting

### Key Design Decisions

- **Regex-based parsing**: Balance between simplicity and power
- **Modular architecture**: Separate parsing and translation concerns
- **Defensive programming**: Extensive error handling and validation
- **Memory efficiency**: Process rules sequentially, not all in memory

## 🔍 Parser Implementation

### Parsing State Machine

```
Start ──┐
        │
        ▼
   Skip Comments/Newlines ──┐
        │                  │
        ▼                  │
   Identify Line Type      │
        │                  │
        ├─ INCLUDE ────────┤
        ├─ LAYER ──────────┤  
        ├─ ASSIGNMENT ─────┤
        ├─ RULE_START ─────┤
        └─ UNKNOWN ────────┘
```

### Line Processing Algorithm

```python
def parse_lines(self, lines):
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            i += 1
            continue
            
        # Determine line type and process
        if line.startswith('INCLUDE'):
            self.parse_include(line, i+1)
        elif line.startswith('LAYER'):
            self.parse_layer_definition(line, i+1)
        elif '=' in line and '{' not in line:
            self.parse_derived_layer(line, i+1)
        elif '{' in line or self.next_line_has_brace(lines, i):
            i = self.parse_drc_rule(lines, i, i+1)
            
        i += 1
```

### Rule Block Parsing

The most complex part is parsing multi-line rule blocks:

```python
def parse_drc_rule(self, lines, start_idx, line_num):
    # Handle rule name extraction
    rule_name = self.extract_rule_name(lines[start_idx])
    
    # Find complete rule block by tracking braces
    rule_lines = []
    brace_count = 0
    i = start_idx
    found_opening_brace = False
    
    while i < len(lines):
        current_line = lines[i].strip()
        if current_line:
            rule_lines.append(current_line)
        
        # Track brace balance
        open_braces = current_line.count('{')
        close_braces = current_line.count('}')
        
        if open_braces > 0:
            found_opening_brace = True
        
        brace_count += open_braces - close_braces
        
        # Rule complete when braces balanced
        if found_opening_brace and brace_count == 0:
            break
            
        i += 1
    
    # Extract rule details from collected lines
    rule_content = ' '.join(rule_lines)
    self.extract_rule_details(rule_name, rule_content, line_num)
    
    return i
```

### Rule Detail Extraction

Uses regex patterns to extract rule components:

```python
RULE_PATTERNS = [
    # Pattern format: (regex, rule_category, groups)
    (r'(INTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'width'),
    (r'(EXTERNAL1)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'spacing'),
    (r'(AREA)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'area'),
    (r'(\w+)\s+NOT\s+INSIDE\s+(\w+)\s+BY\s+==\s*([\d.]+)', 'enclosure'),
    (r'(DENSITY)\s+(\w+)\s+WINDOW\s+[\d.]+\s+[\d.]+\s*(<|>|==)\s*([\d.]+)', 'density'),
]
```

## 🔄 Translation Algorithm

### Translation Flow

```
SVRF Rule ──┐
            │
            ▼
    Rule Type Detection
            │
            ▼
    Mapping Table Lookup
            │
            ▼ 
    ICV Syntax Generation
            │
            ▼
    Validation & Output
```

### Rule Type Mapping Strategy

```python
class SVRFToICVTranslator:
    def __init__(self):
        self.rule_mappings = {
            'internal1': self.translate_internal1,
            'internal2': self.translate_internal2,
            'external1': self.translate_external1,
            'external': self.translate_external,
            'area': self.translate_area,
            'density': self.translate_density,
            'enclosure': self.translate_enclosure
        }
```

### Translation Functions

Each rule type has a dedicated translation function:

```python
def translate_internal1(self, rule: DRCRule) -> ICVRule:
    """Translate width/size rules"""
    icv_syntax = f"width({rule.layer}) {rule.operator} {rule.value}"
    
    return ICVRule(
        name=rule.name,
        layer=rule.layer,
        icv_syntax=icv_syntax,
        # ... other fields
    )
```

### Smart Layer Recognition

The translator uses heuristics to identify related layers:

```python
def extract_second_layer(self, rule_name, description):
    """Extract second layer from rule context"""
    patterns = [
        r'(\w+)_(\w+)_SPACE',      # LAYER1_LAYER2_SPACE
        r'(\w+)\s+to\s+(\w+)',     # "LAYER1 to LAYER2"
        r'(\w+)\s+and\s+(\w+)',    # "LAYER1 and LAYER2"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, rule_name, re.IGNORECASE)
        if match:
            return match.group(2)
    
    return None
```

## 📊 Data Structures

### Core Data Classes

```python
@dataclass
class Layer:
    """Represents a layer definition"""
    name: str                    # Layer identifier
    gds_number: Optional[int]    # GDS layer number (primary)
    expression: Optional[str]    # Boolean expression (derived)
    line_number: int = 0         # Source line number

@dataclass  
class DRCRule:
    """Represents a DRC rule"""
    name: str                   # Rule identifier
    description: str            # Human-readable description
    rule_type: str             # Rule category
    layer: str                 # Primary layer
    operator: str              # Comparison operator
    value: float               # Constraint value
    line_number: int           # Source line number
    extra_params: List[str]    # Additional parameters

@dataclass
class ICVRule:
    """Represents translated ICV rule"""
    name: str                  # Rule identifier
    description: str           # Description
    layer: str                # Primary layer
    operation: str            # Operation type
    constraint: str           # Constraint specification
    value: float              # Constraint value
    icv_syntax: str           # Generated ICV syntax
    line_number: int = 0      # Source line number
```

### Internal State Management

```python
class SVRFParser:
    def __init__(self):
        self.layers: List[Layer] = []           # Parsed layers
        self.rules: List[DRCRule] = []          # Parsed rules
        self.includes: List[str] = []           # Include files
        self.errors: List[str] = []             # Parse errors
        self.warnings: List[str] = []           # Warnings
        
        # Parse statistics
        self.line_count = 0
        self.rule_count = 0
        self.layer_count = 0
```

## 🗺 Rule Type Mappings

### Complete Mapping Table

| SVRF Rule Type | SVRF Syntax Example | ICV Function | ICV Syntax Example |
|----------------|---------------------|--------------|-------------------|
| INTERNAL1 | `INTERNAL1 M1 < 0.25` | width() | `width(M1) < 0.25` |
| INTERNAL2 | `INTERNAL2 GATE < 0.18` | length() | `length(GATE) < 0.18` |
| EXTERNAL1 | `EXTERNAL1 M1 < 0.25` | space() | `space(M1) < 0.25` |
| EXTERNAL | `EXTERNAL M1 POLY < 0.15` | space() | `space(M1, POLY) < 0.15` |
| AREA | `AREA M1 < 0.1` | area() | `area(M1) < 0.1` |
| DENSITY | `DENSITY M1 WINDOW 100 100 > 0.7` | density() | `density(M1, 100, 100) > 0.7` |
| Enclosure | `VIA NOT INSIDE M1 BY == 0.05` | enclosure() | `enclosure(M1, VIA) >= 0.05` |

### Layer Expression Mappings

| SVRF Operator | ICV Operator | Example |
|---------------|--------------|---------|
| AND | & | `POLY & ACTIVE` |
| OR | \| | `M1 \| M2 \| M3` |
| NOT | ! | `! NWELL` |

### Operator Translations

| SVRF Constraint | ICV Constraint | Notes |
|-----------------|----------------|-------|
| `< value` | `< value` | Direct mapping |
| `> value` | `> value` | Direct mapping |
| `== value` | `>= value` | Enclosure rules (minimum) |
| `NOT INSIDE BY ==` | `>= value` | Converted to enclosure |

## ⚠️ Error Handling

### Error Categories

1. **Syntax Errors**: Malformed SVRF syntax
2. **Semantic Errors**: Valid syntax, invalid meaning
3. **Translation Errors**: Unsupported constructs
4. **I/O Errors**: File access issues

### Error Collection Strategy

```python
class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def add_error(self, message, line_number=None):
        error = f"Line {line_number}: {message}" if line_number else message
        self.errors.append(error)
        
    def add_warning(self, message, line_number=None):
        warning = f"Line {line_number}: {message}" if line_number else message
        self.warnings.append(warning)
```

### Graceful Degradation

- **Parser**: Continue on non-critical errors
- **Translator**: Skip unsupported rules, warn user  
- **Output**: Generate partial results when possible

### Validation Checks

```python
def validate_rule(self, rule: DRCRule) -> List[str]:
    """Validate rule for common issues"""
    issues = []
    
    # Check for negative values
    if rule.value < 0:
        issues.append(f"Negative constraint value: {rule.value}")
    
    # Check for unrealistic values  
    if rule.rule_type in ['internal1', 'external1'] and rule.value > 100:
        issues.append(f"Unusually large constraint: {rule.value}")
    
    # Check layer references
    if rule.layer not in self.known_layers:
        issues.append(f"Unknown layer reference: {rule.layer}")
        
    return issues
```

## 🚀 Performance Analysis

### Time Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| File Parsing | O(n) | O(m) |
| Rule Translation | O(r) | O(r) |
| Layer Processing | O(l) | O(l) |
| Output Generation | O(r + l) | O(1) |

Where:
- n = number of lines in input file
- r = number of rules
- l = number of layers  
- m = size of parsed data structures

### Performance Bottlenecks

1. **Regex Compilation**: Pre-compile patterns for better performance
2. **File I/O**: Use buffered I/O for large files
3. **String Operations**: Minimize string concatenation in loops
4. **Memory Allocation**: Reuse objects where possible

### Optimization Strategies

```python
# Pre-compile regex patterns
class PatternCache:
    def __init__(self):
        self.patterns = {}
        
    def get_pattern(self, pattern_str):
        if pattern_str not in self.patterns:
            self.patterns[pattern_str] = re.compile(pattern_str)
        return self.patterns[pattern_str]

# Use generators for large datasets
def parse_rules_lazy(self, lines):
    """Generator-based parsing for memory efficiency"""
    for i, line in enumerate(lines):
        if self.is_rule_line(line):
            yield self.parse_single_rule(line, i)
```

### Memory Usage Patterns

```
Parse Phase:  ████████░░░░░░░░░░░░  40%
Translate:    ████████████░░░░░░░░  60%
Output:       ████████████████░░░░  80%
Complete:     ████████████████████ 100%
```

Typical memory usage:
- Small files (< 1MB): 10-50 MB
- Medium files (1-10MB): 50-200 MB  
- Large files (> 10MB): 200-500 MB

## 🔧 Extension Points

### Adding New Rule Types

1. **Update Pattern Recognition**:
```python
# Add to RULE_PATTERNS in extract_rule_details()
RULE_PATTERNS.append(
    (r'(NEW_RULE_TYPE)\s+(\w+)\s*(<|>|==)\s*([\d.]+)', 'new_category')
)
```

2. **Add Translation Function**:
```python  
def translate_new_rule_type(self, rule: DRCRule) -> ICVRule:
    icv_syntax = f"new_function({rule.layer}) {rule.operator} {rule.value}"
    return ICVRule(...)
```

3. **Register in Mapping Table**:
```python
self.rule_mappings['new_rule_type'] = self.translate_new_rule_type
```

### Custom Output Formats

```python
class CustomTranslator(SVRFToICVTranslator):
    def write_custom_format(self, output_file):
        """Write in custom format"""
        with open(output_file, 'w') as f:
            f.write("# Custom Format\n")
            for rule in self.icv_rules:
                f.write(f"RULE {rule.name}: {rule.icv_syntax}\n")
```

### Plugin Architecture

```python
class PluginManager:
    def __init__(self):
        self.plugins = []
        
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
        
    def process_rule(self, rule):
        for plugin in self.plugins:
            rule = plugin.transform_rule(rule)
        return rule
```

### Analysis Extensions

```python
class CustomAnalyzer(SVRFAnalyzer):
    def find_technology_specific_issues(self):
        """Add technology-specific analysis"""
        issues = []
        
        # Check for technology-specific patterns
        for rule in self.result.rules:
            if self.is_problematic_for_tech(rule):
                issues.append(f"Tech issue in {rule.name}")
                
        return issues
```

### Configuration System

```python
@dataclass
class TranslatorConfig:
    technology: str = "Generic"
    process_node: str = "180nm"
    output_format: str = "icv"
    include_comments: bool = True
    group_rules: bool = True
    validate_output: bool = False
    
    @classmethod
    def from_file(cls, config_file: str):
        """Load configuration from file"""
        import json
        with open(config_file, 'r') as f:
            data = json.load(f)
        return cls(**data)
```

## 🔬 Testing Strategy

### Unit Testing

```python
import unittest

class TestSVRFParser(unittest.TestCase):
    def test_basic_parsing(self):
        parser = SVRFParser()
        test_lines = [
            "LAYER M1 100",
            "M1_WIDTH { @ \"test\"",
            "    INTERNAL1 M1 < 0.25",
            "}"
        ]
        parser.parse_lines(test_lines)
        
        self.assertEqual(len(parser.layers), 1)
        self.assertEqual(len(parser.rules), 1)
        self.assertEqual(parser.rules[0].value, 0.25)
```

### Integration Testing

```python
def test_full_translation():
    """Test complete SVRF to ICV translation"""
    translator = SVRFToICVTranslator()
    success = translator.translate_file("test_input.svrf", "test_output.icv")
    
    assert success
    assert len(translator.icv_rules) > 0
    
    # Validate output file
    with open("test_output.icv", 'r') as f:
        content = f.read()
        assert "rule " in content
        assert "width(" in content
```

### Performance Testing

```python
import time
import memory_profiler

@memory_profiler.profile
def benchmark_parsing(file_size):
    """Benchmark parsing performance"""
    start_time = time.time()
    
    parser = SVRFParser()
    parser.parse_file(f"test_{file_size}.svrf")
    
    end_time = time.time()
    return end_time - start_time
```

This technical reference provides the deep implementation details needed to understand, modify, and extend the SVRF DRC parser and ICV translator system.