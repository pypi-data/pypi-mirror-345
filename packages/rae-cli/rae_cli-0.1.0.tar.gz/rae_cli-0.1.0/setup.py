from setuptools import setup, find_packages

setup(
    name="rae-cli",
    version="0.1.0",
    description="CLI tool for scaffolding analytics engineering data stacks.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="James Reeves",
    author_email="james@codebrojim.com",
    url="https://github.com/CodeBroJim/rae",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "asciimatics==1.15.0",
        "click==8.1.7",
        "PyYAML==6.0.2",
        "pyfiglet==1.0.2",
        "questionary==2.0.1",
        "rich==14.0.0",
    ],
    extras_require={
        "dev": [
            "black==24.10.0",
            "coverage==7.6.10",
            "flake8==7.1.1",
            "isort==5.13.2",
            "mypy==1.10.0",
            "nodeenv==1.9.1",
            "pre_commit==4.2.0",
            "Pygments==2.19.1",
            "pytest==8.3.4",
            "pytest-cov==6.0.0",
            "pytest-mock==3.14.0",
            "virtualenv==20.30.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rae=rapid_analytics_engineering.main:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    license="Proprietary",
    python_requires=">=3.8",
)
