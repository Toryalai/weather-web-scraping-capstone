import pandas as pd

RAW_FILE = "data/raw_weather.csv"
CLEAN_FILE = "data/clean_weather.csv"

# --- Load raw data ---
df = pd.read_csv(RAW_FILE)

print("Raw Data Sample:")
print(df.head())
print("\nRows before cleaning:", len(df))

# --- Cleaning helpers ---
def clean_temperature(temp):
    if pd.isna(temp):
        return None
    return int(temp.replace("°F", "").strip())

def clean_wind(wind):
    if pd.isna(wind):
        return None
    return int(wind.replace("mph", "").strip())

def clean_humidity(hum):
    if pd.isna(hum):
        return None
    return int(hum.replace("%", "").strip())

# --- Apply cleaning ---
df["Temperature_F"] = df["Temperature"].apply(clean_temperature)
df["Wind_mph"] = df["Wind"].apply(clean_wind)
df["Humidity_pct"] = df["Humidity"].apply(clean_humidity)

# --- Drop old columns ---
df.drop(columns=["Temperature", "Wind", "Humidity"], inplace=True)

# --- Remove duplicates ---
df.drop_duplicates(inplace=True)

print("\nCleaned Data Sample:")
print(df.head())
print("\nRows after cleaning:", len(df))

# --- Save cleaned data ---
df.to_csv(CLEAN_FILE, index=False)

print(f"\nCleaned weather data saved to {CLEAN_FILE}")
