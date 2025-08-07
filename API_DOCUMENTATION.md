# SVRF DRC Tools - API Documentation

## 📋 Table of Contents

- [SVRFParser Class](#svrfparser-class)
- [SVRFAnalyzer Class](#svrfanalyzer-class) 
- [SVRFToICVTranslator Class](#svrftoicvtranslator-class)
- [Data Classes](#data-classes)
- [Utility Functions](#utility-functions)
- [Error Handling](#error-handling)
- [Examples](#examples)

## 📖 SVRFParser Class

**File**: `simple_svrf_parser.py`

### Constructor

```python
class SVRFParser:
    def __init__(self):
        """Initialize SVRF parser with empty state"""
```

**Attributes**:
- `layers: List[Layer]` - Parsed layer definitions
- `rules: List[DRCRule]` - Parsed DRC rules
- `includes: List[str]` - Include file paths
- `errors: List[str]` - Parse errors

### Methods

#### parse_file()
```python
def parse_file(self, filename: str) -> None:
    """
    Parse SVRF file from disk
    
    Args:
        filename: Path to SVRF file
        
    Raises:
        FileNotFoundError: If file doesn't exist
        
    Example:
        parser = SVRFParser()
        parser.parse_file("rules.svrf")
    """
```

#### parse_lines()
```python
def parse_lines(self, lines: List[str]) -> None:
    """
    Parse SVRF content from list of lines
    
    Args:
        lines: List of SVRF file lines
        
    Example:
        lines = ["LAYER M1 100", "M1_WIDTH { @ \"test\"", "    INTERNAL1 M1 < 0.25", "}"]
        parser.parse_lines(lines)
    """
```

#### get_statistics()
```python  
def get_statistics(self) -> Dict[str, Any]:
    """
    Get parsing statistics
    
    Returns:
        Dict containing:
        - layers: Total layer count
        - layer_types: Dict of layer type counts
        - rules: Total rule count  
        - rule_types: Dict of rule type counts
        - includes: Include file count
        - errors: Error count
        
    Example:
        stats = parser.get_statistics()
        print(f"Total rules: {stats['rules']}")
    """
```

#### print_results()
```python
def print_results(self) -> None:
    """Print parsing summary to stdout"""
```

#### print_layers()
```python
def print_layers(self) -> None:
    """Print layer information to stdout"""
```

#### print_rules()
```python
def print_rules(self, rule_filter: Optional[str] = None) -> None:
    """
    Print rule information to stdout
    
    Args:
        rule_filter: Optional filter by rule type (e.g., "spacing", "width")
    """
```

### Private Methods

#### parse_include()
```python
def parse_include(self, line: str, line_num: int) -> None:
    """Parse INCLUDE statement"""
```

#### parse_layer_definition()
```python
def parse_layer_definition(self, line: str, line_num: int) -> None:
    """Parse LAYER definition"""
```

#### parse_derived_layer()
```python
def parse_derived_layer(self, line: str, line_num: int) -> None:
    """Parse derived layer assignment"""
```

#### parse_drc_rule()
```python
def parse_drc_rule(self, lines: List[str], start_idx: int, line_num: int) -> int:
    """
    Parse DRC rule block
    
    Returns:
        Last processed line index
    """
```

#### extract_rule_details()
```python
def extract_rule_details(self, rule_name: str, content: str, line_num: int) -> None:
    """Extract rule details from rule content"""
```

## 🔬 SVRFAnalyzer Class

**File**: `simple_svrf_parser.py`

### Constructor

```python
class SVRFAnalyzer:
    def __init__(self, parser: SVRFParser):
        """
        Initialize analyzer with parsed data
        
        Args:
            parser: SVRFParser instance with parsed data
        """
```

### Methods

#### get_layer_stats()
```python
def get_layer_stats(self) -> Dict[str, Any]:
    """
    Get layer statistics
    
    Returns:
        Dict containing:
        - total_layers: Total number of layers
        - primary_layers: Count of primary layers
        - derived_layers: Count of derived layers  
        - layer_names: List of all layer names
    """
```

#### get_rule_stats()
```python
def get_rule_stats(self) -> Dict[str, Any]:
    """
    Get rule statistics
    
    Returns:
        Dict containing:
        - total_rules: Total number of rules
        - rule_types: Dict of rule type counts
        - layers_with_rules: Count of layers that have rules
        - covered_layers: List of layer names with rules
    """
```

#### get_spacing_rules()
```python
def get_spacing_rules(self) -> List[DRCRule]:
    """
    Get all spacing-related rules
    
    Returns:
        List of DRCRule objects for spacing checks
    """
```

#### get_width_rules()
```python
def get_width_rules(self) -> List[DRCRule]:
    """
    Get all width-related rules
    
    Returns:
        List of DRCRule objects for width checks
    """
```

#### find_potential_issues()
```python
def find_potential_issues(self) -> List[str]:
    """
    Identify potential issues in the ruleset
    
    Returns:
        List of issue descriptions
        
    Checks for:
        - Layers without rules
        - Very restrictive rules
        - Unusual constraint values
    """
```

## 🔄 SVRFToICVTranslator Class

**File**: `svrf_to_icv_translator.py`

### Constructor

```python
class SVRFToICVTranslator:
    def __init__(self):
        """Initialize SVRF to ICV translator"""
```

**Attributes**:
- `svrf_parser: SVRFParser` - Internal SVRF parser
- `icv_rules: List[ICVRule]` - Translated ICV rules
- `icv_layers: List[str]` - Translated layer definitions
- `technology: str` - Technology name (default: "Generic")
- `process_node: str` - Process node (default: "180nm")

### Methods

#### translate_file()
```python
def translate_file(self, svrf_file: str, output_file: str = None) -> bool:
    """
    Translate SVRF file to ICV format
    
    Args:
        svrf_file: Input SVRF file path
        output_file: Output ICV file path (optional)
        
    Returns:
        True if translation successful, False otherwise
        
    Example:
        translator = SVRFToICVTranslator()
        success = translator.translate_file("input.svrf", "output.icv")
    """
```

#### translate_layers()
```python
def translate_layers(self) -> None:
    """Translate SVRF layer definitions to ICV format"""
```

#### translate_rules()
```python  
def translate_rules(self) -> None:
    """Translate SVRF rules to ICV format"""
```

#### write_icv_file()
```python
def write_icv_file(self, output_file: str) -> None:
    """
    Write translated rules to ICV format file
    
    Args:
        output_file: Output file path
    """
```

#### print_translation_summary()
```python
def print_translation_summary(self) -> None:
    """Print translation statistics to stdout"""
```

#### print_icv_rules()
```python
def print_icv_rules(self, limit: int = 10) -> None:
    """
    Print sample ICV rules to stdout
    
    Args:
        limit: Maximum number of rules to display
    """
```

### Rule Translation Methods

#### translate_internal1()
```python
def translate_internal1(self, rule: DRCRule) -> ICVRule:
    """
    Translate INTERNAL1 (width) rules
    
    Args:
        rule: SVRF DRC rule
        
    Returns:
        Translated ICV rule
        
    Translation:
        INTERNAL1 M1 < 0.25 → width(M1) < 0.25
    """
```

#### translate_external1()
```python
def translate_external1(self, rule: DRCRule) -> ICVRule:
    """
    Translate EXTERNAL1 (spacing) rules
    
    Translation:
        EXTERNAL1 M1 < 0.25 → space(M1) < 0.25
    """
```

#### translate_area()
```python
def translate_area(self, rule: DRCRule) -> ICVRule:
    """
    Translate AREA rules
    
    Translation:
        AREA M1 < 0.1 → area(M1) < 0.1
    """
```

#### translate_enclosure()
```python
def translate_enclosure(self, rule: DRCRule) -> ICVRule:
    """
    Translate enclosure rules
    
    Translation:
        VIA NOT INSIDE M1 BY == 0.05 → enclosure(M1, VIA) >= 0.05
    """
```

#### translate_density()
```python
def translate_density(self, rule: DRCRule) -> ICVRule:
    """
    Translate DENSITY rules
    
    Translation:
        DENSITY M1 WINDOW 100 100 > 0.7 → density(M1, 100, 100) > 0.7
    """
```

### Utility Methods

#### translate_layer_expression()
```python
def translate_layer_expression(self, expression: str) -> str:
    """
    Translate SVRF layer expressions to ICV format
    
    Args:
        expression: SVRF boolean expression
        
    Returns:
        ICV boolean expression
        
    Translations:
        AND → &
        OR → |  
        NOT → !
    """
```

#### extract_second_layer()
```python
def extract_second_layer(self, rule_name: str, description: str) -> Optional[str]:
    """
    Extract second layer name from inter-layer spacing rules
    
    Args:
        rule_name: Rule identifier
        description: Rule description
        
    Returns:
        Second layer name if found, None otherwise
    """
```

#### extract_enclosing_layer()
```python
def extract_enclosing_layer(self, rule_name: str, description: str) -> Optional[str]:
    """
    Extract enclosing layer name from enclosure rules
    
    Args:
        rule_name: Rule identifier  
        description: Rule description
        
    Returns:
        Enclosing layer name if found, None otherwise
    """
```

## 📊 Data Classes

### Layer
```python
@dataclass
class Layer:
    """Represents a layer definition"""
    name: str                    # Layer identifier
    gds_number: Optional[int]    # GDS layer number (for primary layers)
    expression: Optional[str]    # Boolean expression (for derived layers)
    line_number: int = 0         # Source line number
    
    def is_primary(self) -> bool:
        """Check if this is a primary layer"""
        return self.gds_number is not None
        
    def is_derived(self) -> bool:
        """Check if this is a derived layer"""
        return self.expression is not None
```

### DRCRule
```python
@dataclass  
class DRCRule:
    """Represents a DRC rule"""
    name: str                   # Rule identifier
    description: str            # Human-readable description
    rule_type: str             # Rule category (internal1, external1, etc.)
    layer: str                 # Primary layer name
    operator: str              # Comparison operator (<, >, ==)
    value: float               # Constraint value
    line_number: int = 0       # Source line number  
    extra_params: List[str] = None  # Additional parameters
    
    def is_width_rule(self) -> bool:
        """Check if this is a width rule"""
        return self.rule_type in ['internal1', 'internal2']
        
    def is_spacing_rule(self) -> bool:
        """Check if this is a spacing rule"""
        return self.rule_type in ['external1', 'external']
        
    def is_restrictive(self, threshold: float = 0.1) -> bool:
        """Check if rule has very tight constraints"""
        return self.value < threshold and self.operator == '<'
```

### ICVRule
```python
@dataclass
class ICVRule:
    """Represents translated ICV rule"""
    name: str                  # Rule identifier
    description: str           # Rule description
    layer: str                # Primary layer
    operation: str            # Operation type (width check, spacing check, etc.)
    constraint: str           # Constraint specification
    value: float              # Constraint value
    icv_syntax: str           # Generated ICV syntax
    line_number: int = 0      # Source line number
    
    def get_icv_rule_block(self) -> str:
        """Generate complete ICV rule block"""
        return f"""rule {self.name.lower()} {{
    check_rule = {self.icv_syntax};
    error_message = "{self.description}";
}}"""
```

## 🛠 Utility Functions

### Command Line Parsers

#### create_parser_args()
```python
def create_parser_args() -> argparse.ArgumentParser:
    """Create argument parser for SVRF parser"""
```

#### create_translator_args()
```python
def create_translator_args() -> argparse.ArgumentParser:
    """Create argument parser for SVRF to ICV translator"""
```

### File Operations

#### validate_svrf_file()
```python
def validate_svrf_file(filename: str) -> List[str]:
    """
    Validate SVRF file for common issues
    
    Args:
        filename: SVRF file path
        
    Returns:
        List of validation issues found
    """
```

#### backup_file()
```python
def backup_file(filename: str) -> str:
    """
    Create backup of file before modification
    
    Args:
        filename: Original file path
        
    Returns:
        Backup file path
    """
```

## ⚠️ Error Handling

### Exception Classes

#### SVRFParseError
```python
class SVRFParseError(Exception):
    """Raised when SVRF parsing fails"""
    def __init__(self, message: str, line_number: int = None):
        self.message = message
        self.line_number = line_number
        super().__init__(f"Line {line_number}: {message}" if line_number else message)
```

#### ICVTranslationError
```python
class ICVTranslationError(Exception):
    """Raised when ICV translation fails"""
    def __init__(self, message: str, rule_name: str = None):
        self.message = message
        self.rule_name = rule_name
        super().__init__(f"Rule {rule_name}: {message}" if rule_name else message)
```

### Error Handling Patterns

#### Try-Catch with Graceful Degradation
```python
try:
    parser.parse_file("rules.svrf")
except SVRFParseError as e:
    print(f"Parse error: {e}")
    # Continue with partial results
    if len(parser.rules) > 0:
        print(f"Partially parsed {len(parser.rules)} rules")
```

#### Validation with Error Collection
```python
def validate_and_parse(filename):
    errors = []
    warnings = []
    
    # Pre-validation
    if not Path(filename).exists():
        errors.append(f"File not found: {filename}")
        return None, errors, warnings
    
    # Parse with error collection
    parser = SVRFParser()
    try:
        parser.parse_file(filename)
        errors.extend(parser.errors)
    except Exception as e:
        errors.append(str(e))
    
    return parser, errors, warnings
```

## 📝 Examples

### Basic Parsing Example
```python
from simple_svrf_parser import SVRFParser

# Parse SVRF file
parser = SVRFParser()
parser.parse_file("example_rules.svrf")

# Check results
if parser.errors:
    print("Parse errors:")
    for error in parser.errors:
        print(f"  {error}")
else:
    print(f"Successfully parsed {len(parser.rules)} rules")

# Print statistics
stats = parser.get_statistics()
print(f"Layers: {stats['layers']}")
print(f"Rules: {stats['rules']}")
```

### Advanced Analysis Example
```python
from simple_svrf_parser import SVRFParser, SVRFAnalyzer

# Parse and analyze
parser = SVRFParser()
parser.parse_file("complex_rules.svrf")

analyzer = SVRFAnalyzer(parser)

# Get detailed statistics
layer_stats = analyzer.get_layer_stats()
rule_stats = analyzer.get_rule_stats()

print(f"Total layers: {layer_stats['total_layers']}")
print(f"Primary layers: {layer_stats['primary_layers']}")
print(f"Derived layers: {layer_stats['derived_layers']}")

# Find issues
issues = analyzer.find_potential_issues()
if issues:
    print("Potential issues found:")
    for issue in issues:
        print(f"  - {issue}")

# Get specific rule types
spacing_rules = analyzer.get_spacing_rules()
width_rules = analyzer.get_width_rules()

print(f"Spacing rules: {len(spacing_rules)}")
print(f"Width rules: {len(width_rules)}")
```

### Translation Example
```python
from svrf_to_icv_translator import SVRFToICVTranslator

# Create translator with custom settings
translator = SVRFToICVTranslator()
translator.technology = "TSMC 28nm"
translator.process_node = "28nm"

# Translate file
success = translator.translate_file("input.svrf", "output.icv")

if success:
    # Print translation summary
    translator.print_translation_summary()
    
    # Show sample translations
    translator.print_icv_rules(5)
    
    print(f"Translation completed: output.icv")
else:
    print("Translation failed")
```

### Custom Processing Example
```python
from simple_svrf_parser import SVRFParser
from svrf_to_icv_translator import SVRFToICVTranslator

def process_multiple_technologies(file_mappings):
    """Process multiple SVRF files for different technologies"""
    results = []
    
    for svrf_file, tech_info in file_mappings.items():
        # Parse SVRF
        parser = SVRFParser()
        parser.parse_file(svrf_file)
        
        # Create custom translator
        translator = SVRFToICVTranslator()
        translator.technology = tech_info['technology']
        translator.process_node = tech_info['process_node']
        
        # Translate
        icv_file = f"{tech_info['technology'].replace(' ', '_')}.icv"
        success = translator.translate_file(svrf_file, icv_file)
        
        results.append({
            'svrf_file': svrf_file,
            'icv_file': icv_file,
            'technology': tech_info['technology'],
            'success': success,
            'rule_count': len(translator.icv_rules),
            'layer_count': len(translator.icv_layers)
        })
    
    return results

# Usage
file_mappings = {
    'tsmc28.svrf': {'technology': 'TSMC 28nm', 'process_node': '28nm'},
    'tsmc40.svrf': {'technology': 'TSMC 40nm', 'process_node': '40nm'},
}

results = process_multiple_technologies(file_mappings)
for result in results:
    print(f"{result['technology']}: {result['rule_count']} rules translated")
```

This API documentation provides comprehensive reference for all public interfaces and usage patterns in the SVRF DRC parser and ICV translator suite.