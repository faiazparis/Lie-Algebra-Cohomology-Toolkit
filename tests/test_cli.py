import os, json, tempfile, shutil
from spectral_lie.config import load_config
from spectral_lie.model import SpectralLieModel

def test_cli_like_run_tmpdir():
    tmp = tempfile.mkdtemp()
    try:
        cfg_dict = {
            "input": {
                "format": "structure_json",
                "path": "configs/examples/sl2_structure.json",
                "cartan_type": "",
                "validate_jacobi": True
            },
            "cohomology": {
                "max_degree": 2,
                "trivial_coefficients": True,
                "compute_betti": True,
                "sparse_matrices": False
            },
            "spectral": {
                "compute_eigenvalues": True,
                "compute_eigenvectors": False,
                "laplacian_type": "hodge",
                "precision": 53
            },
            "physics": {
                "analyze_symmetries": True,
                "gauge_theory_invariants": False,
                "export_characteristic_classes": False
            },
            "output": {
                "directory": tmp,
                "save_matrices": True,
                "save_spectrum": True,
                "save_cohomology": True,
                "export_sage_objects": False,
                "format": "json"
            },
            "seed": 42
        }
        # Direct object config instead of file for the test
        class SimpleCfg: pass
        cfg = SimpleCfg()
        cfg.__dict__.update(cfg_dict)
        model = SpectralLieModel(cfg)
        results = model.fit()
        model.export(results)
        assert os.path.exists(os.path.join(tmp, "results.json"))
        data = json.load(open(os.path.join(tmp, "results.json")))
        assert "cohomology" in data and "spectral_analysis" in data
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
