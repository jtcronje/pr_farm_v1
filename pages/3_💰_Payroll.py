# pages/3_💰_Payroll.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Payroll & Compensation", page_icon="💰", layout="wide")

# Generate payroll dummy data
@st.cache_data
def generate_payroll_data():
    # Define constants
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    roles = [
        'Fixed Field Workers',
        'Seasonal Field Workers', 
        'Machine Operators', 
        'Admin Staff', 
        'Management'
    ]
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Base salaries for different roles (in ZAR)
    base_salaries = {
        'Fixed Field Workers': 4500,     # Monthly base for permanent workers
        'Seasonal Field Workers': 150,    # Daily rate for seasonal
        'Machine Operators': 8000,
        'Admin Staff': 12000,
        'Management': 25000
    }
    
    data = []
    for date in dates:
        for farm in farms:
            for role in roles:
                # Different employee number ranges based on role
                if role == 'Fixed Field Workers':
                    n_employees = np.random.randint(20, 40)
                elif role == 'Seasonal Field Workers':
                    # More seasonal workers during peak seasons (example: summer months)
                    if date.month in [11, 12, 1, 2]:  # Peak season
                        n_employees = np.random.randint(30, 60)
                    else:
                        n_employees = np.random.randint(10, 20)
                elif role == 'Machine Operators':
                    n_employees = np.random.randint(5, 15)
                elif role == 'Admin Staff':
                    n_employees = np.random.randint(3, 8)
                else:  # Management
                    n_employees = np.random.randint(2, 5)
                
                base_salary = base_salaries[role]
                
                # Add some variation to base salary
                if role == 'Seasonal Field Workers':
                    avg_salary = base_salary  # Daily rate stays fixed
                else:
                    avg_salary = base_salary * (1 + np.random.normal(0, 0.05))
                
                # Generate overtime hours based on role
                if role in ['Fixed Field Workers', 'Seasonal Field Workers', 'Machine Operators']:
                    overtime_hours = max(0, np.random.normal(5, 2))
                else:
                    overtime_hours = max(0, np.random.normal(2, 1))
                
                # Calculate overtime cost (1.5x hourly rate)
                if role == 'Seasonal Field Workers':
                    hourly_rate = avg_salary / 8  # Assuming 8-hour workday
                    daily_cost = avg_salary * n_employees
                else:
                    hourly_rate = avg_salary / (22 * 8)  # Monthly salary to hourly
                    daily_cost = (avg_salary / 22) * n_employees  # Daily cost based on 22 working days
                
                overtime_cost = overtime_hours * hourly_rate * 1.5
                
                data.append({
                    'date': date,
                    'farm': farm,
                    'role': role,
                    'employees': n_employees,
                    'base_salary': avg_salary,
                    'overtime_hours': overtime_hours,
                    'overtime_cost': overtime_cost,
                    'total_cost': daily_cost + (overtime_cost * n_employees)
                })
    
    return pd.DataFrame(data)

def format_currency(value):
    """Format currency in South African Rand"""
    return f"R{value:,.2f}"

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
        df = generate_payroll_data()
        selected_farms = st.multiselect(
            "Select Farms",
            options=df['farm'].unique(),
            default=df['farm'].unique()
        )
        
        # Role selector
        selected_roles = st.multiselect(
            "Select Roles",
            options=df['role'].unique(),
            default=df['role'].unique()
        )
        
        return date_range, selected_farms, selected_roles

def main():
    st.title("💰 Payroll & Compensation Analysis")
    
    # Get filters
    date_range, selected_farms, selected_roles = add_filters()
    
    # Load and filter data
    df = generate_payroll_data()
    filtered_df = df[
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['farm'].isin(selected_farms)) &
        (df['role'].isin(selected_roles))
    ]
    
    # Calculate monthly totals for metrics
    monthly_totals = filtered_df.groupby(pd.Grouper(key='date', freq='M')).agg({
        'total_cost': 'sum',
        'overtime_cost': 'sum',
        'overtime_hours': 'sum'
    }).iloc[-1]  # Get latest month
    
    # Monthly change calculation
    monthly_series = filtered_df.groupby(pd.Grouper(key='date', freq='M'))['total_cost'].sum()
    
    # Check if we have at least 2 months of data
    if len(monthly_series) >= 2:
        prev_month = monthly_series.iloc[-2]
        monthly_change = ((monthly_totals['total_cost'] - prev_month) / prev_month) * 100
        delta_display = f"{monthly_change:+.1f}%"
    else:
        delta_display = None
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Monthly Payroll",
            format_currency(monthly_totals['total_cost']),
            delta_display,
            delta_color="inverse"
        )
    with col2:
        st.metric(
            "Total Overtime Cost",
            format_currency(monthly_totals['overtime_cost'])
        )
    with col3:
        st.metric(
            "Total Overtime Hours",
            f"{monthly_totals['overtime_hours']:,.1f}"
        )
    
    # Average Salary by Role
    st.subheader("Average Salary by Role")
    avg_salary = filtered_df.groupby('role')['base_salary'].mean().reset_index()
    
    # Sort roles to group fixed and seasonal workers together
    role_order = ['Fixed Field Workers', 'Seasonal Field Workers', 'Machine Operators', 'Admin Staff', 'Management']
    avg_salary['role'] = pd.Categorical(avg_salary['role'], categories=role_order, ordered=True)
    avg_salary = avg_salary.sort_values('role')
    
    # Create salary visualization with different colors for fixed vs seasonal
    fig_salary = px.bar(
        avg_salary,
        x='role',
        y='base_salary',
        title="Average Monthly/Daily Salary by Role",
        labels={'base_salary': 'Salary (ZAR)', 'role': 'Role'},
        color='role',
        color_discrete_map={
            'Fixed Field Workers': '#2ecc71',
            'Seasonal Field Workers': '#82e0aa',
            'Machine Operators': '#3498db',
            'Admin Staff': '#9b59b6',
            'Management': '#34495e'
        }
    )
    
    # Add salary annotations
    fig_salary.update_traces(
        texttemplate='R%{y:,.0f}',
        textposition='outside'
    )
    
    # Add note about seasonal workers
    fig_salary.add_annotation(
        text="Note: Seasonal Workers shown as daily rate",
        xref="paper", yref="paper",
        x=0, y=-0.15,
        showarrow=False,
        font=dict(size=10)
    )
    
    st.plotly_chart(fig_salary, use_container_width=True)
    
    # Payroll Cost by Farm (Stacked)
    st.subheader("Monthly Payroll Cost by Farm and Role")
    monthly_farm_cost = filtered_df.groupby([
        pd.Grouper(key='date', freq='M'),
        'farm',
        'role'
    ])['total_cost'].sum().reset_index()
    
    fig_farm_cost = px.bar(
        monthly_farm_cost,
        x='date',
        y='total_cost',
        color='role',
        facet_col='farm',
        facet_col_wrap=2,
        title="Monthly Payroll Cost by Farm and Role",
        labels={'total_cost': 'Total Cost', 'date': 'Month'}
    )
    fig_farm_cost.update_layout(showlegend=True)
    fig_farm_cost.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig_farm_cost, use_container_width=True)
    
    # Overtime Trends
    st.subheader("Overtime Trends")
    daily_overtime = filtered_df.groupby(['date', 'farm'])[['overtime_hours', 'overtime_cost']].sum().reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        fig_ot_hours = px.line(
            daily_overtime,
            x='date',
            y='overtime_hours',
            color='farm',
            title="Daily Overtime Hours by Farm",
            labels={'overtime_hours': 'Overtime Hours', 'date': 'Date'}
        )
        st.plotly_chart(fig_ot_hours, use_container_width=True)
    
    with col2:
        fig_ot_cost = px.line(
            daily_overtime,
            x='date',
            y='overtime_cost',
            color='farm',
            title="Daily Overtime Cost by Farm",
            labels={'overtime_cost': 'Overtime Cost', 'date': 'Date'}
        )
        st.plotly_chart(fig_ot_cost, use_container_width=True)
    
    # Add download button for filtered data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Payroll Data",
        csv,
        "payroll_compensation.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()