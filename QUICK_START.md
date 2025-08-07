# SVRF to ICV Translator - Quick Start Guide

Get up and running with the SVRF to ICV translator in minutes.

## ⚡ 30-Second Setup

```bash
# 1. Clone the repository
git clone https://github.com/StevenJWChen/svrf-to-icv-translator.git
cd svrf-to-icv-translator

# 2. Run the translator (no dependencies needed for core functionality)
python3 final_enhanced_translator.py test_comprehensive.svrf

# 3. Check the output
ls *.icv
```

## 🎯 Basic Usage

### Translate Your First SVRF File
```bash
# Translate simple rules
python3 final_enhanced_translator.py example_drc_rules.svrf

# Translate complex foundry rules
python3 final_enhanced_translator.py complex_drc_rules.svrf

# Check translation results
cat test_comprehensive.icv
```

### Expected Output
```
Final Enhanced SVRF to ICV Translation
Input: test_comprehensive.svrf
Output: test_comprehensive.icv
==================================================
Final Enhanced SVRF to ICV Translation:
  Input Layers: 10
  Input Rules: 13
  Translated Rules: 13
  Coverage: 100.0%
  Parse Errors: 0

🎯 SUCCESS: 100.0% coverage achieved!
✅ Near 100% translation coverage
```

## 📁 Key Files

### Core Translator
- `final_enhanced_translator.py` - Main translator (100% coverage)
- `enhanced_svrf_parser.py` - Advanced SVRF parser

### Test Files
- `test_comprehensive.svrf` - Clean test cases (13 rules)
- `complex_drc_rules.svrf` - Real foundry file (77 rules)
- `example_drc_rules.svrf` - Simple examples

### Generated Outputs
- `*.icv` - ICV format output files
- Production-ready for IC Validator

## 🚀 Common Commands

```bash
# Test with different files
python3 final_enhanced_translator.py example_drc_rules.svrf
python3 final_enhanced_translator.py complex_drc_rules.svrf

# Check project statistics
./push_to_github.sh

# View documentation
cat README.md
cat TECHNICAL_REFERENCE.md
```

## ✅ Verify Installation

Run this test to verify everything works:

```bash
python3 -c "
from final_enhanced_translator import FinalEnhancedTranslator
print('✅ Translator imported successfully')

translator = FinalEnhancedTranslator()
translator.parse_file('test_comprehensive.svrf')
print(f'✅ Parsed {len(translator.rules)} rules')

translator.translate_to_icv()
print(f'✅ Translated {len(translator.icv_rules)} rules')
print('🎯 All systems ready!')
"
```

Expected output:
```
✅ Translator imported successfully
✅ Parsed 13 rules
✅ Translated 13 rules
🎯 All systems ready!
```

## 🎓 Next Steps

1. **Read the docs**: `cat README.md`
2. **Try complex files**: Use `complex_drc_rules.svrf`
3. **Check output**: Examine generated `.icv` files
4. **Explore features**: See `TECHNICAL_REFERENCE.md`

## ⚡ Troubleshooting

### Issue: "No such file or directory"
**Solution**: Make sure you're in the project directory
```bash
cd svrf-to-icv-translator
ls *.py
```

### Issue: "Import error" 
**Solution**: The translator uses only Python standard library
```bash
python3 --version  # Should be 3.6+
```

### Issue: "No output generated"
**Solution**: Check if input file exists
```bash
ls *.svrf
python3 final_enhanced_translator.py --help
```

## 🎉 Success Indicators

You'll know it's working when you see:
- ✅ "100.0% coverage achieved!"
- ✅ Generated `.icv` files
- ✅ Zero parsing errors
- ✅ All rule types supported

Ready to use in production semiconductor design verification workflows!