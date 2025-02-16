# pages/7_📊_Performance.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(
    page_title="Performance & Disciplinary Analysis",
    page_icon="📊",
    layout="wide"
)

# Add custom CSS for disciplinary status indicators
st.markdown("""
    <style>
        .status-active {
            color: #e74c3c;
            font-weight: bold;
        }
        .status-warning {
            color: #f1c40f;
            font-weight: bold;
        }
        .status-clear {~
            color: #2ecc71;
            font-weight: bold;
        }
        .metric-card {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
            padding: 1rem;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_performance_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    departments = ['Field Workers', 'Machine Operators', 'Admin', 'Management']
    months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    incident_types = ['Minor', 'Moderate', 'Severe']
    hearing_outcomes = ['Verbal Warning', 'Written Warning', 'Final Warning', 'Suspension', 'Termination']
    
    data = []
    employee_data = []
    
    # Generate employee base data
    n_employees = 1000
    for i in range(n_employees):
        farm = np.random.choice(farms)
        department = np.random.choice(departments)
        performance_rating = np.random.normal(3.5, 0.5)  # Normal distribution around 3.5
        performance_rating = max(1, min(5, performance_rating))  # Clamp between 1 and 5
        
        employee_data.append({
            'employee_id': f'EMP{i+1:04d}',
            'name': f'Employee {i+1}',
            'farm': farm,
            'department': department,
            'performance_rating': round(performance_rating, 2),
            'years_service': round(np.random.uniform(0, 15), 1),
            'status': 'Active'  # Add employee status
        })
    
    employees_df = pd.DataFrame(employee_data)
    
    # Generate incident data
    for month in months:
        for farm in farms:
            farm_employees = employees_df[employees_df['farm'] == farm]
            
            # Generate random number of incidents
            n_incidents = np.random.poisson(5)  # Average 5 incidents per farm per month
            
            for _ in range(n_incidents):
                # Select random employee from farm
                employee = farm_employees.sample(1).iloc[0]
                
                # Incident severity more likely to be minor
                severity = np.random.choice(incident_types, p=[0.6, 0.3, 0.1])
                
                # Hearing outcome based on severity
                if severity == 'Minor':
                    outcome_probs = [0.5, 0.3, 0.2, 0, 0]
                elif severity == 'Moderate':
                    outcome_probs = [0.2, 0.3, 0.3, 0.2, 0]
                else:  # Severe
                    outcome_probs = [0, 0.1, 0.3, 0.3, 0.3]
                
                outcome = np.random.choice(hearing_outcomes, p=outcome_probs)
                
                # Generate random incident description
                incident_descriptions = [
                    "Late arrival to work",
                    "Unauthorized absence",
                    "Safety protocol violation",
                    "Insubordination",
                    "Policy violation",
                    "Performance issue",
                    "Misconduct"
                ]
                
                data.append({
                    'date': month,
                    'farm': farm,
                    'department': employee['department'],
                    'employee_id': employee['employee_id'],
                    'incident_severity': severity,
                    'hearing_outcome': outcome,
                    'performance_rating': employee['performance_rating'],
                    'incident_description': np.random.choice(incident_descriptions),
                    'case_number': f'CASE{len(data)+1:04d}'
                })
    
    incidents_df = pd.DataFrame(data)
    return incidents_df, employees_df

def get_employee_status(incidents_df, employee_id):
    """Calculate employee's current disciplinary status"""
    recent_incidents = incidents_df[
        (incidents_df['employee_id'] == employee_id) &
        (incidents_df['date'] > pd.Timestamp.now() - pd.DateOffset(months=6))
    ]
    
    if len(recent_incidents[recent_incidents['incident_severity'] == 'Severe']) > 0:
        return "High Risk", "status-active"
    elif len(recent_incidents[recent_incidents['incident_severity'] == 'Moderate']) > 1:
        return "Warning", "status-warning"
    elif len(recent_incidents) == 0:
        return "Clear", "status-clear"
    else:
        return "Monitor", "status-warning"

def main():
    st.title("📊 Performance & Disciplinary Analysis")
    
    # Load data
    incidents_df, employees_df = generate_performance_data()
    
    # Filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(incidents_df['date'].min(), incidents_df['date'].max()),
        min_value=incidents_df['date'].min(),
        max_value=incidents_df['date'].max()
    )
    
    # Farm selection
    selected_farms = st.sidebar.multiselect(
        "Select Farms",
        options=incidents_df['farm'].unique(),
        default=incidents_df['farm'].unique()
    )
    
    # Department selection
    selected_departments = st.sidebar.multiselect(
        "Select Departments",
        options=incidents_df['department'].unique(),
        default=incidents_df['department'].unique()
    )
    
    # Filter data
    filtered_incidents = incidents_df[
        (incidents_df['date'].dt.date >= date_range[0]) &
        (incidents_df['date'].dt.date <= date_range[1]) &
        (incidents_df['farm'].isin(selected_farms)) &
        (incidents_df['department'].isin(selected_departments))
    ]
    
    filtered_employees = employees_df[
        (employees_df['farm'].isin(selected_farms)) &
        (employees_df['department'].isin(selected_departments))
    ]
    
    # Key Metrics
    st.subheader("Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_incidents = len(filtered_incidents)
        st.metric(
            "Total Incidents",
            total_incidents,
            "Reported cases"
        )
    
    with col2:
        severe_ratio = (
            len(filtered_incidents[filtered_incidents['incident_severity'] == 'Severe']) / 
            total_incidents * 100 if total_incidents > 0 else 0
        )
        st.metric(
            "Severe Incidents",
            f"{severe_ratio:.1f}%",
            "of total cases"
        )
    
    with col3:
        avg_performance = filtered_employees['performance_rating'].mean()
        st.metric(
            "Avg Performance",
            f"{avg_performance:.2f}/5.0",
            "Rating"
        )
    
    with col4:
        top_performers = (
            len(filtered_employees[filtered_employees['performance_rating'] >= 4.5]) /
            len(filtered_employees) * 100
        )
        st.metric(
            "Top Performers",
            f"{top_performers:.1f}%",
            "Rating ≥ 4.5"
        )
    
    # Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Incident Analysis",
        "Performance Analysis",
        "Correlation Analysis",
        "Employee Records"
    ])
    
    with tab1:
        st.subheader("Disciplinary Incident Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity by Farm
            severity_farm = filtered_incidents.groupby(
                ['farm', 'incident_severity']
            ).size().reset_index(name='count')
            
            fig_severity = px.bar(
                severity_farm,
                x='farm',
                y='count',
                color='incident_severity',
                title="Incident Severity by Farm",
                labels={'count': 'Number of Incidents'},
                color_discrete_map={
                    'Minor': '#2ecc71',
                    'Moderate': '#f1c40f',
                    'Severe': '#e74c3c'
                }
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        
        with col2:
            # Hearing Outcomes
            outcomes = filtered_incidents['hearing_outcome'].value_counts()
            
            fig_outcomes = px.pie(
                values=outcomes.values,
                names=outcomes.index,
                title="Hearing Outcomes Distribution",
                color_discrete_sequence=px.colors.sequential.YlGnBu_r
            )
            st.plotly_chart(fig_outcomes, use_container_width=True)
        
        # Monthly Trend
        monthly_incidents = filtered_incidents.groupby(
            ['date', 'incident_severity']
        ).size().reset_index(name='count')
        
        fig_trend = px.line(
            monthly_incidents,
            x='date',
            y='count',
            color='incident_severity',
            title="Monthly Incident Trends",
            labels={'count': 'Number of Incidents', 'date': 'Month'},
            color_discrete_map={
                'Minor': '#2ecc71',
                'Moderate': '#f1c40f',
                'Severe': '#e74c3c'
            }
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab2:
        st.subheader("Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance Distribution by Farm
            fig_perf = px.box(
                filtered_employees,
                x='farm',
                y='performance_rating',
                title="Performance Rating Distribution by Farm",
                labels={
                    'performance_rating': 'Performance Rating',
                    'farm': 'Farm'
                }
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        
        with col2:
            # Top Performers by Department
            dept_performance = filtered_employees.groupby('department')['performance_rating'].mean()
            
            fig_dept = px.bar(
                x=dept_performance.index,
                y=dept_performance.values,
                title="Average Performance by Department",
                labels={
                    'x': 'Department',
                    'y': 'Average Performance Rating'
                }
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        
        # Top Performers Table
        st.subheader("Top Performing Employees")
        top_employees = filtered_employees[
            filtered_employees['performance_rating'] >= 4.5
        ].sort_values('performance_rating', ascending=False)
        
        st.dataframe(
            top_employees[['name', 'farm', 'department', 'performance_rating', 'years_service']],
            use_container_width=True
        )
    
    with tab3:
        st.subheader("Performance vs. Incidents Analysis")
        
        # Merge incidents with employee data
        employee_incidents = filtered_incidents.groupby('employee_id').size().reset_index(name='incident_count')
        performance_correlation = pd.merge(
            employees_df,
            employee_incidents,
            on='employee_id',
            how='left'
        )
        performance_correlation['incident_count'] = performance_correlation['incident_count'].fillna(0)
        
        # Create scatter plot
        fig_correlation = px.scatter(
            performance_correlation,
            x='performance_rating',
            y='incident_count',
            color='farm',
            title="Performance Rating vs. Number of Incidents",
            labels={
                'performance_rating': 'Performance Rating',
                'incident_count': 'Number of Incidents'
            },
            trendline="ols"
        )
        st.plotly_chart(fig_correlation, use_container_width=True)
        
        # Calculate correlation
        correlation = performance_correlation['performance_rating'].corr(
            performance_correlation['incident_count']
        )
        
        st.info(f"""
            Performance-Incident Correlation: {correlation:.2f}
            
            Note: A negative correlation indicates that employees with higher performance ratings 
            tend to have fewer incidents, while a positive correlation would suggest the opposite.
        """)
    
    with tab4:
        st.subheader("Employee Disciplinary Records")
        
        # Employee search/filter section
        col1, col2, col3 = st.columns([2,2,1])
        
        with col1:
            search_term = st.text_input("Search by Employee Name or ID")
        
        with col2:
            search_farm = st.selectbox(
                "Filter by Farm",
                options=["All Farms"] + list(filtered_employees['farm'].unique())
            )
        
        with col3:
            show_active = st.checkbox("Show Active Only", value=True)
        
        # Filter employees based on search criteria
        employee_filter = filtered_employees.copy()
        if search_term:
            employee_filter = employee_filter[
                (employee_filter['name'].str.contains(search_term, case=False)) |
                (employee_filter['employee_id'].str.contains(search_term, case=False))
            ]
        if search_farm != "All Farms":
            employee_filter = employee_filter[employee_filter['farm'] == search_farm]
        
        # Employee selection
        selected_employee = st.selectbox(
            "Select Employee",
            options=employee_filter['employee_id'].unique(),
            format_func=lambda x: f"{x} - {employee_filter[employee_filter['employee_id'] == x]['name'].iloc[0]}"
        )
        
        if selected_employee:
            # Get employee details
            employee = employees_df[employees_df['employee_id'] == selected_employee].iloc[0]
            employee_incidents = filtered_incidents[filtered_incidents['employee_id'] == selected_employee]
            
           # Calculate employee status
            status, status_class = get_employee_status(incidents_df, selected_employee)
            
            # Display employee details
            st.markdown("### Employee Details")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Name", employee['name'])
            with col2:
                st.metric("Farm", employee['farm'])
            with col3:
                st.metric("Department", employee['department'])
            with col4:
                st.metric("Performance Rating", f"{employee['performance_rating']:.2f}/5.0")
            
            # Display employee status
            st.markdown(f"""
                <div style='padding: 10px; border-radius: 5px; margin: 10px 0; background-color: #f8f9fa;'>
                    <strong>Current Status:</strong> <span class='{status_class}'>{status}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Incident Summary
            st.markdown("### Disciplinary Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Incidents",
                    len(employee_incidents),
                    "All time"
                )
            
            with col2:
                active_warnings = len(employee_incidents[
                    (employee_incidents['hearing_outcome'].isin(['Written Warning', 'Final Warning'])) &
                    (employee_incidents['date'] > pd.Timestamp.now() - pd.DateOffset(months=6))
                ])
                st.metric(
                    "Active Warnings",
                    active_warnings,
                    "Last 6 months"
                )
            
            with col3:
                severe_incidents = len(employee_incidents[
                    employee_incidents['incident_severity'] == 'Severe'
                ])
                st.metric(
                    "Severe Incidents",
                    severe_incidents,
                    "All time"
                )
            
            # Detailed incident history
            st.markdown("### Incident History")
            if not employee_incidents.empty:
                # Create incident history table
                incident_history = employee_incidents.sort_values('date', ascending=False)
                
                # Format the data for display
                display_incidents = incident_history[[
                    'date', 'incident_severity', 'incident_description', 'hearing_outcome', 'case_number'
                ]].copy()
                
                # Add color coding for severity
                def color_severity(val):
                    colors = {
                        'Minor': 'background-color: #d5f5e3',
                        'Moderate': 'background-color: #fdebd0',
                        'Severe': 'background-color: #fadbd8'
                    }
                    return colors.get(val, '')
                
                # Style the dataframe
                styled_incidents = display_incidents.style.applymap(
                    color_severity, 
                    subset=['incident_severity']
                )
                
                # Display the styled table
                st.dataframe(
                    styled_incidents,
                    use_container_width=True
                )
                
                # Incident trend visualization
                st.markdown("### Incident Trend")
                monthly_count = employee_incidents.resample('M', on='date').size().reset_index()
                monthly_count.columns = ['date', 'incidents']
                
                fig_trend = px.line(
                    monthly_count,
                    x='date',
                    y='incidents',
                    title="Monthly Incident History",
                    labels={'incidents': 'Number of Incidents', 'date': 'Month'}
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Add performance overlay
                st.markdown("### Performance vs Incidents")
                fig_performance = go.Figure()
                
                # Add incident bars
                fig_performance.add_trace(go.Bar(
                    x=monthly_count['date'],
                    y=monthly_count['incidents'],
                    name='Incidents',
                    marker_color='#e74c3c'
                ))
                
                # Add performance line
                performance_trend = employee_incidents.groupby('date')['performance_rating'].mean().reset_index()
                fig_performance.add_trace(go.Scatter(
                    x=performance_trend['date'],
                    y=performance_trend['performance_rating'],
                    name='Performance Rating',
                    yaxis='y2',
                    line=dict(color='#2ecc71')
                ))
                
                # Update layout for dual axis
                fig_performance.update_layout(
                    title="Performance Rating vs Incidents",
                    yaxis=dict(title="Number of Incidents"),
                    yaxis2=dict(
                        title="Performance Rating",
                        overlaying='y',
                        side='right',
                        range=[1, 5]
                    ),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_performance, use_container_width=True)
                
            else:
                st.info("No incidents recorded for this employee.")
            
            # Performance History
            st.markdown("### Performance History")
            performance_history = employee_incidents[['date', 'performance_rating']].sort_values('date')
            
            if not performance_history.empty:
                fig_perf = px.line(
                    performance_history,
                    x='date',
                    y='performance_rating',
                    title="Performance Rating Trend",
                    labels={'performance_rating': 'Rating', 'date': 'Date'}
                )
                fig_perf.add_hline(
                    y=4.5,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Excellent Performance"
                )
                fig_perf.add_hline(
                    y=2.5,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Performance Warning"
                )
                st.plotly_chart(fig_perf, use_container_width=True)
            
            # Employee Report Generation
            st.markdown("### Employee Report")
            col1, col2 = st.columns(2)
            
            with col1:
                report_period = st.radio(
                    "Select Report Period",
                    ["Last 6 Months", "Last 12 Months", "All Time"]
                )
            
            with col2:
                report_format = st.radio(
                    "Select Format",
                    ["Excel", "CSV"]
                )
            
            if st.button("Generate Employee Report"):
                # Filter data based on selected period
                if report_period == "Last 6 Months":
                    report_data = employee_incidents[
                        employee_incidents['date'] > pd.Timestamp.now() - pd.DateOffset(months=6)
                    ]
                elif report_period == "Last 12 Months":
                    report_data = employee_incidents[
                        employee_incidents['date'] > pd.Timestamp.now() - pd.DateOffset(months=12)
                    ]
                else:
                    report_data = employee_incidents
                
                if report_format == "Excel":
                    # Prepare Excel report
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        # Employee Details
                        pd.DataFrame([employee]).to_excel(writer, sheet_name='Employee Details', index=False)
                        # Incident History
                        report_data.to_excel(writer, sheet_name='Incident History', index=False)
                    
                    st.download_button(
                        label="Download Excel Report",
                        data=buffer.getvalue(),
                        file_name=f"employee_report_{selected_employee}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    # Prepare CSV report
                    csv = report_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV Report",
                        data=csv,
                        file_name=f"employee_report_{selected_employee}.csv",
                        mime="text/csv"
                    )
    
    # Add data download option
    st.sidebar.markdown("---")
    csv = filtered_incidents.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "📥 Download Complete Analysis Data",
        csv,
        "performance_disciplinary_analysis.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()