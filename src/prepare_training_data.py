#data augmentation — creating additional training examples when you don't have enough real data. Real ML engineers do this all the time.

import pandas as pd
import os
from sqlalchemy import create_engine

engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

# Load your manually labelled data
df = pd.read_csv("data/labelling.csv")
print(f"Original labelled data: {len(df)} rows")
print(df["risk_label"].value_counts())

# Additional training examples per category
# These are hand-crafted examples to balance the dataset
extra_examples = [
    # natural_disaster
    {"title": "Massive earthquake disrupts manufacturing in Turkey", "description": "A 7.2 magnitude earthquake has halted production at several factories", "risk_label": "natural_disaster"},
    {"title": "Flooding shuts down industrial zones in Bangladesh", "description": "Heavy monsoon floods have forced closure of garment factories", "risk_label": "natural_disaster"},
    {"title": "Typhoon forces closure of Philippine ports", "description": "Major ports shut down as typhoon makes landfall", "risk_label": "natural_disaster"},
    {"title": "Wildfires threaten California semiconductor plants", "description": "Chip manufacturers evacuate as wildfires spread near facilities", "risk_label": "natural_disaster"},
    {"title": "Volcanic ash disrupts air freight across Europe", "description": "Airline cargo operations suspended due to volcanic activity", "risk_label": "natural_disaster"},

    # geopolitical
    {"title": "US imposes new tariffs on Chinese electronics", "description": "25% tariff on semiconductors and electronics components announced", "risk_label": "geopolitical"},
    {"title": "Russia Ukraine conflict disrupts wheat exports", "description": "Global wheat supply threatened as Black Sea ports remain blocked", "risk_label": "geopolitical"},
    {"title": "India China border tensions impact trade routes", "description": "Trade restrictions imposed following border disputes", "risk_label": "geopolitical"},
    {"title": "OPEC cuts oil production affecting fuel prices globally", "description": "Supply cuts expected to raise transportation costs worldwide", "risk_label": "geopolitical"},
    {"title": "Sanctions on Iran disrupt oil tanker routes", "description": "New sanctions force rerouting of oil shipments through longer routes", "risk_label": "geopolitical"},
    {"title": "Taiwan Strait tensions threaten semiconductor supply", "description": "Military exercises near Taiwan disrupt chip shipments globally", "risk_label": "geopolitical"},
    {"title": "Red Sea attacks force shipping companies to reroute", "description": "Houthi attacks on cargo ships add weeks to delivery times", "risk_label": "geopolitical"},

    # labour_strike
    {"title": "Dock workers strike at Los Angeles port", "description": "Thousands of dock workers walk off the job demanding higher wages", "risk_label": "labour_strike"},
    {"title": "Amazon warehouse workers go on strike in Germany", "description": "Workers demand better conditions and pay during peak season", "risk_label": "labour_strike"},
    {"title": "Auto workers union strikes at Ford plants", "description": "UAW calls strike at three major assembly plants", "risk_label": "labour_strike"},
    {"title": "UK rail strike disrupts freight movement", "description": "Rail workers strike causes major disruption to goods transport", "risk_label": "labour_strike"},
    {"title": "French truck drivers blockade highways", "description": "Protesting fuel prices, truck drivers block major supply routes", "risk_label": "labour_strike"},
    {"title": "Mining workers strike in Chile copper mines", "description": "Copper production halted as workers demand wage increases", "risk_label": "labour_strike"},

    # material_shortage
    {"title": "Global semiconductor shortage worsens in Q3", "description": "Auto and electronics industries face production cuts due to chip shortage", "risk_label": "material_shortage"},
    {"title": "Lithium prices surge as EV demand outpaces supply", "description": "Battery manufacturers struggle to secure lithium supplies", "risk_label": "material_shortage"},
    {"title": "Steel shortage hits construction sector globally", "description": "Steel prices at record high as demand outstrips production capacity", "risk_label": "material_shortage"},
    {"title": "Cotton shortage threatens textile industry", "description": "Poor harvests in major cotton producing countries cause supply crunch", "risk_label": "material_shortage"},
    {"title": "Rare earth metal shortage threatens green energy transition", "description": "Wind turbine and EV manufacturers face critical supply constraints", "risk_label": "material_shortage"},
    {"title": "Wheat shortage drives food prices higher globally", "description": "Drought and conflict reduce global wheat stockpiles to 10 year low", "risk_label": "material_shortage"},

    # logistics
    {"title": "Suez Canal congestion delays thousands of shipments", "description": "Container ships waiting up to 5 days to transit the canal", "risk_label": "logistics"},
    {"title": "Shanghai port delays hit global supply chains", "description": "COVID lockdowns cause massive backlog at world's busiest port", "risk_label": "logistics"},
    {"title": "Air freight costs triple amid cargo capacity crunch", "description": "Limited cargo capacity pushes air freight rates to record levels", "risk_label": "logistics"},
    {"title": "Truck driver shortage causes delivery delays across US", "description": "Shortage of 80000 truck drivers disrupts last mile delivery", "risk_label": "logistics"},
    {"title": "Panama Canal drought reduces ship traffic by 30 percent", "description": "Low water levels force ships to reduce load or take longer routes", "risk_label": "logistics"},
    {"title": "Rotterdam port strike disrupts European supply chains", "description": "Workers strike at Europe's largest port causing cargo backlog", "risk_label": "logistics"},

    # political
    {"title": "India imposes export ban on rice to control inflation", "description": "Government restricts rice exports affecting global food supply", "risk_label": "political"},
    {"title": "New environmental regulations shut down factories in China", "description": "Stricter emission rules force temporary closure of manufacturing plants", "risk_label": "political"},
    {"title": "Brexit causes customs delays at UK ports", "description": "New border checks slow down imports and exports significantly", "risk_label": "political"},
    {"title": "US export controls restrict semiconductor sales to China", "description": "New rules limit chip exports affecting tech supply chains globally", "risk_label": "political"},
    {"title": "India raises import duties on electronics components", "description": "Higher tariffs on imported components impact domestic manufacturers", "risk_label": "political"},

    # no_risk
    {"title": "Apple reports record quarterly earnings", "description": "iPhone maker beats analyst expectations with strong services revenue", "risk_label": "no_risk"},
    {"title": "Amazon expands warehouse network across India", "description": "E-commerce giant opens 5 new fulfillment centers in tier 2 cities", "risk_label": "no_risk"},
    {"title": "Tata Motors launches new electric vehicle lineup", "description": "Company unveils three new EV models targeting urban consumers", "risk_label": "no_risk"},
    {"title": "Infosys wins major cloud transformation deal", "description": "IT giant secures 5 year contract with European banking client", "risk_label": "no_risk"},
    {"title": "Reliance Industries posts strong Q4 results", "description": "Conglomerate reports 15 percent growth in net profit", "risk_label": "no_risk"},
]

# Convert to dataframe
extra_df = pd.DataFrame(extra_examples)
extra_df["keyword"] = "augmented"

# Combine original + extra
df_clean = df[["title", "description", "keyword", "risk_label"]].copy()
combined_df = pd.concat([df_clean, extra_df], ignore_index=True)

# Remove rows with missing labels
combined_df = combined_df.dropna(subset=["risk_label"])
combined_df = combined_df[combined_df["risk_label"] != ""]

print(f"\nCombined dataset: {len(combined_df)} rows")
print("\nLabel distribution:")
print(combined_df["risk_label"].value_counts())

# Save final training data
os.makedirs("data", exist_ok=True)
combined_df.to_csv("data/training_data.csv", index=False)
print(f"\n✅ Training data saved to data/training_data.csv")