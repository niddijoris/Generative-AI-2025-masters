"""
Chart generation for business insights visualization
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any


def create_price_distribution_chart(data: pd.DataFrame) -> go.Figure:
    """
    Create a histogram showing price distribution
    
    Args:
        data: DataFrame with sellingprice column
        
    Returns:
        Plotly figure
    """
    fig = px.histogram(
        data,
        x='sellingprice',
        nbins=50,
        title='Car Price Distribution',
        labels={'sellingprice': 'Selling Price ($)', 'count': 'Number of Cars'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_top_makes_chart(stats: Dict[str, Any]) -> go.Figure:
    """
    Create a bar chart showing top car makes
    
    Args:
        stats: Statistics dictionary with top_makes data
        
    Returns:
        Plotly figure
    """
    top_makes = stats.get('top_makes', [])
    
    if not top_makes:
        return go.Figure()
    
    makes = [item['make'] for item in top_makes]
    counts = [item['count'] for item in top_makes]
    
    fig = go.Figure(data=[
        go.Bar(
            x=makes,
            y=counts,
            marker_color='#2ca02c',
            text=counts,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Top 5 Car Makes',
        xaxis_title='Make',
        yaxis_title='Number of Cars',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_condition_pie_chart(stats: Dict[str, Any]) -> go.Figure:
    """
    Create a pie chart showing condition distribution
    
    Args:
        stats: Statistics dictionary with condition_distribution data
        
    Returns:
        Plotly figure
    """
    condition_dist = stats.get('condition_distribution', [])
    
    if not condition_dist:
        return go.Figure()
    
    # Take top 10 conditions
    condition_dist = condition_dist[:10]
    
    conditions = [str(item['condition']) for item in condition_dist]
    counts = [item['count'] for item in condition_dist]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=conditions,
            values=counts,
            hole=0.3
        )
    ])
    
    fig.update_layout(
        title='Car Condition Distribution',
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_price_by_make_chart(db_manager) -> go.Figure:
    """Create a bar chart of average price by make (top 10)"""
    query = """
        SELECT make, AVG(sellingprice) as avg_price 
        FROM cars 
        GROUP BY make 
        ORDER BY avg_price DESC 
        LIMIT 10
    """
    result = db_manager.execute_query(query)
    
    if result['success'] and result['data']:
        df = pd.DataFrame(result['data'])
        fig = px.bar(
            df, 
            x='make', 
            y='avg_price',
            title='Top 10 Average Prices by Make',
            labels={'make': 'Make', 'avg_price': 'Average Price ($)'},
            template='plotly_white',
            color='avg_price',
            color_continuous_scale='Blues'
        )
        return fig
    else:
        # Return empty figure if data fails
        return go.Figure()


def create_dynamic_chart(data: list, chart_type: str, title: str, x_label: str, y_label: str) -> go.Figure:
    """
    Create a dynamic chart based on data and configuration provided by the AI agent.
    
    Args:
        data: List of dictionaries containing the data
        chart_type: Type of chart ('bar', 'column', 'line', 'pie', 'scatter')
        title: Chart title
        x_label: Name of the column for X axis
        y_label: Name of the column for Y axis (or value for pie)
        
    Returns:
        Plotly Figure object
    """
    if not data:
        return go.Figure()
        
    df = pd.DataFrame(data)
    
    # Ensure labels exist in dataframe, if not, use first columns
    if x_label not in df.columns:
        x_label = df.columns[0]
    if y_label not in df.columns and len(df.columns) > 1:
        y_label = df.columns[1]
    elif y_label not in df.columns:
        y_label = x_label

    if chart_type.lower() in ['bar', 'column']:
        fig = px.bar(
            df, 
            x=x_label, 
            y=y_label, 
            title=title,
            template='plotly_white',
            color=y_label if y_label != x_label else None
        )
    elif chart_type.lower() == 'line':
        fig = px.line(
            df, 
            x=x_label, 
            y=y_label, 
            title=title,
            template='plotly_white',
            markers=True
        )
    elif chart_type.lower() == 'pie':
        fig = px.pie(
            df, 
            names=x_label, 
            values=y_label, 
            title=title,
            template='plotly_white'
        )
    elif chart_type.lower() == 'scatter':
        fig = px.scatter(
            df, 
            x=x_label, 
            y=y_label, 
            title=title,
            template='plotly_white',
            color=y_label if y_label != x_label else None
        )
    else:
        # Fallback to bar chart
        fig = px.bar(df, x=x_label, y=y_label, title=title, template='plotly_white')
        
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=x_label,
        yaxis_title=y_label if chart_type.lower() != 'pie' else ""
    )
    
    return fig
