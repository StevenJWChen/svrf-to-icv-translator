# SVRF DRC Tools - Quick Reference

## 🚀 Quick Commands

### Parse SVRF Rules
```bash
# Basic parsing
python simple_svrf_parser.py rules.svrf

# With full analysis
python simple_svrf_parser.py rules.svrf --analyze --stats --layers --rules

# Filter by rule type
python simple_svrf_parser.py rules.svrf --rules spacing
python simple_svrf_parser.py rules.svrf --rules width
```

### Translate to ICV
```bash
# Basic translation
python svrf_to_icv_translator.py rules.svrf

# Custom output with preview
python svrf_to_icv_translator.py rules.svrf -o output.icv --summary --preview 10

# Technology-specific
python svrf_to_icv_translator.py rules.svrf --technology "TSMC 28nm" --process "28nm"
```

### Demo Scripts
```bash
# Full parser demo
python demo_parser.py

# Full translator demo  
python demo_translator.py
```

## 📊 Rule Type Support

| SVRF Rule | ICV Translation | Example |
|-----------|----------------|---------|
| `INTERNAL1 M1 < 0.25` | `width(M1) < 0.25` | Width check |
| `EXTERNAL1 M1 < 0.25` | `space(M1) < 0.25` | Spacing check |
| `AREA M1 < 0.1` | `area(M1) < 0.1` | Area check |
| `VIA NOT INSIDE M1 BY == 0.05` | `enclosure(M1, VIA) >= 0.05` | Enclosure |
| `DENSITY M1 WINDOW 100 100 > 0.7` | `density(M1, 100, 100) > 0.7` | Density |

## 🔍 Common Use Cases

### 1. Rule Analysis
```python
from simple_svrf_parser import SVRFParser

parser = SVRFParser()
parser.parse_file("rules.svrf")
parser.print_results()      # Statistics
parser.print_layers()       # Layer info
parser.print_rules()        # All rules
```

### 2. Find Specific Rules
```bash
# Find tight spacing rules
python simple_svrf_parser.py rules.svrf --rules | grep "< 0.1"

# Count rule types
python simple_svrf_parser.py rules.svrf --stats
```

### 3. Batch Translation
```bash
for file in *.svrf; do
    python svrf_to_icv_translator.py "$file" -o "${file%.svrf}.icv"
done
```

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Parser hangs | Check brace matching in SVRF |
| Translation fails | Check rule type support |
| Missing rules | Verify SVRF syntax |
| File not found | Check path and permissions |

## 📝 File Formats

### SVRF Input Structure
```svrf
// Comments
INCLUDE "file.svrf"

LAYER M1 100
DERIVED = POLY AND ACTIVE

RULE_NAME { @ "Description"
    INTERNAL1 LAYER < VALUE
}
```

### ICV Output Structure  
```icv
run_options { ... }

LAYER M1 = 100;
LAYER DERIVED = POLY & ACTIVE;

rule name {
    check_rule = width(M1) < 0.25;
    error_message = "Description";
}
```

## 🛠 Common Parameters

### Parser Options
- `--layers` - Show layer details
- `--rules` - Show rule details
- `--filter TYPE` - Filter by rule type
- `--analyze` - Detailed analysis
- `--stats` - Statistics only

### Translator Options
- `-o FILE` - Output file
- `--summary` - Translation summary
- `--preview N` - Preview N rules
- `--technology NAME` - Tech name
- `--process NODE` - Process node

## 📊 Output Examples

### Parser Statistics
```
SVRF Parsing Results:
  Layers: 13 (Primary: 9, Derived: 4)
  Rules: 28
  Includes: 2
  Errors: 0

Rule Types:
  internal1: 9    (width rules)
  external1: 8    (spacing rules)
  enclosure: 6    (enclosure rules)
  area: 1         (area rules)
  density: 1      (density rules)
```

### Translation Summary
```
SVRF to ICV Translation Summary:
  Input SVRF Rules: 28
  Translated ICV Rules: 28
  Input SVRF Layers: 13
  Translated ICV Layers: 13

Rule Type Distribution:
  width check: 9
  spacing check: 8
  enclosure check: 6
```

## 🔧 Integration Examples

### Python Integration
```python
# Parse and analyze
from simple_svrf_parser import SVRFParser, SVRFAnalyzer

parser = SVRFParser()
parser.parse_file("rules.svrf")

analyzer = SVRFAnalyzer(parser)
stats = analyzer.get_layer_stats()

# Translate
from svrf_to_icv_translator import SVRFToICVTranslator

translator = SVRFToICVTranslator()
translator.translate_file("rules.svrf", "rules.icv")
```

### Shell Integration
```bash
#!/bin/bash
# CAD flow integration

SVRF_FILE="$1"
TECH="$2"

# Parse and validate
python simple_svrf_parser.py "$SVRF_FILE" --stats > parse_log.txt
if [ $? -ne 0 ]; then
    echo "Parse failed"
    exit 1
fi

# Translate
python svrf_to_icv_translator.py "$SVRF_FILE" --technology "$TECH" --summary
```

## 🎯 Performance Tips

- **Large files**: Use `--preview` for quick validation
- **Batch processing**: Process in parallel for multiple files
- **Memory usage**: Monitor for files > 10MB
- **Speed**: Pre-filter if only specific rules needed

## 🔗 Quick Links

- [README.md](README.md) - Complete documentation
- [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) - Implementation details
- [simple_svrf_parser.py](simple_svrf_parser.py) - Parser source
- [svrf_to_icv_translator.py](svrf_to_icv_translator.py) - Translator source