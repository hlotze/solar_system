import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt


def get_data_from_csv(fn : str,
                      df : pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv('solar_system.csv', 
                     sep = ';',
                     dtype = { 'object' : str,
                               'diameter_in_km' : np.int32,
                               'mio_km_from_sun' : np.float64,
                               'color' : str } )

    speed_of_light = 299_792.458 # in km / sec
    df = df.assign(duration_for_light_from_sun = 
                   lambda x : pd.to_timedelta(x.mio_km_from_sun * 1_000_000 / speed_of_light, unit='s'))
    
    # drop the row for moon, as we only ned the planets
    df.drop(df[df['object'] == 'Moon'].index, inplace = True)
    
    # drop the ns to make is more readable --> [x days hh:mm:ss], 
    # by using np.rint, so the ns are round up to the next second
    df['duration_for_light_from_sun'] = [pd.to_timedelta(np.rint(x.total_seconds()), unit='s') 
                                         for x in df.duration_for_light_from_sun]
    # sort by diameter - descending
    df.sort_values('mio_km_from_sun', axis=0, ascending=True, ignore_index=True, inplace=True)
    return(df)

def gen_planets_as_circles(df: pd.DataFrame, e_factor: int) -> (np.array, np.array):
    # get the values for the objects' plt.Circle
    # and do some scaling so that it fits into a diagram
    vals = [ [obj,
              #                                               2: diameter -> radius, 1_000_000: km -> mio_km       
              df.loc[df.object == obj, 'diameter_in_km'].to_list()[0]/2 /1_000_000 * e_factor,
              df.loc[df.object == obj, 'mio_km_from_sun'].to_list()[0],
              df.loc[df.object == obj, 'color'].to_list()[0] ]
             for obj in df.object.to_list() ]
    circles = [ plt.Circle((val[2], 0), radius=val[1], color=val[3]) for val in vals ]
    return(circles, vals)

def gen_diagram(fig: plt.figure, ax: plt.axes, vals: np.array, df: pd.DataFrame, e_factor: int):
    # get the values for the objects' plt.Circle
    circles, vals = gen_planets_as_circles(df, e_factor)
    # the planets as Circles
    for p in circles[1:]:
        ax.add_patch(p)
    # the sun's surface in the diagram
    # is at (0,0) to get better relation 
    # with the distances
    ax.add_patch(plt.Circle((-1 * vals[0][1], 0), radius=vals[0][1], color=vals[0][3]))

    # get / define the sizing
    xmax = max([ float(x) for x in list(np.transpose(np.array(vals[1:]))[2]) ])
    plt.xlim(-200, xmax*1.05)
    plt.ylim(-xmax*1.05/10,xmax*1.05/10)

    # set aspect 'equal' to have circles - not elipses
    ax.set_aspect('equal', adjustable='box')

    # drop the diagram's frame
    ax.set(frame_on=False)

    # ticks for x-axis below
    # take the planets distance as ticks
    ticks = [ int(x) for x in 
                         [ float(x) for x in list(np.transpose(np.array(vals[1:]))[2]) ] 
                         if(x > 500) ] # drop the inner plannets' values as they to dense to display
    # add the distance value for Earth
    ticks.insert(0, 149) 

    # get the time values
    timelist = [ str(x).replace('0 days ', '').replace('00:', '') for x in df.duration_for_light_from_sun.to_list()[1:] ]
    from operator import itemgetter
    # take only Earth(2), Jupiter(4), Saturn(5), Uranus(6), Neptune(7), Pluto(8)
    got = itemgetter(2, 4, 5, 6, 7, 8)(timelist)
    # make labels from ticks and timelist
    names = df.object.to_list()[-5:]
    names.insert(0, 'Earth')
    label = [ "{}\n{}\n{}".format(km_, time_, name_) for km_, time_, name_ in 
              zip(
                      [ f'{x:,}'.replace(',', '.') for x in ticks ], # km_
                      got,                                           # time_
                      names                                          # name_
                 ) 
            ]
    plt.xticks(ticks=ticks,
               # add "." as separator
               labels=label,
               fontsize=8)
    plt.xlabel("\nMillion km to Sun\nlight's time traveling from Sun", fontsize=8)

    ax.set_yticks([])
    return()