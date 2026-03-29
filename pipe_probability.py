import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

pipes = pd.read_csv("Datasets/pipe dataset.csv")   
                                                


def parse_year(val):
    if pd.isna(val): return np.nan
    try:
        return int(str(val)[:4]) if str(val)[:4].isdigit() else pd.to_datetime(val).year
    except:
        return np.nan

pipes["Install_Year"] = pipes["Install_Date"].apply(parse_year)
pipes["Pipe_Age"]     = 2026 - pipes["Install_Year"]
pipes["Pipe_Age"]     = pipes["Pipe_Age"].fillna(pipes["Pipe_Age"].median())


pipes["Slope_pct"] = pipes["Slope_pct"].fillna(pipes["Slope_pct"].median())


roughness_map = {
    "Concrete":                   0.013,
    "Reinforced Concrete Pipe":   0.013,
    "Vitrified Clay":             0.014,
    "Cast Iron Pipe":             0.015,
    "Ductile Iron Pipe":          0.012,
    "Polyvinyl Chloride":         0.009,
    "High Density Polyethylene":  0.011,
    "Brick":                      0.016,
    "Asbestos Cement":            0.011,
    "Unknown":                    0.013,
}
pipes["Roughness_n"] = pipes["Material"].map(roughness_map).fillna(0.013)


pipes["Diameter_m"]       = pipes["Diameter_in"] * 0.0254
pipes["Area_m2"]          = np.pi * (pipes["Diameter_m"] / 2) ** 2
pipes["Hydraulic_Radius"] = pipes["Diameter_m"] / 4
pipes["Slope_safe"]       = pipes["Slope_pct"].clip(lower=0.01) / 100

pipes["Capacity_m3_s"] = (
    (1 / pipes["Roughness_n"])
    * pipes["Area_m2"]
    * (pipes["Hydraulic_Radius"] ** (2/3))
    * (pipes["Slope_safe"] ** 0.5)
)


def degradation(row):
    age = row["Pipe_Age"]
    mat = row["Material"]
    if mat in ["Vitrified Clay", "Brick", "Asbestos Cement", "Cast Iron Pipe"]:
        return max(0.3, 1 - age * 0.008) 
    elif mat in ["Concrete", "Reinforced Concrete Pipe"]:
        return max(0.4, 1 - age * 0.006)  
    else:
        return max(0.6, 1 - age * 0.003)  

pipes["Degradation_Factor"] = pipes.apply(degradation, axis=1)
pipes["Effective_Capacity"] = pipes["Capacity_m3_s"] * pipes["Degradation_Factor"]


np.random.seed(42)
base_flow_fraction      = np.random.uniform(0.3, 1.4, len(pipes))
pipes["Pipe_Flow_m3_s"] = (
    pipes["Effective_Capacity"] * 
    (0.4 + 0.5 * (pipes["Pipe_Age"] / pipes["Pipe_Age"].max())) +
    np.random.normal(0, 0.05, len(pipes))  # small realistic noise only
)


pipes["Utilization"] = pipes["Pipe_Flow_m3_s"] / pipes["Effective_Capacity"]

def classify(u):
    if u < 0.6:   return 0  
    elif u < 0.9: return 1  
    else:         return 2 

pipes["Pipe_Status_Label"] = pipes["Utilization"].apply(classify)


features = [
    "Diameter_in",       
    "Pipe_Age",           
    "Slope_pct",          
    "Utilization",        
    "Degradation_Factor", 
    "Roughness_n",        
]

X = pipes[features]
y = pipes["Pipe_Status_Label"]

scaler   = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
model.fit(X_train, y_train)


probabilities = model.predict_proba(X_scaled)
n_classes     = probabilities.shape[1]

if n_classes == 3:
    pipes["Failure_Probability"] = probabilities[:, 1] + probabilities[:, 2]
elif n_classes == 2:
    pipes["Failure_Probability"] = probabilities[:, 1]
else:
    pipes["Failure_Probability"] = 1 - probabilities[:, 0]


status_map         = {0: "SAFE", 1: "STRESSED", 2: "CRITICAL"}
pipes["Pipe_Status"] = pipes["Pipe_Status_Label"].map(status_map)


print("Status distribution:")
print(pipes["Pipe_Status"].value_counts())
print("\nFailure Probability stats:")
print(pipes["Failure_Probability"].describe().round(3))

max_idx = pipes["Failure_Probability"].idxmax()
target  = pipes.loc[max_idx]
print(f"\nHighest Risk Pipe")
print(f"Pipe ID             : {target['Pipe_ID']}")
print(f"Material            : {target['Material']}")
print(f"Age                 : {int(target['Pipe_Age'])} years")
print(f"Utilization         : {target['Utilization']*100:.1f}%")
print(f"Failure Probability : {target['Failure_Probability']*100:.1f}%")

pipes.to_csv("pipe results.csv", index=False)
print("\nDone! Saved to pipe_final_results.csv")
