import csv
import math
from golf_physics.complete_golf_sim import CompleteGolfSim

def generate_massive_data(output_csv: str):
    """
    Automatically enumerates a wide range of clubs, speeds, angles, etc.
    Writes results to output_csv with no manual input required.
    """

    sim = CompleteGolfSim()

    # clubs with min->max loft
    clubs = [
        ("Driver",    9,   12),
        ("3-Wood",   14,   16),
        ("4-Wood",   15,   17),
        ("5-Wood",   17,   19),
        ("7-Wood",   20,   21),
        ("2-Hybrid", 17,   18),
        ("3-Hybrid", 19,   20),
        ("4-Hybrid", 21,   23),
        ("5-Hybrid", 24,   26),
        ("2-Iron",   18,   19),
        ("3-Iron",   18,   21),
        ("4-Iron",   20,   24),
        ("5-Iron",   23,   27),
        ("6-Iron",   26,   31),
        ("7-Iron",   30,   35),
        ("8-Iron",   35,   39),
        ("9-Iron",   39,   44),
        ("PW",       45,   47),
        ("GW",       50,   52),
        ("SW",       54,   58),
        ("LW",       58,   64)
    ]

    # For each club speed in m/s (~ 56..157 mph if range is 25..70)
    club_speeds  = [i for i in range(20, 140, 1)]  # e.g. 25,30,35,...70
    face_angles  = list(range(-4, 5, 2))         # -4,-2,0,2,4
    h_offsets    = [-2.0, -1.0, 0.0, 1.0, 2.0]
    v_offsets    = [-1.0, -0.5, 0.0, 0.5, 1.0]

    wind_speeds  = [0, 3, 6, 9, 12]
    wind_dirs    = [0, 90, 180, 270]
    temps        = [10, 20, 30]
    humidities   = [0.2, 0.5, 0.8]
    elevations   = [0, 500, 1000]

    with open(output_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "club_name", "loft_deg",
            "club_speed_mps", "face_angle_deg",
            "horizontal_offset_cm", "vertical_offset_cm",
            "wind_speed_mps", "wind_dir_deg",
            "temperature_c", "humidity", "elevation_m",
            "final_x", "final_y", "final_z",
            "carry_2d", "roll_2d", "total_2d"
        ])

        for (club_name, loft_min, loft_max) in clubs:
            for loft_deg in range(loft_min, loft_max+1):
                for speed in club_speeds:
                    for face_deg in face_angles:
                        for hx in h_offsets:
                            for vx in v_offsets:
                                for wspd in wind_speeds:
                                    for wdir in wind_dirs:
                                        for t in temps:
                                            for hum in humidities:
                                                for elev in elevations:
                                                    # Simulate
                                                    result = sim.simulate_shot(
                                                        club_speed_mps=float(speed),
                                                        club_loft_deg=float(loft_deg),
                                                        club_face_angle_deg=float(face_deg),
                                                        horizontal_offset_cm=hx,
                                                        vertical_offset_cm=vx,
                                                        wind_speed_mps=float(wspd),
                                                        wind_dir_deg=float(wdir),
                                                        temperature_c=float(t),
                                                        humidity=hum,
                                                        elevation_m=float(elev)
                                                    )

                                                    flight_path = result["flight_path"]
                                                    roll_path   = result["roll_path"]

                                                    # compute carry, final distances
                                                    if len(flight_path)>0:
                                                        cx, cy, cz, *_ = flight_path[-1]
                                                    else:
                                                        cx, cy, cz = 0,0,0

                                                    if len(roll_path)>0:
                                                        fx, fy, fz, *_ = roll_path[-1]
                                                    else:
                                                        fx, fy, fz = cx, cy, cz

                                                    carry_2d = math.sqrt(cx*cx + cy*cy)
                                                    total_2d = math.sqrt(fx*fx + fy*fy)
                                                    roll_2d  = total_2d - carry_2d

                                                    writer.writerow([
                                                        club_name, loft_deg,
                                                        speed, face_deg,
                                                        hx, vx,
                                                        wspd, wdir,
                                                        t, hum, elev,
                                                        fx, fy, fz,
                                                        carry_2d, roll_2d, total_2d
                                                    ])

def main():
    output_file = "massive_golf_data.csv"
    print("Generating large-scale golf shot dataset. Please wait...")
    generate_massive_data(output_file)
    print(f"Done! Data written to {output_file}")

if __name__ == "__main__":
    main()
