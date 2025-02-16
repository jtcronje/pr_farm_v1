# 👥_People_Radar_Dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(
    page_title="People Radar Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        .metric-card {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
            padding: 1rem;
            text-align: center;
        }
        a {
            text-decoration: none;
            color: #0066cc;
        }
        a:hover {
            color: #004080;
            text-decoration: underline;
        }
        div[data-testid="stSidebarNav"] li div a {
            margin-left: 1rem;
        }
        div[data-testid="stSidebarNav"] li div::before {
            content: "👥";
            margin-right: 0.5rem;
        }
        div[data-testid="stSidebarNav"] li:nth-child(1) div::before {
            content: "👥";
        }
        div[data-testid="stSidebarNav"] li:nth-child(2) div::before {
            content: "👥";
        }
        div[data-testid="stSidebarNav"] li:nth-child(3) div::before {
            content: "📊";
        }
        div[data-testid="stSidebarNav"] li:nth-child(4) div::before {
            content: "💰";
        }
        div[data-testid="stSidebarNav"] li:nth-child(5) div::before {
            content: "📋";
        }
        div[data-testid="stSidebarNav"] li:nth-child(6) div::before {
            content: "📅";
        }
        div[data-testid="stSidebarNav"] li:nth-child(7) div::before {
            content: "📊";
        }
    </style>
""", unsafe_allow_html=True)

# Generate dummy data
@st.cache_data
def generate_overview_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    departments = ['Field Workers', 'Machine Operators', 'Admin', 'Management']
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    races = ['African', 'White', 'Coloured', 'Indian']
    disabilities = ['None', 'Physical', 'Visual', 'Hearing', 'Mental', 'Multiple']
    
    # Probability weights
    race_weights = [0.76, 0.12, 0.09, 0.03]  # Approximate SA demographics
    disability_weights = [0.95, 0.01, 0.01, 0.01, 0.01, 0.01]
    
    data = []
    for date in dates:
        for farm in farms:
            # Base fixed workers for each farm
            base_fixed = np.random.randint(150, 200)
            
            # Seasonal workers vary by season
            if date.month in [11, 12, 1, 2]:  # Peak season
                seasonal_workers = np.random.randint(40, 70)
            elif date.month in [3, 4, 9, 10]:  # Medium season
                seasonal_workers = np.random.randint(20, 40)
            else:  # Low season
                seasonal_workers = np.random.randint(5, 15)
            
            total_workers = base_fixed + seasonal_workers
            
            # Generate demographic data
            races_dist = np.random.choice(races, total_workers, p=race_weights)
            disabilities_dist = np.random.choice(disabilities, total_workers, p=disability_weights)
            
            # Add department breakdown with demographic distribution
            dept_data = {}
            for dept in departments:
                dept_size = np.random.randint(20, 80)
                dept_races = np.random.choice(races, dept_size, p=race_weights)
                dept_disabilities = np.random.choice(disabilities, dept_size, p=disability_weights)
                
                dept_data[f'{dept}_count'] = dept_size
                dept_data[f'{dept}_diversity'] = np.sum(dept_races != 'White') / dept_size
                dept_data[f'{dept}_pwd'] = np.sum(dept_disabilities != 'None')
            
            daily_data = {
                'date': date,
                'farm': farm,
                'fixed_workers': base_fixed,
                'seasonal_workers': seasonal_workers,
                'total_employees': total_workers,
                'attendance_rate': np.random.uniform(0.90, 0.98),
                'productivity_index': np.random.uniform(0.85, 1.15),
                'daily_cost': (base_fixed * 400) + (seasonal_workers * 200),
                'diversity_ratio': np.sum(races_dist != 'White') / total_workers,
                'pwd_ratio': np.sum(disabilities_dist != 'None') / total_workers,
                **dept_data
            }
            data.append(daily_data)
    
    return pd.DataFrame(data)

def add_filters():
    with st.sidebar:
        st.header("Dashboard Filters")
        
        # Date filter
        st.subheader("Date Range")
        date_range = st.date_input(
            "Select period",
            value=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2024, 12, 31),
            key="date_range"
        )
        
        # Farm filter
        df = generate_overview_data()
        selected_farms = st.multiselect(
            "Select Farms",
            options=df['farm'].unique(),
            default=df['farm'].unique()
        )
        
        return date_range, selected_farms

def main():
    # Page Title with custom styling
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 2rem;'>
            👥 People Radar Dashboard
        </h1>
        <p style='text-align: center; font-size: 1.2em; color: #666; margin-bottom: 3rem;'>
            Comprehensive workforce analytics and insights at your fingertips
        </p>
    """, unsafe_allow_html=True)
    
    # Get filters
    date_range, selected_farms = add_filters()
    
    # Load and filter data
    df = generate_overview_data()
    filtered_df = df[
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['farm'].isin(selected_farms))
    ]
    
    # Latest metrics
    latest_date = filtered_df['date'].max()
    latest_metrics = filtered_df[filtered_df['date'] == latest_date]
    
    # Display metrics in cards
    st.subheader("Key Metrics")
    
    # Workforce Metrics
    st.markdown("##### Workforce Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Fixed Workers",
            f"{latest_metrics['fixed_workers'].sum():,}",
            "Permanent employees"
        )
    
    with col2:
        st.metric(
            "Seasonal Workers",
            f"{latest_metrics['seasonal_workers'].sum():,}",
            "Current season"
        )
    
    with col3:
        avg_diversity = latest_metrics['diversity_ratio'].mean() * 100
        st.metric(
            "Diversity Ratio",
            f"{avg_diversity:.1f}%",
            "Workforce diversity"
        )
    
    with col4:
        avg_pwd = latest_metrics['pwd_ratio'].mean() * 100
        st.metric(
            "PWD Ratio",
            f"{avg_pwd:.1f}%",
            "Persons with disabilities"
        )
    
    # Performance Metrics
    st.markdown("##### Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Productivity Index",
            f"{latest_metrics['productivity_index'].mean():.2f}",
            "Current productivity"
        )
    
    with col2:
        st.metric(
            "Attendance Rate",
            f"{latest_metrics['attendance_rate'].mean()*100:.1f}%",
            "Current attendance"
        )
    
    with col3:
        st.metric(
            "Daily Cost",
            f"R{latest_metrics['daily_cost'].sum():,.2f}",
            "Combined workforce"
        )
    
    with col4:
        cost_per_worker = (
            latest_metrics['daily_cost'].sum() / 
            latest_metrics['total_employees'].sum()
        )
        st.metric(
            "Cost per Worker",
            f"R{cost_per_worker:.2f}",
            "Daily average"
        )
    
    # Workforce Distribution
    st.subheader("Workforce Distribution")
    
    col1, col2 = st.columns(2)
    
    # Distribution by Farm
    with col1:
        farm_dist = latest_metrics.groupby('farm')[['fixed_workers', 'seasonal_workers']].sum()
        fig_farm = px.bar(
            farm_dist,
            barmode='stack',
            title="Workforce Distribution by Farm",
            labels={'value': 'Number of Workers', 'variable': 'Worker Type'},
            color_discrete_map={
                'fixed_workers': '#2ecc71',
                'seasonal_workers': '#f1c40f'
            }
        )
        st.plotly_chart(fig_farm, use_container_width=True)
    
    # Distribution by Department
    with col2:
        dept_cols = ['Field Workers_count', 'Machine Operators_count', 'Admin_count', 'Management_count']
        dept_data = latest_metrics[dept_cols].sum()
        dept_data.index = [col.replace('_count', '') for col in dept_data.index]
        
        fig_dept = px.pie(
            values=dept_data.values,
            names=dept_data.index,
            title="Workforce Distribution by Department"
        )
        st.plotly_chart(fig_dept, use_container_width=True)
    
    # Trends
    st.subheader("Workforce Trends")
    
    # Daily trends
    daily_metrics = filtered_df.groupby('date').agg({
        'fixed_workers': 'sum',
        'seasonal_workers': 'sum',
        'diversity_ratio': 'mean',
        'pwd_ratio': 'mean',
        'productivity_index': 'mean'
    }).reset_index()
    
    fig_trends = px.line(
        daily_metrics,
        x='date',
        y=['fixed_workers', 'seasonal_workers', 'productivity_index'],
        title="Daily Workforce Metrics",
        labels={'value': 'Value', 'date': 'Date', 'variable': 'Metric'},
        color_discrete_map={
            'fixed_workers': '#2ecc71',
            'seasonal_workers': '#f1c40f',
            'productivity_index': '#3498db'
        }
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Navigation cards
    st.markdown("### Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>👥 Demographics</h3>
                <p>Analyze workforce composition and distributions</p>
                <a href='Demographics' target='_self'>View Demographics →</a>
            </div>
            
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>📊 Attendance</h3>
                <p>Track attendance patterns and performance</p>
                <a href='Attendance' target='_self'>View Attendance →</a>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>💰 Payroll</h3>
                <p>Monitor compensation and cost analysis</p>
                <a href='Payroll' target='_self'>View Payroll →</a>
            </div>
            
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>📋 Planning</h3>
                <p>Workforce planning and future projections</p>
                <a href='Planning' target='_self'>View Planning →</a>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>📅 Leave</h3>
                <p>Leave management and analysis</p>
                <a href='Leave' target='_self'>View Leave →</a>
            </div>
            
            <div style='padding: 1rem; background-color: #f8f9fa; border-radius: 0.5rem; margin-bottom: 1rem;'>
                <h3 style='margin: 0'>📊 Seasonal vs Fixed</h3>
                <p>Compare seasonal and fixed workforce patterns</p>
                <a href='Seasonal_vs_Fixed' target='_self'>View Analysis →</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()