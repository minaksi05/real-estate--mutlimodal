import os
import time
import requests
import pandas as pd



MAPBOX_TOKEN = "pk.eyJ1IjoiZzBwYWwxOTM3IiwiYSI6ImNtamQ5ZWN0azAzNm0zZnF4YThtN2Q1cWYifQ.EWJnoa1hjAlAmDZ6DP8SGg"   
ZOOM = 18
IMAGE_SIZE = "256x256"

CSV_PATH = "/content/drive/MyDrive/multimodal-real-estate/data/raw/test_image_coords.csv"
SAVE_DIR = "/content/drive/MyDrive/multimodal-real-estate/data/raw/images/test"

SLEEP_TIME = 0.2        # polite rate limit 
TIMEOUT = 10            # seconds

# ============================================================
# SETUP
# ============================================================

os.makedirs(SAVE_DIR, exist_ok=True)

print("Loading coordinate CSV...")
df = pd.read_csv(CSV_PATH)

print(f"Total rows in CSV: {len(df)}")
print(f"Saving images to: {SAVE_DIR}")
print("--------------------------------------------------")

# ============================================================
# DOWNLOAD LOOP
# ============================================================

downloaded = 0
skipped = 0
failed = 0

for idx, row in df.iterrows():
    house_id = str(row["id"])
    lat = row["lat"]
    lon = row["long"]

    image_name = f"id_{house_id}.jpg"
    image_path = os.path.join(SAVE_DIR, image_name)

    # --------------------------------------------------------
    # Skip if image already exists (RESUME SAFE)
    # --------------------------------------------------------
    if os.path.exists(image_path):
        skipped += 1
        continue

    # --------------------------------------------------------
    # Mapbox Static API URL
    # --------------------------------------------------------
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
        f"{lon},{lat},{ZOOM}/{IMAGE_SIZE}"
        f"?access_token={MAPBOX_TOKEN}"
    )

    try:
        response = requests.get(url, timeout=TIMEOUT)

        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            downloaded += 1
        else:
            failed += 1

    except Exception:
        failed += 1

    
    time.sleep(SLEEP_TIME)

    # --------------------------------------------------------
    # Progress logging every 100 rows
    # --------------------------------------------------------
    if (idx + 1) % 100 == 0:
        print(
            f"[{idx + 1}/{len(df)}] "
            f"Downloaded: {downloaded} | Skipped: {skipped} | Failed: {failed}"
        )

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n================ DOWNLOAD COMPLETE ================")
print(f"Total rows       : {len(df)}")
print(f"Downloaded images: {downloaded}")
print(f"Skipped images   : {skipped}")
print(f"Failed downloads : {failed}")
print("===================================================")
