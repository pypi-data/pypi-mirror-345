from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="voly",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        install_requires=[
            "pandas>=1.3.0",
            "numpy>=1.20.0",
            "scipy>=1.7.0",
            "plotly>=5.3.0",
            "scikit-learn>=1.0.0",
            "websockets>=10.0",
            "requests>=2.26.0",
            "loguru>=0.5.3",
        ],
        extras_require={
            'dev': [
                "black>=22.1.0",
                "isort>=5.10.1",
                "mypy>=0.931",
                "flake8>=4.0.1",
                "twine>=4.0.0",
                "build>=0.8.0",
            ]
        }
    )
