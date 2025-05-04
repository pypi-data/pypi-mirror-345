# CoMPAS navlib

[![Latest version](https://badge.fury.io/py/navlib.svg)](https://badge.fury.io/py/navlib.svg) [![PyPI Downloads](https://static.pepy.tech/badge/navlib)](https://pepy.tech/projects/navlib)

> CoMPAS navlib is a Python library developed by the CoMPAS Lab that provides a modular and extensible toolbox for navigation-related tasks, sensor processing, and robotics research. It includes utilities for array-based math, transformations in SO(3)/SE(3), filtering, environmental data processing, geolocation, time handling, calibration, and navigation.

## Features

* **Math Utilities**: Convenient array-based operations designed for navigation and signal processing.
* **Lie Groups**: Functions for working with SO(3) and SE(3) transformations.
* **Filters**: Various filtering methods for pre-processing navigation data.
* **Environmental Processing**: Tools for post-processing CTD (Conductivity, Temperature, Depth) sensor data.
* **Geographic Utilities**: Functions for working with geographic coordinates, including transformations to UTM and other projections.
* **Time Handling**: Utilities for managing time, including UTC conversions and date-time formatting.
* **Calibration Tools**: Functions for calibrating sensors such as AHRS/IMUs, magnetometers, and Doppler Velocity Logs (DVLs).
* **Navigation Algorithms**: Implementations of attitude estimation and dead reckoning algorithms for underwater vehicle navigation including an specific EKF for uncrewed underwater vehicles.
* **LCM Log Utilities**: Tools for parsing and working with LCM (Lightweight Communications and Marshalling) logs.
* **MB-System Utilities**: Functions for parsing and processing data from the [MB-System](https://github.com/dwcaress/MB-System) software package.

## Installation

Clone the repository and install in editable mode:

```bash
python3 -m pip install navlib
```

or

```bash
git clone https://github.com/CoMPASLab/compas_navlib.git
cd compas_navlib
poetry install
poetry build
pip install dist/*.whl
```

## Documentation

The documentation is hosted on [CoMPAS Navlib](https://compaslab.github.io/compas_navlib). It includes detailed descriptions of the library's features, usage examples, and API references.

## Contributing

Pull requests and issues are welcome! If you’d like to contribute, please: fork the repository, create a feature branch and submit a pull request

### Development

If you want to install the library for development purposes, you can install the required packages in the virtual environment with the following command inside the repository:

``` bash
poetry install
```

Now, to run and modify the code, you have to spawn a new shell with the environment activated:

```bash
poetry shell
```

### Static Documentation

Documentation is built with [mkdocs](https://www.mkdocs.org/). To create it, you will need to install the project development dependencies:

```bash
poetry install --no-root
```

Then, run the following command:

```bash
mkdocs build
```

By default, this will create a `site/` directory with the built documentation in html format. However, if you want to build the documentation and serve it locally, you can run the following command:

```bash
mkdocs serve
```

Then, navigate to [http://localhost:8000/](http://localhost:8000/) to view the documentation.

## License

MIT License — see LICENSE for details.
