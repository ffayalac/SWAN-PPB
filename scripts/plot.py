import matplotlib as mpl
import matplotlib.pyplot as plt
from pykml import parser
import numpy as np


mpl.font_manager.fontManager.addfont('/home/fayalacruz/runs/Helvetica.ttf')
mpl.font_manager.fontManager.addfont('/home/fayalacruz/runs/Helvetica-Light.ttf')
mpl.font_manager.fontManager.addfont('/home/fayalacruz/runs/Helvetica-Bold.ttf')

newparams = {'axes.grid': False,
             'lines.linewidth': 1.5,
             'ytick.labelsize':12,
             'xtick.labelsize':12,
             'axes.labelsize':12,
             'axes.titlesize':13,
             'legend.fontsize':12,
             'figure.titlesize':15,
             'font.family':'Helvetica Light'}
plt.rcParams.update(newparams)

def coordXform(orig_crs, target_crs, x, y):
    """
    Converts array of (y,x) from orig_crs -> target_crs
    y, x: numpy array of float values
    orig_crs: source CRS
    target_crs: target CRS
    """

    # original code is one-liner
    # it leaves an open axes that need to plt.close() later
    # return plt.axes( projection = target_crs ).projection.transform_points( orig_crs, x, y )

    # new improved code follows
    xys = plt.axes( projection = target_crs ).projection.transform_points(orig_crs, x, y)
    plt.close()         # Kill GeoAxes
    lon_new=xys[:,0]
    lat_new=xys[:,1]
    return lon_new,lat_new

def coordXform_new(orig_crs, target_crs, x):
   a=target_crs.transform_points( orig_crs, x )
   # print(a)
   lon,lat,depth=a[:,0],a[:,1],a[:,2]
   return lon,lat

def getting_shoreline(path_shoreline):
    with open(path_shoreline, 'r') as f:
        root = parser.parse(f).getroot()
        namespace = {"kml": 'http://www.opengis.net/kml/2.2'}
        pms = root.xpath(".//kml:Placemark[.//kml:Polygon]", namespaces=namespace)
        for p in pms:
            a=p.Polygon.outerBoundaryIs.LinearRing.coordinates

        list_a=str(a).split(',')
        len_list=int((len(list_a)-1)/2)

        lon_shoreline=np.empty((len_list))
        lat_shoreline=np.empty((len_list))
        for idx,element in enumerate(list_a[:-1]):
            if idx%2:
                lat_shoreline[int(idx/2)]=float(element)
            else:
                lon_shoreline[int(idx/2)]=np.sum([float(x) for x in element.split(' ')])
    return lon_shoreline,lat_shoreline

def horizontal_colorbar(fig,axes,cf,pad,width,label,join):
        if join==1:
                cax= fig.add_axes([axes[0].get_position().x0,axes[0].get_position().y0-pad,
                                                axes[0].get_position().width,width])
        elif join ==2:
                cax= fig.add_axes([axes[0].get_position().x0,axes[0].get_position().y0-pad,
                                                axes[0].get_position().width+1.4*axes[1].get_position().width,width])

        cbar=plt.colorbar(cf,cax=cax,orientation="horizontal")
        cbar.set_label(label)
        return cbar

def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))