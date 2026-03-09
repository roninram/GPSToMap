#!/usr/bin/env python3
"""
CSV GPS Path Mapper
====================
Reads GPS coordinates from a CSV file and generates
an interactive HTML map showing the path.

CSV must have columns: latitude, longitude
Optional columns:  id, filename, timestamp, label

Usage:
    python csv_gps_mapper.py <input.csv> [--output map.html]
"""

import csv
import sys
import argparse
from pathlib import Path
import folium
from folium import plugins


def load_csv(filepath: str) -> list:
    """Read GPS rows from a CSV file."""
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                lat = float(row["latitude"])
                lon = float(row["longitude"])
            except (KeyError, ValueError) as e:
                print(f"  [SKIP] Row {i}: {e}")
                continue

            rows.append({
                "index":     i,
                "latitude":  lat,
                "longitude": lon,
                "id":        row.get("id", str(i)),
                "filename":  row.get("filename", ""),
                "timestamp": row.get("timestamp", ""),
                "label":     row.get("label", f"Waypoint {i}"),
            })

    return rows


def build_map(rows: list, output_file: str):
    """Create a Folium map with path and markers."""

    coords = [(r["latitude"], r["longitude"]) for r in rows]

    # Center map
    avg_lat = sum(c[0] for c in coords) / len(coords)
    avg_lon = sum(c[1] for c in coords) / len(coords)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=14, tiles=None)

    # Tile layers
    folium.TileLayer("CartoDB dark_matter", name="Dark",         show=True).add_to(m)
    folium.TileLayer("OpenStreetMap",       name="Street").add_to(m)
    folium.TileLayer("CartoDB positron",    name="Light").add_to(m)

    # Path line
    folium.PolyLine(coords, color="#00d4ff", weight=3, opacity=0.8).add_to(m)

    # Animated direction arrows
    plugins.AntPath(
        coords, color="#00d4ff", weight=4,
        delay=800, dash_array=[10, 20], pulse_color="#ffffff"
    ).add_to(m)

    # Markers
    for r in rows:
        is_first = r["index"] == 1
        is_last  = r["index"] == len(rows)

        color = "green" if is_first else ("red" if is_last else "blue")
        icon  = "play"  if is_first else ("stop" if is_last else "map-marker")

        popup_html = f"""
        <div style="font-family:monospace;font-size:12px;min-width:200px">
          <b style="color:#58a6ff">WAYPOINT {r['index']:02d}</b><br>
          <hr style="border-color:#30363d;margin:4px 0">
          📁 {r['filename'] or '—'}<br>
          🏷️ {r['label']}<br>
          🕐 {r['timestamp'] or '—'}<br>
          🌍 {r['latitude']:.6f}, {r['longitude']:.6f}
        </div>"""

        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            tooltip=f"#{r['index']} — {r['label']}",
            popup=folium.Popup(popup_html, max_width=260),
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(m)

    plugins.MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(m)
    plugins.Fullscreen(position="topright").add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)

    m.save(output_file)
    print(f"✅ Map saved → {output_file}  ({len(rows)} waypoints)")


def main():
    parser = argparse.ArgumentParser(description="CSV GPS Path Mapper")
    parser.add_argument("csv",    help="Input CSV file with latitude/longitude columns")
    parser.add_argument("--output", default="gps_path_map.html", help="Output HTML map file")
    args = parser.parse_args()

    print(f"\n📂 Reading: {args.csv}")
    rows = load_csv(args.csv)

    if not rows:
        print("[ERROR] No valid GPS rows found in CSV.")
        sys.exit(1)

    print(f"🗺️  Plotting {len(rows)} waypoints...")
    build_map(rows, args.output)


if __name__ == "__main__":
    main()
