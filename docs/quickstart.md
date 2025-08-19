# Quickstart Guide

## Prerequisites
- Python >= 3.9
- SageMath >= 10.0 (importable in Python) - **optional**

## Installation
```bash
pip install lie-algebra-cohomology-toolkit
```

## Basic Usage

### Run with structure constants (sl2):
```bash
lie-cohomology run -c configs/default.yaml -v
```

### Validate configuration:
```bash
lie-cohomology validate-config -c configs/default.yaml
```

### Inspect differentials:
```bash
lie-cohomology inspect-d -c configs/default.yaml -d 2
```

## Results
- `outputs/results.json` with cohomology summary and per-degree spectra
- Detailed differential matrices and spectral analysis
- Configuration validation and error reporting
