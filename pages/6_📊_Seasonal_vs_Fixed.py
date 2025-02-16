# pages/6_📊_Seasonal_vs_Fixed.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(
    page_title="Seasonal vs Fixed Analysis",
    page_icon="📊",
    layout="wide"
)

# Generate sample data
@st.cache_data
def generate_workforce_data():
    farms = ['Farm A', 'Farm B', 'Farm C', 'Farm D']
    months = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    
    data = []
    
    for farm in farms:
        # Base number of fixed workers for each farm
        base_fixed = np.random.randint(30, 50)
        
        for date in months:
            # Minimal variation in fixed workers
            fixed_workers = int(base_fixed * (1 + np.random.uniform(-0.05, 0.05)))
            
            # Seasonal workers vary by season
            if date.month in [11, 12, 1, 2]:  # Peak harvest season
                seasonal_workers = np.random.randint(40, 70)
                season_type = 'Peak'
            elif date.month in [3, 4, 9, 10]:  # Medium season
                seasonal_workers = np.random.randint(20, 40)
                season_type = 'Medium'
            else:  # Low season
                seasonal_workers = np.random.randint(5, 15)
                season_type = 'Low'
            
            # Calculate costs
            fixed_cost = fixed_workers * 8000  # R8000 per fixed worker per month
            seasonal_cost = seasonal_workers * 4400   # R200 per day * 22 working days
            
            data.append({
                'date': date,
                'farm': farm,
                'season_type': season_type,
                'fixed_workers': fixed_workers,
                'seasonal_workers': seasonal_workers,
                'fixed_cost': fixed_cost,
                'seasonal_cost': seasonal_cost,
                'total_workers': fixed_workers + seasonal_workers,
                'total_cost': fixed_cost + seasonal_cost
            })
    
    return pd.DataFrame(data)

def format_currency(value):
    """Format values to South African Rand"""
    return f"R{value:,.2f}"

def main():
    st.title("📊 Seasonal vs Fixed Workforce Analysis")
    st.markdown("Compare seasonal and fixed workforce patterns across farms and seasons")
    
    # Load data
    df = generate_workforce_data()
    
    # Filters
    st.sidebar.header("Filters")
    
    selected_farms = st.sidebar.multiselect(
        "Select Farms",
        options=df['farm'].unique(),
        default=df['farm'].unique()
    )
    
    selected_seasons = st.sidebar.multiselect(
        "Select Seasons",
        options=df['season_type'].unique(),
        default=df['season_type'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['farm'].isin(selected_farms)) &
        (df['season_type'].isin(selected_seasons))
    ]
    
    # Current Overview
    latest_data = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Fixed Workers",
            f"{latest_data['fixed_workers'].sum():,}",
            "Current Month"
        )
    
    with col2:
        st.metric(
            "Total Seasonal Workers",
            f"{latest_data['seasonal_workers'].sum():,}",
            "Current Month"
        )
    
    with col3:
        fixed_ratio = (latest_data['fixed_workers'].sum() / 
                      latest_data['total_workers'].sum() * 100)
        st.metric(
            "Fixed Worker Ratio",
            f"{fixed_ratio:.1f}%",
            "of Total Workforce"
        )
    
    with col4:
        st.metric(
            "Total Monthly Cost",
            format_currency(latest_data['total_cost'].sum()),
            "Combined Workforce"
        )
    
    # Analysis Tabs
    tab1, tab2, tab3 = st.tabs([
        "Workforce Distribution",
        "Seasonal Patterns",
        "Cost Analysis"
    ])
    
    with tab1:
        st.subheader("Monthly Workforce Distribution")
        
        # Monthly distribution chart
        fig_monthly = px.bar(
            filtered_df,
            x='date',
            y=['fixed_workers', 'seasonal_workers'],
            title="Fixed vs Seasonal Workers Over Time",
            labels={
                'date': 'Month',
                'value': 'Number of Workers',
                'variable': 'Worker Type'
            },
            barmode='group',
            color_discrete_map={
                'fixed_workers': '#2ecc71',
                'seasonal_workers': '#f1c40f'
            }
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Farm-wise breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Current distribution by farm
            fig_farm = px.bar(
                latest_data,
                x='farm',
                y=['fixed_workers', 'seasonal_workers'],
                title="Current Workforce by Farm",
                labels={
                    'farm': 'Farm',
                    'value': 'Number of Workers',
                    'variable': 'Worker Type'
                },
                barmode='group',
                color_discrete_map={
                    'fixed_workers': '#2ecc71',
                    'seasonal_workers': '#f1c40f'
                }
            )
            st.plotly_chart(fig_farm, use_container_width=True)
        
        with col2:
            # Workforce composition
            latest_data['fixed_ratio'] = latest_data['fixed_workers'] / latest_data['total_workers'] * 100
            
            fig_ratio = px.bar(
                latest_data,
                x='farm',
                y='fixed_ratio',
                title="Fixed Worker Ratio by Farm",
                labels={
                    'farm': 'Farm',
                    'fixed_ratio': 'Fixed Workers (%)'
                }
            )
            fig_ratio.update_traces(
                text=latest_data['fixed_ratio'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside'
            )
            st.plotly_chart(fig_ratio, use_container_width=True)
    
    with tab2:
        st.subheader("Seasonal Patterns Analysis")
        
        # Seasonal averages
        seasonal_avg = filtered_df.groupby('season_type').agg({
            'fixed_workers': 'mean',
            'seasonal_workers': 'mean',
            'total_cost': 'mean'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Worker numbers by season
            fig_season = px.bar(
                seasonal_avg,
                x='season_type',
                y=['fixed_workers', 'seasonal_workers'],
                title="Average Workers by Season",
                labels={
                    'season_type': 'Season',
                    'value': 'Average Number of Workers',
                    'variable': 'Worker Type'
                },
                barmode='group',
                color_discrete_map={
                    'fixed_workers': '#2ecc71',
                    'seasonal_workers': '#f1c40f'
                }
            )
            st.plotly_chart(fig_season, use_container_width=True)
        
        with col2:
            # Cost by season
            fig_season_cost = px.line(
                seasonal_avg,
                x='season_type',
                y='total_cost',
                title="Average Total Cost by Season",
                labels={
                    'season_type': 'Season',
                    'total_cost': 'Average Cost (ZAR)',
                    'variable': 'Season Type'
                },
                markers=True
            )
            st.plotly_chart(fig_season_cost, use_container_width=True)
    
    with tab3:
        st.subheader("Cost Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Average cost per worker type by farm
            avg_costs = []
            for farm in selected_farms:
                farm_data = filtered_df[filtered_df['farm'] == farm]
                avg_fixed_cost = farm_data['fixed_cost'].sum() / farm_data['fixed_workers'].sum()
                avg_seasonal_cost = farm_data['seasonal_cost'].sum() / farm_data['seasonal_workers'].sum()
                avg_costs.extend([
                    {'farm': farm, 'worker_type': 'Fixed', 'avg_cost': avg_fixed_cost},
                    {'farm': farm, 'worker_type': 'Seasonal', 'avg_cost': avg_seasonal_cost}
                ])
            
            avg_cost_df = pd.DataFrame(avg_costs)
            
            # Create bar chart for average costs
            fig_avg_cost = px.bar(
                avg_cost_df,
                x='farm',
                y='avg_cost',
                color='worker_type',
                title="Average Monthly Cost per Worker Type by Farm",
                labels={
                    'farm': 'Farm',
                    'avg_cost': 'Average Cost per Worker (ZAR)',
                    'worker_type': 'Worker Type'
                },
                barmode='group',
                color_discrete_map={
                    'Fixed': '#2ecc71',
                    'Seasonal': '#f1c40f'
                }
            )
            
            # Add value labels
            fig_avg_cost.update_traces(
                texttemplate='R%{y:,.0f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_avg_cost, use_container_width=True)
        
        with col2:
            # Monthly stacked cost trends by farm
            monthly_farm_costs = filtered_df.groupby(['date', 'farm']).agg({
                'fixed_cost': 'sum',
                'seasonal_cost': 'sum'
            }).reset_index()
            
            # Create stacked bar chart
            fig_monthly_cost = go.Figure()
            
            # Color palette for farms
            farm_colors = {
                'Farm A': '#2ecc71',  # Green
                'Farm B': '#3498db',  # Blue
                'Farm C': '#e74c3c',  # Red
                'Farm D': '#f1c40f'   # Yellow
            }
            
            # Add traces for each farm's fixed costs
            for farm in selected_farms:
                farm_data = monthly_farm_costs[monthly_farm_costs['farm'] == farm]
                
                # Fixed costs
                fig_monthly_cost.add_trace(go.Bar(
                    name=f'{farm} - Fixed',
                    x=farm_data['date'],
                    y=farm_data['fixed_cost'],
                    marker_color=farm_colors[farm],
                    text=farm_data['fixed_cost'].apply(lambda x: f'R{x:,.0f}'),
                    textposition='inside',
                    opacity=0.8
                ))
                
                # Seasonal costs
                fig_monthly_cost.add_trace(go.Bar(
                    name=f'{farm} - Seasonal',
                    x=farm_data['date'],
                    y=farm_data['seasonal_cost'],
                    marker_color=farm_colors[farm],
                    text=farm_data['seasonal_cost'].apply(lambda x: f'R{x:,.0f}'),
                    textposition='inside',
                    opacity=0.4
                ))
            
            # Update layout
            fig_monthly_cost.update_layout(
                title="Monthly Cost Distribution by Farm",
                barmode='stack',
                xaxis_title="Month",
                yaxis_title="Cost (ZAR)",
                hovermode='x unified',
                showlegend=True,
                legend_title="Farm & Cost Type",
                height=500
            )
            
            st.plotly_chart(fig_monthly_cost, use_container_width=True)
            
            # Add a note about opacity
            st.markdown("""
                <div style='text-align: center; color: #666;'>
                    <small>Note: Solid colors represent fixed costs, transparent colors represent seasonal costs</small>
                </div>
            """, unsafe_allow_html=True)

    # Add data download option
    st.sidebar.markdown("---")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "📥 Download Analysis Data",
        csv,
        "seasonal_fixed_analysis.csv",
        "text/csv",
        key='download-csv'
    )

if __name__ == "__main__":
    main()