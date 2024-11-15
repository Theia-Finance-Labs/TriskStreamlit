import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import leafmap.foliumap as leafmap
from theia_streamlit_css import load_visual_identity
import branca
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def get_colormap(cmap_name='YlOrBr', vmin=0, vmax=0.2, num_colors=10, invert=False):
    # Generate the colormap
    cmap = plt.get_cmap(cmap_name)
    colors = [mcolors.rgb2hex(cmap(i / (num_colors - 1))) for i in range(num_colors)]
    
    # If invert is True, reverse the color list
    if invert:
        cmap_name='blues'
        colors = colors[::-1]
    
    # Create the LinearColormap
    colormap = branca.colormap.LinearColormap(
        colors=colors,
        vmin=vmin,
        vmax=vmax
    )
    return colormap
    


st.set_page_config(
    page_title="SME T-risk",
    page_icon="pages/logo.png",
    layout="wide"

)
load_visual_identity('pages/header.png')
st.logo(icon_image='pages/TheiaLogo.svg',image='pages/logo.png',size='large')

# Load the NUTS shapefile
@st.cache_data
def load_gis_data():
    gdf = gpd.read_file("shapefiles/world-administrative-boundaries.shp")
    return gdf.loc[gdf.status=="Member State"][['iso_3166_1_','geometry']]

col1,sepcol,col2,coly = st.columns([5,1,5,2])
col1.title("T-risk")
col2.title("")

# Load and cache the data
@st.cache_data
def load_data():
    processed_df = pd.read_feather('WorldAssets.feather')
    return processed_df

data = load_data()

# Selection for weight column to visualize
weight = col1.selectbox(
    'Select Weighting for Heatmap',
    [ 'production_plan_company_technology', 'production_baseline_scenario',
       'production_target_scenario', 'production_shock_scenario', 'pd',
       'net_profit_margin', 'debt_equity_ratio', 'volatility',
       'scenario_price_baseline', 'price_shock_scenario',
       'net_profits_baseline_scenario', 'net_profits_shock_scenario',
       'discounted_net_profits_baseline_scenario',
       'discounted_net_profits_shock_scenario', 'count']
)

# Select baseline scenario and filter data
baseline_scenario = col1.selectbox('Baseline Scenario', data['baseline_scenario'].unique())
shock_year = col1.selectbox('Shock Year', data['shock_year'].unique())
year = col1.selectbox('Year', data['year'].unique())

# Filter valid shock scenarios based on baseline scenario selection
valid_target_scenarios = data[data['baseline_scenario'] == baseline_scenario]['target_scenario'].unique()
target_scenario = col1.selectbox('Target Scenario', valid_target_scenarios)
technology = col1.selectbox('Select the technology', data['technology'].unique())

def format_column(col):
    # Check if the column consists of numeric values
    if pd.api.types.is_numeric_dtype(col):
        return col.apply(lambda x: 
            # If the absolute value is less than 1, format as a percentage with 3 decimal places
            f"{x:.3%}" if abs(x) < 1 else (
            
            # If the absolute value is between 0 and 180 (inclusive), return the value as is
            x if 0 <= abs(x) <= 180 else (
            
            # If the absolute value is less than 3000, format as an integer without decimals
            f"{x:.0f}" if 2000 <=abs(x) < 2100 else 
            
            # If the absolute value is greater than or equal to 3000, format with commas for thousands
            f"{x:,.0f}")))
    else:
        # Return the column as is if it is not numeric
        return col
    
filtered_data = data.loc[data['baseline_scenario'].isin([baseline_scenario])].loc[data['target_scenario'].isin([target_scenario])].loc[data['year'].isin([year])].loc[data['technology'].isin([technology])]
#select_company = st.multiselect('Search Company',filtered_data['company_name'].unique())
#selected_companies = filtered_data.loc[data['company_name'].isin(select_company)].apply(format_column)
#st.dataframe(selected_companies)
boundaries = load_gis_data()
merged_df = filtered_data.merge(boundaries,how='inner',left_on='country_iso2',right_on='iso_3166_1_')#.dropna(subset='geography')
geodf = gpd.GeoDataFrame(merged_df, geometry='geometry')
#st.dataframe(geodf)

# Initialize a Leafmap object centered on the data points with a closer zoom level
m2 = leafmap.Map()
# Define the style_function to dynamically apply color based on the `weight` column
# Define the colormap manually (from light to dark)
vmin = data[weight].min()
vmax=0.7*data[weight].max()
if vmin<=-0.001:
    colormap = get_colormap(vmin=vmin,vmax=vmax,num_colors=20,invert=True)
else:
    colormap = get_colormap(vmin=vmin,vmax=vmax,num_colors=20)

m2.add_colormap(width=0.3, height=2, vmin=100*abs(vmin), vmax=100*abs(vmax),palette='YlOrBr',label='%',transparent=True,orientation='vertical',position=(85,0))

def style_function(feature):
    # Get the value from the `weight` column for the feature
    value = feature["properties"].get(weight)  # Adjust "weight" as per your actual column name
    color = colormap(value) if value is not None else "#8c8c8c"  # Default color if None
    # Return the style for the feature
    return {
        "fillColor": color,       # Color based on the value
        "fillOpacity": 0.9,       # Adjust fill opacity
        "weight": 0.1,              # No outline weight
        "stroke": True,         
        "color": "#000000",       # White border color (if needed)
    }

# Define the highlight_function to change the style when a feature is highlighted (hovered)
def highlight_function(feature):
    return {
        "fillOpacity": 0.9,       # Slightly increase opacity on hover
        "weight": 2,              # Thicker border on hover
        "stroke": True,           # Add stroke on hover
        "color": "#ff0000",       # Red border on hover
    }

# Add a choropleth layer based on NUTS boundaries without outlines
m2.add_data(
    geodf,
    column=weight,
    layer_name=weight,
    add_legend=False,
    fill_opacity=0.7,  # Adjust fill opacity for better visibility
    style_function=style_function,       # Apply the style function
    highlight_function=highlight_function,  # Apply the highlight function on hover
    #fields=['NAME_LATN',weight+' '+technology],
    style=("background-color: white; color: black; font-weight: bold;"),
    sticky=True
)

#m2.add_circle_markers_from_xy(selected_companies,x='longitude',y='latitude',popup=['company_name','year','net_present_value_baseline','net_present_value_shock','net_present_value_difference','pd_baseline','pd_shock','pd_difference','crispy_perc_value_change',],size=20)


# Display the map in Streamlit
with col2:
    m2.to_streamlit(width=700, height=500,add_layer_control=False)
