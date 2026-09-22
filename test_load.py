import fastf1
import os

# Create a local cache directory so telemetry only downloads once
cache_dir = "cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

print("Connecting to FastF1 and loading 2024 Monaco GP Race session...")
session = fastf1.get_session(2024, "Monaco", "R")
session.load()

# Print out a summary of the fastest lap in the race
fastest_lap = session.laps.pick_fastest()
driver = fastest_lap["Driver"]
lap_time = fastest_lap["LapTime"]

print("\n--- Success! ---")
print(f"Fastest Lap: {driver} with a time of {lap_time}")
print(f"Total laps recorded in session: {len(session.laps)}")