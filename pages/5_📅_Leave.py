# pages/5_📅_Leave.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Leave Analysis", page_icon="📅", layout="wide")

# Generate leave analysis dummy data
@st.cache_data
def generate_leave_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    departments = ['Field Workers', 'Machine Operators', 'Admin', 'Management']
    leave_types = ['Annual', 'Sick', 'Maternity', 'Study', 'Unpaid', 'Emergency']
    
    # Generate employee base data
    n_employees = 1000
    employees = []
    for i in range(n_employees):
        employee = {
            'employee_id': f'EMP{i+1:04d}',
            'name': f'Employee {i+1}',
            'farm': np.random.choice(farms),
            'department': np.random.choice(departments),
            'annual_leave_balance': np.random.randint(0, 25),
            'sick_leave_balance': np.random.randint(0, 15)
        }
        employees.append(employee)
    
    employees_df = pd.DataFrame(employees)
    
    # Generate leave records
    leave_records = []
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    for employee in employees_df.to_dict('records'):
        # Generate random number of leave instances
        n_leaves = np.random.randint(1, 10)
        for _ in range(n_leaves):
            start_date = np.random.choice(dates)
            duration = np.random.randint(1, 10)
            leave_type = np.random.choice(leave_types, p=[0.4, 0.3, 0.05, 0.1, 0.1, 0.05])
            
            leave_records.append({
                'employee_id': employee['employee_id'],
                'name': employee['name'],
                'farm': employee['farm'],
                'department': employee['department'],
                'leave_type': leave_type,
                'start_date': start_date,
                'duration': duration,
                'is_planned': leave_type in ['Annual', 'Study', 'Maternity']
            })
    
    return pd.DataFrame(leave_records), employees_df

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
        leave_df, _ = generate_leave_data()
        selected_farms = st.multiselect(
            "Select Farms",
            options=leave_df['farm'].unique(),
            default=leave_df['farm'].unique()
        )
        
        # Department selector
        selected_departments = st.multiselect(
            "Select Departments",
            options=leave_df['department'].unique(),
            default=leave_df['department'].unique()
        )
        
        return date_range, selected_farms, selected_departments

def main():
    st.title("📅 Leave Analysis Dashboard")
    
    # Get filters
    date_range, selected_farms, selected_departments = add_filters()
    
    # Load data
    leave_df, employees_df = generate_leave_data()
    
    # Filter data
    filtered_df = leave_df[
        (leave_df['start_date'].dt.date >= date_range[0]) &
        (leave_df['start_date'].dt.date <= date_range[1]) &
        (leave_df['farm'].isin(selected_farms)) &
        (leave_df['department'].isin(selected_departments))
    ]
    
    # Calculate key metrics
    total_leave_days = filtered_df['duration'].sum()
    unplanned_rate = (filtered_df[~filtered_df['is_planned']]['duration'].sum() / 
                     total_leave_days * 100)
    avg_duration = filtered_df['duration'].mean()
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Leave Days (YTD)",
            f"{total_leave_days:,}",
            "Days taken"
        )
    with col2:
        st.metric(
            "Unplanned Leave Rate",
            f"{unplanned_rate:.1f}%",
            "Of total leave"
        )
    with col3:
        st.metric(
            "Average Leave Duration",
            f"{avg_duration:.1f} days",
            "Per request"
        )
    
    # Leave Type Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Leave Type Distribution")
        leave_type_dist = filtered_df.groupby('leave_type')['duration'].sum()
        fig_type = px.pie(
            values=leave_type_dist.values,
            names=leave_type_dist.index,
            title="Leave Days by Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        st.subheader("Planned vs Unplanned Leave")
        planned_dist = filtered_df.groupby('is_planned')['duration'].sum()
        fig_planned = px.pie(
            values=planned_dist.values,
            names=['Unplanned', 'Planned'],
            title="Planned vs Unplanned Leave Distribution",
            color_discrete_sequence=['#ff7f7f', '#7fb3ff']
        )
        st.plotly_chart(fig_planned, use_container_width=True)
    
    # Leave Utilization by Farm
    st.subheader("Leave Utilization by Farm")
    farm_leave = filtered_df.pivot_table(
        values='duration',
        index='farm',
        columns='leave_type',
        aggfunc='sum',
        fill_value=0
    )
    
    fig_farm = px.bar(
        farm_leave,
        title="Leave Days by Farm and Type",
        labels={'value': 'Days', 'variable': 'Leave Type'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_farm, use_container_width=True)
    
    # Monthly Leave Trend
    st.subheader("Monthly Leave Trends")
    monthly_leave = filtered_df.groupby([
        pd.Grouper(key='start_date', freq='M'),
        'leave_type'
    ])['duration'].sum().reset_index()
    
    fig_trend = px.line(
        monthly_leave,
        x='start_date',
        y='duration',
        color='leave_type',
        title="Monthly Leave Trends by Type",
        labels={'duration': 'Days', 'start_date': 'Month'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Top Leave Takers
    st.subheader("Employees with Highest Leave Days")
    top_leave = filtered_df.groupby(['employee_id', 'name', 'farm', 'department'])[
        'duration'
    ].sum().reset_index().sort_values('duration', ascending=False).head(10)
    
    fig_top = px.bar(
        top_leave,
        x='name',
        y='duration',
        color='farm',
        title="Top 10 Leave Takers",
        labels={'duration': 'Days', 'name': 'Employee'},
        text='duration'
    )
    fig_top.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Leave Balance Analysis
    st.subheader("Leave Balance Analysis")
    
    # Filter employees based on selected farms and departments
    filtered_employees = employees_df[
        (employees_df['farm'].isin(selected_farms)) &
        (employees_df['department'].isin(selected_departments))
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Annual Leave Balance by Farm
        annual_balance = filtered_employees.groupby('farm')['annual_leave_balance'].mean()
        fig_annual = px.bar(
            x=annual_balance.index,
            y=annual_balance.values,
            title="Average Annual Leave Balance by Farm",
            labels={'x': 'Farm', 'y': 'Days'}
        )
        st.plotly_chart(fig_annual, use_container_width=True)
    
    with col2:
        # Sick Leave Balance by Farm
        sick_balance = filtered_employees.groupby('farm')['sick_leave_balance'].mean()
        fig_sick = px.bar(
            x=sick_balance.index,
            y=sick_balance.values,
            title="Average Sick Leave Balance by Farm",
            labels={'x': 'Farm', 'y': 'Days'}
        )
        st.plotly_chart(fig_sick, use_container_width=True)
    
    # Individual Employee Leave Details
    st.subheader("Individual Employee Leave Details")
    selected_employee = st.selectbox(
        "Select Employee",
        options=filtered_df['employee_id'].unique(),
        format_func=lambda x: f"{x} - {filtered_df[filtered_df['employee_id'] == x]['name'].iloc[0]}"
    )
    
    if selected_employee:
        employee_leave = filtered_df[filtered_df['employee_id'] == selected_employee]
        employee_details = employees_df[employees_df['employee_id'] == selected_employee].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Annual Leave Balance", f"{employee_details['annual_leave_balance']} days")
        with col2:
            st.metric("Sick Leave Balance", f"{employee_details['sick_leave_balance']} days")
        with col3:
            st.metric("Total Leave Taken", f"{employee_leave['duration'].sum()} days")
        
        st.dataframe(
            employee_leave[['start_date', 'duration', 'leave_type', 'is_planned']],
            use_container_width=True
        )
    
    # Add download button for leave data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Leave Data",
        csv,
        "leave_analysis.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()