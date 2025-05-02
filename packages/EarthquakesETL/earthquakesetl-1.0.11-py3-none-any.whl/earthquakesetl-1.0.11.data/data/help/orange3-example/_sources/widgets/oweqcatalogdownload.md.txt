EQ Catalog Download
===========

The "EQ Catalog Download" widget allows users to acquire earthquake data from two Open
Data APIs: [USGS](https://www.usgs.gov/) (United States Geological Survey) and the [Chile Sismology website](https://www.sismologia.cl/). This
tool enables precise data extraction based on user-defined parameters such as location,
time period, and minimum magnitude.

Data Source Options
-----------

- **USGS**: Provides global earthquake data, including parameters like magnitude, location, and depth. 
- **Chile Sismology**: Offers detailed seismic data specifically for Chile, ideal for regional studies.

Configuration Parameters
-----------

The widget offers a variety of configuration options to customize the data acquisition:

- **Data Source**: Choose between "USGS" or "Chile Sismology".
- **Time Period**:
  - **Start Date**: Select the starting date for the data acquisition.
  - **End Date**: Specify the ending date for the data acquisition. Ensure that the end date is after the start date.
- **Minimum Magnitude**: Define the minimum earthquake magnitude to filter events (range: 0.0 to 10.0).

Location Options:
--------------

- **By Rectangle**: Define a bounding box with:
  - Min Latitude
  - Max Latitude
  - Min Longitude
  - Max Longitude

- **By Circle**: Provide the central coordinates (Latitude, Longitude) and the radius (Max positive Radius in km).

Outputs
-----------

- **Data**: A table containing earthquake events with attributes such as magnitude, location, depth, and timestamp.
- **Configuration Table**: A summary of the user-defined parameters used for data acquisition.

Usage Tips
--------------

- For precise results, adjust the magnitude and location parameters carefully.
- Utilize the "Generate" button to initiate data acquisition, and the "Reset" button to clear configurations and start anew.
- When using "Chile Sismology", verify that the chosen coordinates are within the country's geographical limits.

![ChileImage.jpg](images/ChileImage.jpg)