import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("🏠 Melbourne Housing Dashboard")

# Load data
df = pd.read_excel("melbourne_housing_data.xlsx", sheet_name="Suburb_Overview")

# Show raw data
if st.checkbox("Show Raw Data"):
    st.write(df)

# Clean data
df = df.dropna()

# Select suburb
suburb = st.selectbox("Select Suburb", df['Suburb'].unique())

filtered_df = df[df['Suburb'] == suburb]

st.write(f"Data for {suburb}")
st.write(filtered_df)

# Average price by suburb
avg_price = df.groupby('Suburb')['Price'].mean().sort_values(ascending=False)

st.subheader("Top 10 Expensive Suburbs")
st.bar_chart(avg_price.head(10))

# Bedrooms vs Price
st.subheader("Bedrooms vs Price")

fig, ax = plt.subplots()
ax.scatter(df['Bedrooms'], df['Price'])
ax.set_xlabel("Bedrooms")
ax.set_ylabel("Price")

st.pyplot(fig)