#!/usr/bin/env python3

"""
Device Health Report
This script visualizes device health status, sensor status, communication, 
data collection, and cloud connectivity from Microsoft Defender for Endpoint.
"""

import os
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from getpass import getpass

def get_credentials():
    """Prompt for credentials if not already set in environment."""
    tenant_id = os.environ.get('MDE_TENANT_ID')
    client_id = os.environ.get('MDE_CLIENT_ID')
    client_secret = os.environ.get('MDE_CLIENT_SECRET')
    
    if not tenant_id:
        tenant_id = input("Enter your Tenant ID: ").strip()
        os.environ['MDE_TENANT_ID'] = tenant_id
        
    if not client_id:
        client_id = input("Enter your Client ID: ").strip()
        os.environ['MDE_CLIENT_ID'] = client_id
        
    if not client_secret:
        client_secret = getpass("Enter your Client Secret: ").strip()
        os.environ['MDE_CLIENT_SECRET'] = client_secret
    
    return tenant_id, client_id, client_secret

def get_token(tenant_id, client_id, client_secret):
    """Get OAuth2 token with WindowsDefenderATP scope."""
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://api.securitycenter.windows.com/.default',
        'grant_type': 'client_credentials'
    }
    print("Requesting access token...")
    resp = requests.post(url, data=data)
    if not resp.ok:
        print(f"Token request failed with status {resp.status_code}")
        print(f"Error details: {resp.text}")
    resp.raise_for_status()
    return resp.json()['access_token']

def fetch_device_data(token):
    """Fetch device data from Microsoft Defender API."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    url = 'https://api.securitycenter.windows.com/api/machines'
    print(f"Requesting data from: {url}")
    response = requests.get(url, headers=headers)
    print(f"API request status: {response.status_code}")
    
    if not response.ok:
        print(f"API request failed: {response.text}")
    response.raise_for_status()
    
    return response.json()['value']

def process_data(data):
    """Process and transform the device data."""
    df = pd.json_normalize(data)
    
    # Map the columns from Defender API to dashboard format
    df['Health Status'] = df['healthStatus']
    df['Sensor'] = df['onboardingStatus'].map({'Onboarded': 'Enabled', 'NotOnboarded': 'Disabled'})
    df['Sensor Communication'] = df['healthStatus']
    df['Sensor Data Collection'] = df['healthStatus']
    df['Cloud Connectivity'] = df['healthStatus']
    
    return df

def calculate_statistics(df):
    """Calculate summary statistics from the device data."""
    total_devices = len(df)
    healthy_devices = df[df['Health Status'] == 'Healthy']
    unhealthy_devices = df[df['Health Status'] != 'Healthy']
    healthy_pct = 100 * len(healthy_devices) / total_devices if total_devices else 0
    unhealthy_pct = 100 * len(unhealthy_devices) / total_devices if total_devices else 0
    
    return {
        'total': total_devices,
        'healthy': len(healthy_devices),
        'unhealthy': len(unhealthy_devices),
        'healthy_pct': healthy_pct,
        'unhealthy_pct': unhealthy_pct
    }

def create_dashboard(df, stats):
    """Create and display the dashboard visualizations."""
    # Print summary statistics
    print("\nDevice Health Summary:")
    summary_df = pd.DataFrame({
        'Healthy Devices': [f'{stats["healthy_pct"]:.2f}% ({stats["healthy"]} Devices)'],
        'UnHealthy Devices': [f'{stats["unhealthy_pct"]:.2f}% ({stats["unhealthy"]} Devices)']
    })
    print(summary_df.to_string(index=False))

    # Create main figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        specs=[[{'type': 'domain'}],
               [{'type': 'table'}]],
        row_heights=[0.6, 0.4],
        vertical_spacing=0.05
    )

    # Define metrics
    metrics = [
        ('Health Status', 'Healthy'),
        ('Sensor', 'Enabled'),
        ('Sensor Communication', 'Healthy'),
        ('Sensor Data Collection', 'Healthy'),
        ('Cloud Connectivity', 'Healthy')
    ]

    # Add donut charts directly to the main figure
    for i, (col, good_val) in enumerate(metrics):
        good = (df[col] == good_val).sum()
        bad = stats['total'] - good
        
        # Calculate domain positions for evenly spaced donuts
        x_start = 0.02 + (i * 0.195)  # Start at 2% and space evenly
        x_end = x_start + 0.175       # Leave small gap between donuts
        
        fig.add_trace(
            go.Pie(
                values=[good, bad],
                labels=['Healthy', 'Unhealthy'],
                hole=0.7,
                name=col,
                title=dict(
                    text=f"<b>{col}</b><br>{good}/{stats['total']}<br>Healthy",
                    font=dict(size=12),
                    position="top center"
                ),
                marker_colors=['#21c521', '#d62728'],
                textinfo='percent+value',
                hoverinfo='label+percent+value',
                domain={
                    'x': [x_start, x_end],
                    'y': [0.5, 0.95]  # Position in upper half of first row
                },
                hovertemplate="<b>%{label}</b><br>" +
                            "Count: %{value}<br>" +
                            "Percentage: %{percent}<br>" +
                            "<extra></extra>"
            )
        )


        # Create table with important columns
    table_columns = [
        'computerDnsName',
        'osPlatform',
        'version',
        'healthStatus',
        'onboardingStatus',
        'lastIpAddress',
        'lastExternalIpAddress',
        'lastSeen'
    ]

    # Add table to the main figure
    fig.add_trace(
        go.Table(
            header=dict(
                values=[col.replace('_', ' ').title() for col in table_columns],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12)
            ),
            cells=dict(
                values=[df[col] for col in table_columns],
                fill_color='lavender',
                align='left',
                font=dict(size=11)
            )),
        row=2, col=1
    )

    # Update main figure layout
    fig.update_layout(
        height=1200,
        width=1500,
        title=dict(
            text='Device Health Dashboard',
            x=0.5,
            y=0.98,
            xanchor='center',
            yanchor='top',
            font=dict(size=24)
        ),
        showlegend=False,
        margin=dict(t=120, b=20, l=20, r=20),  # Increased top margin for title
        grid=dict(rows=2, columns=1, pattern='independent'),  # Ensure independent sizing
        annotations=[
            # Add Device Health Overview subtitle
            dict(
                text="Device Health Overview",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.9,  # Position above the donut charts
                showarrow=False,
                font=dict(size=18),
                xanchor="center"
            )
        ]
    )

    # Save the combined dashboard to HTML
    dashboard_html = 'device_health_dashboard.html'
    fig.write_html(dashboard_html)
    print(f"\nDashboard saved to: {dashboard_html}")

    # Open the HTML file in the default browser
    import webbrowser
    webbrowser.open(dashboard_html)

def main():
    """Main execution function."""
    try:
        print("Please enter your Microsoft Defender for Endpoint API credentials:")
        tenant_id, client_id, client_secret = get_credentials()
        
        if not all([client_id, client_secret, tenant_id]):
            raise ValueError("All credentials (Tenant ID, Client ID, and Client Secret) are required.")
        
        token = get_token(tenant_id, client_id, client_secret)
        data = fetch_device_data(token)
        df = process_data(data)
        stats = calculate_statistics(df)
        create_dashboard(df, stats)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
