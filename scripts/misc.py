import numpy as np
from scipy.stats import pearsonr
from scipy.signal import find_peaks
from shapely.geometry.polygon import Polygon
import pandas as pd 

def metrics(measurements,model):

    MSE = np.sqrt(((measurements - model)**2).mean()) 
    RMSE = round(MSE,2)

    bias = np.sqrt(((measurements - np.mean(measurements))**2).mean()) -\
            np.sqrt(((model - np.mean(model))**2).mean())
    bias = round(bias,2)

    MBE = np.mean(measurements - model)
    MBE = round(MBE,2)

    corr, _ = pearsonr(measurements,model)
    corr=round(corr,2)

    return RMSE,MBE,corr

def z_score(intensity,threshold):

    mean_int = np.mean(intensity)
    std_int = np.std(intensity)
    z_scores = (intensity - mean_int) / std_int
    z_score_hs = np.array(abs(z_scores))
    idx_nan = np.where(z_score_hs>threshold)
    intensity_new=np.copy(intensity)
    intensity_new[idx_nan]=np.NaN
    return intensity_new

def remove_spikes(intensity):
    peaks, _ = find_peaks(intensity,threshold=(0.7,None), prominence=(0.6,None))
    intensity_new=np.copy(intensity)
    intensity_new[peaks]=np.NaN
    return intensity_new

def vertices_per_record(x):
    longitudes=x[0][2][0,:]
    latitudes=x[0][3][0,:]
    polygon = Polygon([(lon, lat) for lat, lon in zip(latitudes, longitudes)])
    return polygon    

def remove_nan_coordinates(polygon):
    clean_exterior = [coord for coord in polygon.exterior.coords if any(~np.isnan(x) for x in coord)]
    return Polygon(clean_exterior)

def closest_nodes(nodes,nodes_target,nbr_points):
    nodes = np.asarray(nodes)
    indx=np.empty((len(nodes_target),nbr_points),dtype=np.int)
    for idx,node in enumerate(nodes_target):
      dist_2 = np.sum((nodes - node)**2, axis=1)
      series=pd.Series(dist_2)
      series=series.sort_values(ascending=True)
      indx[idx,:]=series.index[:nbr_points]
    return indx