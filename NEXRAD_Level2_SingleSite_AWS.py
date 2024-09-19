from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.plots import colortables
import numpy as np
import boto3
import tempfile
import os
import re
import pyart
from botocore import UNSIGNED
from botocore.client import Config

def list_files(bucket_name, prefix):
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    files = []
    for page in page_iterator:
        if 'Contents' in page:
            for item in page['Contents']:
                files.append(item['Key'])
    return files

def get_datetime_from_filename(filename):
    # Use double curly braces {{}} to escape them in the format string
    match = re.match(r'^{}([0-9]{{8}})_([0-9]{{6}})_V06'.format(station), filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        datetime_str = date_str + time_str
        dt = datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
        return dt
    else:
        return None

def find_closest_file(files_times, desired_time):
    min_diff = timedelta.max
    closest_file = None
    for key, file_time in files_times:
        diff = abs(file_time - desired_time)
        if diff < min_diff:
            min_diff = diff
            closest_file = key
    return closest_file

def download_file(bucket_name, key):
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    tmp = tempfile.NamedTemporaryFile(delete=False)
    s3_client.download_fileobj(bucket_name, key, tmp)
    tmp.close()
    return tmp.name

# Set date and station
date = datetime.utcnow()
# Uncomment the next line and set a specific date/time to fetch radar data for a different time
# date = datetime(2023, 9, 1, 12, 0, 0)
station = 'KJAX'

# Access NEXRAD data on AWS S3
bucket_name = 'noaa-nexrad-level2'
prefix = f"{date:%Y/%m/%d}/{station}/"
files = list_files(bucket_name, prefix)

# Get list of files with their datetimes
files_times = []
for key in files:
    filename = os.path.basename(key)
    file_dt = get_datetime_from_filename(filename)
    if file_dt:
        files_times.append((key, file_dt))

# Find the closest file to the desired date
closest_file_key = find_closest_file(files_times, date)
if not closest_file_key:
    # Try the previous day if no files are found
    date = date - timedelta(days=1)
    prefix = f"{date:%Y/%m/%d}/{station}/"
    files = list_files(bucket_name, prefix)
    files_times = []
    for key in files:
        filename = os.path.basename(key)
        file_dt = get_datetime_from_filename(filename)
        if file_dt:
            files_times.append((key, file_dt))
    closest_file_key = find_closest_file(files_times, date)
    if not closest_file_key:
        raise ValueError("No radar files found for the specified date and station.")

# Download the radar file
file_path = download_file(bucket_name, closest_file_key)

# Read the radar data
radar = pyart.io.read_nexrad_archive(file_path)

# Choose a sweep (e.g., lowest elevation angle)
sweep = 0

# Extract data
ref = radar.get_field(sweep, 'reflectivity')

# Get gate latitude and longitude
gate_lats, gate_lons, gate_alts = radar.get_gate_lat_lon_alt(sweep)

# Plot radar data
fig, ax = plt.subplots(figsize=(10, 9), subplot_kw=dict(projection=ccrs.PlateCarree()))

# Plot the data
cmap = colortables.get_colortable('NWSStormClearReflectivity')
img = ax.pcolormesh(gate_lons, gate_lats, ref, cmap=cmap, vmin=-30, vmax=80)

# Add colorbar
plt.colorbar(img, ax=ax, orientation='vertical', pad=0.01, aspect=50)

# Add map features
ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_2_counties', '10m', facecolor='none'),
               edgecolor='gray')
ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black')

# Set extent
slat = radar.latitude['data'][0]
slon = radar.longitude['data'][0]
ax.set_extent([slon - 2, slon + 2, slat - 2, slat + 2], ccrs.PlateCarree())

# Finalize the map
start_time = radar.time['units'].split(' ')[-1]
start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')

plt.title(f'{radar.metadata["instrument_name"]}: Reflectivity', loc='left')
plt.title(f'Valid: {start_dt}', loc='right')

# Uncomment the next line to save the plot as a .png file instead of showing it
# plt.savefig(f'{station}_radar_reflectivity.png', dpi=300)
plt.show()

# Clean up the temporary file
os.remove(file_path)