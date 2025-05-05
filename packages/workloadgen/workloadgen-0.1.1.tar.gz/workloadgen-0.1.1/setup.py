from setuptools import setup, find_packages

setup(
    name="workloadgen",
    version="0.1.1",
    description="Synthetic SWF workload generation using Variational Autoencoders",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "torch", "pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"
    ],
    entry_points={
        "console_scripts": [
            "workloadgen-train=scripts.train_and_generate:main",
        ]
    },
)
