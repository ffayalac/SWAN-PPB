from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import os

def buoy_data_slicing(f_csv,period,names):
    period = pd.to_datetime(period,format='%Y-%m-%d %H:%M:%S') # from period
    df = pd.read_csv(f_csv,header=None,names=names)

    times_buoy = df['timestamp'][1::].astype('int').astype("datetime64[s]") # convert Unix time to datetime 

    # # Find the closest indices in the csv file that match the 'period' required
    idxs = [abs((idx-times_buoy)).idxmin() for idx in period] # list comprehensive is used
    df = df.iloc [idxs[0]:idxs[1]]
    times_buoy =times_buoy[idxs[0]:idxs[1]]
    return df, times_buoy


def time_series_from_raw(tab_filepath,input_filepath,stations_all):
    headers = ['Hsig','Dir','Tm01','TPsmoo']
    org_ds=np.genfromtxt(tab_filepath,comments='%')    
    file = open(input_filepath, "r")
    for line in file:
        if line.startswith('COMPUTE'):
            final_line=line.split(' ')
            start_date=datetime.strptime(final_line[3],'%Y%m%d.%H%M%S')
            final_date=datetime.strptime(final_line[-1][:-2],'%Y%m%d.%H%M%S')
    sim_time_range=pd.date_range(start_date,final_date,freq='1H')
    filt_model_data=np.empty((11,len(sim_time_range),4))
    for i in range(11):
        filt_model_data[i,:,:]=np.reshape(org_ds[i::11,:],(1,len(sim_time_range),4))
    time_series_dict={key:pd.DataFrame(index=sim_time_range,data=filt_model_data[index,:,:],columns=headers) for index,key in enumerate(stations_all.keys())}
    return time_series_dict

def diameter_to_swan(map,target_dir,start_x_deg,end_x_deg,start_y_deg,end_y_deg,dx_deg,dy_deg):
    target_pathfile=f'{target_dir}/diameter_dist.txt'
    metadata_path=f'{target_dir}/metadata_diameter_dist.txt'
    # Save data to a txt file with space delimiter, aligned and with 3 decimal positions
    np.savetxt(target_pathfile, map, fmt='%6s', delimiter=' ')

    meshes_y=(end_y_deg-start_y_deg)/dy_deg
    meshes_x=(end_x_deg-start_x_deg)/dx_deg

    if os.path.isfile(f"metadata_diameter_dist.txt"):
        os.system(f"rm {metadata_path}")
    f = open(metadata_path, "a")
    f.write(f'start lon [deg]: {start_x_deg}, start lat [deg]: {start_y_deg} \n')
    f.write(f'dx [deg]: {dx_deg}, dy [deg]: {dy_deg} \n')
    f.write(f'meshes in lon: {round(meshes_x)}, meshes in lat: {round(meshes_y)}')
    f.close()

def sg_to_swan(map,target_dir,start_x_deg,end_x_deg,start_y_deg,end_y_deg,dx_deg,dy_deg):
    target_pathfile=f'{target_dir}/sg_dist.txt'
    metadata_path=f'{target_dir}/metadata_sg_dist.txt'
    # Save data to a txt file with space delimiter, aligned and with 3 decimal positions
    np.savetxt(target_pathfile, map, fmt='%6s', delimiter=' ')

    meshes_y=(end_y_deg-start_y_deg)/dy_deg
    meshes_x=(end_x_deg-start_x_deg)/dx_deg

    if os.path.isfile(f"metadata_sg_dist.txt"):
        os.system(f"rm {metadata_path}")
    f = open(metadata_path, "a")
    f.write(f'start lon [deg]: {start_x_deg}, start lat [deg]: {start_y_deg} \n')
    f.write(f'dx [deg]: {dx_deg}, dy [deg]: {dy_deg} \n')
    f.write(f'meshes in lon: {round(meshes_x)}, meshes in lat: {round(meshes_y)}')
    f.close()