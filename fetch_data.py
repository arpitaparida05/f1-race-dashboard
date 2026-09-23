import os
import fastf1
import pandas as pd

# Setup local cache
os.makedirs("cache", exist_ok=True)
os.makedirs("data", exist_ok=True)
fastf1.Cache.enable_cache("cache")

races = [
    (2024, "Monaco"),
    (2024, "Bahrain"),
    (2024, "Silverstone"),
    (2024, "Monza")
]

for year, gp in races:
    print(f"Extracting {year} {gp} Grand Prix...")
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
    
    output_path = f"data/{year}_{gp.lower()}_laps.csv"
    clean_laps.to_csv(output_path, index=False)
    print(f"Saved {len(clean_laps)} clean laps to {output_path}")

print("Data generation complete!")