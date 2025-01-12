# CSV Quality Check with Frictionless
This [Streamlit app](https://bfe-ogd-quality-process.streamlit.app/) enables users to perform quality checks on CSV files of SFOE OGD publications using the Frictionless framework. The app allows for easy validation of CSV files against defined schemas (extracted from corresponding `datapackage.json`) found on _uvek-gis_, ensuring data integrity and adherence to specified formats.

You can find the app [here](https://bfe-ogd-quality-process.streamlit.app/)

## Features
- **File Upload**: Users can upload CSV files for validation directly through the Streamlit interface.
- **Schema-based Validation**: Leveraging Frictionless, the app validates uploaded CSV files against predefined schemas or inferred data structures.
- **Error Handling**: Error messages are provided in case of validation issues, aiding users in understanding and rectifying data problems.


## Files
- `app.py`: This is the main Python file containing the Streamlit application code.
- `mapping.py`: This file contains the mapping from file name to OGD number. Note: There is not a datapackage for every SFOE OGD publication.
- `requirements.txt`: Lists the Python dependencies required for running the Streamlit app.
- `.streamlit/config.toml`: This is the Streamlit configuraion file. It allows customization of Streamlit's behavior, including server settings, theming, and other preferences.


## Problems
The structure of the code is as follows: the CSV content is loaded in a _pd.DataFrame_ and it's validated with _frictionless.validate_ using the corresponding _schema_ from the `datpackage.json`.
While testing we found out that even if the CSV is _valid_, it is recognized as _invalid_ if all the columns are of datatype _int64_. But if you change the column dtype of a random column to _float_, The

Attempts to improve it:
- Store the CSV file "locally" using the path `file_name.csv` and access & use it with the datapackage. **failed: "Source for frictionless.validate() is empty"**
- Save the CSV file in a temporary directory and use the datapackage. **failed: "frictionless.validate() cannot access source form unsecure origin"**
