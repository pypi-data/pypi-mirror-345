from setuptools import setup, find_packages
import os
import subprocess


def build_tree_sitter():
    """Build the tree-sitter-rust parser"""
    rust_dir = os.path.join(os.path.dirname(__file__), 'tree-sitter-rust')
    if os.path.exists(rust_dir):
        try:
            subprocess.run(['tree-sitter', 'build'], cwd=rust_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to build tree-sitter-rust: {e}")
        except FileNotFoundError:
            print(
                "Warning: tree-sitter command not found. Please install tree-sitter CLI")


# Build tree-sitter-rust before setup
build_tree_sitter()

setup(
    name="stylus-analyzer",
    version="0.1.6",
    packages=find_packages(),
    package_data={
        'stylus_analyzer': [
            'build/*',
            'build/**/*',
        ],
    },
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "tree-sitter>=0.20.0",
        "tree-sitter-rust>=0.21.1",
        "setuptools>=42.0.0",
        "reportlab>=3.6.0",
    ],
    entry_points={
        "console_scripts": [
            "stylus-analyzer=stylus_analyzer.cli:main",
        ],
    },
    description="AI-powered bug detection tool for Stylus/Rust contracts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jay Sojitra",
    author_email="jaysojitra1011@gmail.com",
    url="https://github.com/Jay-Sojitra/stylus-analyzer",
    keywords="stylus, rust, security, smart-contracts, analysis, ai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
