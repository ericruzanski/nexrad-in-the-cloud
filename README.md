# NEXRAD in the Cloud

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange.svg)](https://jupyter.org/)
[![NEXRAD on AWS](https://img.shields.io/badge/data%20source-NEXRAD%20on%20AWS-blue)](https://registry.opendata.aws/noaa-nexrad/)

## Overview

This project is a collection of scripts and Jupyter Notebooks that retrieve and visualize Level II weather radar reflectivity data from NOAA NEXRAD stations. The data is sourced from AWS. The scripts access the most recent radar files from the `noaa-nexrad-level2` public S3 bucket, processes the data using [Py-ART](https://arm-doe.github.io/pyart/), and overlay it on a Cartopy map with county and state boundaries.

If radar data is unavailable for a specific site, the script skips plotting for that station and, optionally, annotates the map with a message placeholder.

## Features

- Fetches NEXRAD Level II data directly from AWS S3
- Automatically handles closest timestamp retrieval
- Plots multiple radars on a single map
- Visualizes radar reflectivity with accurate colormap and overlays
- Annotates missing/offline radar stations

## Running the Notebook

Launch the Jupyter Notebook interface and open `NEXRAD_Reflectivity_Tennessee.ipynb`:

```bash
jupyter lab
```

Or try it online via Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ericruzanski/nexrad-in-the-cloud/HEAD?labpath=tennessee_radar_reflectivity.ipynb)

## Data Source

Radar data is sourced from the [NEXRAD Level II Public Dataset on AWS](https://registry.opendata.aws/noaa-nexrad/). For details on access, usage, and citation requirements, refer to the [official documentation](https://docs.opendata.aws/noaa-nexrad/readme.html).

## Acknowledgments

- [Py-ART](https://arm-doe.github.io/pyart/) — Toolkit for working with weather radar data.
- [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) — Mapping library for geospatial data visualization.
- [MetPy](https://unidata.github.io/MetPy/latest/index.html) — Meteorological tools for data analysis and plotting.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
