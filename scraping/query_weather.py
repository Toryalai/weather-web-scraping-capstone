import sqlite3
import pandas as pd
import os
from datetime import datetime


# CONFIGURATION
DATABASE_FILE = "data/weather.db"


# QUERY FUNCTIONS
def check_database_exists():

    if not os.path.exists(DATABASE_FILE):
        print(f"\nError: Database not found at {DATABASE_FILE}")
        print("Please run store_database.py first to create the database.")
        return False
    return True


def connect_database():

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def query_all_records(conn):

    print("ALL WEATHER RECORDS")
    print("=" * 80)
    
    query = """
        SELECT 
            id,
            city,
            time_clean as time,
            temperature_f as temp_f,
            weather,
            wind_mph,
            humidity_pct
        FROM weather 
        ORDER BY id DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("No records found in database.")
    else:
        print(f"\nTotal Records: {len(df)}")
        print("\n" + df.to_string(index=False))


def query_temperature_stats(conn):
    print("TEMPERATURE STATISTICS")
    print("=" * 80)
    
    query = """
        SELECT 
            city,
            COUNT(*) as total_records,
            MIN(temperature_f) as min_temp_f,
            MAX(temperature_f) as max_temp_f,
            ROUND(AVG(temperature_f), 1) as avg_temp_f,
            ROUND(MIN(temperature_c), 1) as min_temp_c,
            ROUND(MAX(temperature_c), 1) as max_temp_c,
            ROUND(AVG(temperature_c), 1) as avg_temp_c
        FROM weather 
        WHERE temperature_f IS NOT NULL
        GROUP BY city
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("No temperature data found.")
    else:
        print("\n" + df.to_string(index=False))


def query_humidity_distribution(conn):
    print("HUMIDITY DISTRIBUTION")
    print("=" * 80)
    
    query = """
        SELECT 
            CASE 
                WHEN humidity_pct < 30 THEN 'Low (0-29%)'
                WHEN humidity_pct < 60 THEN 'Medium (30-59%)'
                WHEN humidity_pct < 80 THEN 'High (60-79%)'
                ELSE 'Very High (80-100%)'
            END as humidity_range,
            COUNT(*) as count,
            ROUND(AVG(temperature_f), 1) as avg_temp_f
        FROM weather 
        WHERE humidity_pct IS NOT NULL
        GROUP BY humidity_range
        ORDER BY MIN(humidity_pct)
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("No humidity data found.")
    else:
        print("\n" + df.to_string(index=False))


def query_wind_analysis(conn):
    print("WIND SPEED ANALYSIS")
    print("=" * 80)
    
    query = """
        SELECT 
            city,
            MIN(wind_mph) as min_wind_mph,
            MAX(wind_mph) as max_wind_mph,
            ROUND(AVG(wind_mph), 1) as avg_wind_mph,
            ROUND(MIN(wind_kmh), 1) as min_wind_kmh,
            ROUND(MAX(wind_kmh), 1) as max_wind_kmh,
            ROUND(AVG(wind_kmh), 1) as avg_wind_kmh
        FROM weather 
        WHERE wind_mph IS NOT NULL
        GROUP BY city
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("No wind data found.")
    else:
        print("\n" + df.to_string(index=False))


def query_weather_conditions(conn):
    print("WEATHER CONDITIONS BREAKDOWN")
    print("=" * 80)
    
    query = """
        SELECT 
            weather as condition,
            COUNT(*) as occurrences,
            ROUND(AVG(temperature_f), 1) as avg_temp_f,
            ROUND(AVG(humidity_pct), 1) as avg_humidity
        FROM weather 
        WHERE weather IS NOT NULL AND weather != ''
        GROUP BY weather
        ORDER BY occurrences DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("No weather condition data found.")
    else:
        print("\n" + df.to_string(index=False))


def query_by_date(conn):
    print("RECORDS BY DATE")
    print("=" * 80)
    
    # First show available dates
    date_query = """
        SELECT DISTINCT scraped_date 
        FROM weather 
        ORDER BY scraped_date DESC
    """
    dates_df = pd.read_sql_query(date_query, conn)
    
    if len(dates_df) == 0:
        print("No records found.")
        return
    
    print("\nAvailable dates:")
    for idx, row in dates_df.iterrows():
        print(f"  {idx + 1}. {row['scraped_date']}")
    
    try:
        choice = input("\nEnter date number (or press Enter for all): ").strip()
        
        if choice == "":
            # Show all dates summary
            query = """
                SELECT 
                    scraped_date,
                    COUNT(*) as record_count,
                    ROUND(AVG(temperature_f), 1) as avg_temp_f,
                    ROUND(AVG(humidity_pct), 1) as avg_humidity
                FROM weather 
                GROUP BY scraped_date
                ORDER BY scraped_date DESC
            """
        else:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(dates_df):
                selected_date = dates_df.iloc[choice_idx]['scraped_date']
                query = f"""
                    SELECT 
                        time_clean as time,
                        temperature_f,
                        weather,
                        wind_mph,
                        humidity_pct
                    FROM weather 
                    WHERE scraped_date = '{selected_date}'
                    ORDER BY id
                """
            else:
                print("Invalid choice.")
                return
        
        df = pd.read_sql_query(query, conn)
        print("\n" + df.to_string(index=False))
        
    except (ValueError, IndexError):
        print("Invalid input.")


def query_extreme_conditions(conn):
    print("EXTREME CONDITIONS")
    print("=" * 80)
    
    # Hottest
    print("\nHottest Recorded:")
    query = """
        SELECT 
            time_clean as time,
            temperature_f,
            weather,
            humidity_pct,
            scraped_date
        FROM weather 
        WHERE temperature_f = (SELECT MAX(temperature_f) FROM weather)
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    # Coldest
    print("\nColdest Recorded:")
    query = """
        SELECT 
            time_clean as time,
            temperature_f,
            weather,
            humidity_pct,
            scraped_date
        FROM weather 
        WHERE temperature_f = (SELECT MIN(temperature_f) FROM weather)
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    # Windiest
    print("\nWindiest Recorded:")
    query = """
        SELECT 
            time_clean as time,
            wind_mph,
            weather,
            temperature_f,
            scraped_date
        FROM weather 
        WHERE wind_mph = (SELECT MAX(wind_mph) FROM weather)
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    # Most Humid
    print("\nMost Humid Recorded:")
    query = """
        SELECT 
            time_clean as time,
            humidity_pct,
            temperature_f,
            weather,
            scraped_date
        FROM weather 
        WHERE humidity_pct = (SELECT MAX(humidity_pct) FROM weather)
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))


def custom_query(conn):
    print("CUSTOM SQL QUERY")
    print("=" * 80)
    print("\nTable: weather")
    print("Columns: id, city, time, time_clean, temperature_f, temperature_c,")
    print("         weather, wind_mph, wind_kmh, humidity_pct, scraped_at,")
    print("         scraped_date, created_at")
    print("\nExample: SELECT * FROM weather WHERE temperature_f > 80 LIMIT 10")
    print("\n" + "=" * 80)
    
    query = input("\nEnter SQL query: ").strip()
    
    if not query:
        print("No query entered.")
        return
    
    try:
        df = pd.read_sql_query(query, conn)
        print(f"\nQuery Results ({len(df)} rows):")
        print("\n" + df.to_string(index=False))
        
        # Ask if user wants to export
        export = input("\nExport results to CSV? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"data/query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"Results exported to: {filename}")
            
    except Exception as e:
        print(f"Error executing query: {e}")


def export_all_data(conn):
    print("EXPORT DATABASE")
    print("=" * 80)
    
    query = "SELECT * FROM weather"
    df = pd.read_sql_query(query, conn)
    
    filename = f"data/weather_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"\nExported {len(df)} records to: {filename}")


# MAIN MENU
def display_menu():
    print(" WEATHER DATABASE QUERY TOOL")
    print("=" * 80)
    print("\n  Select a query option:\n")
    print("  1   View All Records")
    print("  2   Temperature Statistics")
    print("  3   Humidity Distribution")
    print("  4   Wind Speed Analysis")
    print("  5   Weather Conditions Breakdown")
    print("  6   Query by Date")
    print("  7   Extreme Conditions")
    print("  8   Custom SQL Query")
    print("  9   Export All Data to CSV")
    print("  0   Exit")
    print("\n" + "=" * 80)


def main():
    # Check if database exists
    if not check_database_exists():
        return
    
    # Connect to database
    conn = connect_database()
    if not conn:
        return
    
    print("\nConnected to database successfully!")
    
    # Get record count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM weather")
    record_count = cursor.fetchone()[0]
    print(f"Total records in database: {record_count}")
    
    # Main menu loop
    while True:
        display_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == '1':
            query_all_records(conn)
        elif choice == '2':
            query_temperature_stats(conn)
        elif choice == '3':
            query_humidity_distribution(conn)
        elif choice == '4':
            query_wind_analysis(conn)
        elif choice == '5':
            query_weather_conditions(conn)
        elif choice == '6':
            query_by_date(conn)
        elif choice == '7':
            query_extreme_conditions(conn)
        elif choice == '8':
            custom_query(conn)
        elif choice == '9':
            export_all_data(conn)
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number from 0-9.")
        
        input("\nPress Enter to continue...")
    
    # Close connection
    conn.close()
    print("Database connection closed.")


if __name__ == "__main__":
    main()