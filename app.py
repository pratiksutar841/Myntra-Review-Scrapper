import pandas as pd
import streamlit as st
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews

st.set_page_config(page_title="Myntra Review Scrapper", page_icon="🛒", layout="centered")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛍️ Myntra Review Scrapper & Analyzer")
st.markdown("Easily extract and analyze customer reviews from Myntra.")
st.divider()

st.session_state["data"] = False

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not isinstance(text, str):
        return "Neutral"
    score = analyzer.polarity_scores(text)
    if score['compound'] >= 0.05:
        return 'Positive'
    elif score['compound'] <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

@st.cache_data
def fetch_reviews(product_name, no_of_products):
    scrapper = ScrapeReviews(product_name=product_name, no_of_products=no_of_products)
    return scrapper.get_review_data()

def form_input():
    # Use columns to align the inputs nicely
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product = st.text_input("Product Name or URL", placeholder="e.g. Polo T-Shirt", help="Enter the exact product name to search on Myntra.")
        st.session_state[SESSION_PRODUCT_KEY] = product
    
    with col2:
        no_of_products = st.number_input("Number of Items", step=1, min_value=1, value=1, help="Number of products to scrape reviews from.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Center the button
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        scrape_clicked = st.button("🚀 Scrape & Analyze Reviews", use_container_width=True, type="primary")

    if scrape_clicked:
        if not product.strip():
            st.error("Please enter a product name to search.")
            return

        with st.spinner("Scraping and analyzing reviews in the background..."):
            scrapped_data = fetch_reviews(product, int(no_of_products))
            
            if scrapped_data is not None and not scrapped_data.empty:
                st.session_state["data"] = True
                
                # Perform Sentiment Analysis if 'Comment' column exists
                if 'Comment' in scrapped_data.columns:
                    scrapped_data['Sentiment'] = scrapped_data['Comment'].apply(get_sentiment)
                
                # Save to MongoDB
                try:
                    mongoio = MongoIO()
                    mongoio.store_reviews(product_name=product, reviews=scrapped_data)
                    st.success("✅ Reviews successfully scraped, analyzed, and saved to database!")
                except Exception as e:
                    st.warning("✅ Reviews scraped and analyzed successfully!")
                    st.error(f"⚠️ Could not save to MongoDB (Connection Error). The app will still display your results below.")
                
                st.divider()
                
                # Display Visualizations
                if 'Sentiment' in scrapped_data.columns:
                    st.markdown("### 📊 Sentiment Distribution")
                    sentiment_counts = scrapped_data['Sentiment'].value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']
                    
                    fig = px.pie(
                        sentiment_counts, 
                        values='Count', 
                        names='Sentiment', 
                        color='Sentiment',
                        color_discrete_map={'Positive':'#00cc96', 'Neutral':'#636efa', 'Negative':'#ef553b'},
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 📄 Scraped Data")
                st.dataframe(scrapped_data, use_container_width=True)
            else:
                st.warning("No reviews found for this product.")

if __name__ == "__main__":
    form_input()
