# Police_Log
Used VScode and PostgreSQL for working this project
As a first step I saved the CSV file to a known location in my  C FOLDER 
Using VS code installed all the necessary packages and libraries like pandas, streamlit
Now I have to access the csv file using python and creating a data frame and reading it 
As a next step, im removing the columns that contain only missing values and replacing the nan values in the column as "unknown"
next step is to change the unstructured data into a structured data - here i have changed the format of the year and the timestamp 
For Database Design (SQL)Installing pip install sqlalchemy in the vs code,Next opening the pgadmin, and created a new database "securecheck_db"
In the SQL terminal i have used the code to create a table "traffic_stops" - now we can see the table in the database created 
Now using PostgreSQL connection details and Inserted the DataFrame into the police_logs table successfully
Now for the data output in streamlit  Dashboard created a police.py file 
For the Dashboard Layout, The app title and layout are defined using st.set_page_config() and st.title() and The full police logs are displayed in a dataframe for overview and debugging purposes.
have given a simple textual summary
For SQL-Based Query Selector, given a dropdown that = allows users to choose from 15 predefined analytical queries.
When the "Run Query" button is clicked, the selected SQL query is executed using pandas' read_sql().




