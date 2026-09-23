import os
import fastf1
import pandas as pd

os.makedirs("cache", exist_ok=True)
os.makedirs("data", exist_ok=True)
fastf1.Cache.enable_cache("cache")

races = [
    # 2025 Season
    (2025, "Australia"),
    (2025, "Monaco"),
    (2025, "Silverstone"),
    (2025, "Monza"),
    # 2024 Season
    (2024, "Monaco"),
    (2024, "Bahrain"),
    (2024, "Silverstone"),
    (2024, "Monza")
]

for year, gp in races:
    output_path = f"data/{year}_{gp.lower()}_laps.csv"
    
    # Skip if already downloaded
    if os.path.exists(output_path):
        print(f"Skipping {year} {gp} (already exists).")
        continue
        
    print(f"Extracting {year} {gp} Grand Prix...")
    try:
        session = fastf1.get_session(year, gp, "R")
        session.load()
        
        raw_laps = session.laps
        df = pd.DataFrame({
            "Driver": raw_laps["Driver"],
            "LapNumber": raw_laps["LapNumber"],
            "LapTime": raw_laps["LapTime"],
            "Compound": raw_laps["Compound"],
            "TyreLife": raw_laps["TyreLife"],
            "Stint": raw_laps["Stint"],
            "PitInTime": raw_laps["PitInTime"],
            "PitOutTime": raw_laps["PitOutTime"],
        })
        
        df["LapTimeSeconds"] = df["LapTime"].dt.total_seconds()
        clean_laps = df.loc[(df["PitInTime"].isna()) & (df["PitOutTime"].isna())].dropna(subset=["LapTimeSeconds"]).copy()
        
        clean_laps.to_csv(output_path, index=False)
        print(f"Saved {len(clean_laps)} laps to {output_path}")
    except Exception as e:
        print(f"Failed to fetch {year} {gp}: {e}")

print("Data fetch completed!")