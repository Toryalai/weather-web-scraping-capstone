import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from datetime import datetime

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="Weather",
    layout="wide",
    initial_sidebar_state="expanded"
)


# DATABASE FUNCTIONS
DATABASE_FILE = "data/weather.db"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():

    if not os.path.exists(DATABASE_FILE):
        return None
    
    conn = sqlite3.connect(DATABASE_FILE)
    query = "SELECT * FROM weather ORDER BY id"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert date columns
    if 'scraped_at' in df.columns:
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    if 'scraped_date' in df.columns:
        df['scraped_date'] = pd.to_datetime(df['scraped_date'])
    
    return df


# MAIN DASHBOARD
def main():

    st.title("Weather Data Dashboard")
    st.markdown("""
    Welcome to the **Weather Data Dashboard**! This interactive tool visualizes hourly 
    weather data scraped from [timeanddate.com](https://www.timeanddate.com/weather/usa/washington-dc/hourly).
    
    Use the sidebar filters to customize your view and explore different aspects of the weather data.
    """)
    
    st.markdown("---")
    
    # LOAD DATA
    with st.spinner("Loading weather data from database..."):
        df = load_data()
    
    if df is None or len(df) == 0:
        st.error("No data found in database!")
        st.info("Please run the following scripts in order:")
        st.code("""
                1. python scrape_weather.py
                2. python clean_weather.py
                3. python store_database.py
        """)
        return
    
    st.success(f"Loaded {len(df)} weather records")
    
    # SIDEBAR FILTERS
    st.sidebar.header("Filters & Controls")
    
    # Date filter
    if 'scraped_date' in df.columns and df['scraped_date'].notna().any():
        available_dates = sorted(df['scraped_date'].dropna().dt.date.unique())
        
        if len(available_dates) > 0:
            selected_dates = st.sidebar.multiselect(
                "Select Scrape Date(s)",
                options=available_dates,
                default=available_dates,
                help="Filter data by the date it was scraped"
            )
            
            if selected_dates:
                df = df[df['scraped_date'].dt.date.isin(selected_dates)]
    
    # Temperature filter
    if 'temperature_f' in df.columns and df['temperature_f'].notna().any():
        temp_min = int(df['temperature_f'].min())
        temp_max = int(df['temperature_f'].max())
        
        temp_range = st.sidebar.slider(
            "Temperature Range (°F)",
            min_value=temp_min,
            max_value=temp_max,
            value=(temp_min, temp_max),
            help="Filter data by temperature range"
        )
        
        df = df[
            (df['temperature_f'] >= temp_range[0]) & 
            (df['temperature_f'] <= temp_range[1])
        ]
    
    # Weather condition filter
    if 'weather' in df.columns and df['weather'].notna().any():
        weather_conditions = sorted(df['weather'].dropna().unique())
        
        if len(weather_conditions) > 0:
            selected_conditions = st.sidebar.multiselect(
                "Weather Condition(s)",
                options=weather_conditions,
                default=weather_conditions,
                help="Filter by weather condition"
            )
            
            if selected_conditions:
                df = df[df['weather'].isin(selected_conditions)]
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Filtered Records:** {len(df)}")
    
    # KEY METRICS
    st.header("Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'temperature_f' in df.columns:
            avg_temp = df['temperature_f'].mean()
            st.metric(
                label="Average Temperature",
                value=f"{avg_temp:.1f}°F",
                delta=f"{avg_temp - 32:.1f}°C"
            )
        else:
            st.metric("Average Temperature", "N/A")
    
    with col2:
        if 'humidity_pct' in df.columns:
            avg_humidity = df['humidity_pct'].mean()
            st.metric(
                label="Average Humidity",
                value=f"{avg_humidity:.1f}%"
            )
        else:
            st.metric("Average Humidity", "N/A")
    
    with col3:
        if 'wind_mph' in df.columns:
            avg_wind = df['wind_mph'].mean()
            st.metric(
                label="Average Wind Speed",
                value=f"{avg_wind:.1f} mph",
                delta=f"{avg_wind * 1.60934:.1f} km/h"
            )
        else:
            st.metric("Average Wind Speed", "N/A")
    
    with col4:
        st.metric(
            label="Total Records",
            value=len(df)
        )
    
    st.markdown("---")
    

    # VISUALIZATION 1: Temperature Over Time
    st.header("Visualization 1: Temperature Trends")
    
    if 'temperature_f' in df.columns and 'time_clean' in df.columns:
        # Create time index for better plotting
        df_temp = df[df['temperature_f'].notna()].copy()
        df_temp['record_index'] = range(len(df_temp))
        
        # Create the plot
        fig1 = go.Figure()
        
        # Add Fahrenheit trace
        fig1.add_trace(go.Scatter(
            x=df_temp['record_index'],
            y=df_temp['temperature_f'],
            mode='lines+markers',
            name='Temperature (°F)',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=6),
            hovertemplate='<b>Time:</b> %{text}<br>' +
                          '<b>Temperature:</b> %{y}°F<br>' +
                          '<extra></extra>',
            text=df_temp['time_clean']
        ))
        
        # Add Celsius trace if available
        if 'temperature_c' in df.columns:
            fig1.add_trace(go.Scatter(
                x=df_temp['record_index'],
                y=df_temp['temperature_c'],
                mode='lines+markers',
                name='Temperature (°C)',
                line=dict(color='#4ECDC4', width=2, dash='dash'),
                marker=dict(size=6),
                hovertemplate='<b>Time:</b> %{text}<br>' +
                              '<b>Temperature:</b> %{y}°C<br>' +
                              '<extra></extra>',
                text=df_temp['time_clean'],
                visible='legendonly'  # Hidden by default
            ))
        
        fig1.update_layout(
            title="Temperature Over Time",
            xaxis_title="Record Index",
            yaxis_title="Temperature",
            hovermode='x unified',
            height=500,
            template='plotly_white',
            showlegend=True
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        st.info(" **Tip:** Click on the legend to toggle between Fahrenheit and Celsius.")
    else:
        st.warning("Temperature data not available")
    
    st.markdown("---")
    

    # VISUALIZATION 2: Weather Conditions Distribution
    st.header("Visualization 2: Weather Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of weather conditions
        if 'weather' in df.columns:
            weather_counts = df['weather'].value_counts()
            
            fig2 = px.pie(
                values=weather_counts.values,
                names=weather_counts.index,
                title="Weather Condition Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4  # Donut chart
            )
            
            fig2.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>' +
                              'Count: %{value}<br>' +
                              'Percentage: %{percent}<br>' +
                              '<extra></extra>'
            )
            
            fig2.update_layout(height=400)
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Weather condition data not available")
    
    with col2:
        # Bar chart of weather conditions with temperature
        if 'weather' in df.columns and 'temperature_f' in df.columns:
            weather_temp = df.groupby('weather').agg({
                'temperature_f': 'mean',
                'id': 'count'
            }).reset_index()
            weather_temp.columns = ['Weather', 'Avg_Temp', 'Count']
            weather_temp = weather_temp.sort_values('Count', ascending=False)
            
            fig3 = go.Figure()
            
            fig3.add_trace(go.Bar(
                x=weather_temp['Weather'],
                y=weather_temp['Count'],
                name='Occurrences',
                marker_color='#95E1D3',
                yaxis='y',
                hovertemplate='<b>%{x}</b><br>' +
                              'Occurrences: %{y}<br>' +
                              '<extra></extra>'
            ))
            
            fig3.add_trace(go.Scatter(
                x=weather_temp['Weather'],
                y=weather_temp['Avg_Temp'],
                name='Avg Temperature',
                mode='lines+markers',
                marker=dict(size=10, color='#FF6B6B'),
                line=dict(width=3, color='#FF6B6B'),
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>' +
                              'Avg Temp: %{y:.1f}°F<br>' +
                              '<extra></extra>'
            ))
            
            fig3.update_layout(
                title="Weather Conditions: Count & Avg Temperature",
                xaxis_title="Weather Condition",
                yaxis=dict(title="Occurrences", side='left'),
                yaxis2=dict(title="Avg Temperature (°F)", overlaying='y', side='right'),
                hovermode='x unified',
                height=400,
                template='plotly_white',
                showlegend=True
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Weather/temperature data not available")
    
    st.markdown("---")
    
    # VISUALIZATION 3: Humidity vs Temperature Scatter Plot
    st.header("Visualization 3: Humidity vs Temperature Analysis")
    
    if 'humidity_pct' in df.columns and 'temperature_f' in df.columns:
        # Create scatter plot
        fig4 = px.scatter(
            df[df['humidity_pct'].notna() & df['temperature_f'].notna()],
            x='temperature_f',
            y='humidity_pct',
            color='weather' if 'weather' in df.columns else None,
            size='wind_mph' if 'wind_mph' in df.columns else None,
            hover_data=['time_clean', 'weather', 'wind_mph'] if all(col in df.columns for col in ['time_clean', 'weather', 'wind_mph']) else None,
            title="Humidity vs Temperature (bubble size = wind speed)",
            labels={
                'temperature_f': 'Temperature (°F)',
                'humidity_pct': 'Humidity (%)',
                'weather': 'Condition',
                'wind_mph': 'Wind Speed (mph)'
            },
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig4.update_layout(
            height=500,
            template='plotly_white',
            showlegend=True
        )
        
        fig4.update_traces(
            marker=dict(
                line=dict(width=1, color='DarkSlateGray'),
                opacity=0.7
            )
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        st.info(" **Tip:** Hover over points to see detailed information. " +
                "Bubble size represents wind speed (if available).")
    else:
        st.warning("Humidity/temperature data not available")
    
    st.markdown("---")
    

    # VISUALIZATION 4: Wind Speed Distribution
    st.header("Visualization 4: Wind Speed Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of wind speeds
        if 'wind_mph' in df.columns:
            fig5 = px.histogram(
                df[df['wind_mph'].notna()],
                x='wind_mph',
                nbins=20,
                title="Wind Speed Distribution",
                labels={'wind_mph': 'Wind Speed (mph)', 'count': 'Frequency'},
                color_discrete_sequence=['#38B6FF']
            )
            
            fig5.update_layout(
                height=400,
                template='plotly_white',
                showlegend=False
            )
            
            fig5.update_traces(
                marker=dict(
                    line=dict(width=1, color='DarkSlateGray')
                )
            )
            
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.warning("Wind speed data not available")
    
    with col2:
        # Box plot of wind speeds by weather condition
        if 'wind_mph' in df.columns and 'weather' in df.columns:
            fig6 = px.box(
                df[df['wind_mph'].notna()],
                x='weather',
                y='wind_mph',
                title="Wind Speed by Weather Condition",
                labels={'wind_mph': 'Wind Speed (mph)', 'weather': 'Weather Condition'},
                color='weather',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig6.update_layout(
                height=400,
                template='plotly_white',
                showlegend=False
            )
            
            fig6.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.warning("Wind/weather data not available")
    
    st.markdown("---")
    

    # DATA TABLE
    st.header("Raw Data Table")
    
    st.markdown("""
    Explore the raw data below. You can sort by clicking on column headers, 
    and use the search box to find specific records.
    """)
    
    # Select which columns to display
    display_columns = st.multiselect(
        "Select columns to display",
        options=list(df.columns),
        default=[col for col in ['city', 'time_clean', 'temperature_f', 'weather', 
                                  'wind_mph', 'humidity_pct', 'scraped_date'] if col in df.columns]
    )
    
    if display_columns:
        st.dataframe(
            df[display_columns],
            use_container_width=True,
            height=400
        )
    else:
        st.dataframe(df, use_container_width=True, height=400)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # FOOTER
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Weather Data Dashboard</strong> | Capstone Project 2026</p>
        <p style='font-size: 12px;'>
            Data sourced from <a href='https://www.timeanddate.com/weather/usa/washington-dc/hourly' target='_blank'>timeanddate.com</a>
        </p>
    </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()