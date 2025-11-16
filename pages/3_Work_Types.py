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
st.set_page_config(page_title="Work Type Config", page_icon="📝", layout="wide")
st.title("📝 Work Type Configuration")

# --- Load Data ---
df_work_types = fetch_lookup_tables("work_types")
df_origin_types = fetch_lookup_tables("work_type_origin_types")

if df_origin_types.empty:
    st.error("Failed to load Work Type Origins. Is the API running?")
    # We can still proceed, but the map will be empty
    
origin_map = dict(zip(df_origin_types['work_type_origin_type_id'], df_origin_types['work_type_origin_type_name']))

# --- Tabs ---
tab1, tab2 = st.tabs(["Work Types", "Work Type Origins"])

# --- Tab 1: Work Types ---
with tab1:
    st.subheader("Manage Work Types")
    
    if df_origin_types.empty:
        st.warning("You must add at least one Work Type Origin before you can add a Work Type.")
    else:
        # Add form
        with st.expander("➕ Add New Work Type"):
            with st.form("new_work_type_form", clear_on_submit=True):
                work_type_name = st.text_input("Work Type Name")
                origin_id = st.selectbox(
                    "Origin Type", 
                    options=origin_map.keys(), 
                    format_func=lambda id: origin_map.get(id, "Unknown")
                )
                submitted = st.form_submit_button("Add Work Type")
                if submitted:
                    if work_type_name:
                        payload = {"work_type_name": work_type_name, "work_type_origin_type_id": origin_id}
                        try:
                            response = requests.post(f"{API_URL}/work_types/", json=payload)
                            if response.status_code == 200:
                                st.success(f"Work Type '{work_type_name}' added.")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                handle_api_error(response, "add work type")
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Work Type Name is required.")

    # Edit table
    st.subheader("Edit Work Types")
    if df_work_types.empty:
        st.info("No Work Types found. Add one using the form above.")
    else:
        edited_work_types = st.data_editor(
            df_work_types,
            key="work_type_editor",
            num_rows="dynamic",
            disabled=["work_type_id"],
            column_config={
                "work_type_id": st.column_config.NumberColumn("ID", disabled=True),
                "work_type_name": st.column_config.TextColumn("Work Type Name", required=True),
                "work_type_origin_type_id": st.column_config.SelectboxColumn(
                    "Origin Type",
                    options=origin_map.keys(),
                    format_func=lambda id: origin_map.get(id, "Unknown"),
                    required=True
                )
            },
            use_container_width=True
        )
        
        if st.button("💾 Save Work Type Changes"):
            original_df = df_work_types.set_index('work_type_id')
            edited_df = edited_work_types.set_index('work_type_id')
            
            update_count, delete_count = 0, 0

            # Updates
            for id, row in edited_df.iterrows():
                if id not in original_df.index: continue
                original_row = original_df.loc[id]
                if not row.equals(original_row):
                    payload = row.to_dict()
                    response = requests.put(f"{API_URL}/work_types/{id}", json=payload)
                    if response.status_code == 200: update_count += 1
                    else: handle_api_error(response, f"update work type {id}")

            # Deletions
            deleted_ids = set(original_df.index) - set(edited_df.index)
            for id in deleted_ids:
                response = requests.delete(f"{API_URL}/work_types/{id}")
                if response.status_code == 200: delete_count += 1
                else: handle_api_error(response, f"delete work type {id}")
            
            if update_count > 0 or delete_count > 0:
                st.success(f"Saved {update_count} update(s) and {delete_count} deletion(s).")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info("No changes detected.")

# --- Tab 2: Work Type Origins ---
with tab2:
    st.subheader("Manage Work Type Origins")

    # Add form
    with st.expander("➕ Add New Origin Type"):
        with st.form("new_origin_form", clear_on_submit=True):
            origin_name = st.text_input("Origin Type Name")
            submitted = st.form_submit_button("Add Origin Type")
            if submitted:
                if origin_name:
                    payload = {"work_type_origin_type_name": origin_name}
                    try:
                        response = requests.post(f"{API_URL}/work_type_origin_types/", json=payload)
                        if response.status_code == 200:
                            st.success(f"Origin Type '{origin_name}' added.")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            handle_api_error(response, "add origin type")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Origin Type Name is required.")
    
    # Edit table
    st.subheader("Edit Origin Types")
    if df_origin_types.empty:
        st.info("No Work Type Origins found. Add one using the form above.")
    else:
        edited_origins = st.data_editor(
            df_origin_types,
            key="origin_editor",
            num_rows="dynamic",
            disabled=["work_type_origin_type_id"],
            column_config={
                "work_type_origin_type_id": st.column_config.NumberColumn("ID", disabled=True),
                "work_type_origin_type_name": st.column_config.TextColumn("Origin Type Name", required=True),
            },
            use_container_width=True
        )
        
        if st.button("💾 Save Origin Type Changes"):
            original_df = df_origin_types.set_index('work_type_origin_type_id')
            edited_df = edited_origins.set_index('work_type_origin_type_id')
            
            update_count, delete_count = 0, 0

            # Updates
            for id, row in edited_df.iterrows():
                if id not in original_df.index: continue
                original_row = original_df.loc[id]
                if not row.equals(original_row):
                    payload = row.to_dict()
                    response = requests.put(f"{API_URL}/work_type_origin_types/{id}", json=payload)
                    if response.status_code == 200: update_count += 1
                    else: handle_api_error(response, f"update origin type {id}")

            # Deletions
            deleted_ids = set(original_df.index) - set(edited_df.index)
            for id in deleted_ids:
                response = requests.delete(f"{API_URL}/work_type_origin_types/{id}")
                if response.status_code == 200: delete_count += 1
                else: handle_api_error(response, f"delete origin type {id}")
            
            if update_count > 0 or delete_count > 0:
                st.success(f"Saved {update_count} update(s) and {delete_count} deletion(s).")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info("No changes detected.")