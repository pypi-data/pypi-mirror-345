# aind-data-schema-models

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)
![Python](https://img.shields.io/badge/python->=3.10-blue?logo=python)

## Installation
To install from pypi, run
```bash
pip install aind-data-schema-models
```

To install from source, in the root directory, run
```bash
pip install -e .
```

To develop the code, run
```bash
pip install -e .[dev]
```

## Contributing

### How to add a new model class

#### tl;dr

Add new classes to the `_generators/models/*.csv` files.

Run `./run_all.sh` in the top-level folder.

#### Details

The model class files, `brain_atlas.py` etc, are auto-generated. **You should never need to modify the class files directly.**

Instead, take a look at the `jinja2` templates in the folder `_generators/templates`. The filename of the template is used to pull the corresponding `.csv` file and populate the `data` DataFrame. In the template you can pull data from the various columns and use them to populate each of the fields in your class.

To re-build all the models, run the `run_all.sh` bash script in the root folder, which loops through the template files and runs them through the `generate_code` function.

There are a few special cases, e.g. if data are missing in columns they will show up as `float: nan`. See the `organizations.txt` template for examples of how to handle this.
