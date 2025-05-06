# GPP Prediction

A Python package for predicting gross primary production (GPP) in ecological systems.

## Installation

```bash
pip install gpp-prediction
```

## Features

- Convert solar radiation to photosynthetically active radiation (PAR)
- Calculate GPP using environmental parameters
- Handle various input formats (single values, arrays, pandas Series)

## Usage

```python
import pandas as pd
import numpy as np
from gpp_prediction import swrad2par, calc_gpp

# Convert solar radiation to PAR
swrad = 0.5  # kW m^-2
par = swrad2par(swrad)  # kJ m^-2 day^-1

# Sample data
data = {
    'swrad': [0.4, 0.5, 0.6],
    'fapar': [0.6, 0.7, 0.8],
    'tmin': [5, 8, 10],
    'vpd': [0.5, 1.0, 1.5]
}
df = pd.DataFrame(data)

# Calculate PAR from solar radiation
df['par'] = swrad2par(df['swrad'])

# Model parameters
params = {
    'eps_max': 2.5,
    'tmin_min': 0,
    'tmin_max': 12,
    'vpd_min': 0.2,
    'vpd_max': 2.0
}

# Calculate GPP
df['gpp'] = calc_gpp(
    df['par'],
    df['fapar'],
    df['tmin'],
    df['vpd'],
    **params
)

print(df)
```

## License

This project is licensed under the MIT License
