import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import os, sys
from src.exception import CustomException


class DashboardGenerator:
    def __init__(self, data):
        self.data = data

    def display_general_info(self):
        st.header("📊 General Information")

        # Convert 'Over_All_Rating' and 'Price' columns to numeric
        self.data["Over_All_Rating"] = pd.to_numeric(
            self.data["Over_All_Rating"], errors="coerce"
        )
        self.data["Price"] = pd.to_numeric(
            self.data["Price"].astype(str).str.replace("₹", "", regex=False).str.replace(",", "", regex=False), errors="coerce"
        )

        self.data["Rating"] = pd.to_numeric(self.data["Rating"], errors="coerce")

        col1, col2 = st.columns(2)
        
        with col1:
            # Summary pie chart of average ratings by product
            product_ratings = (
                self.data.groupby("Product Name", as_index=False)["Over_All_Rating"]
                .mean()
                .dropna()
            )
    
            # Make product names shorter for the legend if they are too long
            product_ratings['Short Name'] = product_ratings['Product Name'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
    
            fig_pie = px.pie(
                product_ratings,
                values="Over_All_Rating",
                names="Short Name",
                title="Average Ratings by Product",
                hole=0.3
            )
            fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart comparing average prices of different products with different colors
            avg_prices = (
                self.data.groupby("Product Name", as_index=False)["Price"].mean().dropna()
            )
            avg_prices['Short Name'] = avg_prices['Product Name'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
            
            fig_bar = px.bar(
                avg_prices,
                x="Short Name",
                y="Price",
                color="Short Name",
                title="Average Price Comparison",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_bar.update_layout(showlegend=False)
            fig_bar.update_xaxes(title="Product")
            fig_bar.update_yaxes(title="Average Price (₹)")
            st.plotly_chart(fig_bar, use_container_width=True)

    def display_product_sections(self):
        st.header("📦 Product Sections")

        product_names = self.data["Product Name"].unique()
        
        # Use tabs instead of columns so they don't squish together
        if len(product_names) > 0:
            short_names = [name[:20] + '...' if len(name) > 20 else name for name in product_names]
            tabs = st.tabs(short_names)
    
            for i, product_name in enumerate(product_names):
                product_data = self.data[self.data["Product Name"] == product_name]
    
                with tabs[i]:
                    st.subheader(f"{product_name}")
    
                    # Display price and rating side by side
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        avg_price = product_data["Price"].mean()
                        st.info(f"💰 **Average Price:** ₹{avg_price:.2f}")
                    with metric_col2:
                        avg_rating = product_data["Over_All_Rating"].mean()
                        st.success(f"⭐ **Average Rating:** {avg_rating:.2f} / 5.0")
    
                    st.markdown("---")
                    
                    review_col1, review_col2 = st.columns(2)
                    
                    with review_col1:
                        # Display top positive comments with great ratings
                        positive_reviews = product_data[product_data["Rating"] >= 4].nlargest(
                            5, "Rating"
                        )
                        st.markdown("### 👍 Top Positive Reviews")
                        if positive_reviews.empty:
                            st.write("No highly positive reviews found.")
                        for index, row in positive_reviews.iterrows():
                            st.markdown(f"**{row['Rating']}⭐** - {row['Comment']}")
    
                    with review_col2:
                        # Display top negative comments with worst ratings
                        negative_reviews = product_data[product_data["Rating"] <= 2].nsmallest(
                            5, "Rating"
                        )
                        st.markdown("### 👎 Top Negative Reviews")
                        if negative_reviews.empty:
                            st.write("No highly negative reviews found.")
                        for index, row in negative_reviews.iterrows():
                            st.markdown(f"**{row['Rating']}⭐** - {row['Comment']}")
    
                    st.markdown("---")
                    # Display rating counts in different categories
                    st.subheader("📊 Rating Distribution")
                    rating_counts = (
                        product_data["Rating"].value_counts().sort_index(ascending=False).reset_index()
                    )
                    rating_counts.columns = ['Rating', 'Count']
                    
                    fig = px.bar(
                        rating_counts, 
                        y='Rating', 
                        x='Count', 
                        orientation='h',
                        title="Count of each Star Rating",
                        color='Rating',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
