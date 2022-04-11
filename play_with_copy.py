# Trying the different ways to copy/duplicate a dataframe

import pandas as pd

def play_wit_df():
    def create_df():
        ''' Create a dataframe '''
        data = {'Name':['Alfa', 'Bravo', 'Charlie', 'Delta'] }
        return pd.DataFrame(data)

    print ("1) df_b = df_a")
    df_a = create_df()
    df_b = df_a
    df_b.iloc[0]["Name"] = "Zulu"
    print (df_a)  #ZBCD
    print (df_b)  #ZBCD

    print ("2) df_b = df_a.copy()")
    df_a = create_df()
    df_b = df_a.copy()
    df_b.iloc[0]["Name"] = "Zulu"
    print (df_a) #ABCD
    print(df_b)  #ZBCD

    print ("3) df_b = df_a.copy(deep=False)")
    df_a = create_df()
    df_b = df_a.copy(deep=False)
    df_b.iloc[0]["Name"] = "Zulu"
    print (df_a) #ZBCD
    print(df_b)  #ZBCD

    print("4) df_b = df_a.copy(deep=True)")
    df_a = create_df()
    df_b = df_a.copy(deep=True)
    df_b.iloc[0]["Name"] = "Zulu"
    print (df_a) #ABCD
    print(df_b) #ZBCD

    # 1 and 3 are the same?
    # 2 and 4 are the same?
    # probably yes because deep = True is the default

def play_with_list_modifiy_a():
    import copy

    def make_list_a():
        return  ["A", "B", ["C", "D"]]


    list_a =make_list_a()
    list_b = list_a #asignment
    print (list_a)
    list_a[0]="Z"
    list_a[2][0]="Y"

    print ("assignment")
    print (list_a) #ZBYCD
    print (list_b) #ZBYCD

    list_a =make_list_a()
    list_b = list_a.copy() # shallow copy
    list_a[0]="Z"
    list_a[2][0]="Y"

    print ("shallowcopy")
    print (list_a) #ZBYCD
    print (list_b) #ABYCD

    list_a =make_list_a()
    list_b = copy.deepcopy(list_a) # deep copy
    list_a[0]="Z"
    list_a[2][0]="Y"
    print ("deepcopy")
    print (list_a) #ZBYCD
    print (list_b) #ABCD

def play_with_list_modifiy_b():
    import copy

    def make_list_a():
        return  ["A", "B", "C", "D"]


    list_a =make_list_a()
    list_b = list_a #asignment
    list_b[0]="Z"
    print ("assignment")
    print (list_a) #ZBCD
    print (list_b) #ZBCD

    list_a =make_list_a()
    list_b = list_a.copy() # shallow copy
    list_b[0]="Z"

    print ("shallowcopy")
    print (list_a) #ABCD
    print (list_b) #ZBCD

    list_a =make_list_a()
    list_b = copy.deepcopy(list_a) # deep copy
    list_b[0]="Z"
    print ("deepcopy")
    print (list_a) #ABCD
    print (list_b) #ZBCD

play_with_list_modifiy_a()


play_with_list_modifiy_b()