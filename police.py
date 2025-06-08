import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# PostgreSQL connection setup
db_user = 'postgres'
db_password = '1234'
db_host = 'localhost'
db_port = '5432'
db_name = 'securecheck_db'

engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Page settings
st.set_page_config(page_title="SecureCheck Dashboard", layout="wide")
st.title("🚨 SecureCheck Police Logs Dashboard")

# Load data from PostgreSQL
@st.cache_data
def load_data():
    query = "SELECT * FROM police_logs"
    return pd.read_sql(query, engine)

df = load_data()

# Show available columns (for dev/debug)
st.write("📄 Available Columns:", df.columns.tolist())

# Section 1: View the full log
st.subheader("📋 Police Log Entries")
st.dataframe(df)

# Section 2: Show one example summary
st.subheader("📝 Stop Summary")
if not df.empty:
    row = df.iloc[0]
    summary = f"""
    🚗 A {row['driver_age']}-year-old {row['driver_gender']} driver was stopped for **{row['violation']}** at {row['stop_time']}.
    {"A search was conducted." if row['search_conducted'] else "No search was conducted."}
    {"The stop was drug-related." if row['drugs_related_stop'] else "It was not drug-related."}
    """
    st.markdown(summary)
else:
    st.warning("No police logs found.")

# Section 3: SQL Query Based Insights
st.subheader("📊 Quick SQL Query Insights")

# Full query selection dropdown with 15 queries
query_option = st.selectbox("Select a query to run", [
    # 🚗 Vehicle-Based
    "Top 10 Drug-Related Vehicle Numbers",
    "Most Frequently Searched Vehicles",

    # 🧍 Demographic-Based
    "Highest Arrest Rate by Driver Age Group",
    "Gender Distribution by Country",
    "Race-Gender Combination with Highest Search Rate",

    # 🕒 Time & Duration-Based
    "Peak Traffic Stop Time of Day",
    "Average Stop Duration by Violation",
    "Nighttime Stops Leading to Arrest",

    # ⚖️ Violation-Based
    "Violations Most Associated with Searches or Arrests",
    "Most Common Violations Among Drivers Under 25",
    "Violations That Rarely Lead to Search or Arrest",

    # 🌍 Location-Based
    "Countries with Most Drug-Related Stops",
    "Arrest Rate by Country and Violation",
    "Country with Most Searches Conducted",

    # 🧠 Complex Analysis
    "Yearly Breakdown of Stops and Arrests by Country"
])

query_sql = None

if query_option == "Top 10 Drug-Related Vehicle Numbers":
    query_sql = """
        SELECT vehicle_number, COUNT(*) AS count
        FROM police_logs
        WHERE violation ILIKE '%drug%'
        GROUP BY vehicle_number
        ORDER BY count DESC
        LIMIT 10;
    """
    st.code(query_sql)

elif query_option == "Most Frequently Searched Vehicles":
    query_sql = """
        SELECT vehicle_number, COUNT(*) AS search_count
        FROM police_logs
        WHERE search_conducted = true
        GROUP BY vehicle_number
        ORDER BY search_count DESC
        LIMIT 10;
    """
    

elif query_option == "Highest Arrest Rate by Driver Age Group":
    query_sql = """
        SELECT driver_age, ROUND(AVG(CASE WHEN is_arrested = true THEN 1 ELSE 0 END)*100, 2) AS arrest_rate
        FROM police_logs
        GROUP BY driver_age
        ORDER BY arrest_rate DESC
        LIMIT 5;
    """
    st.code(query_sql)

elif query_option == "Gender Distribution by Country":
    query_sql = """
        SELECT country_name, driver_gender, COUNT(*) AS count
        FROM police_logs
        GROUP BY country_name, driver_gender
        ORDER BY country_name, count DESC;
    """
    st.code(query_sql)

elif query_option == "Race-Gender Combination with Highest Search Rate":
    query_sql = """
        SELECT driver_race, driver_gender,
               ROUND(AVG(CASE WHEN search_conducted = true THEN 1 ELSE 0 END)*100, 2) AS search_rate
        FROM police_logs
        GROUP BY driver_race, driver_gender
        ORDER BY search_rate DESC
        LIMIT 1;
    """
    st.code(query_sql)

elif query_option == "Peak Traffic Stop Time of Day":
    query_sql = """
        SELECT EXTRACT(HOUR FROM stop_time::timestamp) AS hour, COUNT(*) AS stop_count
        FROM police_logs
        GROUP BY hour
        ORDER BY stop_count DESC;
    """
    st.code(query_sql)

elif query_option == "Average Stop Duration by Violation":
    query_sql = """
        SELECT violation, ROUND(AVG(stop_duration), 2) AS avg_duration
        FROM police_logs
        GROUP BY violation
        ORDER BY avg_duration DESC;
    """
    st.code(query_sql)

elif query_option == "Nighttime Stops Leading to Arrest":
    query_sql = """
        SELECT COUNT(*) AS night_arrests
        FROM police_logs
        WHERE EXTRACT(HOUR FROM stop_time) BETWEEN 20 AND 23
          AND is_arrested = true;
    """
    st.code(query_sql)

elif query_option == "Violations Most Associated with Searches or Arrests":
    query_sql = """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = true THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN is_arrested = true THEN 1 ELSE 0 END) AS arrests
        FROM police_logs
        GROUP BY violation
        ORDER BY searches DESC, arrests DESC
        LIMIT 5;
    """
    st.code(query_sql)

elif query_option == "Most Common Violations Among Drivers Under 25":
    query_sql = """
        SELECT violation, COUNT(*) AS count
        FROM police_logs
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY count DESC
        LIMIT 5;
    """
    st.code(query_sql)

elif query_option == "Violations That Rarely Lead to Search or Arrest":
    query_sql = """
        SELECT violation,
               COUNT(*) AS total,
               SUM(CASE WHEN search_conducted = true THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN is_arrested = true THEN 1 ELSE 0 END) AS arrests
        FROM police_logs
        GROUP BY violation
        HAVING SUM(CASE WHEN search_conducted = true THEN 1 ELSE 0 END) = 0
            AND SUM(CASE WHEN is_arrested = true THEN 1 ELSE 0 END) = 0
        ORDER BY total DESC;
    """
    st.code(query_sql)

elif query_option == "Countries with Most Drug-Related Stops":
    query_sql = """
        SELECT country_name, COUNT(*) AS drug_stops
        FROM police_logs
        WHERE violation ILIKE '%drug%'
        GROUP BY country_name
        ORDER BY drug_stops DESC;
    """
    st.code(query_sql)

elif query_option == "Arrest Rate by Country and Violation":
    query_sql = """
        SELECT country_name, violation,
               ROUND(AVG(CASE WHEN is_arrested = true THEN 1 ELSE 0 END)*100, 2) AS arrest_rate
        FROM police_logs
        GROUP BY country_name, violation
        ORDER BY arrest_rate DESC;
    """
    st.code(query_sql)

elif query_option == "Country with Most Searches Conducted":
    query_sql = """
        SELECT country_name, COUNT(*) AS search_count
        FROM police_logs
        WHERE search_conducted = true
        GROUP BY country_name
        ORDER BY search_count DESC
        LIMIT 1;
    """
    st.code(query_sql)

elif query_option == "Yearly Breakdown of Stops and Arrests by Country":
    query_sql = """
        SELECT country_name,
               EXTRACT(YEAR FROM stop_date) AS year,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = true THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(AVG(CASE WHEN is_arrested = true THEN 1 ELSE 0 END)*100, 2) AS arrest_rate
        FROM police_logs
        GROUP BY country_name, year
        ORDER BY year, country_name;
    """
    st.code(query_sql)

if st.button("Run Query") and query_sql:
    try:
        result = pd.read_sql(sql=query_sql, con=engine)
        st.dataframe(result)
    except Exception as e:
        st.error(f"❌ Error running query: {e}")