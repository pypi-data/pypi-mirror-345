from setuptools import setup, find_packages

setup(
    name="tscalc",
    version="2.0.0",
    description="A comprehensive assessment tool to evaluate personal attributes related to toughness, success potential, and personality type.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Craig Michael Dsouza",
    author_email="dsouzacraigmichael@gmail.com",
    url="https://github.com/CraigMLdsouza/tscalc",
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    install_requires=[
        "numpy",
        "tabulate",
        "colorama",
        "reportlab"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "tscalc=tscalc.cli:main",
        ],
    },
)
