import sqlite3
import pandas as pd
from datetime import datetime
import os

# CONFIGURATION
CLEAN_FILE = "data/clean_weather.csv"
DATABASE_FILE = "data/weather.db"

# DATABASE FUNCTIONS

def create_database():

    # Create data directory if needed
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    
    # Connect to database 
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create weather table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            time TEXT,
            time_clean TEXT,
            temperature_f INTEGER,
            temperature_c REAL,
            weather TEXT,
            wind_mph INTEGER,
            wind_kmh REAL,
            humidity_pct INTEGER,
            scraped_at TEXT,
            scraped_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, time, scraped_at)
        )
    """)
    
    # Create indexes for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_city 
        ON weather(city)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_temperature 
        ON weather(temperature_f)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_scraped_date 
        ON weather(scraped_date)
    """)
    
    conn.commit()
    print("Database and table created")
    
    return conn


def get_record_count(conn):

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM weather")
    count = cursor.fetchone()[0]
    return count


def insert_weather_data(conn, df):

    cursor = conn.cursor()
    records_inserted = 0
    duplicates_skipped = 0
    
    # Prepare column mapping
    column_mapping = {
        'City': 'city',
        'Time': 'time',
        'Time_Clean': 'time_clean',
        'Temperature_F': 'temperature_f',
        'Temperature_C': 'temperature_c',
        'Weather': 'weather',
        'Wind_mph': 'wind_mph',
        'Wind_kmh': 'wind_kmh',
        'Humidity_pct': 'humidity_pct',
        'Scraped_At': 'scraped_at',
        'Scraped_Date': 'scraped_date'
    }
    
    # Process each row
    for idx, row in df.iterrows():
        try:
            # Build insert statement
            insert_sql = """
                INSERT OR IGNORE INTO weather 
                (city, time, time_clean, temperature_f, temperature_c, weather, 
                 wind_mph, wind_kmh, humidity_pct, scraped_at, scraped_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            values = (
                row.get('City'),
                row.get('Time'),
                row.get('Time_Clean'),
                row.get('Temperature_F'),
                row.get('Temperature_C'),
                row.get('Weather'),
                row.get('Wind_mph'),
                row.get('Wind_kmh'),
                row.get('Humidity_pct'),
                row.get('Scraped_At'),
                row.get('Scraped_Date')
            )
            
            cursor.execute(insert_sql, values)
            
            # Check if insert was successful
            if cursor.rowcount > 0:
                records_inserted += 1
            else:
                duplicates_skipped += 1
                
        except sqlite3.IntegrityError:
            duplicates_skipped += 1
            continue
        except Exception as e:
            print(f"Error inserting row {idx}: {e}")
            continue
    
    conn.commit()
    return records_inserted, duplicates_skipped


def display_sample_queries(conn):

    print("\n" + "=" * 70)
    print("SAMPLE QUERIES")
    print("=" * 70)
    
    # Query 1: Latest 5 records
    print("\n1 Latest 5 Weather Records:")
    print("-" * 70)
    df = pd.read_sql_query("""
        SELECT city, time_clean, temperature_f, weather, humidity_pct 
        FROM weather 
        ORDER BY id DESC 
        LIMIT 5
    """, conn)
    print(df.to_string(index=False))
    
    # Query 2: Temperature statistics
    print("\n2 Temperature Statistics:")
    print("-" * 70)
    df = pd.read_sql_query("""
        SELECT 
            city,
            COUNT(*) as record_count,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            AVG(temperature_f) as avg_temp
        FROM weather 
        WHERE temperature_f IS NOT NULL
        GROUP BY city
    """, conn)
    print(df.to_string(index=False))
    
    # Query 3: Humidity ranges
    print("\n3 Humidity Distribution:")
    print("-" * 70)
    df = pd.read_sql_query("""
        SELECT 
            CASE 
                WHEN humidity_pct < 30 THEN 'Low (0-29%)'
                WHEN humidity_pct < 60 THEN 'Medium (30-59%)'
                WHEN humidity_pct < 80 THEN 'High (60-79%)'
                ELSE 'Very High (80-100%)'
            END as humidity_range,
            COUNT(*) as count
        FROM weather 
        WHERE humidity_pct IS NOT NULL
        GROUP BY humidity_range
        ORDER BY MIN(humidity_pct)
    """, conn)
    print(df.to_string(index=False))
    
    # Query 4: Wind speed analysis
    print("\n4 Wind Speed Analysis:")
    print("-" * 70)
    df = pd.read_sql_query("""
        SELECT 
            MIN(wind_mph) as min_wind,
            MAX(wind_mph) as max_wind,
            AVG(wind_mph) as avg_wind,
            COUNT(*) as total_records
        FROM weather 
        WHERE wind_mph IS NOT NULL
    """, conn)
    print(df.to_string(index=False))
    
    # Query 5: Records per scrape date
    print("\n5 Records by Scrape Date:")
    print("-" * 70)
    df = pd.read_sql_query("""
        SELECT 
            scraped_date,
            COUNT(*) as record_count
        FROM weather 
        GROUP BY scraped_date
        ORDER BY scraped_date DESC
        LIMIT 5
    """, conn)
    print(df.to_string(index=False))
    
    print("=" * 70)


# MAIN EXECUTION
def main():

    print("WEATHER DATABASE STORAGE SCRIPT")
    print("=" * 70)
    print(f"Input File: {CLEAN_FILE}")
    print(f"Database: {DATABASE_FILE}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # STEP 1: Check if cleaned data exists
    print("\nStep 1: Checking for cleaned data...")
    
    if not os.path.exists(CLEAN_FILE):
        print(f"Error: Cleaned data file not found at {CLEAN_FILE}")
        print("Please run clean_weather.py first to generate cleaned data.")
        return
    
    print(f"Found cleaned data file")
    
    # STEP 2: Load cleaned data
    print("\nStep 2: Loading cleaned data...")
    df = pd.read_csv(CLEAN_FILE)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    
    # STEP 3: Create/connect to database
    print("\nStep 3: Creating/connecting to database...")
    conn = create_database()
    
    # Check existing records
    existing_count = get_record_count(conn)
    print(f"Existing records in database: {existing_count}")

    # STEP 4: Insert data into database
    print("\nStep 4: Inserting data into database...")
    records_inserted, duplicates_skipped = insert_weather_data(conn, df)
    
    print(f"Insertion complete:")
    print(f"- Records inserted: {records_inserted}")
    print(f"- Duplicates skipped: {duplicates_skipped}")
    
    # Check new total
    new_count = get_record_count(conn)
    print(f"Total records in database: {new_count}")
    
    # STEP 5: Display sample queries
    print("\nStep 5: Running sample queries...")
    display_sample_queries(conn)
    
    # STEP 6: Database information
    
    print("DATABASE INFORMATION")
    print("=" * 70)
    print(f"Database file: {DATABASE_FILE}")
    print(f"Database size: {os.path.getsize(DATABASE_FILE) / 1024:.2f} KB")
    print(f"Total records: {new_count}")
    
    # Get table schema
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(weather)")
    schema = cursor.fetchall()
    
    print("\nTable Schema:")
    print(f"{'Column':<20} {'Type':<15} {'Not Null':<10}")
    print("-" * 70)
    for col in schema:
        print(f"{col[1]:<20} {col[2]:<15} {'Yes' if col[3] else 'No':<10}")

    # STEP 7: Close connection
    conn.close()
    print("\nDatabase connection closed")
    
    print("\n" + "=" * 70)
    print("DATABASE STORAGE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Run query_weather.py to query the database")
    print("2. Run streamlit run dashboard.py to view visualizations")


if __name__ == "__main__":
    main()