import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
import io

def generate_manufacturing_data(n_samples=1000):
    """Generate synthetic manufacturing quality data"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=n_samples)
    dimensions = np.random.normal(100, 2, n_samples)
    weights = np.random.normal(250, 5, n_samples)
    density = np.random.normal(2.7, 0.1, n_samples)
    
    dimensions[::50] += np.random.uniform(5, 10, len(dimensions[::50]))
    weights[::40] -= np.random.uniform(10, 20, len(weights[::40]))
    
    batch_numbers = [f"B{i:04d}" for i in range(1, n_samples + 1)]
    
    return pd.DataFrame({
        'Date': dates,
        'Batch': batch_numbers,
        'Dimension_mm': dimensions,
        'Weight_g': weights,
        'Density_g_cm3': density
    })

def calculate_process_capability(data, column, lsl, usl):
    """Calculate Cp, Cpk, and other process capability metrics"""
    mean = data[column].mean()
    std = data[column].std()
    
    cp = (usl - lsl) / (6 * std)
    cpu = (usl - mean) / (3 * std)
    cpl = (mean - lsl) / (3 * std)
    cpk = min(cpu, cpl)
    
    return {
        'Mean': mean,
        'StdDev': std,
        'Cp': cp,
        'Cpk': cpk,
        'CPU': cpu,
        'CPL': cpl
    }

def load_data(uploaded_file):
    """Load and process uploaded data file"""
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        data = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Unsupported file format")
    
    # Convert date column if exists
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])
    
    return data

def main():
    st.title("Quality Engineering Analysis Dashboard")
    
    # File upload section
    st.sidebar.header("Data Input")
    data_source = st.sidebar.radio(
        "Select Data Source",
        ["Upload File", "Use Sample Data"]
    )
    
    if data_source == "Upload File":
        uploaded_file = st.sidebar.file_uploader(
            "Upload your data file",
            type=['csv', 'xlsx', 'xls']
        )
        if uploaded_file:
            try:
                data = load_data(uploaded_file)
                st.sidebar.success("File loaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error loading file: {str(e)}")
                return
        else:
            st.info("Please upload a file or select 'Use Sample Data'")
            return
    else:
        data = generate_manufacturing_data()
    
    # Display available columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    
    # Analysis parameters
    st.sidebar.header("Analysis Parameters")
    feature = st.sidebar.selectbox(
        "Select Feature",
        numeric_columns
    )
    
    # User-defined specification limits
    st.sidebar.subheader("Specification Limits")
    default_mean = data[feature].mean()
    default_std = data[feature].std()
    
    lsl = st.sidebar.number_input("Lower Spec Limit", 
                                 value=float(default_mean - 3*default_std))
    usl = st.sidebar.number_input("Upper Spec Limit", 
                                 value=float(default_mean + 3*default_std))
    target = st.sidebar.number_input("Target Value", 
                                    value=float(default_mean))
    
    # Statistical Analysis
    stats_data = calculate_process_capability(data, feature, lsl, usl)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cp", f"{stats_data['Cp']:.2f}")
    col2.metric("Cpk", f"{stats_data['Cpk']:.2f}")
    col3.metric("Mean", f"{stats_data['Mean']:.2f}")
    col4.metric("Std Dev", f"{stats_data['StdDev']:.2f}")
    
    # Control Chart
    fig_control = go.Figure()
    x_axis = data.index if 'Date' not in data.columns else data['Date']
    fig_control.add_trace(go.Scatter(x=x_axis, y=data[feature], mode='lines+markers'))
    fig_control.add_hline(y=usl, line_color='red', line_dash='dash')
    fig_control.add_hline(y=lsl, line_color='red', line_dash='dash')
    fig_control.add_hline(y=target, line_color='green')
    fig_control.update_layout(title='Control Chart', height=400)
    st.plotly_chart(fig_control, use_container_width=True)
    
    # Histogram
    fig_hist = px.histogram(data, x=feature, nbins=30)
    fig_hist.add_vline(x=usl, line_color='red', line_dash='dash')
    fig_hist.add_vline(x=lsl, line_color='red', line_dash='dash')
    fig_hist.add_vline(x=target, line_color='green')
    fig_hist.update_layout(title='Distribution Analysis', height=400)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Raw Data Table
    st.subheader("Raw Data Sample")
    st.dataframe(data.head(10))
    
    # Download processed data
    if st.button("Download Analyzed Data"):
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="analyzed_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()