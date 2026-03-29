import csv

def run_base_physics_engine(input_file, output_file):
    results = []
    
    with open(input_file, mode='r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['Q_runoff', 'Q_baseflow', 'Q_total_in', 'Q_eff', 'Utilization_Ratio', 'Operational_Status']
        
        for row in reader:
            rain = float(row['Rainfall_mm_hr'])
            area = float(row['Catchment_km2'])
            coeff = float(row['Runoff_coeff'])
            imp = float(row['Impervious_frac'])
            cap = float(row['Design_Capacity_m3hr'])
            deg = float(row['Degradation_Factor'])
            
            q_runoff = rain * area * coeff * 100
            q_baseflow = 5 * area * imp
            q_total_in = q_runoff + q_baseflow
            q_eff = cap * deg
            util = q_total_in / q_eff if q_eff != 0 else 0
            
            if util < 0.6: status = 'SAFE'
            elif util <= 0.9: status = 'STRESSED'
            else: status = 'CRITICAL'
            
            row.update({
                'Q_runoff': q_runoff, 'Q_baseflow': q_baseflow,
                'Q_total_in': q_total_in, 'Q_eff': q_eff,
                'Utilization_Ratio': util, 'Operational_Status': status
            })
            results.append(row)

    # Save to Outfile
    with open(output_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Physics Engine Complete! Results saved to {output_file}")

# Run it
run_base_physics_engine('Datasets/Drain Dataset.csv', 'Datasets/Drain Condition(after calculations)2.csv')