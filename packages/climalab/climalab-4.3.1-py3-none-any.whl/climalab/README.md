# climalab

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/climalab.svg)](https://pypi.org/project/climalab/)

**climalab** is a Python toolkit designed to facilitate climate data analysis and manipulation, including tools for data extraction, processing, and visualization. It leverages external tools and standards like CDO and CDS to streamline workflows for climate-related research.

## Features

- **Meteorological Tools**:
  - Comprehensive handling of meteorological variables and data
  - Weather software input file generation
  - Variable conversion and standardisation utilities
- **NetCDF Tools**:
  - Advanced CDO operations for netCDF file manipulation
  - NCO tools for efficient data processing
  - Faulty file detection and reporting
  - Basic information extraction from netCDF files
- **Supplementary Analysis Tools**:
  - Visualisation tools for maps and basic plots
  - Bias correction methods (parametric and non-parametric quantile mapping)
  - Statistical analysis tools
  - Auxiliary functions for data processing
- **Project Structure**:
  - Sample project templates for data analysis workflows
  - Standardised directory organisation
  - Version control and changelog management

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **Required Third-Party Libraries**:

  ```bash
  pip install numpy pandas scipy cdsapi PyYAML
  ```

  Or via Anaconda (recommended channel: `conda-forge`):

  ```bash
  conda install -c conda-forge numpy pandas scipy cdsapi pyyaml
  ```

- **Other Internal Packages**:

  ```bash
  pip install filewise paramlib pygenutils
  ```

### Installation (from PyPI)

Install the package using pip:

```bash
pip install climalab
```

### Development Installation

For development purposes, you can install the package in editable mode:

```bash
git clone https://github.com/yourusername/climalab.git
cd climalab
pip install -e .
```

## Usage

### Basic Example

```python
from climalab.meteorological import variables
from climalab.netcdf_tools import cdo_tools

# Convert temperature from Kelvin to Celsius
temp_celsius = variables.convert_temperature(temp_kelvin, 'K', 'C')

# Process netCDF files using CDO
cdo_tools.merge_files(input_files, output_file)
```

### Advanced Example

```python
from climalab.supplementary_tools import bias_correction
from climalab.netcdf_tools import nco_tools

# Apply quantile mapping bias correction
corrected_data = bias_correction.quantile_mapping(
    obs_data, model_data, future_data
)

# Extract specific variables from netCDF files
nco_tools.extract_variables(input_file, output_file, ['tas', 'pr'])
```

## Project Structure

The package is organised into several sub-packages:

```text
climalab/
├── meteorological/
│   ├── variables.py
│   └── weather_software.py
├── netcdf_tools/
│   ├── cdo_tools.py
│   ├── nco_tools.py
│   ├── detect_faulty.py
│   └── extract_basics.py
├── supplementary_tools/
│   ├── bias_correction/
│   ├── plotting/
│   └── statistics/
└── data_analysis_projects_sample/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Climate Data Operators (CDO) team
- Copernicus Climate Data Store (CDS)
- NetCDF Operators (NCO) team

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.
