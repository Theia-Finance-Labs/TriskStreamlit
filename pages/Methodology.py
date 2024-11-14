import streamlit as st
from visualsetup import load_visual_identity

st.set_page_config(
    page_title="SME T-risk",
    page_icon="logo.png",
    layout="wide"
)
load_visual_identity('header.png')
st.logo(icon_image='TheiaLogo.svg',image='logo.png',size='large')
sepcol,col,coly = st.columns([1,5,2])
col.title("Methodology")

col.markdown("""
This Streamlit application, **"SME T-risk,"** visualizes risk metrics and economic scenarios for SMEs across specified regions, integrating geographic and statistical data. The methodology is as follows:

### 1. Load and Configure Visualization
- The app uses `Streamlit` for interactive UI elements, `Pandas` for data handling, `Geopandas` for geographic data processing, and `leafmap` for map display.
- Initial configurations are set up, including the page title, logo, and layout via `st.set_page_config`.
- A custom visual identity function (`load_visual_identity`) is loaded to style the UI, followed by logo and title placement.

### 2. Data Loading and Caching
- The app loads two main datasets using `@st.cache_data` to enhance performance:
  - A **NUTS (Nomenclature of Territorial Units for Statistics)** shapefile representing European geographic boundaries.
  - A primary data file in `.feather` format containing geocoded SME risk metrics.
- Filters remove specific non-EU regions to limit visual scope to mainland France and Germany.

### 3. User Input and Filtering
- Users select from a range of filters:
  - **Weighting metric** for heatmap visualization, including options like `pd_baseline`, `pd_shock`, `crispy_perc_value_change`, and `pd_difference`.
  - **Baseline and shock scenarios**, **term year**, and **sector** to refine which scenarios and industries are shown.
  - **Company filter** to focus on specific SMEs.
- The filtered data is displayed in a table, allowing users to view selected companies’ details.

### 4. Spatial Aggregation
- Based on user-defined regional aggregation (NUTS Level 1–3), the app groups data by NUTS region, calculating average values for the selected weighting metric.

### 5. Colormap Configuration
- A custom colormap (`get_colormap`) scales color values to the data range, with an optional inverted palette. The color range is adjusted dynamically based on user-selected metrics to enhance visibility.

### 6. Map Visualization
- A `leafmap` map object displays the data points, with configurable styles for fill color, opacity, and hover effects.
- A choropleth layer visualizes aggregated data at the regional NUTS level, applying colors based on the selected weighting metric.
- Hover and highlight effects emphasize regions, and circle markers highlight specific SME locations with popups showing detailed risk metrics.

### 7. Display and Interactivity
- The map, table, and filters are laid out using Streamlit columns to ensure responsive design and intuitive user interaction.
""")