EQ Feature Engineering
===========


The EQ Feature Engineering node generates earthquake-related attributes from a dataset of seismic events.
It uses different approaches to compute seismic indicators that can be used in machine learning models for earthquake prediction.

This node takes a table of seismic events as input and generates seismic attributes based on configurable parameters.

Input Parameters
-------

**1. Events for b-value Morales (nMorales)**:

- Number of previous events considered for calculating the b-value using Morales' method.

- Recommended values: 10 - 100 (default: 10).

**2. Events for b-value Adeli (nAdeli)**:

- Number of previous events considered for calculating the b-value using Adeli's method.

- Recommended values: 1 - 10 (default: 1).

**3. Reference Magnitude (referenceMagnitude)**:

- Reference magnitude used in b-value calculation.

- Recommended value: 3.0.

**4. Days for Prediction (dayspred)**:

- Number of future days considered for prediction.

- Recommended value: 5 - 7 (default: 6).

**5. Classification: From (classFrom)**:

- Minimum magnitude for discrete class creation.

- Recommended value: 2.0 - 5.0.

**6. Classification: To (classTo)**:

- Maximum magnitude for discrete class creation.

- Recommended value: 2.0 - 6.0.

**7. Classification Step (classStep)**:

- Increment between magnitude classes.

- Recommended values: 0.05 - 0.5.

**8. Threshold for mu and c (chth)**:

- Characteristic threshold used in the calculation of mu and c attributes.

- Recommended values: 0.01 - 1.0.

**9. Output Type (outputType)**:

- Defines the set of generated attributes.

- Options:
     - `attYorch/bM` – Yorch attributes with Morales’ b-value.
     - `attYorch/bA` – Yorch attributes with Adeli’s b-value.
     - `attAdeli/bM` – Adeli attributes with Morales’ b-value.
     - `attAdeli/bA` – Adeli attributes with Adeli’s b-value.

Output Attributes
-----------

The generated attributes include seismic indicators based on b-value calculations and other factors:

- **b-value (bM, bA):** Based on Morales' (bM) or Adeli's (bA) method.
- **a-value:** Gutenberg-Richter law value.
- **b-value increments (x1 - x5):** Variation of b-value in previous events.
- **Weekly maximum magnitude (x6):** Highest magnitude recorded in the last week.
- **Probability of magnitude >=6.0 (x7):** Calculated using probability density distribution.
- **Elapsed time (T):** Time since the last significant seismic event.
- **Coefficient of variation (c):** Ratio between standard deviation and mean time between events.
- **Mean square deviation (η):** Variability in seismic activity.
- **Magnitude deficit (∆M):** Difference between observed and expected magnitudes.
- **dE12:** This parameter represents the rate of the square root of seismic energy, measuring the speed at which seismic energy is released after applying a square root transformation to reduce its dispersion.
- **Mmean:** This is the mean magnitude, calculated as the average of the magnitudes of the events recorded in the catalog.
- **μ:** This parameter denotes the mean time, representing the average time interval between seismic events.