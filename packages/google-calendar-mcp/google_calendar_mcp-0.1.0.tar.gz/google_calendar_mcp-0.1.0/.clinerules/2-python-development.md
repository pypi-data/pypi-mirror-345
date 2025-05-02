# LLM 向け最適化.clinerules

## 2. Python 開発規約

### 2.1 ライブラリ構造

Python ライブラリ開発には`src-layout`を使用する：

```
project_root_directory
├── pyproject.toml
├── setup.py
└── src/
    └── mypkg/
        ├── __init__.py
        ├── module.py
        └── subpkg1/
            ├── __init__.py
            └── module1.py
```

### 2.2 設定ファイル例

#### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=42", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "project_root_directory"
description = "AWS Security Group Mapping Tool"
readme = "README.md"
license = {file = "LICENSE"}
classifiers = [
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.12.0"
dependencies = [
    "boto3>=1.20.0",
    "click>=8.0.0",
]
dynamic = ["version"]

[project.scripts]
project = "project.cli:main"

[tools.setuptools.package-dir]
project_root_directory = "src/project_root_directory"

[tool.setuptools_scm]
write_to = "src/project_root_directory/_version.py"
```

#### setup.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="project",
    use_scm_version=True,
    description="AWS Security Group Mapping Tool",
    author="youyo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.20.0",
        "click>=8.0.0",
    ],
    python_requires=">=3.12.0",
    entry_points={
        "console_scripts": [
            "project=project.cli:main",
        ],
    },
    setup_requires=["setuptools_scm>=6.2"],
)
```

#### GitHub Actions (publish.yaml)

```yaml
name: Publish python package

on:
  push:
    branches-ignore:
      - "**"
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install --upgrade build setuptools setuptools_scm
      - name: Build package
        run: |
          python -m build
      - name: Publish package distributions to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```
