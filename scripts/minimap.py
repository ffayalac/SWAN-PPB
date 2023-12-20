import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

from plot import *
import constants

# Settting up the data to plot
crs_origin = ccrs.PlateCarree() 
crs_target = ccrs.UTM('55','S',ccrs.Globe(ellipse='GRS80'))

stations_PPB = {'Rosebud':'1628','Eliza':'0278','Sandringham':'0715','Werribee':'0318','Indented Head':'1630',
                'Central PPB':'0605'}

markers_sts = {key:marker for key,marker in zip(stations_PPB.keys(),constants.MARKERS)}
colors_sts = {key:marker for key,marker in zip(stations_PPB.keys(),constants.COLOR_MARKERS)}

lon_shoreline,lat_shoreline=getting_shoreline('/data/projects/punim1660/swan_ppb/ugrid/shorelines/PPB_BOUND.kml')
lon_shoreline,lat_shoreline=coordXform(crs_origin,crs_target,lon_shoreline,lat_shoreline)

top_level_dir='/data/projects/punim1660/pre_pros_swan_PPB/plots/'

PPB_set=dict(xticks=(np.arange(2.6e5,3.41e5,20000).tolist()),xlim=(2.6e5,3.45e5),ylim=(5.73e6,5.82e6),
            yticks=(np.arange(5.74e6,5.83e6,20000).tolist()))  

# Setting up the figure
fig,ax=plt.subplots(1,1,figsize=(6,6),subplot_kw={'projection': crs_target})
ax.plot(lon_shoreline,lat_shoreline,c='k',linewidth=2,transform=crs_target,label='Shoreline')
ax.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'])

ax.set_facecolor('aliceblue')

for station, id in stations_PPB.items():
    f_csv = f'{constants.OB_DIR}/spot-{id}.csv'  # path of each station
    df = pd.read_csv(f_csv,header=None,names=constants.COLUMNS_SPOTTER)
    lat_point,lon_point=float(df['latitude'][100]),float(df['longitude'][100])
    ax.scatter(lon_point,lat_point,marker=markers_sts[station],s=170,color=colors_sts[station],edgecolor='black',transform=crs_origin)

plt.savefig(f'{top_level_dir}maps/coastline_miniature.png',dpi=1000,bbox_inches='tight',pad_inches=0)

