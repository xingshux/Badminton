# Import libraries
from select import select
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Functions
def create_name():
    lastname_input = st.text_input("Player's Last Name: ")
    lastname_input = lastname_input.upper()
    firstname_input = st.text_input("Player's First Name: ")
    if " " in firstname_input:
        i = firstname_input.index(" ")
        s1 = firstname_input[0:i+1]
        s2 = firstname_input[i+1::]
        firstname_input = s1.capitalize() + s2.capitalize()
    else:
        firstname_input = firstname_input.capitalize()
    name_input = lastname_input + " " + firstname_input
    return name_input,firstname_input,lastname_input

def search(df,key:str,visual=False):
    if key == "Nationality":
        nal = st.selectbox("Country",pd.unique(df["Nationality"]))
        df1 = df[df["Nationality"] == nal]
        h = st.checkbox("Hide Table")
        if not h:
            st.dataframe(df[df["Nationality"] == nal].reset_index(drop=True))
        if visual:
            df1["Percentage"] = df1["Win"] / df1["Total"]
            option = st.selectbox("what to check: ",["Win","Lose","Total","Percentage"])
            f = alt.Chart(df1).mark_bar().encode(
            x='Name',
            y=option,
            color='Percentage',)
            st.altair_chart(f,use_container_width=True)
        p = st.checkbox("Check specific players")
        if p:
            n = st.selectbox("Player", df1["Name"])
            w = df1[df1["Name"] == n].reset_index(drop = True)["Win"][0]
            l = df1[df1["Name"] == n].reset_index(drop = True)["Lose"][0]
            st.table(df1[df1["Name"]==n])
            fig = plt.figure(figsize=(2,2))
            plt.rcParams.update({'font.size': 9})
            colors = sns.color_palette('bright')[5::]
            plt.pie([w,l],labels=["Win","Lose"],colors= colors,autopct='%1.2f%%')
            plt.title(n,fontsize=9)
            st.pyplot(fig)
    else:
        name = st.selectbox("Name", df["Name"])
        w = df[df["Name"] == name].reset_index(drop = True)["Win"][0]
        l = df[df["Name"] == name].reset_index(drop = True)["Lose"][0]
        st.table(df[df["Name"]==name])
        if visual:
            fig = plt.figure(figsize=(3,3))
            colors = sns.color_palette('bright')
            plt.pie([w,l],labels=["Win","Lose"],colors= colors,autopct='%1.2f%%')
            plt.title(name)
            st.pyplot(fig)
    return

def add(df,name:str,fname:str,lname:str):
    if name not in df["Name"].unique():
        Nationality = st.text_input("Enter nationality: ")
        Nationality = Nationality.upper()
        Result = st.selectbox("Win or Lose: ",["Win","Lose"])
        df = df.copy()
        if Result == "Win":
            new_df = {"Nationality": Nationality,"Name": name,"Last Name": lname,"First Name":fname,"Win":1,"Lose":0,"Total":1}
        else:
            new_df = {"Nationality": Nationality,"Name": name,"Last Name": lname,"First Name":fname,"Win":0,"Lose":1,"Total":1}
        df = df.append(new_df,ignore_index=True)
    else:
        i = df[df["Name"]==name].index[0]
        Result = st.selectbox("Win or Lose: ",["Win","Lose"])
        t = df.loc[i,["Total"]]
        df.loc[i,["Total"]] = t+1
        if Result == "Win":
            w = df.loc[i,["Win"]]
            df.loc[i,["Win"]] = w+1
        else:
            l = df.loc[i,["Lose"]]
            df.loc[i,["Lose"]] = l+1
    return df

def remove(df,name):
    index = df[df["Name"] == name].index[0]
    return df.drop(index)

def update(name, col,val,df):
    index = df[df["Name"] == name].index[0]
    df.loc[index,col] = val
    return


# Load Data
file = st.file_uploader("Upload H2H CSV file",type = "csv")
H2H = pd.read_csv(file)
# Interface
st.title("Head to Head")
H2H["Total"] = H2H["Win"]+H2H["Lose"]
H2H["Name"] = H2H["Last Name"] + " " + H2H["First Name"] 
H2H = H2H[["Nationality","Name","First Name", "Last Name", "Win","Lose","Total"]]
H2H = H2H.sort_values(by = ["Total","Win"],ascending=False,ignore_index=True)
H2H = H2H.reset_index(drop = True)
H2H["First Name"] = H2H["First Name"].str.strip()
H2H["Last Name"] = H2H["Last Name"].str.strip()
H2H["Name"] = H2H["Name"].str.strip()
if st.checkbox("Show All Data"):
    st.dataframe(H2H)

service = st.selectbox("Choose what you want to do: ", ["Search", "Add","Update","Remove"])

if service == "Search":

    keywrd = st.selectbox("Search by: ", ["Nationality", "Name"])
    v = st.checkbox("Detailed Analysis")
    search(H2H,keywrd,v)

elif service == "Add":
    H2H_copy = H2H.copy()
    name_input,firstname_input,lastname_input = create_name()
    H2H_copy = add(H2H_copy,name_input,firstname_input,lastname_input)
    st.dataframe(H2H_copy[H2H_copy["Name"] == name_input])
    check = st.checkbox("Confirm the updated H2H")
    if check:
        H2H = H2H_copy
        csv = H2H.to_csv(index=False)
        st.download_button("Press to download csv",csv,file_name = "H2H.csv")

elif service == "Update":

    H2H_copy = H2H.copy()
    name_input,firstname_input,lastname_input = create_name()
    if name_input not in H2H_copy["Name"].unique():
        st.write("invalid name")
    else:
        u = st.selectbox("Which information you want to update: ",[x for x in H2H_copy.columns.tolist() if x != "Total"])
        if u in ["Win","Lose"]:
            update_value = st.number_input("Updated Value",min_value = 0,format = "%i")
        else:
            update_value = st.text_input("Updated Value")
        update(name_input,[u],update_value,H2H_copy)
        st.dataframe(H2H_copy[H2H_copy["Name"] == name_input])
        check = st.checkbox("Confirm the updated H2H")
        if check:
            H2H = H2H_copy
            csv = H2H.to_csv(index=False)
            st.download_button("Press to download csv",csv,file_name = "H2H.csv")
else:
    H2H_copy = H2H.copy()
    name = st.selectbox("Who do you want to remove?",H2H_copy["Name"])
    H2H_copy = remove(H2H_copy,name)
    st.dataframe(H2H_copy)
    check = st.checkbox("Confirm the updated H2H")
    if check:
        H2H = H2H_copy
        csv = H2H.to_csv(index=False)
        st.download_button("Press to download csv",csv,file_name = "H2H.csv")


    


