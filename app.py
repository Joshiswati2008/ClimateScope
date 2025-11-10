import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import st_folium
from fpdf import FPDF

# ----------------------------------------
# PAGE CONFIG
# ----------------------------------------
st.set_page_config(page_title="🌍 ClimateScope Dashboard",
                   layout="wide",
                   page_icon="🌦️")

st.title("🌡️ ClimateScope – Visualizing Global Weather Trends & Extreme Events")
st.markdown("##### Infosys Internship 2025 | Data Visualization & Climate Awareness")

# ----------------------------------------
# LOAD DATA
# ----------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/weather_cleaned.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Please add 'data/weather_cleaned.csv' file in the 'data' folder.")
    st.stop()

# ----------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------
st.sidebar.header("🌍 Filter Options")

country = st.sidebar.selectbox("Select Country", sorted(df['Country'].unique()))
year = st.sidebar.selectbox("Select Year", sorted(df['Year'].unique()))
metric = st.sidebar.selectbox("Select Metric", ['Temperature', 'Humidity', 'WindSpeed', 'Precipitation'])

filtered_df = df[(df['Country'] == country) & (df['Year'] == year)]

# ----------------------------------------
# SECTION 1: LINE CHART
# ----------------------------------------
st.subheader(f"📈 {metric} Trends in {country} ({year})")
fig_line = px.line(filtered_df, x='Month', y=metric, markers=True,
                   title=f"{metric} Variation by Month in {country}",
                   color_discrete_sequence=['#1f77b4'])
st.plotly_chart(fig_line, use_container_width=True)

# ----------------------------------------
# SECTION 2: MONTHLY BAR CHART
# ----------------------------------------
st.subheader(f"📊 Monthly Average Comparison – {country}")
fig_bar = px.bar(filtered_df, x='Month', y=metric,
                 color='Month', title=f"Average {metric} by Month",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------------------
# SECTION 3: SCATTER (Temperature vs Humidity)
# ----------------------------------------
st.subheader("☁️ Correlation: Temperature vs Humidity")
fig_scatter = px.scatter(df, x='Temperature', y='Humidity',
                         color='Country', size='WindSpeed',
                         hover_name='Country',
                         title="Temperature vs Humidity Across Countries")
st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------
# SECTION 4: CHOROPLETH MAP (Global Temperature)
# ----------------------------------------
st.subheader("🌍 Global Temperature Distribution")
fig_map = px.choropleth(df, locations="Country",
                        locationmode="country names",
                        color="Temperature",
                        animation_frame="Year",
                        color_continuous_scale="RdYlBu_r",
                        title="Average Global Temperature Over Years")
st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------------
# SECTION 5: TRAVEL PLANNER – COMFORT INDEX
# ----------------------------------------
st.subheader("🌤️ Travel Planner – Best Countries by Comfort Index")

df['ComfortIndex'] = 100 - abs(df['Temperature'] - 22) - df['Humidity'] * 0.1 - df['AirQualityIndex'] * 0.2
top5 = df.groupby('Country')['ComfortIndex'].mean().sort_values(ascending=False).head(5)
st.table(top5.reset_index().rename(columns={'ComfortIndex': 'Comfort Score'}))

# ----------------------------------------
# SECTION 6: INTERACTIVE MAP (Folium)
# ----------------------------------------
st.subheader("🗺️ Interactive Global Map")
map_center = [20, 0]
m = folium.Map(location=map_center, zoom_start=2)
for _, row in df.iterrows():
    if not np.isnan(row.get('Latitude', np.nan)) and not np.isnan(row.get('Longitude', np.nan)):
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=4,
            popup=f"{row['Country']}: {row['Temperature']}°C",
            color="blue", fill=True
        ).add_to(m)
st_data = st_folium(m, width=700, height=450)

# ----------------------------------------
# SECTION 7: PDF REPORT GENERATION
# ----------------------------------------
st.subheader("🧾 Generate Climate Report (PDF)")

if st.button("Generate Report"):
    avg_value = round(filtered_df[metric].mean(), 2)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Climate Report – {country} ({year})", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Average {metric}: {avg_value}", ln=True, align='L')
    pdf.output(f"reports/{country}_{year}_report.pdf")

    st.success(f"✅ Report generated: reports/{country}_{year}_report.pdf")

# ----------------------------------------
# FOOTER
# ----------------------------------------
st.markdown("---")
st.markdown("Made with ❤️ by Swati Joshi | Infosys Internship 2025 – ClimateScope Project")
