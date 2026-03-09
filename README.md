


Clean and simple. Here's what you get:

**Required CSV columns:**
```
latitude, longitude
```

**Optional columns** (used for popups if present):
```
id, filename, timestamp, label
```

**Run it:**
```bash
python csv_gps_mapper.py my_data.csv
python csv_gps_mapper.py my_data.csv --output case42_map.html
```

The `sample_gps.csv` shows the expected format — just swap in your real coordinates. 
The map still includes the animated path arrows, color-coded start/end markers, and layer switcher (Dark/Street/Light).
