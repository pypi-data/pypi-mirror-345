# filename: codebase/create_visualizations.py
#!/usr/bin/env python3
"""
This script creates standalone visualizations to display the simulation and energy cost results.
It produces two main types of visualizations:

  1. An interactive map showing the geographic distribution of energy operators and user locations.
     User markers are colored by their computed energy cost and a heatmap overlay indicates cost density.
     (Requires the "folium" package. If not installed, the interactive map section will be skipped.)

  2. A static choropleth map using Matplotlib that colors each operator’s service area based 
     on the average energy cost in that county. A colorbar indicates the cost scale.
     
The data is read from CSV files in the "data/" folder:
    - "operators.csv": Contains operator data with polygons stored as WKT strings.
    - "users.csv": Contains simulated user locations.
    - "user_energy_costs.csv": Contains the computed energy cost for each user.
    - "energy_cost_summary.csv": Contains average energy cost statistics by operator county.
    
All visualizations are saved to disk with high resolution.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors, rcParams
from shapely import wkt
from shapely.geometry import mapping

# Enable LaTeX rendering for matplotlib plots and set font family
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

# Try to import folium. If not installed, set folium=None to skip interactive map creation.
try:
    import folium
    from folium.plugins import HeatMap
except ImportError:
    folium = None
    print("WARNING: 'folium' package not installed. Interactive map will not be generated.")

def load_operator_data(filepath="data/operators.csv"):
    r"""
    Loads operator data from CSV and reconstructs polygons from the WKT strings.
    
    Args:
        filepath (str): Path to the operators CSV file.
        
    Returns:
        pd.DataFrame: DataFrame with operator data including a 'polygon' column containing shapely Polygon objects.
    """
    df = pd.read_csv(filepath)
    df["polygon"] = df["polygon_wkt"].apply(wkt.loads)
    return df

def load_user_data(filepath="data/users.csv"):
    r"""
    Loads user data from CSV.
    
    Args:
        filepath (str): Path to the users CSV file.
        
    Returns:
        pd.DataFrame: DataFrame with user data.
    """
    return pd.read_csv(filepath)

def load_energy_cost_data(filepath="data/user_energy_costs.csv"):
    r"""
    Loads user energy cost data from CSV.
    
    Args:
        filepath (str): Path to the user energy cost CSV file.
    
    Returns:
        pd.DataFrame: DataFrame with user energy cost data.
    """
    return pd.read_csv(filepath)

def load_cost_summary(filepath="data/energy_cost_summary.csv"):
    r"""
    Loads energy cost summary by operator county from CSV.
    
    Args:
        filepath (str): Path to the cost summary CSV file.
    
    Returns:
        pd.DataFrame: DataFrame with average energy cost by operator county.
    """
    return pd.read_csv(filepath, index_col="operator_county")

def create_interactive_map():
    r"""
    Creates an interactive map using Folium displaying:
      - Operator service areas as GeoJSON overlays (with tooltips showing county and operator_id).
      - User locations as circle markers, colored by their energy cost.
      - A heatmap overlay showing energy cost density.
      
    The map is centered on the approximate geographic center of the region and includes layer controls.
    The interactive map is saved as "data/interactive_map.html".
    If the folium package is not available, this function will print a warning and skip creation.
    """
    if folium is None:
        print("Interactive map creation skipped because folium is not installed.")
        return
    
    # Load required data
    operators_df = load_operator_data()
    users_df = load_user_data()
    cost_df = load_energy_cost_data()

    # Merge user data with energy cost data to obtain cost info for each user.
    users_cost = pd.merge(users_df, cost_df[["user_id", "energy_cost"]], on="user_id", how="left")
    
    # Set initial map center (approximate center of England)
    map_center = [52.5, 0.5]
    m = folium.Map(location=map_center, zoom_start=6, tiles="OpenStreetMap")
    
    # Create a FeatureGroup for operator polygons
    operators_fg = folium.FeatureGroup(name="Operator Service Areas", show=True)
    for _, row in operators_df.iterrows():
        poly = row["polygon"]
        county = row["county"]
        op_id = row["operator_id"]
        geo_json = folium.GeoJson(data=mapping(poly),
                                  tooltip=f"Operator ID: {op_id}<br>County: {county}",
                                  style_function=lambda feature: {
                                      "fillColor": "orange",
                                      "color": "black",
                                      "weight": 2,
                                      "fillOpacity": 0.3
                                  })
        geo_json.add_to(operators_fg)
    operators_fg.add_to(m)
    
    # Create a FeatureGroup for user markers
    users_fg = folium.FeatureGroup(name="User Locations", show=True)
    # Determine cost range for colormap
    min_cost = users_cost["energy_cost"].min()
    max_cost = users_cost["energy_cost"].max()
    # Define a linear colormap (blue for low cost, red for high cost)
    colormap = folium.LinearColormap(colors=["blue", "lime", "yellow", "red"],
                                     vmin=min_cost, vmax=max_cost,
                                     caption="Energy Cost (£)")
    for _, row in users_cost.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        cost = row["energy_cost"]
        # If cost is NaN, set to gray color
        if pd.isna(cost):
            marker_color = "gray"
            cost_str = "Cost: N/A"
        else:
            marker_color = colormap(cost)
            cost_str = f"Cost: £{cost:.2f}"
        popup_text = f"User ID: {row['user_id']}<br>{cost_str}"
        folium.CircleMarker(location=[lat, lon],
                            radius=3,
                            color=marker_color,
                            fill=True,
                            fill_opacity=0.9,
                            popup=folium.Popup(popup_text, parse_html=True)
                            ).add_to(users_fg)
    users_fg.add_to(m)
    
    # Create a heatmap layer based on user energy costs and locations.
    heat_data = users_cost.dropna(subset=["energy_cost"]).apply(
        lambda row: [row["latitude"], row["longitude"], row["energy_cost"]], axis=1).tolist()
    heatmap = HeatMap(heat_data, 
                      min_opacity=0.3,
                      radius=10,
                      blur=15,
                      max_zoom=10,
                      name="Energy Cost Heatmap")
    heatmap.add_to(m)
    
    # Add layer control and colormap to map
    folium.LayerControl().add_to(m)
    colormap.add_to(m)
    
    # Save the interactive map to an HTML file
    output_path = os.path.join("data", "interactive_map.html")
    m.save(output_path)
    print(f"Interactive map saved to: {output_path}")

def create_static_choropleth():
    r"""
    Creates a static choropleth map using Matplotlib that displays operator service areas colored
    by the average energy cost for the operator's county. The average cost data is obtained from 
    the cost summary CSV.
    
    The map is saved as a high-resolution PNG image ("data/cost_choropleth.png").
    """
    # Load operator and cost summary data
    operators_df = load_operator_data()
    cost_summary_df = load_cost_summary()
    
    # Create a mapping from county to average cost
    cost_by_county = cost_summary_df["mean"].to_dict()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Set colormap and normalization based on cost values
    all_costs = list(cost_by_county.values())
    norm = colors.Normalize(vmin=min(all_costs), vmax=max(all_costs))
    cmap = plt.cm.viridis

    # Plot each operator polygon with face color based on the average cost of its county
    for _, row in operators_df.iterrows():
        poly = row["polygon"]
        county = row["county"]
        avg_cost = cost_by_county.get(county, np.nan)
        facecolor = cmap(norm(avg_cost)) if not np.isnan(avg_cost) else (0.8, 0.8, 0.8, 1.0)
        x, y = poly.exterior.xy
        ax.fill(x, y, facecolor=facecolor, edgecolor="black", alpha=0.7)
        # Annotate county name at the centroid of the polygon
        centroid = poly.centroid
        ax.text(centroid.x, centroid.y, str(county), fontsize=10, fontweight="bold",
                ha="center", va="center", color="white")
    
    ax.set_title(r"Choropleth Map: Average Energy Cost by Operator County", fontsize=14)
    ax.set_xlabel(r"Longitude", fontsize=12)
    ax.set_ylabel(r"Latitude", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    # Create a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array(all_costs)
    cbar = fig.colorbar(sm, ax=ax, pad=0.03)
    cbar.set_label(r"Average Energy Cost (£)", fontsize=12)
    
    ax.relim()
    ax.autoscale_view()
    output_path = os.path.join("data", "cost_choropleth.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Choropleth map saved to: {output_path}")

def main():
    r"""
    Main function to generate standalone visualizations:
      - Generates an interactive map saved as an HTML file.
      - Generates a static choropleth map saved as a PNG image.
    """
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create interactive map (if folium is available)
    create_interactive_map()
    
    # Create static choropleth map of average energy cost by operator county
    create_static_choropleth()

if __name__ == '__main__':
    main()