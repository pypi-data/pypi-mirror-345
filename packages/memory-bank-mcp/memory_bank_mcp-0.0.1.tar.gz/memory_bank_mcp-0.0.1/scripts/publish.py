#!/usr/bin/env python3
"""
Script to build and publish the package to PyPI.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, error_message):
    """Run a command with proper error handling."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {error_message}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout


def main():
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    os.chdir(project_root)

    # Clean up previous builds
    for dir_to_remove in ["dist", "build", "*.egg-info"]:
        cmd = ["rm", "-rf", dir_to_remove]
        run_command(cmd, f"Failed to remove {dir_to_remove}")

    # Install build dependencies
    run_command(["pip", "install", "--upgrade", "build", "twine"],
                "Failed to install build dependencies")

    # Build the package
    print("Building package...")
    run_command(["python", "-m", "build"],
                "Failed to build package")

    # Check the built package
    print("Checking package...")
    run_command(["twine", "check", "dist/*"],
                "Package check failed")

    # Upload to PyPI
    print("\nReady to upload to PyPI!")
    print("Options:")
    print("1. Upload to TestPyPI")
    print("2. Upload to PyPI")
    print("3. Exit without uploading")

    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == "1":
        print("Uploading to TestPyPI...")
        run_command(
            ["twine", "upload", "--repository-url",
                "https://test.pypi.org/legacy/", "dist/*"],
            "Failed to upload to TestPyPI"
        )
        print("\nSuccess! Package uploaded to TestPyPI")
        print("Install with: pip install --index-url https://test.pypi.org/simple/ memory-bank-mcp")

    elif choice == "2":
        print("Uploading to PyPI...")
        run_command(["twine", "upload", "dist/*"],
                    "Failed to upload to PyPI")
        print("\nSuccess! Package uploaded to PyPI")
        print("Install with: pip install memory-bank-mcp")

    else:
        print("Exiting without uploading")


if __name__ == "__main__":
    main()
