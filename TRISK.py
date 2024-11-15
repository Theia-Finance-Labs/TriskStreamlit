import streamlit as st
#import pandas as pd
import modin.pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import leafmap.foliumap as leafmap
from theia_streamlit_css import load_visual_identity
import branca
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Helper to create colormap
def get_colormap(cmap_name='YlOrBr', vmin=0, vmax=0.2, num_colors=10, invert=False):
    cmap = plt.get_cmap(cmap_name)
    colors = [mcolors.rgb2hex(cmap(i / (num_colors - 1))) for i in range(num_colors)]
    if invert:
        cmap_name = 'Blues'
        colors = colors[::-1]
    colormap = branca.colormap.LinearColormap(colors=colors, vmin=vmin, vmax=vmax)
    return colormap

# Streamlit setup
st.set_page_config(page_title="1in100 T-risk", page_icon="pages/logo.png", layout="wide")
load_visual_identity('pages/header.png')
st.logo(icon_image='pages/TheiaLogo.svg', image='pages/logo.png', size='large')

@st.cache_data
def load_gis_data():
    gdf = gpd.read_file("shapefiles/world-administrative-boundaries.shp")
    return gdf.loc[gdf.status == "Member State"][['iso_3166_1_', 'geometry']]

@st.cache_data
def load_data():
    return pd.read_feather('WorldAssets.feather')

# Load data and boundaries
data = load_data()
boundaries = load_gis_data()

# Sidebar for filtering options
col1, sepcol, col2, coly = st.columns([5, 1, 5, 2])
col1.title("T-risk")

# Filter and dropdown setup
with col1:
    weight = st.selectbox('Select Weighting for Heatmap', [
        'production_plan_company_technology', 'production_baseline_scenario',
        'production_target_scenario', 'production_shock_scenario', 'pd',
        'net_profit_margin', 'debt_equity_ratio', 'volatility',
        'scenario_price_baseline', 'price_shock_scenario',
        'net_profits_baseline_scenario', 'net_profits_shock_scenario',
        'discounted_net_profits_baseline_scenario',
        'discounted_net_profits_shock_scenario', 'count'
    ])
    
    # Filter scenarios dynamically
    baseline_scenario = st.selectbox('Baseline Scenario', sorted(data['baseline_scenario'].unique()))
    valid_target_scenarios = data.loc[data['baseline_scenario'] == baseline_scenario, 'target_scenario'].unique()
    target_scenario = st.selectbox('Target Scenario', sorted(valid_target_scenarios))
    
    # Filter technologies based on scenarios
    scenario_filter = (data['baseline_scenario'] == baseline_scenario) & (data['target_scenario'] == target_scenario)
    technology_options = data.loc[scenario_filter, 'technology'].unique()
    technology = st.selectbox('Select the technology', sorted(technology_options))
    
    # Filter years based on selected filters
    year_options = data.loc[scenario_filter & (data['technology'] == technology), 'year'].unique()
    year = st.selectbox('Year', sorted(year_options))
    
    shock_year_options = data.loc[scenario_filter & (data['technology'] == technology), 'shock_year'].unique()
    shock_year = st.selectbox('Shock Year', sorted(shock_year_options))
    
    hover_data = st.multiselect(
        'Hover data', [
            'production_plan_company_technology', 'production_baseline_scenario',
            'production_target_scenario', 'production_shock_scenario', 'pd',
            'net_profit_margin', 'debt_equity_ratio', 'volatility',
            'scenario_price_baseline', 'price_shock_scenario',
            'net_profits_baseline_scenario', 'net_profits_shock_scenario',
            'discounted_net_profits_baseline_scenario',
            'discounted_net_profits_shock_scenario', 'count'
        ], default=weight
    )

# Filtered data based on selections
#@st.cache_data
def get_filtered_data(data, boundaries, baseline_scenario, target_scenario, technology, year):
    filtered = data[
        (data['baseline_scenario'] == baseline_scenario) &
        (data['target_scenario'] == target_scenario) &
        (data['technology'] == technology) &
        (data['year'] == year)
    ]
    return filtered.merge(boundaries, how='inner', left_on='country_iso2', right_on='iso_3166_1_')

filtered_data = get_filtered_data(data, boundaries, baseline_scenario, target_scenario, technology, year)

# Prepare GeoDataFrame for the map
geodf = gpd.GeoDataFrame(filtered_data, geometry='geometry')

# Map rendering
m2 = leafmap.Map(center=(0, 0), zoom=2)
vmin, vmax = filtered_data[weight].min(), filtered_data[weight].max()
colormap = get_colormap(vmin=vmin, vmax=vmax, num_colors=20, invert=vmin < 0)

m2.add_colormap(
    width=0.3, height=2, vmin=100*abs(vmin), vmax=100*abs(vmax),
    palette='YlOrBr', label=weight, transparent=True, orientation='vertical', position=(85, 0)
)

def style_function(feature):
    value = feature["properties"].get(weight)
    color = colormap(value) if value is not None else "#8c8c8c"
    return {"fillColor": color, "fillOpacity": 0.9, "weight": 0.1, "stroke": True, "color": "#000000"}

def highlight_function(feature):
    return {"fillOpacity": 0.9, "weight": 2, "stroke": True, "color": "#ff0000"}

m2.add_data(
    geodf, column=weight, layer_name=weight,
    add_legend=False, fill_opacity=0.7,
    style_function=style_function, highlight_function=highlight_function,
    fields=hover_data, sticky=True
)

# Display map
with col2:
    m2.to_streamlit(width=700, height=700, add_layer_control=False)
