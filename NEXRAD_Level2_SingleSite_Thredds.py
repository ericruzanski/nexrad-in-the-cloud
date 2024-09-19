from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.plots import colortables
import numpy as np
from pyproj import Proj
from siphon.catalog import TDSCatalog
import xarray as xr

def get_radar_file_url(datasets, date):
    rad_date_hour = date.strftime('%Y%m%d_%H')
    files, times = [], []
    for file in datasets:
        if rad_date_hour in file:
            times.append(datetime.strptime(file[-18:-5], '%Y%m%d_%H%M'))
            files.append(file)
    if not files:
        rad_date_hour = (date - timedelta(hours=1)).strftime('%Y%m%d_%H')
        for file in datasets:
            if rad_date_hour in file:
                times.append(datetime.strptime(file[-18:-5], '%Y%m%d_%H%M'))
                files.append(file)
    return list(datasets).index(files[np.argmin(np.abs(np.array(times) - date))])

# Fetch radar data
date = datetime.utcnow()
# Uncomment the next line and set a specific date/time to fetch radar data for a different time
# date = datetime(2024, 9, 1, 12, 0, 0)

station = 'KJAX'
cat = TDSCatalog(f'https://thredds.ucar.edu/thredds/catalog/nexrad/level2/{station}/{date:%Y%m%d}/catalog.html')
ds = xr.open_dataset(cat.datasets[get_radar_file_url(cat.datasets, date)].access_urls['OPENDAP'], decode_times=False)

# Extract data
slat, slon = ds.StationLatitude, ds.StationLongitude
rng, az, ref = ds.distanceR_HI.values, ds.azimuthR_HI.values[0], ds.Reflectivity_HI.values[0]
x, y = rng * np.sin(np.deg2rad(az))[:, None], rng * np.cos(np.deg2rad(az))[:, None]
lon, lat = Proj(f"+proj=stere +lat_0={slat} +lon_0={slon} +ellps=WGS84 +units=m")(x, y, inverse=True)

# Plot radar data
fig, ax = plt.subplots(figsize=(10, 9), subplot_kw=dict(projection=ccrs.PlateCarree()))
img = ax.pcolormesh(lon, lat, ref, vmin=-30, vmax=80, cmap=colortables.get_colortable('NWSStormClearReflectivity'))
plt.colorbar(img, aspect=50, pad=0.05)

# Set extent and add features
ax.set_extent([slon-2, slon+2, slat-2, slat+2], ccrs.PlateCarree())
ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_2_counties', '10m', facecolor='none'), edgecolor='gray')
ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='black')

# Finalize the map
plt.title(f'{ds.Station}: {ds.Reflectivity_HI.name}', loc='left')
plt.title(f'Valid: {datetime.strptime(ds.time_coverage_start, "%Y-%m-%dT%H:%M:%SZ")}', loc='right')

# Uncomment the next line to save the plot as a .png file instead of showing it
# plt.savefig(f'{station}_radar_reflectivity.png', dpi=300)
plt.show()