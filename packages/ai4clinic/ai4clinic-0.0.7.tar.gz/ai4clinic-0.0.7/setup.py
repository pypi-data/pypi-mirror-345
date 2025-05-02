from setuptools import setup, find_packages

VERSION = "0.0.7"
DESCRIPTION = "ai4clinic: Bridging AI and Clinical Practice in Cancer Research"
LONG_DESCRIPTION = """
ai4clinic is a Python package designed to enhance the practical use of drug response prediction (DRP) models in clinical settings. It addresses key challenges such as model generalization to new patient scenarios and aligning model evaluations with clinical needs.

Key Features:
- Implement robust data splitting strategies
- Measure performance metrics per drug and within sensitive ranges
- Generate visualizations to illustrate model performance

This package is ideal for researchers in computational biology and medicine, aiming to translate AI advancements into clinical applications.

"""

setup(
    name="ai4clinic",
    version=VERSION,
    author="Katyna Sada del Real, Josefina Arcagni",
    author_email="ksada@unav.es",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/KatynaSada/ai4clinic",
    project_urls={
        "Source": "https://github.com/KatynaSada/ai4clinic",
        "Tracker": "https://github.com/KatynaSada/ai4clinic/issues",
    },
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=1.5.0",
        "matplotlib>=3.7.0",
        "torch>=2.0.0",
        "torchmetrics>=0.11.0",
        "rich>=13.3.0"
    ],
    keywords=["python", "first package"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Natural Language :: English"
    ],
    python_requires=">=3.9",
)

