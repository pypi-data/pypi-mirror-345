from setuptools import setup, find_packages

setup(
    name = "TimeSub",
    version = "1.0.1",
    author = "Nengjie Zhu",
    author_email = "sjtu_znj@sjtu.edu.cn",
    description = "A Python package for survival analysis with competing risks",
    long_description = """
    A Python package for survival analysis with competing risks, integrating neural networks and statistical inference. 
    Provides tools for time-to-event prediction, model training with PyTorch backend, and comprehensive hypothesis testing.

    Key Features:
    - Neural network models for time-varying and non-time-varying survival analysis
    - Prediction metrics including time-dependent AUC and C-index calculation
    - Bootstrap-based hypothesis testing (structure & significance tests) for model validation
    """,
    license = "MIT Licence",
    url = "https://github.com/sjtu1znj/TimeSub",
    keywords = ["survival analysis", "competing risks", "neural networks", "hypothesis testing", "time-to-event prediction"],
    include_package_data = False,
    packages=find_packages(),
    platforms = "any",
    install_requires=['lifelines==0.30.0', 'numpy==2.2.5', 'scipy==1.15.2', 'torch==2.5.1']
    )