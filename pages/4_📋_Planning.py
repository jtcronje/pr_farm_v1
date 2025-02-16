# pages/4_📋_Planning.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Workforce Planning", page_icon="📋", layout="wide")

# Generate planning dummy data
@st.cache_data
def generate_planning_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    roles = ['Field Workers', 'Machine Operators', 'Admin', 'Management']
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    
    data = []
    # Historical and projected data
    for date in dates:
        for farm in farms:
            base_employees = np.random.randint(200, 300)
            # Add seasonal variation
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * date.month / 12)
            
            for role in roles:
                # Base distribution of roles
                role_ratios = {
                    'Field Workers': 0.5,
                    'Machine Operators': 0.3,
                    'Admin': 0.15,
                    'Management': 0.05
                }
                
                role_employees = int(base_employees * role_ratios[role] * seasonal_factor)
                
                # Generate vacancies (higher in peak seasons)
                vacancy_rate = np.random.uniform(0.05, 0.15) * seasonal_factor
                vacancies = int(role_employees * vacancy_rate)
                
                # Generate training hours (varies by role)
                if role in ['Field Workers', 'Machine Operators']:
                    training_hours = np.random.normal(20, 5)
                else:
                    training_hours = np.random.normal(15, 3)
                
                data.append({
                    'date': date,
                    'farm': farm,
                    'role': role,
                    'current_employees': role_employees,
                    'vacancies': vacancies,
                    'training_hours': max(0, training_hours),
                    'projected_needs': int(role_employees * (1 + np.random.uniform(0.1, 0.2)))
                })
    
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
        df = generate_planning_data()
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
    st.title("📋 Workforce Planning & Future Needs")
    
    # Get filters
    date_range, selected_farms, selected_roles = add_filters()
    
    # Load and filter data
    df = generate_planning_data()
    filtered_df = df[
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1]) &
        (df['farm'].isin(selected_farms)) &
        (df['role'].isin(selected_roles))
    ]
    
    # Calculate current metrics
    current_vacancies = filtered_df['vacancies'].sum()
    avg_training_hours = filtered_df['training_hours'].mean()
    workforce_gap = (filtered_df['projected_needs'].sum() - 
                    filtered_df['current_employees'].sum())
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Open Positions",
            f"{current_vacancies:,}",
            "Current vacancies"
        )
    with col2:
        st.metric(
            "Avg Training Hours",
            f"{avg_training_hours:.1f}",
            "Per employee"
        )
    with col3:
        st.metric(
            "Projected Workforce Gap",
            f"{workforce_gap:,}",
            "Additional staff needed"
        )
    
    # Vacancies by Farm and Role
    st.subheader("Current Vacancies by Farm and Role")
    vacancy_pivot = filtered_df.pivot_table(
        values='vacancies',
        index='farm',
        columns='role',
        aggfunc='sum'
    ).round(0)
    
    st.dataframe(
        vacancy_pivot,
        use_container_width=True
    )
    
    # Workforce Projection
    st.subheader("Workforce Projection")
    projection_data = filtered_df.groupby(['date', 'farm']).agg({
        'current_employees': 'sum',
        'projected_needs': 'sum'
    }).reset_index()
    
    fig_projection = go.Figure()
    
    for farm in selected_farms:
        farm_data = projection_data[projection_data['farm'] == farm]
        
        # Current employees line
        fig_projection.add_trace(go.Scatter(
            x=farm_data['date'],
            y=farm_data['current_employees'],
            name=f"{farm} - Current",
            line=dict(dash='solid')
        ))
        
        # Projected needs line
        fig_projection.add_trace(go.Scatter(
            x=farm_data['date'],
            y=farm_data['projected_needs'],
            name=f"{farm} - Projected",
            line=dict(dash='dash')
        ))
        
        # Add gap annotations
        last_point = farm_data.iloc[-1]
        gap = last_point['projected_needs'] - last_point['current_employees']
        
        fig_projection.add_annotation(
            x=last_point['date'],
            y=last_point['projected_needs'],
            text=f"Gap: {gap:.0f}",
            showarrow=True,
            arrowhead=1
        )
    
    fig_projection.update_layout(
        title="Workforce Projection by Farm",
        xaxis_title="Date",
        yaxis_title="Number of Employees",
        hovermode='x unified'
    )
    st.plotly_chart(fig_projection, use_container_width=True)
    
    # Training Hours Analysis
    st.subheader("Training & Upskilling Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Training hours by role
        training_by_role = filtered_df.groupby('role')['training_hours'].mean().reset_index()
        fig_training_role = px.bar(
            training_by_role,
            x='role',
            y='training_hours',
            title="Average Training Hours by Role",
            labels={'training_hours': 'Training Hours', 'role': 'Role'}
        )
        st.plotly_chart(fig_training_role, use_container_width=True)
    
    with col2:
        # Training hours by farm
        training_by_farm = filtered_df.groupby('farm')['training_hours'].mean().reset_index()
        fig_training_farm = px.bar(
            training_by_farm,
            x='farm',
            y='training_hours',
            title="Average Training Hours by Farm",
            labels={'training_hours': 'Training Hours', 'farm': 'Farm'}
        )
        st.plotly_chart(fig_training_farm, use_container_width=True)
    
    # Add download button for planning data
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Planning Data",
        csv,
        "workforce_planning.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()