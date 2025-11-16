import streamlit as st
import pandas as pd
import requests
import datetime

# --- API Configuration ---
API_URL = "http://127.0.0.1:8000"

# --- API Helper Functions ---

def handle_api_error(response, context="action"):
    """Helper to display API errors in Streamlit."""
    try:
        detail = response.json().get("detail", response.text)
    except requests.exceptions.JSONDecodeError:
        detail = response.text
    st.error(f"Failed to {context}: {response.status_code} - {detail}")

@st.cache_data(ttl=5) # Short cache for editing pages
def fetch_lookup_tables(endpoint_name):
    """Fetches clients, work_type, etc. from the API."""
    try:
        response = requests.get(f"{API_URL}/{endpoint_name}/")
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)

        # --- FIX: Convert date columns after fetching ---
        if endpoint_name == "clients" and not df.empty:
            df['client_start_date'] = pd.to_datetime(df['client_start_date']).dt.date
            df['client_end_date'] = pd.to_datetime(df['client_end_date']).dt.date
        
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching {endpoint_name}: {e}")
        return pd.DataFrame()

# --- Page ---

st.set_page_config(page_title="Client Config", page_icon="👥", layout="wide")
st.title("👥 Client Configuration")

# --- Load Data ---
df_clients = fetch_lookup_tables("clients")
df_units = fetch_lookup_tables("units")

if df_units.empty:
    st.error("Failed to load Business Units. Is the API running?")
    st.stop()

# --- 1. Add New Client ---
st.header("➕ Add New Client")
unit_map = dict(zip(df_units['business_unit_id'], df_units['business_unit_name']))

with st.form("new_client_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        business_unit_id = st.selectbox(
            "Business Unit", 
            options=unit_map.keys(), 
            format_func=lambda id: unit_map.get(id, "Unknown")
        )
    with col2:
        client_start_date = st.date_input("Client Start Date", datetime.date.today())
        client_active = st.checkbox("Client is Active", value=True)
        
    submitted = st.form_submit_button("Add Client")

if submitted:
    if not client_name:
        st.warning("Client Name is required.")
    else:
        payload = {
            "client_name": client_name,
            "client_active": client_active,
            "client_start_date": client_start_date.isoformat(),
            "business_unit_id": business_unit_id,
            "client_end_date": None # Explicitly set end date to None on creation
        }
        try:
            response = requests.post(f"{API_URL}/clients/", json=payload)
            if response.status_code == 200:
                st.success(f"Client '{client_name}' added successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                handle_api_error(response, "add client")
        except requests.exceptions.RequestException as e:
            st.error(f"Error adding client: {e}")

st.divider()

# --- 2. Edit Existing Clients ---
st.header("✏️ Edit Clients")

if df_clients.empty:
     st.info("No clients found. Add one using the form above.")
else:
    # We need to make sure the data editor uses the latest data on rerun
    client_editor_state = st.data_editor(
        df_clients,
        key="client_editor",
        num_rows="dynamic",
        disabled=["client_id"],
        column_config={
            "client_id": st.column_config.NumberColumn("ID", disabled=True),
            "client_name": st.column_config.TextColumn("Client Name", required=True),
            "client_active": st.column_config.CheckboxColumn("Active?"),
            "client_start_date": st.column_config.DateColumn("Start Date", format="YYYY-MM-DD", required=True),
            "client_end_date": st.column_config.DateColumn("End Date", format="YYYY-MM-DD"),
            "business_unit_id": st.column_config.SelectboxColumn(
                "Business Unit",
                options=unit_map.keys(),
                format_func=lambda id: unit_map.get(id, "Unknown"),
                required=True
            )
        },
        use_container_width=True
    )

    if st.button("💾 Save Client Changes"):
        # Compare the edited state with the original dataframe
        original_df = df_clients.set_index('client_id')
        edited_df = client_editor_state.set_index('client_id')
        
        update_count = 0
        delete_count = 0
        
        # Find updates
        # We use 'try...except' to catch rows that might be in one df but not the other
        for client_id, row in edited_df.iterrows():
            if client_id not in original_df.index:
                # This is a new row added via the editor, but we prefer the "Add" form
                st.warning(f"Row for {row['client_name']} was added in the editor. Please use the 'Add New Client' form.")
                continue
                
            original_row = original_df.loc[client_id]
            
            # Convert to dicts for proper comparison
            row_dict = row.to_dict()
            original_row_dict = original_row.to_dict()

            # Handle NaT/None comparison issues
            if pd.isna(row_dict['client_end_date']): row_dict['client_end_date'] = None
            if pd.isna(original_row_dict['client_end_date']): original_row_dict['client_end_date'] = None

            if row_dict != original_row_dict:
                # Row has changed
                payload = row.to_dict()
                # Convert date columns to ISO strings for JSON
                payload['client_start_date'] = payload['client_start_date'].isoformat()
                if pd.notna(payload['client_end_date']):
                    payload['client_end_date'] = payload['client_end_date'].isoformat()
                else:
                    payload['client_end_date'] = None
                
                try:
                    response = requests.put(f"{API_URL}/clients/{client_id}", json=payload)
                    if response.status_code == 200:
                        update_count += 1
                    else:
                        handle_api_error(response, f"update client {client_id}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error updating client {client_id}: {e}")

        # Find deletions
        deleted_ids = set(original_df.index) - set(edited_df.index)
        for client_id in deleted_ids:
            try:
                response = requests.delete(f"{API_URL}/clients/{client_id}")
                if response.status_code == 200:
                    delete_count += 1
                else:
                    handle_api_error(response, f"delete client {client_id}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error deleting client {client_id}: {e}")

        if update_count > 0 or delete_count > 0:
            st.success(f"Successfully saved {update_count} update(s) and {delete_count} deletion(s)!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.info("No changes detected.")