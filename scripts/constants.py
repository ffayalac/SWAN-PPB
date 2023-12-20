import cartopy.crs as ccrs

MARKERS = ['*','D','o','s','X','P']
COLOR_MARKERS = ['purple','red','darkorange','green','blue','brown']
COLUMNS_SPOTTER =  ['timestamp',	'timestamp_gmt','spotter_id', 'spotter_name', 'payload_type', 
          'battery_voltage',	'solar_voltage',	'temperature',	'humidity',	'swh',
          'peak_period',	'mean_period',	'peak_direction',	'peak_directional_spread',	'mean_direction',
          'mean_directional_spread',	'latitude',	'longitude']
OB_DIR = '/data/projects/punim1660/data/vicwaves'
CRS_ORIGIN = ccrs.PlateCarree() 
CRS_UTM55 = ccrs.UTM('55','S',ccrs.Globe(ellipse='GRS80'))
CRS_VICGRID94= ccrs.LambertConformal(central_longitude=145.0,central_latitude=-37,false_easting=2500000,false_northing=2500000,
                                   standard_parallels=(-36,-38),globe=ccrs.Globe(ellipse='GRS80'))
