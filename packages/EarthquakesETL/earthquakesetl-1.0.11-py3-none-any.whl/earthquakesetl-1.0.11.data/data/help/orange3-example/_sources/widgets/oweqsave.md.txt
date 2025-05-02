EQ Save
===========


The "EQ Save" widget allows storing seismic event catalogs, attribute datasets, and configurations in a database.
It supports connections with various SQL databases and provides options to save data in predefined structures.

Inputs
-------
**Data**: Dataset containing attributes and classes generated from seismic events.

**Catalog Config**: Configuration table used for storing the event catalog.

**Dataset Config**: Configuration table used for storing the attribute dataset.

**Dataset Decluster**: Configuration used if the catalog has been declustered.

**Catalog**: Seismic event catalog to be stored.


Configuration Options
-----------
The widget allows choosing between storing a seismic event catalog or an attribute dataset.

**Storage Type**:

- *Catalog*: Saves raw or declustered seismic events.
- *Dataset*: Saves an attribute dataset generated from a catalog of events.


Database Configuration
-----------
Before saving data, a connection must be established with a compatible SQL database. To do this, the following 
connection information must be provided:

- *Username and password*
- *Server and database*


Recommendations
-----------
- Ensure that the data meets the expected structure before storing it.
- Verify the database connection before executing the save operation.
- Use appropriate configurations to ensure data integrity.