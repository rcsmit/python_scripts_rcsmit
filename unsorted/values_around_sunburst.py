# https://stackoverflow.com/questions/70129355/value-annotations-around-plotly-sunburst-diagram

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from math import sin,cos,pi

import plotly.io as pio
import streamlit as st
df = px.data.tips()

aaa = 'day'
bbb = 'time'
ccc = 'sex'
ddd = "total_bill"

fig = px.sunburst(df, path=[aaa, bbb, ccc], values=ddd)
totals_groupby =  df.groupby([aaa, bbb, ccc]).sum()
totals_groupby["aaa_sum"] = getattr(df.groupby([aaa, bbb, ccc]), ddd).sum().groupby(level=aaa).transform('sum')
totals_groupby["aaa_bbb_sum"] = getattr(df.groupby([aaa, bbb, ccc]), ddd).sum().groupby(level=[aaa,bbb]).transform('sum')
totals_groupby["aaa_bbb_ccc_sum"] = getattr(df.groupby([aaa, bbb, ccc]), ddd).sum().groupby(level=[aaa,bbb,ccc]).transform('sum')
totals_groupby = totals_groupby.sort_values(by=["aaa_sum","aaa_bbb_sum","aaa_bbb_ccc_sum"], ascending=[0,0,0])

annotations = [format(v,".0f") for v in  getattr(totals_groupby,ddd).values]

## calculate the angle subtended by each category
sum_ddd = getattr(df,ddd).sum()
delta_angles = 360*totals_groupby[ddd] / sum_ddd


## calculate cumulative sum starting from 0, then take a rolling mean 
## to get the angle where the annotations should go
angles_in_degrees = pd.concat([pd.DataFrame(data=[0]),delta_angles]).cumsum().rolling(window=2).mean().dropna().values

def get_xy_coordinates(angles_in_degrees, r=1):
    return [r*cos(angle*pi/180) for angle in angles_in_degrees], [r*sin(angle*pi/180) for angle in angles_in_degrees]

x_coordinates, y_coordinates = get_xy_coordinates(angles_in_degrees, r=1.05)
fig.add_trace(go.Scatter(
    x=x_coordinates,
    y=y_coordinates,
    mode="text",
    text=annotations,
    hoverinfo="skip",
    textfont=dict(size=14)
))

padding = 0.20
fig.update_layout(
    xaxis=dict(
        range=[-1 - padding, 1 + padding], 
        showticklabels=False
    ), 
    yaxis=dict(
        range=[-1 - padding, 1 + padding],
        showticklabels=False
    ),
    plot_bgcolor='rgba(0,0,0,0)'
)

#fig.show()


st.plotly_chart(fig)


# fig.show(renderer="png")