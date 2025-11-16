import streamlit as st
import pandas as pd
import requests

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

@st.cache_data(ttl=5)
def fetch_lookup_tables(endpoint_name):
    """Fetches data from the API."""
    try:
        response = requests.get(f"{API_URL}/{endpoint_name}/")
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching {endpoint_name}: {e}")
        return pd.DataFrame()

# --- Page ---
st.set_page_config(page_title="Business Structure", page_icon="🏗️", layout="wide")
st.title("🏗️ Business Structure")

# --- Load Data ---
df_verticals = fetch_lookup_tables("verticals")
df_units = fetch_lookup_tables("units")

if df_verticals.empty:
    st.error("Failed to load Business Verticals. Is the API running?")
    # We can still proceed if units load, but the map will be empty
    
vertical_map = dict(zip(df_verticals['business_vertical_id'], df_verticals['business_vertical_name']))

# --- Tabs ---
tab1, tab2 = st.tabs(["Business Verticals", "Business Units"])

# --- Tab 1: Business Verticals ---
with tab1:
    st.subheader("Manage Business Verticals")
    
    # Add form
    with st.expander("➕ Add New Vertical"):
        with st.form("new_vertical_form", clear_on_submit=True):
            vertical_name = st.text_input("Vertical Name")
            submitted = st.form_submit_button("Add Vertical")
            if submitted:
                if vertical_name:
                    try:
                        response = requests.post(f"{API_URL}/verticals/", json={"business_vertical_name": vertical_name})
                        if response.status_code == 200:
                            st.success(f"Vertical '{vertical_name}' added.")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            handle_api_error(response, "add vertical")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Vertical Name is required.")

    # Edit table
    st.subheader("Edit Verticals")
    if df_verticals.empty:
        st.info("No Business Verticals found. Add one using the form above.")
    else:
        edited_verticals = st.data_editor(
            df_verticals,
            key="vertical_editor",
            num_rows="dynamic",
            disabled=["business_vertical_id"],
            column_config={
                "business_vertical_id": st.column_config.NumberColumn("ID", disabled=True),
                "business_vertical_name": st.column_config.TextColumn("Vertical Name", required=True)
            },
            use_container_width=True
        )
        
        if st.button("💾 Save Vertical Changes"):
            # Logic to save changes
            original_df = df_verticals.set_index('business_vertical_id')
            edited_df = edited_verticals.set_index('business_vertical_id')
            
            update_count, delete_count = 0, 0

            # Updates
            for id, row in edited_df.iterrows():
                if id not in original_df.index: continue
                original_row = original_df.loc[id]
                if not row.equals(original_row):
                    payload = row.to_dict()
                    response = requests.put(f"{API_URL}/verticals/{id}", json=payload)
                    if response.status_code == 200: update_count += 1
                    else: handle_api_error(response, f"update vertical {id}")

            # Deletions
            deleted_ids = set(original_df.index) - set(edited_df.index)
            for id in deleted_ids:
                response = requests.delete(f"{API_URL}/verticals/{id}")
                if response.status_code == 200: delete_count += 1
                else: handle_api_error(response, f"delete vertical {id}")
            
            if update_count > 0 or delete_count > 0:
                st.success(f"Saved {update_count} update(s) and {delete_count} deletion(s).")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info("No changes detected.")

# --- Tab 2: Business Units ---
with tab2:
    st.subheader("Manage Business Units")

    if df_verticals.empty:
        st.warning("You must add at least one Business Vertical before you can add a Business Unit.")
    else:
        # Add form
        with st.expander("➕ Add New Business Unit"):
            with st.form("new_unit_form", clear_on_submit=True):
                unit_name = st.text_input("Business Unit Name")
                vertical_id = st.selectbox(
                    "Business Vertical", 
                    options=vertical_map.keys(), 
                    format_func=lambda id: vertical_map.get(id, "Unknown")
                )
                submitted = st.form_submit_button("Add Business Unit")
                if submitted:
                    if unit_name:
                        payload = {"business_unit_name": unit_name, "business_vertical_id": vertical_id}
                        try:
                            response = requests.post(f"{API_URL}/units/", json=payload)
                            if response.status_code == 200:
                                st.success(f"Unit '{unit_name}' added.")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                handle_api_error(response, "add unit")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Unit Name is required.")
    
    # Edit table
    st.subheader("Edit Business Units")
    if df_units.empty:
        st.info("No Business Units found. Add one using the form above.")
    else:
        edited_units = st.data_editor(
            df_units,
            key="unit_editor",
            num_rows="dynamic",
            disabled=["business_unit_id"],
            column_config={
                "business_unit_id": st.column_config.NumberColumn("ID", disabled=True),
                "business_unit_name": st.column_config.TextColumn("Business Unit Name", required=True),
                "business_vertical_id": st.column_config.SelectboxColumn(
                    "Business Vertical",
                    options=vertical_map.keys(),
                    format_func=lambda id: vertical_map.get(id, "Unknown"),
                    required=True
                )
            },
            use_container_width=True
        )
        
        if st.button("💾 Save Unit Changes"):
            # Logic to save changes
            original_df = df_units.set_index('business_unit_id')
            edited_df = edited_units.set_index('business_unit_id')
            
            update_count, delete_count = 0, 0

            # Updates
            for id, row in edited_df.iterrows():
                if id not in original_df.index: continue
                original_row = original_df.loc[id]
                if not row.equals(original_row):
                    payload = row.to_dict()
                    response = requests.put(f"{API_URL}/units/{id}", json=payload)
                    if response.status_code == 200: update_count += 1
                    else: handle_api_error(response, f"update unit {id}")

            # Deletions
            deleted_ids = set(original_df.index) - set(edited_df.index)
            for id in deleted_ids:
                response = requests.delete(f"{API_URL}/units/{id}")
                if response.status_code == 200: delete_count += 1
                else: handle_api_error(response, f"delete unit {id}")
            
            if update_count > 0 or delete_count > 0:
                st.success(f"Saved {update_count} update(s) and {delete_count} deletion(s).")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info("No changes detected.")