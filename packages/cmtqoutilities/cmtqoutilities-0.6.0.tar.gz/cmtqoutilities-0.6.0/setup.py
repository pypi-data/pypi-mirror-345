from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="cmtqoutilities",
    use_scm_version=True,
    setup_requires=["setuptools-scm"],
    description="API for all cmtqo devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian Huber",
    author_email="huberse@phys.ethz.ch",
    url="https://gitlab.phys.ethz.ch/code/experiment/mm-runexperiment",
    packages=find_packages(include=["utilities", "utilities.*"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.18.0",
        "requests>=2.25.0",
        "scipy>=1.5.0",
        "pyserial>=3.5",
        "zaber.serial>=0.9",
        "pymysql>=1.1.1",
        "nbconvert>=7.0.0",
        "nbformat>=5.0.0",
        "jupyter>=1.1.1"
    ]
)


if __name__ == "__main__":
    print("\nTo use this environment in Jupyter, run:")
    print("  python -m ipykernel install --user --name=modop --display-name \"Python (modop)\"\n")
