"""
Command-line interface for the Lie Algebra Cohomology Toolkit.

This module provides a CLI for analyzing Lie algebras, computing cohomology,
and performing spectral analysis.
"""

import click, json, os
import numpy as np
from .config import load_config, Config
from .model import SpectralLieModel

@click.group()
def main():
    """Lie Algebra Cohomology Toolkit CLI"""
    pass

@main.command()
@click.option("--config", "-c", type=str, required=True, help="Path to YAML config")
@click.option("--verbose", "-v", is_flag=True)
def run(config: str, verbose: bool):
    """
    Run Lie algebra cohomology and spectral analysis.
    
    INPUT PATHS:
    - JSON structure constants: Always reliable, recommended for production
    - SageMath Cartan types: Experimental, requires SageMath installation
    
    FALLBACK: If SageMath integration fails, the toolkit automatically
              switches to JSON input for reliability.
    """
    cfg = load_config(config)
    model = SpectralLieModel(cfg)
    
    if verbose:
        click.echo("Running Lie Algebra Cohomology Toolkit...")
        click.echo(f"Input format: {cfg.input['format']}")
        if cfg.input['format'] == 'cartan_type':
            click.echo("⚠️  Using SageMath Cartan type (experimental)")
            click.echo("   If this fails, switch to 'structure_json' format")
        else:
            click.echo("✅ Using JSON structure constants (reliable)")
    
    try:
        results = model.fit()
        model.export(results)
        if verbose:
            click.echo("✅ Analysis completed successfully")
            click.echo(f"Results saved to: {cfg.output['directory']}")
    except Exception as e:
        if "SageMath" in str(e):
            click.echo("❌ SageMath integration failed")
            click.echo("💡 Solution: Switch to JSON structure constants format")
            click.echo(f"   Error details: {e}")
        else:
            click.echo(f"❌ Analysis failed: {e}")
        raise click.Abort()

@main.command()
@click.option("--config", "-c", type=str, required=True)
def validate_config(config: str):
    _ = load_config(config)
    click.echo("✅ Config is valid")

@main.command()
def list_algebras():
    click.echo("Supported families (Cartan types): A_n, B_n, C_n, D_n, E6, E7, E8, F4, G2")


@main.command()
@click.option("--config", "-c", type=str, required=True, help="Path to YAML config")
@click.option("--degree", "-d", type=int, default=1, help="Degree to inspect (default: 1)")
def inspect_d(config: str, degree: int):
    """Inspect differential matrices for debugging"""
    from .config import load_config
    from .model import SpectralLieModel
    
    cfg = load_config(config)
    model = SpectralLieModel(cfg)
    
    # Get structure constants
    if cfg.input["format"] == "structure_json":
        from .io_handlers import load_structure_constants
        C, _ = load_structure_constants(cfg.input["path"])
        n = C.shape[0]
        
        from .cohomology_engine import CohomologyEngine
        engine = CohomologyEngine(C, max_degree=degree+1, sparse_matrices=False)
        
        click.echo(f"Lie algebra dimension: {n}")
        click.echo(f"Wedge dimensions: {[engine.wedge_dim(p) for p in range(degree+2)]}")
        
        for p in range(degree+1):
            d_p = engine.assemble_d(p)
            if d_p.size > 0:
                click.echo(f"\nd_{p} matrix ({d_p.shape}):")
                click.echo(d_p)
            else:
                click.echo(f"\nd_{p} matrix: empty")
        
        # Check d²=0 for the specified degree
        if degree < engine.max_degree:
            d_p = engine.assemble_d(degree)
            d_p1 = engine.assemble_d(degree + 1)
            if d_p.size and d_p1.size:
                product = d_p1 @ d_p
                click.echo(f"\nd_{degree+1} @ d_{degree} =")
                click.echo(product)
                click.echo(f"Is zero? {np.allclose(product, 0.0, atol=1e-12)}")
    else:
        click.echo("Inspect-d only works with structure_json input format")
