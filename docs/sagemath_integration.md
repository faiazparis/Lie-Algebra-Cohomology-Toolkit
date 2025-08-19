# SageMath Integration Guide

## ⚠️ **Important Notice**

**Status**: SageMath integration is **experimental** and under active development. While the core functionality works perfectly without SageMath, the SageMath integration path may not work in all environments.

**Recommendation**: Use the **JSON structure constants path** for production work. SageMath integration is best suited for:
- Academic research and prototyping
- Environments where SageMath is already set up
- Users comfortable with experimental features

## Overview

The Lie Algebra Cohomology Toolkit provides optional integration with SageMath for enhanced Lie algebra workflows. This integration is **completely optional** - the core functionality works perfectly without SageMath.

**Current Implementation Status:**
- ✅ **Core Toolkit**: 100% functional without SageMath
- ✅ **JSON Path**: Fully tested and reliable
- ⚠️ **SageMath Path**: Experimental, requires proper environment setup
- 🔧 **Integration**: Basic structure constants extraction implemented

## What SageMath Adds

### 🚀 Enhanced Input Methods
- **Cartan Type Construction**: `"A1"`, `"E8"`, `"G2"` instead of manual JSON
- **Automatic Validation**: SageMath guarantees Jacobi identity
- **Rich Algebraic Data**: Root systems, fundamental weights, Killing forms

### 🔧 Advanced Features
- **Root System Analysis**: Simple roots, positive roots, Weyl group data
- **Killing Form Computation**: Better metrics for semisimple algebras
- **Academic Integration**: Works with existing SageMath workflows

## Installation

### Option 1: Conda (Recommended)
```bash
conda install -c conda-forge sage
```

### Option 2: System Package
```bash
# Ubuntu/Debian
sudo apt-get install sagemath

# macOS
brew install sage

# Arch Linux
sudo pacman -S sage
```

### Option 3: Download
Download from [https://www.sagemath.org/](https://www.sagemath.org/)

## Usage

### Configuration
```yaml
# configs/examples/sage_cartan_example.yaml
input:
  format: cartan_type
  cartan_type: "A1"  # sl2(C)
```

### Python API
```python
from spectral_lie.sage_backend import SageBackend

# Check availability
sb = SageBackend()
if sb.available():
    # Use SageMath features
    sb.from_cartan("A1")
    print(f"Dimension: {sb.dimension()}")
    print(f"Semisimple: {sb.is_semisimple()}")
    
    # Get root system data
    roots = sb.root_system_data()
    print(f"Simple roots: {roots['simple_roots']}")
else:
    # Fallback to JSON
    print("SageMath not available - use structure constants JSON")
```

## Supported Cartan Types

### Classical Series
- **A_n**: sl(n+1, C) - special linear algebras
- **B_n**: so(2n+1, C) - odd orthogonal algebras  
- **C_n**: sp(2n, C) - symplectic algebras
- **D_n**: so(2n, C) - even orthogonal algebras

### Exceptional Algebras
- **E_6, E_7, E_8**: Exceptional Lie algebras
- **F_4, G_2**: Exceptional Lie algebras

## How It Works

### 1. Lazy Import
```python
try:
    import sage.all as sage
except Exception:
    sage = None
```

### 2. Structure Constants Extraction
When using Cartan types, the toolkit:
1. Constructs the Lie algebra in SageMath
2. Extracts structure constants via bracket operations
3. Converts to NumPy arrays for computation
4. Falls back to JSON path if SageMath unavailable

### 3. Enhanced Detection
- **Semisimple Detection**: Uses SageMath's built-in methods
- **Killing Form**: Computed from adjoint representation
- **Root Systems**: Full root system data available

## Troubleshooting

### Common Issues

#### "SageMath not available"
**Cause**: SageMath not installed or not in PATH
**Solution**: 
1. Install SageMath (see installation above)
2. Use JSON structure constants instead
3. Check virtual environment compatibility

#### Import Errors
**Cause**: SageMath version incompatibility
**Solution**:
1. Use recent SageMath version (≥9.0 recommended)
2. Check Python version compatibility
3. Reinstall SageMath in current environment

#### Path Issues
**Cause**: SageMath not in system PATH
**Solution**:
```bash
# Add to PATH
export PATH="/path/to/sage:$PATH"

# Or use full path
/path/to/sage/python -m spectral_lie.cli run -c config.yaml
```

### Fallback Strategy

If SageMath integration fails:
1. **Switch to JSON**: Change config to `format: structure_json`
2. **Manual Input**: Provide structure constants manually
3. **Core Functionality**: All mathematical features still work

## Performance Considerations

### SageMath Overhead
- **Startup Time**: SageMath adds 1-5 seconds to import
- **Memory Usage**: Additional 50-200MB depending on SageMath version
- **Computation**: Structure constants extraction is O(n³) but only done once

### When to Use SageMath
- **✅ Academic Research**: Rich algebraic data needed
- **✅ Prototyping**: Quick exploration of different algebras
- **✅ Teaching**: Visual and interactive algebra construction
- **❌ Production**: High-performance, repeated computations
- **❌ Minimal Setup**: Environments where SageMath is unavailable

## Examples

### Complete SageMath Workflow
```python
from spectral_lie.sage_backend import SageBackend
from spectral_lie.model import SpectralLieModel
from spectral_lie.config import load_config

# Load SageMath-enhanced config
config = load_config('configs/examples/sage_cartan_example.yaml')

# Create model (will use SageMath if available)
model = SpectralLieModel(config)

# Run analysis
results = model.fit()

# Export results
model.export(results)
```

### Mixed Approach
```python
# Use SageMath for construction, JSON for computation
sb = SageBackend()
if sb.available():
    # Get structure constants from SageMath
    sb.from_cartan("A1")
    C, basis = sb.extract_structure_constants()
    
    # Save to JSON for future use
    save_structure_constants("sl2_from_sage.json", C, basis)
else:
    # Fallback to JSON
    C, basis = load_structure_constants("sl2_structure.json")
```

## Integration with Core Toolkit

### Seamless Fallback
The SageMath integration is designed to:
1. **Enhance** when available
2. **Fallback gracefully** when not available
3. **Maintain compatibility** with all existing features
4. **Provide clear error messages** for troubleshooting

### Configuration Priority
1. **SageMath Cartan Type** (if available and requested)
2. **JSON Structure Constants** (fallback, always works)
3. **Error with helpful message** (if both fail)

## Future Enhancements

### Planned Features
- **More Cartan Types**: Extended Dynkin diagrams
- **Representation Theory**: Character computations
- **Cohomology with Coefficients**: Module coefficients
- **Symbolic Computation**: Exact arithmetic support

### Community Contributions
We welcome contributions to enhance SageMath integration:
- Additional Cartan type support
- Performance optimizations
- Extended algebraic data
- Better error handling

---

*SageMath integration enhances the toolkit but is never required for core functionality.*
