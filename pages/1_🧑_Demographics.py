# pages/1_👥_Demographics.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Workforce Demographics",
    page_icon="👥",
    layout="wide"
)

# Generate dummy data
@st.cache_data
def generate_demographic_data():
    n_employees = 1000
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    departments = ['Field Workers', 'Machine Operators', 'Admin', 'Management']
    education_levels = ['None', 'Matric', 'Diploma', 'Bachelors Degree']
    races = ['African', 'White', 'Coloured', 'Indian']
    disabilities = [
        'None',
        'Physical',
        'Visual',
        'Hearing',
        'Mental',
        'Multiple'
    ]
    
    # Probability weights for realistic demographic distribution
    race_weights = [0.76, 0.12, 0.09, 0.03]  # Approximate SA demographics
    disability_weights = [0.95, 0.01, 0.01, 0.01, 0.01, 0.01]  # Approximate disability distribution
    
    data = {
        'employee_id': range(1, n_employees + 1),
        'farm': np.random.choice(farms, n_employees),
        'department': np.random.choice(departments, n_employees),
        'age': np.random.randint(18, 65, n_employees),
        'gender': np.random.choice(['Male', 'Female'], n_employees),
        'years_of_service': np.random.uniform(0, 20, n_employees),
        'education': np.random.choice(education_levels, n_employees),
        'race': np.random.choice(races, n_employees, p=race_weights),
        'disability': np.random.choice(disabilities, n_employees, p=disability_weights)
    }
    
    return pd.DataFrame(data)

def main():
    st.title("👥 Workforce Demographics Analysis")
    
    # Load data
    df = generate_demographic_data()
    
    # Filters
    st.sidebar.header("Filters")
    
    selected_farms = st.sidebar.multiselect(
        "Select Farms",
        options=df['farm'].unique(),
        default=df['farm'].unique()
    )
    
    selected_departments = st.sidebar.multiselect(
        "Select Departments",
        options=df['department'].unique(),
        default=df['department'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['farm'].isin(selected_farms)) &
        (df['department'].isin(selected_departments))
    ]
    
    # Key Metrics
    st.subheader("Key Demographics Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_employees = len(filtered_df)
        st.metric(
            "Total Employees",
            f"{total_employees:,}",
            "Current workforce"
        )
    
    with col2:
        diversity_ratio = (len(filtered_df[filtered_df['race'] != 'White']) / total_employees * 100)
        st.metric(
            "Workforce Diversity",
            f"{diversity_ratio:.1f}%",
            "Non-white employees"
        )
    
    with col3:
        gender_ratio = (len(filtered_df[filtered_df['gender'] == 'Female']) / total_employees * 100)
        st.metric(
            "Gender Ratio",
            f"{gender_ratio:.1f}%",
            "Female employees"
        )
    
    with col4:
        pwd_ratio = (len(filtered_df[filtered_df['disability'] != 'None']) / total_employees * 100)
        st.metric(
            "PWD Ratio",
            f"{pwd_ratio:.1f}%",
            "Employees with disabilities"
        )
    
    # Tabs for different analyses
    tab1, tab2, tab3 = st.tabs([
        "Race & Gender Analysis",
        "Disability Analysis",
        "Age & Education"
    ])
    
    with tab1:
        st.subheader("Racial and Gender Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Race distribution by department
            race_dept = filtered_df.groupby(['department', 'race']).size().reset_index(name='count')
            fig_race = px.bar(
                race_dept,
                x='department',
                y='count',
                color='race',
                title="Racial Distribution by Department",
                labels={'count': 'Number of Employees'},
                color_discrete_map={
                    'African': '#2ecc71',
                    'White': '#3498db',
                    'Coloured': '#e74c3c',
                    'Indian': '#f1c40f'
                }
            )
            st.plotly_chart(fig_race, use_container_width=True)
        
        with col2:
            # Management racial composition
            management_df = filtered_df[filtered_df['department'] == 'Management']
            race_mgmt = management_df.groupby(['farm', 'race']).size().reset_index(name='count')
            
            fig_mgmt = px.bar(
                race_mgmt,
                x='farm',
                y='count',
                color='race',
                title="Management Racial Composition by Farm",
                labels={'count': 'Number of Managers'},
                color_discrete_map={
                    'African': '#2ecc71',
                    'White': '#3498db',
                    'Coloured': '#e74c3c',
                    'Indian': '#f1c40f'
                }
            )
            st.plotly_chart(fig_mgmt, use_container_width=True)
    
    with tab2:
        st.subheader("Disability Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Disability distribution
            disability_dist = filtered_df['disability'].value_counts()
            
            fig_disability = px.pie(
                values=disability_dist.values,
                names=disability_dist.index,
                title="Overall Disability Distribution",
                hole=0.4
            )
            st.plotly_chart(fig_disability, use_container_width=True)
        
        with col2:
            # Disability by department
            disability_dept = filtered_df[filtered_df['disability'] != 'None'].groupby(
                ['department', 'disability']
            ).size().reset_index(name='count')
            
            fig_disability_dept = px.bar(
                disability_dept,
                x='department',
                y='count',
                color='disability',
                title="Disability Distribution by Department",
                labels={'count': 'Number of Employees'}
            )
            st.plotly_chart(fig_disability_dept, use_container_width=True)
        
        # Disability accommodations tracking
        st.subheader("Disability Support Analysis")
        disability_support = filtered_df[filtered_df['disability'] != 'None'].groupby(
            ['farm', 'disability']
        ).size().reset_index(name='count')
        
        fig_support = px.bar(
            disability_support,
            x='farm',
            y='count',
            color='disability',
            title="Disability Distribution Across Farms",
            labels={'count': 'Number of Employees'},
            barmode='group'
        )
        st.plotly_chart(fig_support, use_container_width=True)
    
    with tab3:
        st.subheader("Age and Education Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Age distribution
            fig_age = px.histogram(
                filtered_df,
                x='age',
                nbins=20,
                title="Age Distribution",
                labels={'age': 'Age', 'count': 'Number of Employees'}
            )
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Education distribution
            edu_dist = filtered_df['education'].value_counts()
            fig_edu = px.pie(
                values=edu_dist.values,
                names=edu_dist.index,
                title="Education Level Distribution"
            )
            st.plotly_chart(fig_edu, use_container_width=True)
        
        # Education by department
        edu_dept = filtered_df.groupby(['department', 'education']).size().reset_index(name='count')
        fig_edu_dept = px.bar(
            edu_dept,
            x='department',
            y='count',
            color='education',
            title="Education Distribution by Department",
            labels={'count': 'Number of Employees'}
        )
        st.plotly_chart(fig_edu_dept, use_container_width=True)
    
    # Download functionality
    st.sidebar.markdown("---")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "📥 Download Demographics Data",
        csv,
        "workforce_demographics.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()