#https://medium.com/mlearning-ai/i-plotted-hong-kong-maps-in-python-using-prettymaps-18df4b0866a5

# # For local execution (does not require installing the library):
# %load_ext autoreload
# %autoreload 2
import sys; sys.path.append('../')
# Prettymaps
from prettymaps import *
# # Vsketch
import vsketch
# OSMNX
import osmnx as ox
# Matplotlib-related
import matplotlib.font_manager as fm
from matplotlib import pyplot as plt
from descartes import PolygonPatch
# Shapely
from shapely.geometry import *
from shapely.affinity import *
from shapely.ops import unary_union

def een():
    # Init matplotlib figure
    fig, ax = plt.subplots(figsize = (12, 12), constrained_layout = True)

    backup = plot(
        # Address:
        'Praça Ferreira do Amaral, Macau',
        # Plot geometries in a circle of radius:
        radius = 1100,
        # Matplotlib axis
        ax = ax,
        # Which OpenStreetMap layers to plot and their parameters:
        layers = {
                # Perimeter (in this case, a circle)
                'perimeter': {},
                # Streets and their widths
                'streets': {
                    'width': {
                        'motorway': 5,
                        'trunk': 5,
                        'primary': 4.5,
                        'secondary': 4,
                        'tertiary': 3.5,
                        'residential': 3,
                        'service': 2,
                        'unclassified': 2,
                        'pedestrian': 2,
                        'footway': 1,
                    }
                },
                # Other layers:
                #   Specify a name (for example, 'building') and which OpenStreetMap tags to fetch
                'building': {'tags': {'building': True, 'landuse': 'construction'}, 'union': False},
                'water': {'tags': {'natural': ['water', 'bay']}},
                'green': {'tags': {'landuse': 'grass', 'natural': ['island', 'wood'], 'leisure': 'park'}},
                'forest': {'tags': {'landuse': 'forest'}},
                'parking': {'tags': {'amenity': 'parking', 'highway': 'pedestrian', 'man_made': 'pier'}}
            },
            # drawing_kwargs:
            #   Reference a name previously defined in the 'layers' argument and specify matplotlib parameters to draw it
            drawing_kwargs = {
                'background': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'hatch': 'ooo...', 'zorder': -1},
                'perimeter': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'lw': 0, 'hatch': 'ooo...',  'zorder': 0},
                'green': {'fc': '#D0F1BF', 'ec': '#2F3737', 'lw': 1, 'zorder': 1},
                'forest': {'fc': '#64B96A', 'ec': '#2F3737', 'lw': 1, 'zorder': 1},
                'water': {'fc': '#a1e3ff', 'ec': '#2F3737', 'hatch': 'ooo...', 'hatch_c': '#85c9e6', 'lw': 1, 'zorder': 2},
                'parking': {'fc': '#F2F4CB', 'ec': '#2F3737', 'lw': 1, 'zorder': 3},
                'streets': {'fc': '#2F3737', 'ec': '#475657', 'alpha': 1, 'lw': 0, 'zorder': 3},
                'building': {'palette': ['#FFC857', '#E9724C', '#C5283D'], 'ec': '#2F3737', 'lw': .5, 'zorder': 4},
            }
    )

def twee():

    fig, ax = plt.subplots(figsize = (20, 20), constrained_layout = True)
    palette = ['#28536B','#A69CAC','#D2E59E']
    dilate = 0
    background_c = '#F2F4CB'
    layers = plot(
    #Centre the map center at   
    (22.2890,114.1701),
    #Set radius for the map
    radius = 2500,
    ax=ax,
    #Name and select the various layers we want on the map
    #We want a square map so ensure that we're not querying for data in a circle
    layers = {
        #we want a square layout, so 
        'perimeter': {},
                'streets': {
                    'width': {
                        'motorway': 5,
                        'trunk': 5,
                        'primary': 4.5,
                        'secondary': 4,
                        'tertiary': 3.5,
                        'cycleway': 3.5,
                        'residential': 3,
                        'service': 2,
                        'unclassified': 2,
                        'pedestrian': 2,
                        'footway': 1,
                    },
                    'circle': False, 'dilate': dilate
                },
                'building': {'tags': {'building': True, 'landuse': 'construction'}, 'union': True, 'circle': False, 'dilate': dilate},
                'water': {
                    'tags':{
                        'waterway': True,
                        'water': True,
                        'harbour': True,
                        'marina': True,
                        'bay': True,
                        'river': True
                    }, 
                    'circle': False, 'dilate': dilate
                },
                'forest': {'tags': {'landuse': 'forest'}, 'circle': False, 'dilate': dilate},
                'green': {'tags': {'landuse': ['grass', 'orchard'], 'natural': ['island', 'wood'], 'leisure': 'park'}, 'circle': False, 'dilate': dilate},
                'beach': {'tags': {'natural': 'beach'}, 'circle': False, 'dilate': dilate},
                'parking': {'tags': {'amenity': 'parking', 'highway': 'pedestrian', 'man_made': 'pier'}, 'circle': False}
            },
            drawing_kwargs = {
                'perimeter': {'fill': False, 'lw': 0, 'zorder': 0},
                'background': {'fc': background_c, 'zorder': -1},
                'green': {'fc': '#8BB174', 'ec': '#2F3737', 'hatch_c': '#A7C497', 'hatch': 'ooo...', 'lw': 1, 'zorder': 1},
                'forest': {'fc': '#64B96A', 'ec': '#2F3737', 'lw': 1, 'zorder': 2},
                'water': {'fc': '#a8e1e6', 'ec': '#2F3737', 'hatch_c': '#9bc3d4', 'hatch': 'ooo...', 'lw': 1, 'zorder': 3},
                'beach': {'fc': '#FCE19C', 'ec': '#2F3737', 'hatch_c': '#d4d196', 'hatch': 'ooo...', 'lw': 1, 'zorder': 3},
                'parking': {'fc': background_c, 'ec': '#2F3737', 'lw': 1, 'zorder': 3},
                'streets': {'fc': '#2F3737', 'ec': '#475657', 'alpha': 1, 'lw': 0, 'zorder': 4},
                'building': {'palette': palette, 'ec': '#2F3737', 'lw': .5, 'zorder': 5},
                
            },

            osm_credit = {'color': '#2F3737'}
    )

    # Set bounds
    #xmin, ymin, xmax, ymax = layers['perimeter'].bounds
    #dx, dy = xmax-xmin, ymax-ymin
    #a = .2
    #ax.set_xlim(xmin+a*dx, xmax-a*dx)
    #ax.set_ylim(ymin+a*dy, ymax-a*dy)

    #ax.text(
    #xmax-.35*dx, ymax+.02*dy,
        #"Kowloon Peninsula & Hong Kong Island",
        #color = '#2F3737',
        #fontproperties = fm.FontProperties(fname = '../assets/Permanent_Marker/PermanentMarker-Regular.ttf', size = 20),
    #)

    #Export a copy
    plt.show()
    plt.savefig('hkandkl.png')

    #Trigger a browser download
    files.download('hkandkl.png')

twee()