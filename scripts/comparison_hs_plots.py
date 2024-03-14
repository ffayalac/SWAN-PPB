from datetime import datetime,timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import math
import string
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

from plot import *
from misc import *
from data import *
import constants

# ------------ User changes --------------------- #

sim_to_compare1='madsen'
sim_to_compare2='smith s2.65 d0.1'

period = ['2021-10-1 00:00:00','2021-11-1 00:00:00']   
# period = ['2021-10-23 00:00:00','2021-11-1 00:00:00'] 

top_level_dic='/data/projects/punim1660/runs_swan/'
plots_dic='/data/projects/punim1660/pre_pros_swan_PPB/plots/'

dic_sim_names={'madsen':'madsen','smith s2.65 d0.1':'smith_s2.65_d0.1',
               'smith s2.65 d0.78':'smith_s2.65_d0.78','smith s2.65 dvar':'smith_s2.65_dvar',
               'smith veg 1lyr Ncons':'smith_veg_1lyr_Ncons','smith s2.65 d0.01':'smith_s2.65_d0.01',
               'smith s2.65 d0.05':'smith_s2.65_d0.05','smith s2.75 d0.01':'smith_s2.75_d0.01'}
colors_sim_names={'madsen':'violet','smith s2.65 d0.1':'darkcyan','smith s2.65 d0.78':'darkorange',
                  'smith s2.65 dvar':'firebrick','smith veg 1lyr Ncons':'g','smith s2.65 d0.01':'blue',
                  'smith s2.65 d0.05':'lightcoral','smith s2.75 d0.01':'darkgreen'}

stations_PPB = {'Rosebud':'1628','Eliza':'0278','Sandringham':'0715','Werribee':'0318','Indented Head':'1630',
                'Central PPB':'0605'}

# stations_PPB = {'Rosebud':'1628','Eliza':'0278'}

stations_all = {'Williamston':'DD','Geelong':'EE','Frankston':'FF','Hovel': 'GG','Portsea':'DD','Rosebud':'1628',
                'Eliza':'0278','Sandringham':'0715','Werribee':'0318','Indented Head':'1630',
                'Central PPB':'0605'}

markers_sts = {key:marker for key,marker in zip(stations_PPB.keys(),constants.MARKERS)}
colors_sts = {key:marker for key,marker in zip(stations_PPB.keys(),constants.COLOR_MARKERS)}  

xlims = [datetime(2021, 10, 1), datetime(2021, 11, 1)]

ts_to_compare1=time_series_from_raw(f'{top_level_dic}{dic_sim_names[sim_to_compare1]}/outputs/Stations.tab',
                                    f'{top_level_dic}{dic_sim_names[sim_to_compare1]}/swan_input_ppb.swn',stations_all)
ts_to_compare2=time_series_from_raw(f'{top_level_dic}{dic_sim_names[sim_to_compare2]}/outputs/Stations.tab',
                                    f'{top_level_dic}{dic_sim_names[sim_to_compare2]}/swan_input_ppb.swn',stations_all)


#------------------- End of user changes --------------------------#

def time_series(stations_PPB,period,ts_to_compare1,ts_to_compare2,presentation_mode):

    nmbr_plots=len(stations_PPB.keys())

    if presentation_mode:
        fig, axs = plt.subplots(int(nmbr_plots/2),2,figsize=(16,2*int(nmbr_plots/2)), constrained_layout=True,
                    sharex=True)
    else:
        fig, axs = plt.subplots(nmbr_plots,1,figsize=(8, 10), constrained_layout=True,sharex=True)
    i = -1
    for station, id in stations_PPB.items():
        i = i+1

        f_csv = f'{constants.OB_DIR}/spot-{id}.csv'  # path of each station
        df, times_buoy = buoy_data_slicing(f_csv,period,constants.COLUMNS_SPOTTER) # data and time of each station

        # getting hs data from each buoy
        hs_buoy =np.asarray(df['swh'].astype(float)) 
        # hs_buoy_removed = z_score(hs_buoy, 9) # removing based on sd
        hs_buoy_removed = remove_spikes(hs_buoy) # removing based on prominences

        if axs.ndim==1:
            if presentation_mode :
                ax=axs[i%2]
            else:
                ax=axs[i]
        else:
            ax=axs[i//2][i%2]

        ax.grid(color = 'grey', linestyle = '-.', linewidth = 0.3)    

        # modelled hs data to compare
        hs_to_compare1=ts_to_compare1[station]['Hsig']
        hs_to_compare2=ts_to_compare2[station]['Hsig']

        ax.plot(times_buoy,hs_buoy_removed,'-k', label='Buoy') # buoy data
        ax.plot(hs_to_compare1,colors_sim_names[sim_to_compare1], label=f'{sim_to_compare1}',linewidth=1.5) # model sim1 data
        ax.plot(hs_to_compare2,colors_sim_names[sim_to_compare2], label=f'{sim_to_compare2}',linewidth=1.5) # model sim2 data
        ax.scatter(times_buoy.iloc[-25],math.ceil(np.nanmax(hs_buoy_removed))-0.3,marker=markers_sts[station],color=colors_sts[station])

        new_yticks=np.arange(1,math.ceil(np.nanmax(hs_buoy_removed))+1,1)
        ax.set(xlim=xlims,ylim=(0,math.ceil(np.nanmax(hs_buoy_removed))),ylabel='$H_s$ [m]',yticks=new_yticks)

        # arranging the minor and major x locators
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.tick_params(which='minor', length=1, color='k',direction="in")
        ax.tick_params(which='major', length=3, color='k',direction="in")
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b-%d')) 
            
        ax.set_title(f'{station}: largest $H_s$: {round(np.nanmax(hs_to_compare1),2)}m ({sim_to_compare1}), {round(np.nanmax(hs_to_compare2),2)}m ({sim_to_compare2}), {round(np.nanmax(hs_buoy_removed),2)}m (Obs.)')

    ax.legend(loc="upper left",ncol=2)
    fig.tight_layout(pad=1, w_pad=1, h_pad=1.0)
    vert=lambda x: 'horz' if x==True else 'vert' 
    fig.savefig(f'{plots_dic}hs_series/{sim_to_compare1}_vs_{sim_to_compare2}_{vert(presentation_mode)}.png',dpi=800)

time_series(stations_PPB,period,ts_to_compare1,ts_to_compare2,False)
# time_series(stations_PPB,period,ts_to_compare1,ts_to_compare2,False)

def scatter_plot(stations_PPB,period,ts_to_compare1,ts_to_compare2,presentation_mode):

    if presentation_mode:
        fig, axs = plt.subplots(2,3,figsize=(10.5,7),constrained_layout=True,sharex=True,sharey=True)
    else:
        fig, axs = plt.subplots(3,2,figsize=(7,10.5),constrained_layout=True,sharex=True,sharey=True)

    i = -1

    for station, id in stations_PPB.items():
        i =i +1
        f_csv = '{}/spot-{}.csv'.format(constants.OB_DIR,id)

        df, times_buoy = buoy_data_slicing(f_csv,period,constants.COLUMNS_SPOTTER)
        hs_buoy =np.asarray (df['swh'].astype(float))
        # hs_buoy_removed = z_score(hs_buoy, 9) # removing based on sd
        hs_buoy_removed = remove_spikes(hs_buoy) # removing based on prominences

        times_buoy_s = times_buoy.astype(int) # model_time = pd.to_datetime(db.time.to_numpy(), utc=True, unit='s')
        times_model = ts_to_compare2[station]['Hsig'].index
        times_model=times_model[times_model.slice_indexer("2021-10-01 00:00:00", "2021-11-01 00:00:00")]
        times_model = times_model.astype(int)

        field_interp_hs = np.interp(times_model,times_buoy_s,hs_buoy_removed)

        hs_to_compare1=ts_to_compare1[station]["2021-10-01 00:00:00":"2021-11-01 00:00:00"]['Hsig']
        hs_to_compare2=ts_to_compare2[station]["2021-10-01 00:00:00":"2021-11-01 00:00:00"]['Hsig']
        
        if presentation_mode :
            ax=axs[i%2][i//2]
        else:
            ax=axs[i//2][i%2]

        ax.scatter(field_interp_hs,hs_to_compare1,s=35,color=colors_sim_names[sim_to_compare1],label=f'{sim_to_compare1}',alpha=0.5)
        ax.scatter(field_interp_hs,hs_to_compare2,s=35,color=colors_sim_names[sim_to_compare2],label=f'{sim_to_compare2}',alpha=0.5)
        ax.set(xlim=(-0.5,4),ylim=(-0.5,4),ylabel='Simulated $H_s$ [m]',xlabel='Observed $H_s$ [m]')
        ax.set_title(f'({string.ascii_lowercase[i]}) {station}')
        ax.plot(np.arange(-0.5,4.1,0.1),np.arange(-0.5,4.1,0.1),'--k')
        ax.scatter(-0.4,3.9,marker=markers_sts[station],color=colors_sts[station])

        if np.any(np.isnan(field_interp_hs)) == True:
            idx_nans=~np.isnan(field_interp_hs)
            field_interp_hs=field_interp_hs[idx_nans]
            hs_to_compare1=hs_to_compare1[idx_nans]
            hs_to_compare2=hs_to_compare2[idx_nans]

        RMSE_to_compare2,MBE_to_compare2,corr_to_compare2=metrics(field_interp_hs,hs_to_compare2)
        RMSE_to_compare1,MBE_to_compare1,corr_to_compare1=metrics(field_interp_hs,hs_to_compare1)
        ax.legend(loc='lower right')

        ax.text(-0.3, 3.2, 'Mean bias error=',fontsize=10)
        ax.text(1.3, 3.2, f'{MBE_to_compare1}',fontsize=10,color=colors_sim_names[sim_to_compare1])
        ax.text(1.85, 3.2, f'{MBE_to_compare2}',fontsize=10,color=colors_sim_names[sim_to_compare2])

        ax.text(-0.3, 2.9, 'Correlation=',fontsize=10)
        ax.text(0.85, 2.9, f'{corr_to_compare1}',fontsize=10,color=colors_sim_names[sim_to_compare1])
        ax.text(1.4, 2.9, f'{corr_to_compare2}',fontsize=10,color=colors_sim_names[sim_to_compare2])

        ax.text(-0.3, 2.6, 'RMSE=',fontsize=10)
        ax.text(0.4, 2.6, f'{RMSE_to_compare1}',fontsize=10,color=colors_sim_names[sim_to_compare1])
        ax.text(0.95, 2.6, f'{RMSE_to_compare2}',fontsize=10,color=colors_sim_names[sim_to_compare2])
                            
    fig.suptitle('Comparison of hourly simulated and observed $H_s$ \n at different buoy stations in Port Phillip Bay')
    vert=lambda x: 'horz' if x==True else 'vert' 
    fig.savefig(f'{plots_dic}scatter/{sim_to_compare1}_vs_{sim_to_compare2}_{vert(presentation_mode)}_sca.png',dpi=800)

# scatter_plot(stations_PPB,period,ts_to_compare1,ts_to_compare2,False)
scatter_plot(stations_PPB,period,ts_to_compare1,ts_to_compare2,False)
