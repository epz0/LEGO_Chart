#%%
import streamlit as st
import gspread
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

def authenticate_google_sheets(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1  # Access the first sheet
    return sheet

def get_data_from_sheet(sheet):
    data = sheet.get_all_records()  # Get all data as a list of dictionaries
    return pd.DataFrame(data)      # Convert to DataFrame

def create_bubble_chart(data):
    fig = px.scatter(
        data,
        x="weight",
        y="height",
        size="performance",
        color="initials",
        hover_name="initials",
        title="Solution performance (height/weight ratio) per participant",
        template="plotly_white"
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20)  # Add margins for better layout
    )
    return fig

def main():
    st.set_page_config(
        page_title="Design Space - LEGO Activity",
        layout="wide",  # Use the full screen width
        page_icon="📊"
    )

    st.title("Design Space - LEGO Activity")

    credentials_dict = st.secrets["google_credentials"]
    creds = service_account.Credentials.from_service_account_info(credentials_dict)

    # Input: Google Sheets details
    sheet_name = "DB_LegoActivity"

    try:
            sheet = authenticate_google_sheets(creds, sheet_name)
            data = get_data_from_sheet(sheet)
            data_subset = data[["date_time", "initials", "height", "weight"]].copy()
            data_subset['performance'] = (data_subset['height'] / data_subset['weight']).round(2)

            # subset data based on submission date
            now = datetime.now()
            twelve_hours_ago = now - timedelta(hours=12)

            data_subset['date_time'] = pd.to_datetime(data_subset['date_time'])
            data_subset = data_subset[(data_subset['date_time'] >= twelve_hours_ago) & (data_subset['date_time'] <= now)]

            st.success("Data loaded successfully!")

            # Generate and display the bubble chart
            fig = create_bubble_chart(data_subset)
            st.plotly_chart(fig, use_container_width=True)

            if st.button("Show Data"):
                st.write("### Data")
                st.dataframe(data_subset)

    except Exception as e:
            st.error(f"Error loading data: {e}")

    # Add footer
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        <p>Developed by <a href="https://esdrasparavizo.com" target="_blank">Esdras Paravizo</a> | <a href="https://doi.org/10.17863/CAM.111233" target="_blank">Download the activity</a></p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

if __name__ == "__main__":
    main()