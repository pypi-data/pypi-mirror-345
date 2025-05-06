# filename: codebase/calculate_energy_costs.py
#!/usr/bin/env python3
"""
This script calculates the energy cost for each user based on their assigned energy operator,
using different pricing models that reflect the actual energy market in England. It reads user data,
operator data, and the matching results (from spatial matching) from CSV files in the 'data/' folder.
Three pricing models are implemented:
    1. Fixed Rate: cost = consumption * operator rate.
    2. Tiered Pricing: first threshold kWh at the base rate, remaining consumption at a higher rate.
    3. Time-of-Use Pricing: assumes a fraction of consumption occurs during peak and off-peak hours
       with different multipliers.
For users with multiple operator matches (overlapping service areas), the operator that yields the 
lowest energy cost (for the selected pricing model and season) is chosen.
The script also computes summary statistics for cost distributions across operator counties and
saves the final results and visualizations to disk.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Enable LaTeX rendering for plots and set font family
rcParams['text.usetex'] = True
rcParams['font.family'] = 'serif'

def fixed_rate(consumption, rate):
    r"""
    Calculates energy cost using the fixed rate pricing model.
    
    Args:
        consumption (float): Energy consumption (in kWh).
        rate (float): Cost per unit of energy.
    
    Returns:
        float: Total energy cost.
    """
    return consumption * rate

def tiered_pricing(consumption, rate, threshold=10, higher_multiplier=1.5):
    r"""
    Calculates energy cost using a tiered pricing model. For consumption up to a given threshold,
    the base rate applies; for consumption beyond the threshold, a higher multiplier is applied.
    
    Args:
        consumption (float): Energy consumption (in kWh).
        rate (float): Base cost per unit of energy.
        threshold (float, optional): kWh threshold for tiered pricing. Defaults to 10.
        higher_multiplier (float, optional): Multiplier for consumption above the threshold. Defaults to 1.5.
    
    Returns:
        float: Total energy cost.
    """
    if consumption <= threshold:
        return consumption * rate
    else:
        cost_first = threshold * rate
        cost_rest = (consumption - threshold) * rate * higher_multiplier
        return cost_first + cost_rest

def time_of_use_pricing(consumption, rate, peak_fraction=0.6, peak_multiplier=1.2, offpeak_multiplier=0.8):
    r"""
    Calculates energy cost using a time-of-use pricing model that assumes a certain fraction of consumption
    occurs during peak hours and the remainder during off-peak hours.
    
    Args:
        consumption (float): Energy consumption (in kWh).
        rate (float): Base cost per unit of energy.
        peak_fraction (float, optional): Fraction of consumption during peak hours. Defaults to 0.6.
        peak_multiplier (float, optional): Price multiplier during peak hours. Defaults to 1.2.
        offpeak_multiplier (float, optional): Price multiplier during off-peak hours. Defaults to 0.8.
    
    Returns:
        float: Total energy cost.
    """
    cost = consumption * (peak_fraction * (rate * peak_multiplier) + (1 - peak_fraction) * (rate * offpeak_multiplier))
    return cost

def load_operator_data(filepath="data/operators.csv"):
    r"""
    Loads operator data from CSV and returns a DataFrame.
    
    Args:
        filepath (str): Path to the operators CSV file.
    
    Returns:
        pd.DataFrame: DataFrame of operator data.
    """
    df = pd.read_csv(filepath)
    return df

def load_user_data(filepath="data/users.csv"):
    r"""
    Loads user data from CSV and returns a DataFrame.
    
    Args:
        filepath (str): Path to the users CSV file.
    
    Returns:
        pd.DataFrame: DataFrame of user data.
    """
    df = pd.read_csv(filepath)
    return df

def load_matching_results(filepath="data/user_operator_matches.csv"):
    r"""
    Loads user to operator matching results from CSV.
    
    Args:
        filepath (str): Path to the matching CSV file.
    
    Returns:
        pd.DataFrame: DataFrame with columns 'user_id' and 'matched_operator_ids'
                      (operator IDs are separated by semicolons).
    """
    df = pd.read_csv(filepath)
    return df

def build_operator_dict(operators_df):
    r"""
    Builds a dictionary mapping operator_id to operator details from the operators DataFrame.
    
    Args:
        operators_df (pd.DataFrame): DataFrame containing operators data.
    
    Returns:
        dict: Mapping from operator_id (int) to operator record (dict).
    """
    operator_dict = {}
    for _, row in operators_df.iterrows():
        op_id = row["operator_id"]
        operator_dict[op_id] = row.to_dict()
    return operator_dict

def compute_user_cost(consumption, rate, pricing_func):
    r"""
    Computes energy cost for a given consumption and rate using the provided pricing function.
    
    Args:
        consumption (float): Energy consumption (in kWh).
        rate (float): Cost per unit.
        pricing_func (function): Pricing function to compute cost.
    
    Returns:
        float: Computed energy cost.
    """
    return pricing_func(consumption, rate)

def calculate_energy_costs(pricing_model="fixed_rate", season="winter"):
    r"""
    Calculates energy costs for each user based on their assigned operator(s) and chosen pricing model.
    For users with multiple operator matches, selects the operator yielding the lowest cost.
    
    Args:
        pricing_model (str, optional): Pricing model to use. Options: "fixed_rate", "tiered", "time_of_use". 
                                       Defaults to "fixed_rate".
        season (str, optional): Season to determine operator rate. Options: "winter", "spring", "summer", "autumn".
                                Defaults to "winter".
    
    Returns:
        pd.DataFrame: DataFrame containing user energy cost data with columns:
                      'user_id', 'user_county', 'consumption', 'chosen_operator_id', 'operator_county',
                      'energy_cost', 'pricing_model', 'season'.
    """
    # Load data
    operators_df = load_operator_data()
    users_df = load_user_data()
    matching_df = load_matching_results()

    # Build operator lookup dictionary keyed by operator_id
    operator_dict = build_operator_dict(operators_df)

    # Map pricing model names to functions
    pricing_funcs = {
        "fixed_rate": fixed_rate,
        "tiered": tiered_pricing,
        "time_of_use": time_of_use_pricing
    }
    if pricing_model not in pricing_funcs:
        raise ValueError(f"Unknown pricing model: {pricing_model}. Choose from {list(pricing_funcs.keys())}.")
    pricing_func = pricing_funcs[pricing_model]

    # Prepare list for final user energy cost records
    cost_records = []
    
    # Convert matching results to dictionary: user_id -> list of operator_ids
    match_dict = {}
    for _, row in matching_df.iterrows():
        user_id = row["user_id"]
        op_str = row["matched_operator_ids"]
        if pd.isna(op_str) or op_str.strip() == "":
            match_dict[user_id] = []
        else:
            # Split by semicolon and convert to int
            op_ids = [int(x) for x in op_str.split(";")]
            match_dict[user_id] = op_ids

    # Process each user
    for _, user in users_df.iterrows():
        user_id = user["user_id"]
        consumption = user["consumption"]
        user_county = user["county"]
        candidate_ops = match_dict.get(user_id, [])
        best_cost = None
        chosen_operator_id = None
        chosen_operator_county = None
        
        # If no operator matched, assign cost as None (or can choose default)
        if not candidate_ops:
            energy_cost = None
        else:
            # Evaluate cost for each candidate operator and choose the one with minimum cost
            for op_id in candidate_ops:
                # Lookup operator record
                op_record = operator_dict.get(op_id)
                if op_record is None:
                    continue
                # Get the seasonal cost rate; e.g., "winter_cost", etc.
                rate_key = f"{season}_cost"
                if rate_key not in op_record:
                    continue
                rate = float(op_record[rate_key])
                cost = compute_user_cost(consumption, rate, pricing_func)
                if (best_cost is None) or (cost < best_cost):
                    best_cost = cost
                    chosen_operator_id = op_id
                    chosen_operator_county = op_record["county"]
            energy_cost = best_cost

        record = {
            "user_id": user_id,
            "user_county": user_county,
            "consumption": consumption,
            "chosen_operator_id": chosen_operator_id,
            "operator_county": chosen_operator_county,
            "energy_cost": energy_cost,
            "pricing_model": pricing_model,
            "season": season
        }
        cost_records.append(record)

    cost_df = pd.DataFrame(cost_records)
    # Save the results to CSV
    output_filepath = os.path.join("data", "user_energy_costs.csv")
    cost_df.to_csv(output_filepath, index=False)
    print(f"User energy cost data saved to: {output_filepath}")

    return cost_df

def plot_energy_cost_distribution(cost_df, output_path="data/energy_cost_distribution.png"):
    r"""
    Plots a histogram of the energy cost distribution across users.
    
    Args:
        cost_df (pd.DataFrame): DataFrame containing user energy cost data.
        output_path (str): File path to save the plot image.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    valid_costs = cost_df["energy_cost"].dropna()
    ax.hist(valid_costs, bins=30, color="skyblue", edgecolor="black", alpha=0.7)
    ax.set_title(r"Distribution of Energy Costs Across Users", fontsize=14)
    ax.set_xlabel(r"Energy Cost (£)", fontsize=12)
    ax.set_ylabel(r"Number of Users", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.relim()
    ax.autoscale_view()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Energy cost distribution plot saved to: {output_path}")

def plot_average_cost_by_operator(cost_df, output_path="data/avg_cost_by_operator.png"):
    r"""
    Plots a bar chart of the average energy cost by operator county.
    
    Args:
        cost_df (pd.DataFrame): DataFrame containing user energy cost data.
        output_path (str): File path to save the plot image.
    """
    # Group by operator_county and compute mean energy cost (ignoring NaNs)
    group = cost_df.dropna(subset=["energy_cost"]).groupby("operator_county")["energy_cost"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(group["operator_county"], group["energy_cost"], color="lightgreen", edgecolor="black", alpha=0.7)
    ax.set_title(r"Average Energy Cost by Operator County", fontsize=14)
    ax.set_xlabel(r"Operator County", fontsize=12)
    ax.set_ylabel(r"Average Energy Cost (£)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.relim()
    ax.autoscale_view()
    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{height:.2f}", ha="center", va="bottom", fontsize=10)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Average cost by operator plot saved to: {output_path}")

def main():
    r"""
    Main function to calculate energy costs for users based on their matched energy operators.
    It applies a specified pricing model (fixed_rate, tiered, or time_of_use) for a given season,
    computes per-user energy cost by selecting the cheapest operator in case of overlapping service areas,
    generates summary statistics, and saves the results and visualizations.
    """
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Choose pricing model and season; these can be changed as needed
    pricing_model = "fixed_rate"  # Options: "fixed_rate", "tiered", "time_of_use"
    season = "winter"             # Options: "winter", "spring", "summer", "autumn"
    
    # Calculate energy costs
    cost_df = calculate_energy_costs(pricing_model=pricing_model, season=season)
    
    # Print summary statistics
    summary = cost_df.describe(include="all")
    print("\nSummary Statistics for Energy Costs:")
    print(summary)
    
    # Group by operator county and print average cost
    operator_grp = cost_df.dropna(subset=["energy_cost"]).groupby("operator_county")["energy_cost"].agg(["mean", "std", "min", "max"])
    print("\nAverage Energy Cost by Operator County:")
    print(operator_grp)
    
    # Save summary statistics to a CSV file
    summary_filepath = os.path.join("data", "energy_cost_summary.csv")
    operator_grp.to_csv(summary_filepath)
    print(f"Operator cost summary saved to: {summary_filepath}")
    
    # Generate visualizations
    plot_energy_cost_distribution(cost_df)
    plot_average_cost_by_operator(cost_df)

if __name__ == '__main__':
    main()