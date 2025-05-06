# filename: codebase/generate_simulated_data.py
#!/usr/bin/env python3
"""
This script generates simulated data for energy operators and users in a region similar to England.
The energy operators have service areas defined by realistic (approximated) geographic boundaries
of counties/regions in England and include seasonal variations in energy cost. Users are generated
with random geographic coordinates within these service areas based on approximated population 
density distributions, along with user-specific energy consumption values.

The generated datasets (operators and users) are saved in CSV format under the 'data/' folder and 
a visualization of the simulated data is saved as a high resolution PNG image.
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from matplotlib import rcParams

# Enable LaTeX rendering for plots and set font family
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

def generate_operator_data():
    r"""
    Generates simulated energy operator data with realistic service areas for counties/regions in England.

    Each operator is associated with a county and a service area defined by a geographic polygon.
    Seasonal energy costs (winter, spring, summer, autumn) are derived from a randomly assigned base cost,
    incorporating small random noise to simulate seasonal variations typically observed in England.

    Returns:
        pd.DataFrame: A DataFrame containing operator details including:
                      'operator_id', 'county', 'polygon' (as a shapely.geometry.Polygon object),
                      'base_cost', 'winter_cost', 'spring_cost', 'summer_cost', 'autumn_cost'.
    """
    # Define operator counties along with their approximated rectangular boundaries (lon, lat)
    counties = {
        "Greater London": [(-0.5, 51.3), (0.2, 51.3), (0.2, 51.7), (-0.5, 51.7)],
        "Kent": [ (0.0, 51.0), (1.0, 51.0), (1.0, 51.3), (0.0, 51.3) ],
        "Essex": [ (0.0, 51.3), (1.3, 51.3), (1.3, 51.8), (0.0, 51.8) ],
        "Yorkshire": [ (-1.0, 53.5), (0.5, 53.5), (0.5, 54.5), (-1.0, 54.5) ],
        "Lancashire": [ (-2.5, 53.0), (-1.0, 53.0), (-1.0, 54.0), (-2.5, 54.0) ]
    }
    
    operators = []
    operator_id = 1
    for county, coords in counties.items():
        poly = Polygon(coords)
        # Assign a base cost per unit (in pounds) between 0.15 and 0.30
        base_cost = random.uniform(0.15, 0.30)
        # Seasonal multipliers with small random noise
        noise_winter = random.uniform(-0.02, 0.02)
        noise_spring = random.uniform(-0.02, 0.02)
        noise_summer = random.uniform(-0.02, 0.02)
        noise_autumn = random.uniform(-0.02, 0.02)
        winter_cost = base_cost * (1.2 + noise_winter)
        spring_cost = base_cost * (1.0 + noise_spring)
        summer_cost = base_cost * (0.9 + noise_summer)
        autumn_cost = base_cost * (1.0 + noise_autumn)
        
        operators.append({
            "operator_id": operator_id,
            "county": county,
            "polygon": poly,
            "base_cost": base_cost,
            "winter_cost": winter_cost,
            "spring_cost": spring_cost,
            "summer_cost": summer_cost,
            "autumn_cost": autumn_cost,
        })
        operator_id += 1

    # Create DataFrame
    df_operators = pd.DataFrame(operators)
    # Save the polygon as WKT string for CSV export
    df_operators['polygon_wkt'] = df_operators['polygon'].apply(lambda poly: poly.wkt)
    return df_operators

def generate_user_data(operators_df, total_users=1000):
    r"""
    Generates simulated user data with random geographic coordinates within the service areas 
    (counties) defined in the operator dataset. Users are distributed based on an approximated 
    population density across counties.

    The function assigns each user:
      - A unique user ID.
      - A county (matching one of the operator counties) chosen according to weighted population density.
      - Random geographic coordinates (longitude and latitude) within the county's service area.
      - A user-specific energy consumption value (kWh per day), generated randomly.

    Args:
        operators_df (pd.DataFrame): DataFrame containing operator data with 'county' and 'polygon' columns.
        total_users (int, optional): The total number of users to generate. Defaults to 1000.

    Returns:
        pd.DataFrame: A DataFrame of simulated user data with columns:
                      'user_id', 'county', 'longitude', 'latitude', 'consumption'.
    """
    # Approximate weights for population density by county (sums to 1)
    population_weights = {
        "Greater London": 0.40,
        "Kent": 0.20,
        "Essex": 0.15,
        "Yorkshire": 0.15,
        "Lancashire": 0.10
    }
    
    users = []
    user_id = 1
    # Ensure reproducibility by using numpy's random functionality
    rng = np.random.default_rng(seed=42)
    
    # For each county/operator, determine the number of users based on population weight
    counties = operators_df[['county', 'polygon']].drop_duplicates().set_index('county')
    # Compute number of users per county
    county_user_counts = {}
    total_assigned = 0
    for county, weight in population_weights.items():
        count = int(round(total_users * weight))
        county_user_counts[county] = count
        total_assigned += count
    # Adjust to ensure the total equals total_users (adjust the largest county)
    if total_assigned != total_users:
        diff = total_users - total_assigned
        county_user_counts["Greater London"] += diff
    
    # Generate users for each county
    for county, count in county_user_counts.items():
        poly = counties.loc[county, 'polygon']
        minx, miny, maxx, maxy = poly.bounds
        # Generate count random points within the bounding box and check membership
        # Since the polygons are defined as rectangles, all generated points are inside.
        xs = rng.uniform(minx, maxx, count)
        ys = rng.uniform(miny, maxy, count)
        for x, y in zip(xs, ys):
            # Optionally, ensure the point lies within the polygon (guaranteed here because of rectangle)
            point = Point(x, y)
            if poly.contains(point) or poly.touches(point):
                consumption = random.uniform(5, 20)  # kWh per day consumption
                users.append({
                    "user_id": user_id,
                    "county": county,
                    "longitude": x,
                    "latitude": y,
                    "consumption": consumption
                })
                user_id += 1
    df_users = pd.DataFrame(users)
    return df_users

def plot_simulated_data(operators_df, users_df, output_path="data/simulated_data.png"):
    r"""
    Creates a visualization of the simulated data by plotting the energy operator service areas 
    (as polygons) and the user locations (as scatter points). The plot includes a legend, axis labels,
    and grid lines for clarity. The resulting figure is saved in high resolution (dpi >= 300).

    Args:
        operators_df (pd.DataFrame): DataFrame containing operator data with columns 'county' and 'polygon'.
        users_df (pd.DataFrame): DataFrame containing user data with columns 'longitude' and 'latitude'.
        output_path (str, optional): The file path to save the generated plot image. Defaults to 'data/simulated_data.png'.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    # Generate distinct colors for each operator/county
    counties = operators_df['county'].unique()
    cmap = plt.get_cmap("tab10")
    color_map = {county: cmap(i) for i, county in enumerate(counties)}
    
    # Plot each operator polygon with fill
    for _, row in operators_df.iterrows():
        poly = row['polygon']
        x, y = poly.exterior.xy
        ax.fill(x, y, alpha=0.3, fc=color_map[row['county']], ec='black', label=row['county'])
    
    # Plot user locations
    ax.scatter(users_df['longitude'], users_df['latitude'], s=10, color='black', alpha=0.6, label="Users")
    
    ax.set_title(r"Simulated Energy Operators and User Distribution in England", fontsize=14)
    ax.set_xlabel(r"Longitude", fontsize=12)
    ax.set_ylabel(r"Latitude", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.relim()
    ax.autoscale_view()
    # Create a legend with unique labels
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper right")
    
    # Save figure in high resolution
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def main():
    r"""
    Main function to generate simulated data for operators and users, store the datasets as CSV files,
    and generate a high-resolution plot visualizing the spatial distribution of operators and users.
    """
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate simulated operator data
    operators_df = generate_operator_data()
    # Save operators data to CSV (store the WKT representation of polygons)
    operators_csv_path = os.path.join(data_dir, "operators.csv")
    operators_df.drop(columns=["polygon"]).to_csv(operators_csv_path, index=False)
    
    # Generate simulated user data
    users_df = generate_user_data(operators_df, total_users=1000)
    # Save users data to CSV
    users_csv_path = os.path.join(data_dir, "users.csv")
    users_df.to_csv(users_csv_path, index=False)
    
    # Plot the simulated data and save the figure
    plot_simulated_data(operators_df, users_df, output_path=os.path.join(data_dir, "simulated_data.png"))
    
    print(f"Simulated operator data saved to: {operators_csv_path}")
    print(f"Simulated user data saved to: {users_csv_path}")
    print(f"Simulation plot saved to: {os.path.join(data_dir, 'simulated_data.png')}")

if __name__ == '__main__':
    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    main()
