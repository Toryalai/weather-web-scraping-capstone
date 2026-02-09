# Weather Scraping Capstone Project

## Overview
This project is part of the Code the Dream Python course web scraping capstone.
The goal is to scrape hourly weather data from a public website, clean and
structure the data, and prepare it for storage and visualization in later phases.

## Key Features

- **Automated Web Scraping**: Uses Selenium to extract hourly weather data
- **Data Cleaning Pipeline**: Transforms raw scraped data into structured, validated datasets
- **Database Storage**: Stores clean data in SQLite with proper indexing
- **Interactive Dashboard**: Streamlit-based visualization with 4+ interactive charts
- **Command-Line Queries**: Tool for exploring data via SQL queries
- **Robust Error Handling**: Handles missing data, duplicates, and pagination
- **Professional Code Quality**: Well-documented, modular, and maintainable

## Setup Instructions

- Python 3.8 or higher
- Google Chrome browser (for Selenium)
- pip (Python package manager)

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Toryalai/weather-web-scraping-capstone.git
   cd weather-web-scraping-capstone
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create data directory**
   ```bash
   mkdir data
   ```

## Usage Guide

### Step 1: Scrape Weather Data

Run the web scraping script to collect hourly weather data:

```bash
python scrape_weather.py
```

**What it does:**
- Navigates to timeanddate.com weather page
- Extracts hourly weather forecasts (temperature, humidity, wind, conditions)
- Saves raw data to `data/raw_weather.csv`
- Implements duplicate checking to avoid redundant scraping
- Uses user-agent headers for ethical scraping

**Output:** `data/raw_weather.csv`

---

### Step 2: Clean and Transform Data

Process the raw data to prepare it for analysis:

```bash
python clean_weather.py
```

**What it does:**
- Loads raw CSV data
- Removes duplicates
- Cleans and validates temperature, humidity, and wind data
- Converts units (adds Celsius, km/h)
- Handles missing values
- Shows before/after comparison
- Saves cleaned data to CSV

**Output:** `data/clean_weather.csv`

---

### Step 3: Store in Database

Load the cleaned data into a SQLite database:

```bash
python store_database.py
```

**What it does:**
- Creates SQLite database and weather table
- Inserts cleaned data with duplicate checking
- Creates indexes for query performance
- Displays sample queries
- Shows database statistics

**Output:** `data/weather.db`

---

### Step 4: Query the Database

Explore the data using the interactive command-line tool:

```bash
python query_weather.py
```

**Available Queries:**
1. View all records
2. Temperature statistics
3. Humidity distribution
4. Wind speed analysis
5. Weather conditions breakdown
6. Query by date
7. Extreme conditions
8. Custom SQL queries
9. Export data to CSV

---

### Step 5: Launch the Dashboard

Start the interactive Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

**Dashboard Features:**
- Key metrics (avg temperature, humidity, wind speed)
- Temperature trends over time
- Weather conditions distribution (pie chart & bar chart)
- Humidity vs Temperature scatter plot
- Wind speed analysis (histogram & box plot)
- Interactive filters (date, temperature range, weather conditions)
- Searchable data table
- CSV export functionality