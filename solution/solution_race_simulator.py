import json
import sys

data = json.load(sys.stdin)

race_config = data["race_config"]
base_lap_time = race_config["base_lap_time"]
total_laps = race_config["total_laps"]
pit_time = race_config["pit_lane_time"]
track_temp = race_config["track_temp"]

strategies = data["strategies"]

tire_offset = {
    "SOFT": -0.8,
    "MEDIUM": 0.0,
    "HARD": 0.8
}

degradation = {
    "SOFT": 0.08,
    "MEDIUM": 0.05,
    "HARD": 0.03
}

grace_laps = {
    "SOFT": 3,
    "MEDIUM": 4,
    "HARD": 5
}

temp_factor = 1 + ((track_temp - 30) * 0.02)

driver_times = []

for key in strategies:
    driver = strategies[key]
    driver_id = driver["driver_id"]
    starting_tire = driver["starting_tire"]
    pit_stops = driver["pit_stops"]

    current_tire = starting_tire
    start_lap = 1
    segments = []

    for stop in pit_stops:
        pit_lap = stop["lap"]
        segments.append((start_lap, pit_lap, current_tire))
        current_tire = stop["to_tire"]
        start_lap = pit_lap + 1

    segments.append((start_lap, total_laps, current_tire))

    total_time = 0.0

    for seg_start, seg_end, tire in segments:
        laps_in_segment = seg_end - seg_start + 1

        for lap_on_tire in range(1, laps_in_segment + 1):
            extra_wear_laps = max(0, lap_on_tire - grace_laps[tire])
            wear = extra_wear_laps * degradation[tire] * temp_factor
            lap_time = base_lap_time + tire_offset[tire] + wear
            total_time += lap_time

    total_time += len(pit_stops) * pit_time
    driver_times.append((driver_id, total_time))

driver_times.sort(key=lambda x: x[1])

finishing_positions = [driver_id for driver_id, _ in driver_times]

output = {
    "race_id": data["race_id"],
    "finishing_positions": finishing_positions
}

print(json.dumps(output))
