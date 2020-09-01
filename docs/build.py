import platform
import subprocess
import sys
import os


if __name__ == "__main__":
    # Generate "testcoverage.rst"
    parent_dir = os.path.join(os.path.dirname(sys.argv[0]), "..")
    coverage = subprocess.check_output(
        ["python", "tests/get_coverage.py"], cwd=parent_dir
    )

    with open("testcoverage.rst", "wb") as f:
        f.write(coverage)

    # Run "make dirhtml"
    command = "make"
    if platform.system() == "Windows":
        command = "make.bat"

    proc = subprocess.Popen([command, "dirhtml"])
    proc.wait()

    os.unlink("testcoverage.rst")

    sys.exit(proc.returncode)
