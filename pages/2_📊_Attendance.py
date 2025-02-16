# pages/2_📊_Attendance.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Attendance & Productivity", page_icon="📊", layout="wide")

# Generate time-series dummy data
@st.cache_data
def generate_attendance_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    data = []
    for farm in farms:
        # Generate daily data for each farm
        base_absenteeism = np.random.uniform(0.02, 0.08)  # Base absenteeism rate
        base_turnover = np.random.uniform(0.01, 0.05)     # Base turnover rate
        base_hours = np.random.uniform(38, 42)            # Base working hours
        base_productivity = np.random.uniform(0.8, 1.2)   # Base productivity
        
        for date in dates:
            # Add some seasonality and random variation
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * date.dayofyear / 365)
            
            daily_data = {
                'date': date,
                'farm': farm,
                'absenteeism_rate': max(0, min(1, base_absenteeism * seasonal_factor + np.random.normal(0, 0.01))),
                'turnover_rate': max(0, min(1, base_turnover + np.random.normal(0, 0.005))),
                'avg_hours_worked': max(30, min(50, base_hours + np.random.normal(0, 2))),
                'productivity': max(0.5, min(1.5, base_productivity * seasonal_factor + np.random.normal(0, 0.05))),
                'total_employees': np.random.randint(200, 300)
            }
            data.append(daily_data)
    
    return pd.DataFrame(data)

def add_filters():
    with st.sidebar:
        st.header("Filters")
        
        # Date range selector
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
            max_value=datetime(2024, 12, 31),
            min_value=datetime(2024, 1, 1)
        )
        
        # Farm selector
        df = generate_attendance_data()
        selected_farms = st.multiselect(
            "Select Farms",
            options=df['farm'].unique(),
            default=df['farm'].unique()
        )
        
        return date_range, selected_farms

def main():
    st.title("📊 Attendance & Productivity Analysis")
    
    # Get filters
    date_range, selected_farms = add_filters()
    
    # Load and filter data
    df = generate_attendance_data()
    filtered_df = df[
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['farm'].isin(selected_farms))
    ]
    
    # Aggregate metrics for KPI cards
    current_metrics = filtered_df.groupby('farm').agg({
        'absenteeism_rate': 'mean',
        'turnover_rate': 'mean',
        'avg_hours_worked': 'mean',
        'productivity': 'mean'
    }).mean()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Average Absenteeism Rate",
            f"{current_metrics['absenteeism_rate']:.1%}",
            delta=None,
            delta_color="inverse"
        )
    with col2:
        st.metric(
            "Average Turnover Rate",
            f"{current_metrics['turnover_rate']:.1%}",
            delta=None,
            delta_color="inverse"
        )
    with col3:
        st.metric(
            "Avg Hours Worked",
            f"{current_metrics['avg_hours_worked']:.1f}",
            delta=None
        )
    with col4:
        st.metric(
            "Productivity Index",
            f"{current_metrics['productivity']:.2f}",
            delta=None
        )
    
    # Absenteeism Rate Trend
    st.subheader("Absenteeism Rate Trends")
    daily_absence = filtered_df.groupby(['date', 'farm'])['absenteeism_rate'].mean().reset_index()
    fig_absence = px.line(
        daily_absence,
        x='date',
        y='absenteeism_rate',
        color='farm',
        title="Daily Absenteeism Rate by Farm",
        labels={'absenteeism_rate': 'Absenteeism Rate', 'date': 'Date'}
    )
    # Add threshold line for high absenteeism
    fig_absence.add_hline(
        y=0.1,  # 10% threshold
        line_dash="dash",
        line_color="red",
        annotation_text="High Absenteeism Threshold (10%)"
    )
    st.plotly_chart(fig_absence, use_container_width=True)
    
    # Hours Worked Comparison
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average Hours Worked by Farm")
        avg_hours = filtered_df.groupby('farm')['avg_hours_worked'].mean().reset_index()
        fig_hours = px.bar(
            avg_hours,
            x='farm',
            y='avg_hours_worked',
            title="Average Hours Worked per Week by Farm",
            labels={'avg_hours_worked': 'Hours Worked', 'farm': 'Farm'}
        )
        st.plotly_chart(fig_hours, use_container_width=True)
    
    # Productivity Trend
    with col2:
        st.subheader("Productivity Index Trend")
        daily_prod = filtered_df.groupby(['date', 'farm'])['productivity'].mean().reset_index()
        fig_prod = px.line(
            daily_prod,
            x='date',
            y='productivity',
            color='farm',
            title="Daily Productivity Index by Farm",
            labels={'productivity': 'Productivity Index', 'date': 'Date'}
        )
        st.plotly_chart(fig_prod, use_container_width=True)
    
    # Employee Turnover Trend
    st.subheader("Employee Turnover Rate Trends")
    monthly_turnover = filtered_df.groupby([
        pd.Grouper(key='date', freq='M'),
        'farm'
    ])['turnover_rate'].mean().reset_index()
    fig_turnover = px.line(
        monthly_turnover,
        x='date',
        y='turnover_rate',
        color='farm',
        title="Monthly Turnover Rate by Farm",
        labels={'turnover_rate': 'Turnover Rate', 'date': 'Month'}
    )
    st.plotly_chart(fig_turnover, use_container_width=True)
    
    # Add download button for filtered data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Attendance & Productivity Data",
        csv,
        "attendance_productivity.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()