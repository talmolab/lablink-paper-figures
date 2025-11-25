#!/usr/bin/env python3
"""
Generate all LabLink paper figures in a timestamped run folder.

This script runs all figure generation scripts in the correct order and collects
all outputs into a single timestamped run folder for easy review.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and report success/failure."""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*80)

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✓ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {description}")
        print(f"  Error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"✗ Failed: {description}")
        print(f"  Error: Command not found - {e}")
        return False


def main():
    """Generate all figures."""
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = Path("figures") / f"run_{timestamp}"

    print(f"\n{'='*80}")
    print(f"Generating all figures to: {run_folder}")
    print(f"{'='*80}\n")

    # Track successes and failures
    results = []

    # 1. Architecture diagrams (essential)
    results.append((
        "Architecture diagrams (essential)",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/generate_architecture_diagram.py",
                "--terraform-dir", "../lablink-template/lablink-infrastructure",
                "--output-dir", str(run_folder / "main"),
                "--diagram-type", "all-essential",
                "--fontsize-preset", "paper",
                "--no-timestamp-runs"
            ],
            "Architecture diagrams (essential)"
        )
    ))

    # 2. Architecture diagrams (supplementary)
    results.append((
        "Architecture diagrams (supplementary)",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/generate_architecture_diagram.py",
                "--terraform-dir", "../lablink-template/lablink-infrastructure",
                "--output-dir", str(run_folder / "supplementary"),
                "--diagram-type", "all-supplementary",
                "--fontsize-preset", "paper",
                "--no-timestamp-runs"
            ],
            "Architecture diagrams (supplementary)"
        )
    ))

    # 3. QR codes
    results.append((
        "QR codes",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/generate_qr_codes.py",
                "--output-dir", str(run_folder / "main")
            ],
            "QR codes"
        )
    ))

    # 4. SLEAP dependency graph
    results.append((
        "SLEAP dependency graph",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/generate_sleap_dependency_graph.py",
                "--preset", "paper",
                "--output-dir", str(run_folder / "main")
            ],
            "SLEAP dependency graph"
        )
    ))

    # 5. Software complexity
    results.append((
        "Software complexity",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_software_complexity.py",
                "--format", "paper",
                "--output-dir", str(run_folder / "main")
            ],
            "Software complexity"
        )
    ))

    # 6. GPU cost trends
    results.append((
        "GPU cost trends",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_gpu_cost_trends.py",
                "--preset", "paper",
                "--output", str(run_folder / "main" / "gpu_cost_trends.png")
            ],
            "GPU cost trends"
        )
    ))

    # 7. GPU reliance
    results.append((
        "GPU reliance",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_gpu_reliance.py",
                "--output-dir", str(run_folder / "main")
            ],
            "GPU reliance"
        )
    ))

    # 8. OS distribution
    results.append((
        "OS distribution",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_os_distribution.py",
                "--output-dir", str(run_folder / "main")
            ],
            "OS distribution"
        )
    ))

    # 9. Configuration hierarchy
    results.append((
        "Configuration hierarchy",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_configuration_hierarchy.py",
                "--output-dir", str(run_folder / "main")
            ],
            "Configuration hierarchy"
        )
    ))

    # 10. Configuration hierarchy (simple)
    results.append((
        "Configuration hierarchy (simple)",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_configuration_hierarchy_simple.py",
                "--output-dir", str(run_folder / "supplementary")
            ],
            "Configuration hierarchy (simple)"
        )
    ))

    # 11. Deployment impact
    results.append((
        "Deployment impact",
        run_command(
            [
                "uv", "run", "python",
                "scripts/plotting/plot_deployment_impact.py",
                "--output-dir", str(run_folder / "main")
            ],
            "Deployment impact"
        )
    ))

    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)

    successes = [name for name, success in results if success]
    failures = [name for name, success in results if not success]

    print(f"\nSuccessful ({len(successes)}/{len(results)}):")
    for name in successes:
        print(f"  ✓ {name}")

    if failures:
        print(f"\nFailed ({len(failures)}/{len(results)}):")
        for name in failures:
            print(f"  ✗ {name}")

    print(f"\n{'='*80}")
    print(f"Output directory: {run_folder.absolute()}")
    print('='*80)

    # Exit with error if any failed
    if failures:
        sys.exit(1)
    else:
        print("\n✓ All figures generated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
