import csv
from sklearn.ensemble import RandomForestClassifier

def probability(input_file):

    X = []
    y = []
    metadata = []

    with open(input_file, mode='r') as f:
        reader = csv.DictReader(f)

        for row in reader:

            features = [
                float(row['Rainfall_mm_hr']),
                float(row['Slope']),
                float(row['Impervious_frac']),
                float(row['Degradation_Factor'])
            ]

            X.append(features)
            y.append(1 if row['Operational_Status'] == 'CRITICAL' else 0)

            metadata.append(row)

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )

    clf.fit(X, y)

    probs = clf.predict_proba(X)[:,1]


    for i,row in enumerate(metadata):
        row["Failure_Probability"] = probs[i]

    max_idx = probs.argmax()
    target = metadata[max_idx]

    print("\nHighest Risk Drain")
    print("-------------------")
    print(f"Drain ID: {target['Drain_ID']}")
    print(f"Load: {float(target['Utilization_Ratio'])*100:.1f}%")
    print(f"Failure Probability: {probs[max_idx]*100:.1f}%")

    with open("Datasets/Data evaluation results.csv","w",newline="") as f:

        writer = csv.DictWriter(f, fieldnames=metadata[0].keys())

        writer.writeheader()
        writer.writerows(metadata)


if __name__ == "__main__":
    probability("Datasets/Drain Condition(after calculations).csv   ")