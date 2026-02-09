import pandas as pd
import numpy as np
from datetime import datetime
import os

# CONFIGURATION

RAW_FILE = "data/raw_weather.csv"
CLEAN_FILE = "data/clean_weather.csv"

# HELPER FUNCTIONS
def clean_temperature(temp):

    if pd.isna(temp) or temp is None or temp == '':
        return None
    
    try:
        # Remove °F and any extra whitespace
        cleaned = str(temp).replace("°F", "").replace("°", "").strip()
        return int(cleaned)
    except (ValueError, AttributeError):
        print(f"Could not parse temperature: '{temp}'")
        return None


def clean_wind(wind):

    if pd.isna(wind) or wind is None or wind == '':
        return None
    
    try:
        # Remove mph and any extra text
        cleaned = str(wind).replace("mph", "").strip()
        
        # Handle ranges 
        if '-' in cleaned:
            parts = cleaned.split('-')
            return int((int(parts[0]) + int(parts[1])) / 2)
        
        return int(cleaned)
    except (ValueError, AttributeError):
        print(f"Could not parse wind: '{wind}'")
        return None


def clean_humidity(hum):

    if pd.isna(hum) or hum is None or hum == '':
        return None
    
    try:
        # Remove % sign and whitespace
        cleaned = str(hum).replace("%", "").strip()
        value = int(cleaned)
        
        # Validate humidity is in reasonable range (0-100%)
        if 0 <= value <= 100:
            return value
        else:
            print(f"Humidity out of range: {value}%")
            return None
            
    except (ValueError, AttributeError):
        print(f"Could not parse humidity: '{hum}'")
        return None


def parse_time(time_str):

    if pd.isna(time_str):
        return None
    return str(time_str).strip()


def print_data_summary(df, title="Data Summary"):
 
    print(f"  {title}")
    print("=" * 70)
    print(f"Total Rows: {len(df)}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"\nColumns: {list(df.columns)}")
    print("\n" + "-" * 70)
    print("First 5 Rows:")
    print(df.head())
    print("\n" + "-" * 70)
    print("Data Types:")
    print(df.dtypes)
    print("\n" + "-" * 70)
    print("Missing Values:")
    print(df.isnull().sum())
    print("=" * 70)


def print_cleaning_comparison(before_df, after_df):

    print("CLEANING COMPARISON")
    print("=" * 70)
    
    print(f"\n{'Metric':<30} {'Before':<15} {'After':<15} {'Change':<15}")
    print("-" * 70)
    
    # Row count
    rows_before = len(before_df)
    rows_after = len(after_df)
    rows_diff = rows_after - rows_before
    print(f"{'Total Rows:':<30} {rows_before:<15} {rows_after:<15} {rows_diff:+<15}")
    
    # Column count
    cols_before = len(before_df.columns)
    cols_after = len(after_df.columns)
    cols_diff = cols_after - cols_before
    print(f"{'Total Columns:':<30} {cols_before:<15} {cols_after:<15} {cols_diff:+<15}")
    
    # Missing values 
    common_cols = set(before_df.columns) & set(after_df.columns)
    if common_cols:
        null_before = before_df.isnull().sum().sum()
        null_after = after_df.isnull().sum().sum()
        null_diff = null_after - null_before
        print(f"{'Total Missing Values:':<30} {null_before:<15} {null_after:<15} {null_diff:+<15}")
    
    # Duplicates
    dup_before = before_df.duplicated().sum()
    dup_after = after_df.duplicated().sum()
    dup_diff = dup_after - dup_before
    print(f"{'Duplicate Rows:':<30} {dup_before:<15} {dup_after:<15} {dup_diff:+<15}")
    
    print("=" * 70)


# MAIN CLEANING PROCESS

def main():

    print("WEATHER DATA CLEANING SCRIPT")
    print("=" * 70)
    print(f"Input File: {RAW_FILE}")
    print(f"Output File: {CLEAN_FILE}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # STEP 1: Load Raw Data
    
    print("\nStep 1: Loading raw data...")
    
    if not os.path.exists(RAW_FILE):
        print(f"Error: Raw data file not found at {RAW_FILE}")
        print("Please run scrape_weather.py first to generate raw data.")
        return
    
    df_raw = pd.read_csv(RAW_FILE)
    print(f"Loaded {len(df_raw)} rows from {RAW_FILE}")
    
    # Display raw data summary
    print_data_summary(df_raw, "RAW DATA SUMMARY")
    
    # Create a copy for cleaning
    df = df_raw.copy()
    
    # STEP 2: Remove Duplicates
    
    print("\nStep 2: Removing duplicate entries...")
    rows_before = len(df)
    df.drop_duplicates(inplace=True)
    rows_after = len(df)
    duplicates_removed = rows_before - rows_after
    print(f"Removed {duplicates_removed} duplicate rows")
    
    # STEP 3: Clean and Transform Data

    print("\nStep 3: Cleaning and transforming data...")
    
    # Clean Time field
    if 'Time' in df.columns:
        df['Time_Clean'] = df['Time'].apply(parse_time)
        print("Cleaned time values")
    
    # Clean Temperature
    if 'Temperature' in df.columns:
        df["Temperature_F"] = df["Temperature"].apply(clean_temperature)
        print(f"Cleaned temperature values")
        print(f"- Valid values: {df['Temperature_F'].notna().sum()}")
        print(f"- Missing values: {df['Temperature_F'].isna().sum()}")
    
    # Clean Wind
    if 'Wind' in df.columns:
        df["Wind_mph"] = df["Wind"].apply(clean_wind)
        print(f"Cleaned wind values")
        print(f"- Valid values: {df['Wind_mph'].notna().sum()}")
        print(f"- Missing values: {df['Wind_mph'].isna().sum()}")
    
    # Clean Humidity
    if 'Humidity' in df.columns:
        df["Humidity_pct"] = df["Humidity"].apply(clean_humidity)
        print(f"Cleaned humidity values")
        print(f"- Valid values: {df['Humidity_pct'].notna().sum()}")
        print(f"- Missing values: {df['Humidity_pct'].isna().sum()}")
    
    # STEP 4: Drop Original Unclean Columns
    
    print("\nStep 4: Removing original unclean columns...")
    columns_to_drop = ['Temperature', 'Wind', 'Humidity']
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    
    if existing_columns:
        df.drop(columns=existing_columns, inplace=True)
        print(f"Dropped columns: {existing_columns}")
    
    # STEP 5: Handle Missing Values
    print("\nStep 5: Handling missing values...")
    
    # Count missing values before
    missing_before = df.isnull().sum().sum()
    
    # Remove rows where ALL numeric columns are null
    numeric_cols = ['Temperature_F', 'Wind_mph', 'Humidity_pct']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    
    if numeric_cols:
        rows_before = len(df)
        df = df.dropna(subset=numeric_cols, how='all')
        rows_after = len(df)
        rows_removed = rows_before - rows_after
        print(f"Removed {rows_removed} rows with all missing numeric values")
    
    missing_after = df.isnull().sum().sum()
    print(f"Missing values: {missing_before} → {missing_after}")
    

    # STEP 6: Add Derived Features
    print("\nStep 6: Adding derived features...")
    
    # Add temperature in Celsius
    if 'Temperature_F' in df.columns:
        df['Temperature_C'] = df['Temperature_F'].apply(
            lambda x: round((x - 32) * 5/9, 1) if pd.notna(x) else None
        )
        print("Added Temperature_C (Celsius)")
    
    # Add wind speed in km/h
    if 'Wind_mph' in df.columns:
        df['Wind_kmh'] = df['Wind_mph'].apply(
            lambda x: round(x * 1.60934, 1) if pd.notna(x) else None
        )
        print("Added Wind_kmh (kilometers per hour)")
    
    # Parse scraped timestamp
    if 'Scraped_At' in df.columns:
        df['Scraped_Date'] = pd.to_datetime(df['Scraped_At']).dt.date
        print("Added Scraped_Date")
    
    # STEP 7: Data Validation
    print("\nStep 7: Validating cleaned data...")
    
    issues = []
    
    # Check temperature range
    if 'Temperature_F' in df.columns:
        temp_min = df['Temperature_F'].min()
        temp_max = df['Temperature_F'].max()
        if temp_min < -50 or temp_max > 150:
            issues.append(f"Temperature out of range: {temp_min}°F to {temp_max}°F")
        else:
            print(f"Temperature range valid: {temp_min}°F to {temp_max}°F")
    
    # Check wind speed range
    if 'Wind_mph' in df.columns:
        wind_max = df['Wind_mph'].max()
        if wind_max > 200:
            issues.append(f"Wind speed suspiciously high: {wind_max} mph")
        else:
            print(f"Wind speed range valid: 0 to {wind_max} mph")
    
    # Check humidity range
    if 'Humidity_pct' in df.columns:
        invalid_humidity = df[
            (df['Humidity_pct'] < 0) | (df['Humidity_pct'] > 100)
        ]
        if len(invalid_humidity) > 0:
            issues.append(f"Found {len(invalid_humidity)} invalid humidity values")
        else:
            print(f"Humidity range valid: 0% to 100%")
    
    if issues:
        print("\nValidation Issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\nAll validation checks passed!")
    
    # STEP 8: Display Results

    # Show cleaned data summary
    print_data_summary(df, "CLEANED DATA SUMMARY")
    
    # Show before/after comparison
    print_cleaning_comparison(df_raw, df)
    
    # STEP 9: Save Cleaned Data
    print("\nStep 9: Saving cleaned data...")
    
    # Create data directory if needed
    os.makedirs(os.path.dirname(CLEAN_FILE), exist_ok=True)
    
    # Save to CSV
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Cleaned data saved to: {CLEAN_FILE}")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Show sample of final data
    print("\nSample of cleaned data:")
    print(df.head(10).to_string())
    
    print("\n" + "=" * 70)
    print("DATA CLEANING COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()