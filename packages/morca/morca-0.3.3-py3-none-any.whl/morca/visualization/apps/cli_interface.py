def orbitals_app():
    """Entry point to run the orbitals marimo app."""
    import subprocess
    import sys
    from pathlib import Path

    # Get the path to the orbitals.py file
    orbitals_path = Path(__file__).parent / "orbitals.py"

    try:
        subprocess.run(
            [sys.executable, "-m", "marimo", "run", orbitals_path, sys.argv[-1]]
        )
    except KeyboardInterrupt:
        # This is needed because we terminate the marimo process
        # with a keyboard interrupt, which also kills the subprocess..
        pass


def tddft_app():
    """Entry point to run the orbitals marimo app."""
    import subprocess
    import sys
    from pathlib import Path

    # Get the path to the orbitals.py file
    tddft_path = Path(__file__).parent / "tddft.py"

    try:
        subprocess.run(
            [sys.executable, "-m", "marimo", "run", tddft_path, sys.argv[-1]]
        )
    except KeyboardInterrupt:
        # This is needed because we terminate the marimo process
        # with a keyboard interrupt, which also kills the subprocess..
        pass
