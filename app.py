import streamlit as st
import pandas as pd
import requests
import datetime

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000"

# --- Page Configuration ---
st.set_page_config(
    page_title="Client Work Forecast",
    page_icon="📊",
    layout="wide"
)

# --- API Helper Functions ---

def handle_api_error(response, context="action"):
    """Helper to display API errors in Streamlit."""
    try:
        detail = response.json().get("detail", response.text)
    except requests.exceptions.JSONDecodeError:
        detail = response.text
    st.error(f"Failed to {context}: {response.status_code} - {detail}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_all_forecasts():
    """Fetches all forecasts from the API."""
    try:
        response = requests.get(f"{API_URL}/forecasts/")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        df = pd.DataFrame(data)
        if not df.empty:
            df['dt'] = pd.to_datetime(df['dt']).dt.date
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching forecasts: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600) # Cache lookups for 10 mins
def fetch_lookup_tables(endpoint_name):
    """Fetches clients, work_type, etc. from the API."""
    try:
        response = requests.get(f"{API_URL}/{endpoint_name}/")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching {endpoint_name}: {e}")
        return pd.DataFrame()

# --- Main Application ---
def main():
    st.title("📊 Client Work Forecast Dashboard")
    
    # Check if API is running
    try:
        requests.get(f"{API_URL}/docs")
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API at {API_URL}.")
        st.info("Please ensure the FastAPI server is running: uvicorn main:app --reload")
        st.stop()

    # --- Load Data ---
    df_forecasts = fetch_all_forecasts()
    df_clients = fetch_lookup_tables("clients")
    df_work_types = fetch_lookup_tables("work_types") # Corrected endpoint name
    
    # These are now only needed for the charts, as lookups are in df_forecasts
    df_business_units = fetch_lookup_tables("units")
    df_business_verticals = fetch_lookup_tables("verticals")

    if df_forecasts.empty:
        st.info("No forecast data found. Use the 'Add New Forecast' form to get started.")
    
    # --- 1. Basic Stats ---
    if not df_forecasts.empty:
        st.header("📈 Basic Stats")
        
        # KPIs
        total_forecast = df_forecasts['forecast_amount'].sum()
        avg_forecast = df_forecasts['forecast_amount'].mean()
        num_clients = df_forecasts['client_name'].nunique()
        num_bus = df_forecasts['business_unit_name'].nunique()
        num_bvs = df_forecasts['business_vertical_name'].nunique()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Forecast Amount", f"${total_forecast:,.0f}")
        col2.metric("Avg. Forecast", f"${avg_forecast:,.2f}")
        col3.metric("Clients", num_clients)
        col4.metric("Business Units", num_bus)
        col5.metric("Verticals", num_bvs)
        
        st.divider()

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Forecast by Business Vertical")
            bv_stats = df_forecasts.groupby('business_vertical_name')['forecast_amount'].sum()
            st.bar_chart(bv_stats)
        
        with col2:
            st.subheader("Forecast by Business Unit")
            bu_stats = df_forecasts.groupby('business_unit_name')['forecast_amount'].sum()
            st.bar_chart(bu_stats)

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Forecast by Client")
            client_stats = df_forecasts.groupby('client_name')['forecast_amount'].sum()
            st.bar_chart(client_stats)
        
        with col4:
            st.subheader("Forecast by Work Type")
            work_type_stats = df_forecasts.groupby('work_type_name')['forecast_amount'].sum()
            st.bar_chart(work_type_stats)

        st.subheader("Forecast Over Time")
        time_stats = df_forecasts.copy()
        time_stats['dt'] = pd.to_datetime(time_stats['dt'])
        time_stats = time_stats.set_index('dt').resample('MS')['forecast_amount'].sum()
        st.line_chart(time_stats)

    # --- 2. Add New Forecast ---
    st.header("➕ Add New Forecast")
    
    # Create maps for easy lookup
    client_map = dict(zip(df_clients['client_name'], df_clients['client_id']))
    work_type_map = dict(zip(df_work_types['work_type_name'], df_work_types['work_type_id']))

    with st.form("new_forecast_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.selectbox("Client", options=sorted(client_map.keys()))
            work_type_name = st.selectbox("Work Type", options=sorted(work_type_map.keys()))
        with col2:
            forecast_date = st.date_input("Forecast Date", datetime.date.today().replace(day=1))
            forecast_amount = st.number_input("Forecast Amount", min_value=0, step=100)
        
        submitted = st.form_submit_button("Add Forecast")

    if submitted:
        client_id = client_map[client_name]
        work_type_id = work_type_map[work_type_name]
        
        # Get the business_unit_id from the selected client
        try:
            client_row = df_clients[df_clients['client_id'] == client_id].iloc[0]
            business_unit_id = int(client_row['business_unit_id'])
        except Exception as e:
            st.error(f"Could not find business unit for client {client_name}. Error: {e}")
            st.stop()

        # Create the payload for the API
        forecast_payload = {
            "client_id": client_id,
            "business_unit_id": business_unit_id,
            "work_type_id": work_type_id,
            "dt": forecast_date.isoformat(),
            "forecast_amount": forecast_amount,
            "forecast_name": f"{client_name} - {work_type_name}" # Optional name
        }

        try:
            response = requests.post(f"{API_URL}/forecasts/", json=forecast_payload)
            if response.status_code == 200:
                st.success("New forecast added successfully!")
                st.cache_data.clear() # Clear all data caches
                st.rerun()
            else:
                handle_api_error(response, "add forecast")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to add new forecast: {e}")

    # --- 3. View & Edit Forecasts ---
    st.header("✏️ View & Edit Forecasts")
    
    if df_forecasts.empty:
        st.info("No data to display.")
    else:
        edited_df = st.data_editor(
            df_forecasts,
            key="forecast_editor",
            num_rows="dynamic", # Allows deleting rows
            disabled=[
                "forecast_id", "business_vertical_name", "business_unit_name", 
                "client_name", "work_type_name", "dt"
            ],
            column_config={
                "forecast_id": st.column_config.NumberColumn("ID", disabled=True),
                "business_vertical_name": st.column_config.TextColumn("Vertical", disabled=True),
                "business_unit_name": st.column_config.TextColumn("Business Unit", disabled=True),
                "client_name": st.column_config.TextColumn("Client", disabled=True),
                "work_type_name": st.column_config.TextColumn("Work Type", disabled=True),
                "dt": st.column_config.DateColumn("Date", format="YYYY-MM-DD", disabled=True),
                "forecast_amount": st.column_config.NumberColumn(
                    "Amount",
                    min_value=0,
                    step=100,
                    format="$%d"
                )
            },
            use_container_width=True,
            height=400
        )

        col1, col2 = st.columns([1, 6])
        
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                comparison_df = df_forecasts.merge(
                    edited_df,
                    on=[
                        'forecast_id', 'business_vertical_name', 'business_unit_name',
                        'client_name', 'work_type_name', 'dt'
                    ],
                    how='outer',
                    suffixes=('_orig', '_new'),
                    indicator=True
                )

                # 1. Handle Updates (amount changed)
                updates = comparison_df[
                    (comparison_df['_merge'] == 'both') &
                    (comparison_df['forecast_amount_orig'] != comparison_df['forecast_amount_new'])
                ]
                
                update_count = 0
                for _, row in updates.iterrows():
                    forecast_id = row['forecast_id']
                    update_payload = {"forecast_amount": int(row['forecast_amount_new'])}
                    try:
                        response = requests.put(f"{API_URL}/forecasts/{forecast_id}", json=update_payload)
                        if response.status_code == 200:
                            update_count += 1
                        else:
                            handle_api_error(response, f"update forecast {forecast_id}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error updating forecast {forecast_id}: {e}")
                
                # 2. Handle Deletions (row in original but not in edited)
                deletions = comparison_df[comparison_df['_merge'] == 'left_only']
                delete_count = 0
                for _, row in deletions.iterrows():
                    forecast_id = row['forecast_id']
                    try:
                        response = requests.delete(f"{API_URL}/forecasts/{forecast_id}")
                        if response.status_code == 200:
                            delete_count += 1
                        else:
                            handle_api_error(response, f"delete forecast {forecast_id}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error deleting forecast {forecast_id}: {e}")

                if update_count > 0 or delete_count > 0:
                    st.success(f"Successfully saved {update_count} update(s) and {delete_count} deletion(s)!")
                    st.cache_data.clear() # Clear caches
                    st.rerun()
                else:
                    st.info("No changes detected.")

if __name__ == "__main__":
    main()