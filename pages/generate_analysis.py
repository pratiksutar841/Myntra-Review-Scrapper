import pandas as pd
import streamlit as st 
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.data_report.generate_data_report import DashboardGenerator

st.set_page_config(page_title="Analysis Report", page_icon="📊", layout="wide")

mongo_con = MongoIO()

def create_analysis_page(review_data: pd.DataFrame):
    if review_data is not None and not review_data.empty:
        st.markdown("### 📄 Raw Scraped Data")
        st.dataframe(review_data, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generate Detailed Analysis", type="primary", use_container_width=True):
            st.divider()
            dashboard = DashboardGenerator(review_data)
            
            # Display general information
            dashboard.display_general_info()
            
            st.divider()
            # Display product-specific sections
            dashboard.display_product_sections()
    else:
        st.warning("No Data Available for analysis. Please go to the search page to scrape data first.")

try:
    if "data" in st.session_state and st.session_state["data"]:
        product_name = st.session_state.get(SESSION_PRODUCT_KEY)
        if product_name:
            data = mongo_con.get_reviews(product_name=product_name)
            create_analysis_page(data)
        else:
            st.warning("No Product selected. Go back to the search page.")
    else:
        st.warning("No Data Available for analysis. Please go to the search page to scrape data first.")
except AttributeError:
    st.error("No Data Available for analysis. Please go to the search page.")
except Exception as e:
    st.error(f"An error occurred: {e}")
