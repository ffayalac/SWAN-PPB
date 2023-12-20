import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime,timedelta
import itertools

import warnings
warnings.filterwarnings("ignore")

from plot import *
from misc import *
import constants

lon_shoreline,lat_shoreline=getting_shoreline('/data/projects/punim1660/swan_ppb/ugrid/shorelines/PPB_BOUND.kml')

# Reading wind data
ds = xr.load_dataset('/data/projects/punim1660/swan_ppb/wind_data/era5_download/era5_20130510.nc')
lon = ds.longitude.values
lat = ds.latitude.values

lat_new_res=np.arange(lat[0],lat[-1]-0.25/10,-0.25/10)
lon_new_res=np.arange(lon[0],lon[-1],0.25/10)

u10,v10 = ds.u10.values, ds.v10.values
msl = ds.msl.values
time = pd.DatetimeIndex(ds.time.values)
start_period = datetime(1990, 1, 1)
end_period = datetime(2020, 12, 31)

lat_mt=np.array([-38.1872])
lon_mt=np.array([145.0920])

lat_mt_station=np.array([-38.16272])
lon_mt_station=np.array([145.05418])

PPB_set=dict(xticks=(np.arange(2.6e5,3.81e5,20000).tolist()),xlim=(2.6e5,3.8e5),ylim=(5.70e6,5.82e6),
            yticks=(np.arange(5.70e6,5.83e6,20000).tolist()))  
PPB_WP_set=dict(xticks=(np.arange(2.6e5,3.81e5,20000).tolist()),xlim=(2.6e5,3.8e5),ylim=(5.72e6,5.82e6),
            yticks=(np.arange(5.72e6,5.83e6,20000).tolist()))  

lon,lat=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon,lat)
lon_new_res,lat_new_res=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_new_res,lat_new_res)
lon_shoreline,lat_shoreline=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_shoreline,lat_shoreline)
lon_mt,lat_mt=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_mt,lat_mt)
lon_mt_station,lat_mt_station=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_mt_station,lat_mt_station)

nodes_target=np.array(list(zip(lon_mt_station,lat_mt_station)))
nodes=np.array(list(itertools.product(lon,lat)))
five_ngbrs=closest_nodes(nodes,nodes_target,5)[0]
lon_black_pt,lat_black_pt=nodes[five_ngbrs[0]][0],nodes[five_ngbrs[0]][1]
lon_pink_pt,lat_pink_pt=nodes[np.append(five_ngbrs[1:3],five_ngbrs[-1])][:,0],nodes[np.append(five_ngbrs[1:3],five_ngbrs[-1])][:,1]

idx_lon_black_pt=np.where(lon==lon_black_pt)
idx_lat_black_pt=np.where(lat==lat_black_pt)
u_serie_black_point=u10[:,idx_lon_black_pt,idx_lat_black_pt].ravel()
v_serie_black_point=v10[:,idx_lon_black_pt,idx_lat_black_pt].ravel()
ws_serie_black_point=np.sqrt((u_serie_black_point**2)+(v_serie_black_point**2))

labels=['upper left','lower right','lower left']
fig,ax=plt.subplots(1,1,figsize=(12,4))
ax.plot(time[2000:2250],ws_serie_black_point[2000:2250],c='k',label='black point')

i=0
for lon_pt,lat_pt in zip(lon_pink_pt,lat_pink_pt):
    idx_lon_pt=np.where(lon==lon_pt)
    idx_lat_pt=np.where(lat==lat_pt)
    u_serie_point=u10[:,idx_lon_pt,idx_lat_pt].ravel()
    v_serie_point=v10[:,idx_lon_pt,idx_lat_pt].ravel()
    ws_serie_point=np.sqrt((u_serie_point**2)+(v_serie_point**2))
    ax.plot(time[2000:2250],ws_serie_point[2000:2250,],label=labels[i])
    i+=1
ax.set(ylabel='wind speed [m/s]',xlabel='Date',title='Comparison of the closer points to Mt Eliza station')
ax.legend()
fig.savefig(f'/data/projects/punim1660/pre_pros_swan_PPB/plots/time_series_points.pdf',
            dpi=700,bbox_inches='tight',pad_inches=0.05)



fig,[ax1,ax2,ax3]=plt.subplots(1,3,figsize=(14,7),subplot_kw={'projection': constants.CRS_UTM55},sharey=True)
fig,ax1=plt.subplots(1,1,figsize=(6,6),subplot_kw={'projection': constants.CRS_UTM55},sharey=True)
ax.set_title(f'ERA5 grid and Mt Eliza station locations on {time[200]}',y=0.8)

# U10 component plot
ax1.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
        yticks=PPB_set['yticks'])
ax1.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
lon,lat=np.meshgrid(lon,lat)
lon_new_res,lat_new_res=np.meshgrid(lon_new_res,lat_new_res)

ax1.plot(lon,lat,c='firebrick',transform=constants.CRS_UTM55,label='ERA5 grid')
ax1.plot(np.transpose(lon),np.transpose(lat),c='firebrick',transform=constants.CRS_UTM55,label='')
cf1=ax1.contourf(lon,lat,u10[200,:,:])
ax1.scatter(lon_mt_station,lat_mt_station,s=5,marker='*',c='darkgreen',label="Mt Eliza station")
ax1.scatter(lon_new_res,lat_new_res,s=0.2,c='darkorange',transform=constants.CRS_UTM55,label='ERA5 redef. grid',zorder=3)
ax1.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
ax1.scatter(lon,lat,c='firebrick')
ax1.scatter(lon_black_pt,lat_black_pt,s=40,c='k')
ax1.scatter(lon_pink_pt,lat_pink_pt,s=40,c='pink')

cax= fig.add_axes([ax1.get_position().x0,ax1.get_position().y0-0.13,
                   ax1.get_position().width,0.02])
cbar=plt.colorbar(cf1,cax=cax,orientation="horizontal")
cbar.set_label('u10 component [m/s]')
legend_without_duplicate_labels(ax1)

fig.savefig(f'/data/projects/punim1660/pre_pros_swan_PPB/plots/maps/grid_redefined.pdf',
            dpi=700,bbox_inches='tight',pad_inches=0.05)

# V10 component plot
# ax2.set(xlabel='East [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'])
# ax2.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
# ax2.plot(lon,lat,c='firebrick',transform=constants.CRS_UTM55,label='ERA5 grid')
# ax2.plot(np.transpose(lon),np.transpose(lat),c='firebrick',transform=constants.CRS_UTM55,label='')
# cf2=ax2.contourf(lon,lat,v10[200,:,:])
# ax2.scatter(lon_mt_station,lat_mt_station,s=40,marker='*',c='darkgreen',label="Mt Eliza station")
# ax2.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
# ax2.scatter(lon,lat,c='firebrick')
# cax2= fig.add_axes([ax2.get_position().x0,ax2.get_position().y0-0.13,
#                    ax2.get_position().width,0.02])
# cbar2=plt.colorbar(cf2,cax=cax2,orientation="horizontal")
# cbar2.set_label('v10 component [m/s]')

# # MSP plot
# ax3.set(xlabel='East [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'])
# ax3.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
# ax3.plot(lon,lat,c='firebrick',transform=constants.CRS_UTM55,label='ERA5 grid')
# ax3.plot(np.transpose(lon),np.transpose(lat),c='firebrick',transform=constants.CRS_UTM55,label='')
# cf3=ax3.contourf(lon,lat,msl[200,:,:],cmap='hot_r')
# ax3.scatter(lon,lat,c='firebrick')
# ax3.scatter(lon_black_pt,lat_black_pt,s=40,c='k')
# ax3.scatter(lon_pink_pt,lat_pink_pt,s=40,c='pink')
# ax3.scatter(lon_mt_station,lat_mt_station,s=5,marker='*',c='darkgreen',label="Mt Eliza station")
# ax3.scatter(lon_new_res,lat_new_res,s=0.2,c='navy',transform=constants.CRS_UTM55,label='ERA5 grid down',zorder=3)

# ax3.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
# cax3= fig.add_axes([ax3.get_position().x1+0.02,ax3.get_position().y0,
#                    0.01,ax3.get_position().height])
# cbar3=plt.colorbar(cf3,cax=cax3,orientation="vertical")
# cbar3.set_label('Mean sea level pressure [Pa]')
# fig.savefig(f'/data/projects/punim1660/scripts_PPB/era5_grid_mt_eliza.pdf',
#             dpi=700,bbox_inches='tight',pad_inches=0.05)
# plt.show()


