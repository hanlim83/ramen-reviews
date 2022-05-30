# Ramen Reviews API / Web App
This repository contains a basic Create, Read, Update, Delete (CRUD) API / Web App that interfaces with an SQLite database. This API / Web app allows anyone to read and submit ramen reviews. This API / Web app is developed using Python using the Flask framework.

This API / Web app have been developed in [GitHub Codespaces](https://github.com/features/codespaces)
## How to run this API / Web App
*This guide assumes that you have already cloned this repository locally or downloded this repository's codes from GitHub*
From the folder where the codes reside,
1. Run `pip install -r  requirements.txt`
2. If the database file `database.db` doesn't exists  or if you wish to reset the SQLite database, please run `python initialise_database.py` to initialize the database
3. Run the following commands to set the flask enviroment variables to run the API / Web App in developer mode
  - **For Linux:**
    - `export FLASK_APP=app`
    - `export FLASK_ENV=development`
  - **For Windows:**
    - `SET FLASK_APP=app`
    - `SET FLASK_ENV=development`
4. Finally, start the API / Web App by running `flask run`
## Database Preparation Steps in initialise_database.py
The database was first created using the SQL schema file under `schema.sql`

Then using the Pandas & Numpy libraries, data in the provided `ramen-ratings.csv` CSV file was imported into the newly created database table.

The following contraints were applied to the database table:
- With the exception of **ExID** column, all other columns require data to be present
- The **ID** column values would be managed by the database table directly. No modification to the **ID** column values would be possible via API / Web App
- The **Type** colummn restricts values to: 'Cup','Pack','Tray','Bowl','Box','Can','Bar'

### Notes
- As the ID Column in the CSV file doesn't contain unique values, it cannot be used as an unique key required by SQL database tables. A new index key named **ID** was created, the values under the ID Column in the CSV file would be created under the column **ExID**
- As there are missing data across columns (Type, Package & Rating), records with these missing data are removed entirely to maintain data integrity at the database level. As a result, although the original CSV file contained 8 unique brands, only 7 unique brands remains (All of Brand M's reviews have missing Type & Rating values)
## API Endpoint Reference
### /api/get/all
- HTTP Methods: GET
- Input Optional Query Paramters: SortBy & SortType
- Output: A JSON array of all review objects
- Notes
  - Both the provided SortBy & SortType query parameters must contain acceptable values. The API will return an error if the parameter values are not as expected.
### /api/get
- HTTP Methods: GET
- Input Query Paramters (A minimum of 1 parameter is needed): ID, Country, Brand, Type, Package, Minimum Rating, Maximum Rating
- Output: A JSON array of review objects matching the provided query parameters
- Notes
    - The ID request parameter must be an Integer. The API would reject the GET request if the ID request parameter is a string / float. Exact Matching is performed
    - Coumtry, Brand, Type, Package request perameters are wildcard parameters (Parital values are accepted) These parameters are assumed to be String
    - Minimum Rating & Maximum Rating parameters must be either an Integer or a float. The API would reject the GET request if the Minimum Rating and/or Maximum Rating request parameter(s) is a string.
    - If an empty array is returned, this means that no reviews match your specified search
### /api/add
  - HTTP Method: POST
  - Input Data: A JSON object containing the review object to be added
  - Output data: The same JSON object but with an **ID** parameter to facilicate direct searching / editing of the review in the future
  - Notes:
    - Only these JSON Key Values will be read: Country, Brand, Type, Package, Minimum Rating
    - Any extra values like **ExID** or **ID** will be ignored. The database will assign the **ID** value automatically
    - The values will be vaildated to ensure data integrity. The API will provide the error message if the data is of the incorrect type
### /api/update
  - HTTP Method: POST
  - Input Data: A JSON object containing the review object with the specific attributes to be update
  - Output data: A message indicating that the review object has been updated successfully
  - Notes:
    - Only these JSON Key Values will be read: ID, Country, Brand, Type, Package, Minimum Rating
    - Any extra values like **ExID** will be ignored. If the database does not contain the corresponding review obejct with the provided **ID**, an error message would be returned
    - The values will be vaildated to ensure data integrity. The API will provide the error message if the data is of the incorrect type
### /api/delete
  - HTTP Method: POST
  - Input Data: A JSON object containing the ID of the review object to be deleted
  - Output data: A message indicating that the review object has been deleted successfully
  - Notes:
    - Only the **ID** JSON Key Values will be read
    - Any extra values like **ExID** will be ignored. If the database does not contain the corresponding review obejct with the provided **ID**, an error message would be returned
## Web App Reference
### /
Displays all reviews stored in the database or the filtered reviews based on the search criteria
### /create
Page for creating a new review
### /edit
Page for editing a review (An ID parameter must been passed in the URL e.g. `/Edit?ID=1`)