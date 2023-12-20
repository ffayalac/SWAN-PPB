import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import cmocean
import cmocean.cm as cmo
import numpy as np

# Related with Geopandas 
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from scipy.interpolate import griddata

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

from plot import *
from data import *
import constants

# Initial parameters
PPB_set=dict(xticks=(np.arange(2.6e5,3.41e5,20000).tolist()),xlim=(2.6e5,3.45e5),ylim=(5.74e6,5.82e6),
            yticks=(np.arange(5.74e6,5.83e6,20000).tolist()))  
top_level_dir='/data/projects/punim1660/pre_pros_swan_PPB/'
lon_shoreline_deg,lat_shoreline_deg=getting_shoreline('/data/projects/punim1660/swan_ppb/ugrid/shorelines/PPB_BOUND.kml')
sed_dist=pd.read_csv(f'{top_level_dir}sediment_lonlat.xyz',delimiter=',',names=['lon_deg','lat_deg','D(phi)'])

# Postprocessing uploaded data
lon_shoreline_m,lat_shoreline_m=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_shoreline_deg,lat_shoreline_deg)
lon,lat=sed_dist['lon_deg'],sed_dist['lat_deg']
sed_dist['lon_m'],sed_dist['lat_m']=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,sed_dist['lon_deg'],sed_dist['lat_deg'])
sed_dist['D(mm)'] = 2**(-1*sed_dist['D(phi)'])  # Converting to mm scale

def plot_grain_dist(top_level_dir,lon_shoreline,lat_shoreline,lon,lat,dataframe,scale_mm=True):
  # cmap=cmo.matter
  cmap=plt.cm.get_cmap('inferno_r')
  if scale_mm==False:
    colors=dataframe['D(phi)']
    pathfile=f'{top_level_dir}/plots/maps/sediment_distribution_phi.png'
    label_cbar='Grain size ($\phi$ scale)'
    mean=dataframe['D(phi)'].mean()
    title=f'Grain size distribution in PPB - mean = {round(mean,2)}'
  else:
    colors=dataframe['D(mm)']
    pathfile=f'{top_level_dir}/plots/maps/sediment_distribution_mm.png'
    label_cbar='Grain diameter size (mm)'
    mean=dataframe['D(mm)'].mean()
    title=f'Grain size distribution in PPB - mean = {round(mean,2)} mm'

  fig,ax=plt.subplots(1,1,figsize=(11,6),subplot_kw={'projection': constants.CRS_UTM55})
  scatter = plt.scatter(lon,lat, c=colors, cmap=cmap,s=0.5)
  ax.plot(lon_shoreline,lat_shoreline,c='k',label='Shoreline')
  ax.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
          yticks=PPB_set['yticks'])
  ax.set_title(title)
  ax.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
  cax= fig.add_axes([ax.get_position().x1+0.02,ax.get_position().y0,0.01,ax.get_position().height])
  cbar=plt.colorbar(scatter,cax=cax,orientation="vertical")
  cbar.set_label(label_cbar)
  plt.savefig(pathfile,dpi=700,bbox_inches='tight',pad_inches=0.05)

# plot_grain_dist(top_level_dir,lon_shoreline_m,lat_shoreline_m,sed_dist['lon_m'],sed_dist['lat_m'],sed_dist)
# plot_grain_dist(top_level_dir,lon_shoreline_m,lat_shoreline_m,sed_dist['lon_m'],sed_dist['lat_m'],sed_dist,scale_mm=False)

#Creating the polygons for PPB
list_vertices_deg=[(i,j) for i,j in zip(lon_shoreline_deg[500:1970],lat_shoreline_deg[500:1970])] # index denote PPB
ppb_polygon_deg = Polygon(list_vertices_deg)
ppb_polygon_geoserie_deg=gpd.GeoSeries(ppb_polygon_deg)

def computing_geodfs(sed_dist,dx,dy,ini_x=min(sed_dist['lon_deg']),ini_y=min(sed_dist['lat_deg']),
                     end_x=max(sed_dist['lon_deg']),end_y=max(sed_dist['lat_deg'])):
  # Creating a regular grid
  x_grid = np.arange(ini_x, end_x+0.001, dx)
  y_grid = np.arange(ini_y, end_y+0.001, dy)
  X_grid, Y_grid = np.meshgrid(x_grid, y_grid)

  # Perform interpolation to estimate Z values on the regular grid
  Z_grid = griddata((sed_dist['lon_deg'], sed_dist['lat_deg']), sed_dist['D(mm)'], (X_grid, Y_grid), method='nearest')
  points = np.vstack([X_grid.ravel(), Y_grid.ravel()]).T

  # Creating Points for the sediment information and regular grid
  points_seds=[Point(xy) for xy in zip(sed_dist['lon_m'][::20],sed_dist['lat_m'][::20])]
  points_reg_grid=[Point(point_coord) for point_coord in points]

  # Creating GeoDataFrames for the Points
  df_points_seds=gpd.GeoDataFrame(sed_dist['D(mm)'][::20], geometry=points_seds)
  df_points_reg_grid=gpd.GeoDataFrame(data=Z_grid.ravel(),columns=['D(mm)'], geometry=points_reg_grid)

  df_points_reg_grid['in_out']=df_points_reg_grid.within(ppb_polygon_deg)
  df_points_reg_grid['corr_D(mm)']=df_points_reg_grid.apply(lambda x: x['D(mm)'] if x['in_out']==True else -9999,axis=1)

  map_to_swan=df_points_reg_grid['corr_D(mm)'].values.reshape((len(y_grid),len(x_grid)))
  
  return X_grid,Y_grid,df_points_seds,df_points_reg_grid,map_to_swan

# Definition of grid parameters
start_x_deg,start_y_deg=144.3,-38.4
end_x_deg,end_y_deg=145.2,-37.8
dx_deg,dy_deg=0.1,0.1

X_grid_deg,Y_grid_deg,df_points_seds,df_points_reg_grid,map_to_swan=computing_geodfs(sed_dist,dx=dx_deg ,dy=dy_deg,
                                                                                     ini_x=start_x_deg,ini_y=start_y_deg,
                                                                                     end_x=end_x_deg,end_y=end_y_deg)

lon_ini_point,lat_ini_point=144.3,-38.4
lon_end_point,lat_end_point=145.2,-37.8

# Plot with diameter interpolation process
fig,[ax1,ax2]=plt.subplots(1,2,figsize=(12,6),sharey=True,subplot_kw={'projection': constants.CRS_UTM55})

if dx_deg<0.05:
   markersize=4
else:
   markersize=12

# First plot (left plot with targeted points)
ppb_polygon_geoserie_deg.plot(ax=ax1,color='white',edgecolor='k',transform=constants.CRS_ORIGIN)
df_points_seds.plot(column='D(mm)',ax=ax1,markersize=1,cmap='inferno_r')
scatter_palette = {True: 'darkcyan', False: 'firebrick'}
cmap = matplotlib.colors.ListedColormap([scatter_palette[b] for b in df_points_reg_grid['in_out'].unique()])
df_points_reg_grid.plot(column='in_out',ax=ax1,markersize=markersize,legend=True,categorical=True,cmap=cmap,transform=constants.CRS_ORIGIN)
ax1.plot(lon_ini_point,lat_ini_point,'ok',transform=constants.CRS_ORIGIN)
ax1.plot(lon_end_point,lat_end_point,'ok',transform=constants.CRS_ORIGIN)
ax1.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
ax1.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
          yticks=PPB_set['yticks'])
sm = plt.cm.ScalarMappable(cmap='inferno_r', norm=plt.Normalize(vmin=sed_dist['D(mm)'].min(), vmax=sed_dist['D(mm)'].max()))
sm._A = []
cax1= fig.add_axes([ax1.get_position().x1-0.0001,ax1.get_position().y0,0.01,ax1.get_position().height])
cbar=plt.colorbar(sm,cax=cax1,orientation="vertical")
cbar.set_label('Grain diameter size (mm)')

# Second plot (right plot with interpolated points)
ppb_polygon_geoserie_deg.plot(ax=ax2,color='white',edgecolor='k',transform=constants.CRS_ORIGIN)
cf=df_points_reg_grid.plot(column='corr_D(mm)',ax=ax2,markersize=markersize,cmap='inferno_r',
                           vmin=df_points_reg_grid['corr_D(mm)'][df_points_reg_grid['corr_D(mm)']!=-9999].min(),
                           transform=constants.CRS_ORIGIN)
ax2.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
ax2.set(xlabel='East [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
          yticks=PPB_set['yticks'])
sm = plt.cm.ScalarMappable(cmap='inferno_r', norm=plt.Normalize(vmin=df_points_reg_grid['corr_D(mm)'][df_points_reg_grid['corr_D(mm)']!=-9999].min(),
                                                                 vmax=df_points_reg_grid['corr_D(mm)'].max()))
sm._A = []
cax2= fig.add_axes([ax2.get_position().x1+0.02,ax2.get_position().y0,0.01,ax2.get_position().height])
cbar=plt.colorbar(sm,cax=cax2,orientation="vertical",extend='min')
cbar.set_label('Grain diameter size (mm)')
fig.suptitle('Regular grid interpolated from grain size distribution in PPB',y=0.9)
pathfile_plot=f'{top_level_dir}/plots/maps/reg_grid_grain_size_{dx_deg}_{dy_deg}.png'
plt.subplots_adjust(wspace=0.4)
plt.savefig(pathfile_plot,dpi=700,bbox_inches='tight',pad_inches=0.05)

map_to_swan=map_to_swan[::-1,:]
map_to_swan_str = np.where(map_to_swan == -9999, str(-9999), np.round(map_to_swan, 3))

# Exporting data to SWAN format
target_dir=f'{top_level_dir}/out_data'
diameter_to_swan(map_to_swan_str,target_dir,start_x_deg,end_x_deg,start_y_deg,end_y_deg,dx_deg,dy_deg)