import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Related with Geopandas 
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry import Point

import warnings
warnings.filterwarnings("ignore")

from plot import *
from misc import *
from data import *
import constants

# Loading habitat map data
dic_data=scipy.io.loadmat('/data/projects/punim1660/swan_ppb/survey_data/ppb_habitats.mat',struct_as_record=True)['data']
field_names = dic_data.dtype.names
top_level_dir='/data/projects/punim1660/pre_pros_swan_PPB/'

# Loading the shoreline
lon_shoreline_deg,lat_shoreline_deg=getting_shoreline('/data/projects/punim1660/swan_ppb/ugrid/shorelines/PPB_BOUND.kml')
lon_shoreline_m,lat_shoreline_m=coordXform(constants.CRS_ORIGIN,constants.CRS_VICGRID94,lon_shoreline_deg,lat_shoreline_deg)

# Creating ds con geometries for each polygon
data=np.array([[column[0] for column in register if column.ndim<=1] for register in dic_data[:,0]])
columns_names=np.array([b for a,b in zip(dic_data[0,0],field_names) if a.ndim<=1])
polygons=np.array(list(map(vertices_per_record,dic_data[:])))
geometry = gpd.GeoSeries(polygons)
dict_geo={'geometry':geometry}

for index,key in enumerate(columns_names):
    dict_geo[key]=data[:,index]

gdf = gpd.GeoDataFrame(dict_geo)

unique_sed_types=gdf['bc_title3'].unique()
# spec_gravity=np.ones(len(unique_sed_types))*2.65  # constant
spec_gravity=[2.65,2.65,2.65,2.65,2.77,2.65,2.77,2.77,2.65,2.7,2.65,2.7,2.65,2.65,2.77,2.65] # variable
category_colors = {-999: 'red',2.65: 'blue',2.7: 'green',2.77: 'orange'}
# Bassalt: 2.77
# Mud: It can be evrything but (22-23ppg)
dic_spec_gravity={key:value for key,value in zip (unique_sed_types,spec_gravity)}

gdf['sg']=gdf.apply(lambda x: dic_spec_gravity[x['bc_title3']],axis=1)

# Creating dataframe with points
def computing_geodfs(dx,dy,ini_x,ini_y,end_x,end_y):
  # Creating a regular grid
  x_grid = np.arange(ini_x, end_x+0.001, dx)
  y_grid = np.arange(ini_y, end_y+0.001, dy)
  X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
  points = np.vstack([X_grid.ravel(), Y_grid.ravel()]).T

  # Creating Points for the sediment information and regular grid
  points_reg_grid=[Point(point_coord) for point_coord in points]

  # Creating GeoDataFrames for the Points
  df_points_reg_grid=gpd.GeoDataFrame(geometry=points_reg_grid)

  return x_grid,y_grid,df_points_reg_grid

# Definition of grid parameters
start_x_deg,start_y_deg=144.3,-38.4
end_x_deg,end_y_deg=145.2,-37.8
dx_deg,dy_deg=0.01,0.01

x_grid,y_grid,df_points_reg_grid=computing_geodfs(dx=dx_deg ,dy=dy_deg,ini_x=start_x_deg,ini_y=start_y_deg,end_x=end_x_deg,end_y=end_y_deg)
# Change the reference system
x_grid_deg,y_grid_deg=df_points_reg_grid['geometry'].x,df_points_reg_grid['geometry'].y
x_grid_vicgrid,y_grid_vicgrid=coordXform(constants.CRS_ORIGIN,constants.CRS_VICGRID94,x_grid_deg,y_grid_deg)

# Creating Points for the sediment information and regular grid
points_vicgrid=[Point(xy) for xy in zip(x_grid_vicgrid,y_grid_vicgrid)]
df_points_reg_grid['geometry']=points_vicgrid

# Intersect the values to points dataset
# Perform a spatial join
joined = gpd.sjoin(df_points_reg_grid, gdf, how="left", op="within")
joined_depured=joined[['geometry','Geometry','bc_title3','sg']]
joined_depured['sg'] = joined_depured['sg'].fillna(value=-999)
joined_depured = joined_depured.drop_duplicates()

# Apply the function to remove NaN coordinates from each polygon
# gdf['geometry'] = gdf['geometry'].apply(remove_nan_coordinates)
# gdf2 = gdf.dissolve(by='bc_title3')

# pt=gdf.plot(ax=ax,column="bc_title3",cmap='tab20',categorical=True,legend=True)
# fig.savefig('bottom_PPB.png',dpi=400)  

if dx_deg<0.05:
   markersize=4
else:
   markersize=12

PPB_set=dict(xticks=(np.arange(2.4342e6,2.5243e6,20000).tolist()),xlim=(2.4342e6,2.5242e6),ylim=(2.342e6,2.412e6),
            yticks=(np.arange(2.342e6,2.403e6,20000).tolist()))  

lon_ini_point,lat_ini_point=144.3,-38.4
lon_end_point,lat_end_point=145.2,-37.8

# Setting up the plot
fig, [ax1,ax2] =plt.subplots(1,2,figsize=(12,6),sharey=True,subplot_kw={'projection': constants.CRS_VICGRID94})

# Left plot (overlapped points)
pt=gdf.plot(ax=ax1,column="bc_title3",cmap='tab20',categorical=True,edgecolor='none')
cf=df_points_reg_grid.plot(ax=ax1,markersize=markersize)
ax1.set(xlabel='East [m, VICGRID94]',ylabel='North [m, VICGRID94]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
          yticks=PPB_set['yticks'])
ax1.plot(lon_shoreline_m,lat_shoreline_m,c='k')
ax1.plot(lon_ini_point,lat_ini_point,'ok',transform=constants.CRS_ORIGIN)
ax1.plot(lon_end_point,lat_end_point,'ok',transform=constants.CRS_ORIGIN)
cax1= fig.add_axes([ax1.get_position().x1+0.55,ax1.get_position().y0,0.01,ax1.get_position().height])
cmap = plt.get_cmap('tab20',16)
cbar=plt.colorbar(mpl.cm.ScalarMappable(cmap=cmap),cax=cax1,orientation="vertical",ticks=np.arange(1/32,1,1/16))
cbar.set_ticklabels(np.sort(gdf['bc_title3'].unique()))
ax1.set_title('Port Phillip Bay (PPB) habitat types')

# Right plot (interpolated points)
# Convert categories to colors
colors = [category_colors[category] for category in joined_depured['sg']]
cmap = plt.cm.colors.ListedColormap(list(category_colors.values()))
bounds = np.arange(0.5, 5, 1)  # Adjust boundaries based on the number of categories
norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
ax2.plot(lon_shoreline_m,lat_shoreline_m,c='k')
c2=joined_depured.plot(column='sg',ax=ax2,markersize=markersize,categorical=True,cmap=cmap)
cax2= fig.add_axes([ax2.get_position().x1+0.02,ax2.get_position().y0-0.19,0.01,ax1.get_position().height])
cbar=plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),cax=cax2,orientation="vertical",ticks=np.arange(1, 5))
cbar.set_ticklabels(list(category_colors.keys()))
cbar.set_label('SG')
ax2.set(xlabel='East [m, VICGRID94]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],yticks=PPB_set['yticks'])
ax2.set_title('Regular grid for specific gravity in PPB')

fig.savefig(f'{top_level_dir}/plots/maps/PPB_habitat_types_{dx_deg}_{dy_deg}.png',dpi=600,bbox_inches='tight',pad_inches=0.05)  

# Preparing output data
map_to_swan=joined_depured['sg'].values.reshape((len(y_grid),len(x_grid)))
map_to_swan=map_to_swan[::-1,:]
map_to_swan_str = np.where(map_to_swan == -999, str(-999), np.round(map_to_swan, 2))

# Exporting data to SWAN format
target_dir=f'{top_level_dir}out_data'
sg_to_swan(map_to_swan_str,target_dir,start_x_deg,end_x_deg,start_y_deg,end_y_deg,dx_deg,dy_deg)