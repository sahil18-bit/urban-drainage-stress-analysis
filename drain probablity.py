import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

drains_monthly = pd.read_csv("Datasets/Updated/Drain Condition(after calculations)2.csv")

print(f"Raw data shape     : {drains_monthly.shape}")
print(f"Unique drains      : {drains_monthly['Drain_ID'].nunique()}")


def worst_status(statuses):
    if 'CRITICAL' in statuses.values:  return 'CRITICAL'
    if 'STRESSED' in statuses.values:  return 'STRESSED'
    return 'SAFE'

drains = drains_monthly.copy()
drains["Peak_Utilization"] = drains["Utilization_Ratio"]
print(f"After aggregation  : {drains.shape}")
print(f"\nStatus distribution:")
print(drains['Operational_Status'].value_counts())

def classify(u):
    if u < 0.6:   return 0 
    elif u < 0.9: return 1  
    else:         return 2 

drains['Status_Label'] = drains['Utilization_Ratio'].apply(classify)

status_map = {0: 'SAFE', 1: 'STRESSED', 2: 'CRITICAL'}
drains['Operational_Status'] = drains['Status_Label'].map(status_map)

print(f"\nRe-classified status distribution:")
print(drains['Operational_Status'].value_counts())

features = [
    'Rainfall_mm_hr',    
    'Slope',             
    'Impervious_frac',    
    'Degradation_Factor', 
    'Catchment_km2',     
    'Runoff_coeff',       
]

X = drains[features]
y = drains['Status_Label']

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
    drains['Failure_Probability'] = probabilities[:, 1] + probabilities[:, 2]
elif n_classes == 2:
    drains['Failure_Probability'] = probabilities[:, 1]
else:
    drains['Failure_Probability'] = 1 - probabilities[:, 0]

max_idx = drains['Failure_Probability'].idxmax()
target  = drains.loc[max_idx]

print("\nHighest Risk Drain")
print("-------------------")
print(f"Drain ID            : {int(target['Drain_ID'])}")
print(f"Mean Load           : {target['Utilization_Ratio']*100:.1f}%")
print(f"Peak Load           : {target['Peak_Utilization']*100:.1f}%")
print(f"Status              : {target['Operational_Status']}")
print(f"Failure Probability : {target['Failure_Probability']*100:.1f}%")

print("\nFailure Probability stats:")
print(drains['Failure_Probability'].describe().round(3))

drains.to_csv("Data evaluation results3.csv", index=False)
print(f"\nDone! Saved {len(drains)} drains to Data_evaluation_results3.csv")


