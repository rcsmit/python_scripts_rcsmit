import streamlit as st
import pandas as pd
import datetime as dt


def cell_background(val):
    """Creates the CSS code for a cell with a certain value to create a heatmap effect
    Args:
        val ([int]): the value of the cell

    Returns:
        [string]: the css code for the cell
    """
    try:
        v = abs(val)
        opacity = 1 if v >100 else v/100
        # color = 'green' if val >0 else 'red'
        if val > 0 :
             color = '193, 57, 43'
        elif val < 0:
            color = '1, 152, 117'
        else:
            color = '255,255,173'
    except:
        # give cells with eg. text or dates a white background
        color = '255,255,255'
        opacity = 1
    return f'background: rgba({color}, {opacity})'


def cell_background_number_of_cases(val,min, middle, max, method):
    """Creates the CSS code for a cell with a certain value to create a heatmap effect
    Args:
        val ([int]): the value of the cell

    Returns:
        [string]: the css code for the cell
    """
    #try:
    opacity = .75
    color = "255,255,255"
    #print(f"{min =} {middle = } {max = } ")
    v = abs(val)
    if method == "exponential_two_color":

        color1 = [255, 255, 255]
        #color_middle = [255, 255, 0]
        color2 = [255, 0, 0]



        value_table = [ [0,0],
                        [0.00390625,0.0625],  #1/256 - 1/16
                        [0.0078125, 0.125], # 1/128 - 1/8
                        [0.015625,0.25],  # 1/ 64 2/8
                        [0.03125,0.375],  #1/32 - 3/8
                        [0.0625,0.50],  # 1/16 - 4/8
                        [0.125,0.625],  # 1/8 - 5/8
                        [0.25,0.75],  # 1/4 - 6/8
                        [0.50,0.875], #1/2 - 7/8   -
                        [0.75,0.9375],  # 3/4 - 15/16
                        [1,1]]    # 1/1 - 8/8
        for vt in value_table:

            if v >= round(vt[0]*max) :
                percent = vt[1]
                opacity = 0.75
                r_ = color1[0] +( percent*(color2[0]-color1[0]))
                g_ = color1[1] +( percent*(color2[1]-color1[1]))
                b_ = color1[2] +( percent*(color2[2]-color1[2]))
                color = f'{r_},{g_},{b_}'

    elif method == "exponential_three_color":

        color_min = [0, 255, 0]
        color_middle = [255, 255, 0]
        color_max = [255, 0, 0]
        if v< middle:
            color1 = color_min
            color2 = color_middle
        else:
            color1 = color_middle
            color2 = color_max

        v = abs(val)

        value_table = [ [0,0],
                        [0.00390625,0.0625],  #1/256 - 1/16
                        [0.0078125, 0.125], # 1/128 - 1/8
                        [0.015625,0.25],  # 1/ 64 2/8
                        [0.03125,0.375],  #1/32 - 3/8
                        [0.0625,0.50],  # 1/16 - 4/8
                        [0.125,0.625],  # 1/8 - 5/8
                        [0.25,0.75],  # 1/4 - 6/8
                        [0.50,0.875], #1/2 - 7/8   -
                        [0.75,0.9375],  # 3/4 - 15/16
                        [1,1]]    # 1/1 - 8/8
        for vt in value_table:

            if v >= round(vt[0]*max) :
                if v< max/2:
                    percent = vt[1]*2
                else:
                    percent = (vt[1]-0.5)*2
                opacity = 0.75
                r_ = color1[0] +( percent*(color2[0]-color1[0]))
                g_ = color1[1] +( percent*(color2[1]-color1[1]))
                b_ = color1[2] +( percent*(color2[2]-color1[2]))
                color = f'{r_},{g_},{b_}'


    elif method == "min_middle_max":
        color_min = [0, 255, 0]
        color_middle = [255, 255, 0]
        color_max = [255, 0, 0]

        if val <= min:
            color = f'{color_min[0]},{color_min[1]},{color_min[2]}'

        elif val > min and val < middle:
            color1=color_min
            color2 = color_middle

            percent = val/(middle-min)

            r_ = color1[0] +( percent*(color2[0]-color1[0]))
            g_ = color1[1] +( percent*(color2[1]-color1[1]))
            b_ = color1[2] +( percent*(color2[2]-color1[2]))


            color = f'{r_},{g_},{b_}'

        elif val == middle:
            color = f'{color_middle[0]},{color_middle[1]},{color_middle[2]}'

        elif val > middle and val < max:
            color1 = color_middle
            color2 = color_max

            percent = (val-middle)/(max-middle)

            r_ = color1[0] +( percent*(color2[0]-color1[0]))
            g_ = color1[1] +( percent*(color2[1]-color1[1]))
            b_ = color1[2] +( percent*(color2[2]-color1[2]))

            color = f'{r_},{g_},{b_}'

        elif val >= max:
            color = f'{color_max[0]},{color_max[1]},{color_max[2]}'
        else:
            color = "128,128,128"



    else:
        color = '0,0,255'
        opacity = 1

    # except:
    #         # give cells with eg. text or dates a white background
    #         color = '255,0,255'
    #         opacity = 1



    return f'background: rgba({color}, {opacity})'

def  make_legenda(min_waarde, middle_waarde, top_waarde,method):
        #stapfracties =   [0, 0.00390625, 0.0078125, 0.015625,  0.03125,  0.0625 , 0.125,  0.25,  0.50, 0.75,  1]
        stapfracties =   [0, 0.00390625, 0.0078125, 0.015625,  0.03125,  0.0625 , 0.1,0.2,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.7,0.8,0.9,  1.0,1.2]

        stapjes =[]
        for i in range(len(stapfracties)):
            stapjes.append((stapfracties[i]*top_waarde))
        d = {'legenda': stapjes}

        df_legenda = pd.DataFrame(data=d)
        st.write (df_legenda.style.format(None, na_rep="-").applymap(lambda x:  cell_background_number_of_cases(x,min_waarde, middle_waarde, top_waarde, method)).set_precision(2))


def main():
    url = "C:\\Users\\rcxsm\\Documents\\pyhton_scripts\\covid19_seir_models\\output\\landelijk_leeftijd_pivot.csv"
    df = pd.read_csv(url, delimiter=",", low_memory=False)
    #df['pos_test_Date_statistics'] = df['pos_test_Date_statistics'].dt.date
    df.rename(columns={"pos_test_Date_statistics": "date"},  inplace=True)
    df=df.drop(columns="date")
    df=df.fillna(0)
    max_waarde = df.max()
    #top_waarde = 0.975*max_waarde
    min_waarde = 200
    middle_waarde = 900
    top_waarde = 1600
    methods = ["exponential_two_color", "exponential_three_color", "min_middle_max"]

    for m in methods:
        st.subheader(m)
        st.write (df.style.format(None, na_rep="-").applymap(lambda x:  cell_background_number_of_cases(x,min_waarde,middle_waarde, top_waarde, m)).set_precision(2))
        make_legenda(min_waarde, middle_waarde, top_waarde, m)
main()