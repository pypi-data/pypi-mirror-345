[![GitHub](https://img.shields.io/badge/GitHub-Orange--EarthquakesETL-gray?labelColor=white&style=flat&logo=GitHub&logoColor=black&link=https://github.com/gualbe/orange-earthquakes-etl)](https://github.com/gualbe/orange-earthquakes-etl) [![PyPI](https://img.shields.io/badge/PyPI-Orange--EarthquakesETL-gray?labelColor=white&style=flat&logo=PyPI&logoColor=blue&link=https://pypi.org/project/EarthquakesETL/)](https://pypi.org/project/EarthquakesETL/) ![Python](https://img.shields.io/badge/Python-3.10-grey?labelColor=yellow&style=flat&logo=Python) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-white?style=flat&logo=PostgreSQL&logoColor=blue&link=https://www.postgresql.org/)](https://www.postgresql.org/) [![Orange Data Mining](https://img.shields.io/badge/Orange%20Data%20Mining-3.38.1-grey?labelColor=orange&style=flat&link=https://orangedatamining.com/)](https://orangedatamining.com/)

Orange3 EarthquakesETL
===============

EarthquakesETL add-on for [Orange] 3 data mining for acquiring global earthquake data via APIs, cleaning the data through a configurable node, and generating seismic attributes for machine learning modeling.

[Orange]: https://orangedatamining.com/

Installation
------------

### Orange add-on installer

Install from Orange add-on installer through Options -> Add-ons.

### Using pip

To install the add-on with pip use

    pip install EarthquakesETL

To install the add-on from source, run

    python setup.py install

To register this add-on with Orange, but keep the code in the development directory (do not copy it to 
Python's site-packages directory), run

    python setup.py develop

You can also run

    pip install -e .

which is sometimes preferable as you can *pip uninstall* packages later.

### Anaconda

If using Anaconda Python distribution, simply run

    pip install EarthquakesETL

**Required Dependencies**:
* psycopg2-binary
* SQLAlchemy>=2.0.40
* bcrypt>=4.3.3
* geopandas>=1.0.1
* bs4>=0.0.2
* typing>=3.7.4.3
* openquake.engine>=3.23.1
* fiona>=1.10.1
* dataclasses>=0.6
* numpy>=1.26.4
* numba==0.58.1
* llvmlite==0.41.1

Usage
-----

After the installation, the widgets from this add-on are registered with Orange. To run Orange from the terminal,
use

    orange-canvas

or

    python3 -m Orange.canvas

New widgets are in the toolbox bar under EarthquakesETL section.

Workflow Example
-----
This is an example of how you can use this add-on.

