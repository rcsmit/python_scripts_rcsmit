import sqlite3 as sl
import pandas as pd
import streamlit as st
import os
from PIL import Image

def delete_db(dir):
    sql_statement = f"DELETE FROM txt_from_images WHERE directory = '{dir}'"
    db_name = dir + os.sep + "my_test.db"
    con = sl.connect(db_name)

    cur = con.cursor()
    st.write(f" PROCESSING {sql_statement}")

    cur.execute(sql_statement)
    con.commit()
    st.write(f" DONE {sql_statement}")

def read_db(filter_file_name, filter_keyword):
    """Search the database for a certain keyword and/or directory
    """    
    #TODO implement filter for directory

    if filter_keyword is not None and filter_file_name is not None:
        sql_statement = f" SELECT directory || '\\' || filename AS complete_path, text_in_image FROM txt_from_images WHERE  (text_in_image LIKE '%{filter_keyword}%' AND complete_path LIKE '%{filter_file_name}%' )"
    elif filter_keyword is  None and filter_file_name is not None:
        sql_statement = f" SELECT directory || ' \\' || filename AS complete_path, text_in_image FROM txt_from_images WHERE  (complete_path LIKE '%{filter_file_name}%' )"
    elif filter_keyword is not None and filter_file_name is  None:
        sql_statement = f" SELECT directory || ' \\' || filename AS complete_path, text_in_image FROM txt_from_images WHERE  (text_in_image LIKE '%{filter_keyword}%' )"
    elif filter_keyword is None and filter_file_name is  None:
        sql_statement = f" SELECT directory || ' \\' || filename AS complete_path,  text_in_image FROM txt_from_images" 
    
    dir_name = r"C:\Users\rcxsm\Pictures\ocr_test"
    dir_name = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"

    db_name = dir_name + os.sep + "my_test.db"
    con = sl.connect(db_name)

    try:
        df = pd.read_sql(sql_statement, con)
        if len(df)== 0:
            st.write("No items found")
        else:
            st.write(f"{len(df)} items found")
            st.dataframe(data=df, width=900, height=None)
    except:
        st.write("Error reading the data. Did you use forbidden characters ?")

    if len(df)< 101:
        for index, row in df.iterrows():    
            url = (f"{row['complete_path']}")
            text=  row['text_in_image']
            try:
                image = Image.open(url)
                st.image(image, caption=url)
            except:
                st.write (f"{url} - not found")
            if len(row['text_in_image'])>400:
                with st.expander(text[0:100] +" ..."):
                    st.write(text)
            else:
                st.write(text)

            st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.write("Too much results to show the images")

def main():
    action = "show"
    if action == "show":
        col1,col2,col3 = st.columns(3)
        with col1:
            filter_text = st.text_input("Filter text")
        with col2:
            filter_file_name = st.text_input("Filter directory/file_name")
    
        read_db(filter_file_name, filter_text)
    elif action == "delete":
        # delete records from a specific directory
        dir = r"C:\Users\rcxsm\Pictures\div\mijn autos\b"
        delete_db(dir)
    else:
        st.write("Give a valid action")



if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
  