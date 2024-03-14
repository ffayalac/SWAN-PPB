from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import scipy.io
import os

import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

from plot import *
import constants

# ------------ User changes --------------------- #

dic_sim_names={'madsen':'madsen','smith s2.65 d0.1':'smith_s2.65_d0.1',
               'smith s2.65 d0.78':'smith_s2.65_d0.78','smith s2.65 dvar':'smith_s2.65_dvar',
               'smith veg 1lyr Ncons':'smith_veg_1lyr_Ncons','smith s2.65 d0.01':'smith_s2.65_d0.01',
               'smith s2.65 d0.05':'smith_s2.65_d0.05','smith s2.75 d0.01':'smith_s2.75_d0.01'}

sim='madsen'
top_level_dir=f'/data/projects/punim1660/runs_swan/{dic_sim_names[sim]}'

#------------------- End of user changes --------------------------#

# Load data from files
bot = np.loadtxt(f'{top_level_dir}/in/SWAN.bot')
grid = np.loadtxt(f'{top_level_dir}/in/SWAN.grd')
dic_data=scipy.io.loadmat(f'{top_level_dir}/outputs/waveparam.mat')

lon_shoreline,lat_shoreline=getting_shoreline('/data/projects/punim1660/swan_ppb/ugrid/shorelines/PPB_BOUND.kml')

# Reshape the grid to a 2x200x100 matrix
grid_rec = grid.reshape((2,200, 100))
grid_rec[grid_rec == -9999] = np.nan     # Replace -9999 with NaN
xgrid = grid_rec[0,:, :]
ygrid = grid_rec[1,:, :]                                 

# Preprocessing data
plot_date = datetime(2021, 10, 29,1)
bot[bot == -9999] = np.nan     # Replace -9999 with NaN
# xp=dic_data['Xp']
# yp=dic_data['Yp']
hs=dic_data[f'Hsig_{plot_date.strftime("%Y%m%d_%H%M%S")}']

xgrid,ygrid=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,xgrid.ravel(),ygrid.ravel())
lon_shoreline,lat_shoreline=coordXform(constants.CRS_ORIGIN,constants.CRS_UTM55,lon_shoreline,lat_shoreline)
xgrid=xgrid.reshape(200,100)
ygrid=ygrid.reshape(200,100)
PPB_set=dict(xticks=(np.arange(2.6e5,3.41e5,20000).tolist()),xlim=(2.6e5,3.4e5),ylim=(5.74e6,5.82e6),
            yticks=(np.arange(5.74e6,5.83e6,20000).tolist()))  

os.system(f'mkdir -p {top_level_dir}/plots')

# Plotting .bot file
fig,ax=plt.subplots(1,1,figsize=(11,6),subplot_kw={'projection': constants.CRS_UTM55})
cf=ax.contourf(xgrid,ygrid,bot,levels=np.arange(0,70.5,5))
ax.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
ax.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
        yticks=PPB_set['yticks'])
ax.set_title('Bathymetry in PPB - SWAN')
ax.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
cax= fig.add_axes([ax.get_position().x1+0.02,ax.get_position().y0,0.01,ax.get_position().height])
cbar=plt.colorbar(cf,cax=cax,orientation="vertical")
cbar.set_label('Bathymetry [m]')
plt.savefig(f'{top_level_dir}/plots/bathymetry_SWAN.pdf',dpi=700,bbox_inches='tight',pad_inches=0.05)

# Plotting .grd file
fig,ax=plt.subplots(1,1,figsize=(11,6),subplot_kw={'projection': constants.CRS_UTM55})
ax.plot(xgrid,ygrid,c='firebrick',transform=constants.CRS_UTM55,lw=0.01)
ax.plot(np.transpose(xgrid),np.transpose(ygrid),c='firebrick',transform=constants.CRS_UTM55,lw=0.01)
ax.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
ax.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
        yticks=PPB_set['yticks'])
ax.set_title('Curvilinear grid for PPB - SWAN')
ax.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
plt.savefig(f'{top_level_dir}/plots/grid_SWAN.pdf',dpi=700,bbox_inches='tight',pad_inches=0.05)

# Plotting Hs file

# fig,ax=plt.subplots(1,1,figsize=(11,6),subplot_kw={'projection': constants.CRS_UTM55})
# cf=ax.contourf(xgrid,ygrid,hs)
# ax.plot(lon_shoreline,lat_shoreline,c='k',transform=constants.CRS_UTM55,label='Shoreline')
# ax.set(xlabel='East [m, GDA z55]',ylabel='North [m, GDA z55]',ylim=PPB_set['ylim'],xlim=PPB_set['xlim'],xticks=PPB_set['xticks'],
#         yticks=PPB_set['yticks'])
# ax.set_title(f'Hs in PPB - {plot_date.strftime("%Y-%m-%d %H:%M:%S")} ({sim})')
# ax.ticklabel_format(style='sci',scilimits=(0,0),axis='both',useMathText=True)
# cax= fig.add_axes([ax.get_position().x1+0.02,ax.get_position().y0,0.01,ax.get_position().height])
# cbar=plt.colorbar(cf,cax=cax,orientation="vertical")
# cbar.set_label('Hs [m]')
# plt.savefig(f'{top_level_dir}/plots/hs_SWAN_{dic_sim_names[sim]}_{plot_date.strftime("%y%m%d%H")}.pdf',dpi=700,bbox_inches='tight',pad_inches=0.05)

