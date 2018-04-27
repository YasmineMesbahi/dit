# from add_vect_cds import *
# from neo4j.v1 import GraphDatabase, basic_auth

import pickle
import sys
from bokeh.models.mappers import LinearColorMapper
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, Div
import matplotlib.pyplot as plt
import numpy as np

def plot_clustering():


    with open("clusters.pickle", "rb") as fp:  # Unpickling
        clusters = pickle.load(fp)

    with open("all_cds.pickle", "rb") as fp:  # Unpickling list of all svo
        (s_all, a_all, o_all, t_all, p_all, verbatim_all) = pickle.load(fp)

    with open("svo_centers.pickle", "rb") as fp:  # Unpickling list of cds summary
        (subject_center, verb_center, object_center, time_center, place_center, verbatim_centers) = pickle.load(fp)


    V=np.load('V.npy')

    plt.scatter(V[:,0], V[:,1])
    plt.show()

    c=np.zeros(len(subject_center),dtype=np.int)


    for i in range(len(subject_center)):
        for cluster in clusters:
            if i==cluster:
                c[i]=c[i]+1

    print(" ")
    print("number of elements for each clusters:")
    print(c)


    mapper = LinearColorMapper(low=0, high=clusters.max(), palette="Spectral10")
    TOOLS="hover,crosshair, wheel_zoom, pan"
    output_file("clustering.html")
    p = figure(plot_width=1500, plot_height=1500,tools=TOOLS)


    V_means = np.zeros((clusters.max()+1,2))
    for i in range(len(V_means)):
        V_means[i] = V[clusters==i].mean(axis=0)

    x = V_means[:, 0]
    y = V_means[:, 1]

    source = ColumnDataSource(data=dict(x=[], y=[], color=[], text=[], cluster=[], sub=[], verb=[], obj=[], time=[], place=[]))


    source.data = dict(
        x=V_means[:, 0],
        y=V_means[:, 1],
        cluster=range(len(V)),
        text=[str(l) for l in verbatim_centers],
        sub=subject_center,
        verb=verb_center,
        obj=object_center,
        time=time_center,
        place=place_center
    )

    p.diamond(x, y, source=source, fill_color={'field': 'cluster', 'transform': mapper}, line_width=1e-5, size=20)

    x = V[:, 0]
    y = V[:, 1]

    source = ColumnDataSource(data=dict(x=[], y=[], color=[], text=[], cluster=[], sub=[], verb=[], obj=[], time=[], place=[]))
    source.data = dict(
        x=V[:, 0],
        y=V[:, 1],
        cluster=clusters,
        text=verbatim_all,
        sub=s_all,
        verb=a_all,
        obj=o_all,
        time=t_all,
        place=p_all
    )
    p.circle(x, y, source=source, fill_color={'field': 'cluster', 'transform': mapper}, line_width=1e-5)

    from collections import OrderedDict

    labels = OrderedDict([
        ("index", "$index"),
        ("(xx,yy)", "(@x, @y)"),
        ("cluster", "@cluster"),
        ("text", "@text"),
        ("subject", "@sub"),
        ("verb", "@verb"),
        ("object", "@obj"),
        ("time", "@time"),
        ("place", "@place"),
    ])

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = labels

    show(p);

def main(argv):
    plot_clustering()

if __name__ == "__main__":
	main(sys.argv[1:])



