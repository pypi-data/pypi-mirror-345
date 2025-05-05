# Skylite

The aim of this project is to create a minimalist approach to managing artifacts generated throughout the model development process.

## Table of Contents

- [Main Features](#main-features)
- [Where to get it](#where-to-get-it)
- [Dependencies](#dependencies)
- [Change log](#change-log)
- [License](#license)
- [Documentation](#documentation)

## Main Features

- **Project**:
A Project is the single element that manages all of your tasks.

- **Store**:
A Store is the single element that manages all artifacts of a single type, across all projects.

## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/jesse-sealand/skylite

The latest released version are available at
[Python Package Index (PyPI)](https://pypi.org/project/skylite/).

```sh
pip install skylite
```

## Examples

```python
from skylite import Exchange

# Settings
home_directory = '~/Documents'
settings = {
    "exchange_name": "Exchange",
    "available_stores": ["data-store", "model-store", "result-store", "project-store"],
}

# Setup
SkyLight = Exchange(home_directory, settings)
SkyLight.open_exchange()


# Create Project
PROJECT_NAME = 'aerial-imagery5'
SkyLight.create_project(PROJECT_NAME)

sky_proj = SkyLight.open_project(PROJECT_NAME)

# Start adding model artifacts when modeling
for i in range(0,10):

    # Create new instance of Trial
    sky_proj.create_trial()

    """
    Perform Modeling / scoring / analysis
    """

    # Store artifacts for this Trial
    data_dict = {'train': df,
                'test': df,
                'score': df}
    
    model_dict = {'model': clf}

    results_dict = {'accuracy': 0.98,
                    'f1-score': 0.75
                    }

    sky_proj.store_objects('data-store', data_dict)
    sky_proj.store_objects('model-store', model_dict)
    sky_proj.store_objects('result-store', results_dict)


    # close instance of trial and save artifacts
    sky_proj.close_trial()

```

## Dependencies

- [TinyDB](https://tinydb.readthedocs.io/en/latest/) A tiny, document oriented database.


## Change Log

See the [change log] for a detailed list of changes in each version.


## License

This extension is [licensed under the MIT License].

[change log]: https://github.com/jesse-sealand/skylite/blob/main/CHANGELOG.md
[licensed under the mit license]: https://github.com/jesse-sealand/skylite/blob/main/LICENSE.txt

## Documentation
The official documentation is hosted on [Read the Docs](http://skylite.readthedocs.io/).
