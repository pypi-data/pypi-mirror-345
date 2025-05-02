EarthquakesETL documentation
============================

This add-on allows users to perform three main activities related to seismic data in an intuitive and efficient way:

**1. EQ Catalog Download**: Retrieve global earthquake data using Open Data APIs. The graphical interface makes it easy for users to configure and download the desired data.

**2. EQ Catalog Declustering**: Connect the downloaded data to a configurable node that performs seismic catalog cleaning, ensuring the data is suitable for further analysis.

**3. EQ Feature Engineering**: Calculate and generate seismic features from the cleaned data, creating datasets ready for supervised modeling using machine learning techniques.

In addition, the addon has a specific node to connect to a database and store raw or declusterized catalogs and attribute and class datasets.

**4. EQ Save**: This add-on is designed to streamline the entire workflow, from data acquisition to preparation for predictive analysis.

This add-on is designed to streamline the entire workflow, from data acquisition to preparation for predictive analysis.

.. toctree::
   :maxdepth: 2

Widgets
-------

.. toctree::
   :maxdepth: 1

   widgets/oweqcatalogdownload
   widgets/oweqcatalogdeclustering
   widgets/oweqfeatureengineering
   widgets/oweqsave

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


