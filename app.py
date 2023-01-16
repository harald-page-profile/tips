import streamlit as st
import os
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader

# Initialize a session state variable that tracks the sidebar state (either 'expanded' or 'collapsed').
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'


st.set_page_config(layout="wide", initial_sidebar_state='collapsed',
        page_title="Edvins läslista",
        page_icon="https://static01.nyt.com/favicon.ico")
st.title("Edvins läslista")


st.markdown(
    """
    <style>
    .css-163ttbj {
    expanded:false;
    }
    .css-ocqkz7 {
    background-color: #f7f6f5;
    margin: 5px 0px 0px 0px;
    border-radius: 10px;
    }
    #.css-1r6slb0 {
    #    margin: 5px;
    #    background-color:white;
    #}
    a:link {
    color: black;
    text-decoration: none;
    }

    /* visited link */
    a:visited {
      color: black;
      text-decoration: none;
    }</style>"""
    ,
    unsafe_allow_html=True
)

def read_data(filename):
    df = pd.read_csv('./data/' + filename)
    return df


def update_data(df,filename):
    df = df.sort_values('timestamp', ascending=False).head(10)
    df.to_csv('./data/' + filename)

def get_container():
    z = st.container()
    _,a,b,_ = z.columns([1,24,16,1])
    return a,b,
    

def get_teaser(url):
    HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0','Accept-Language': 'en-US, en;q=0.5'})
    response = requests.get(url,headers=HEADERS)
    soup = BeautifulSoup(response.text, features="html.parser")
    metas = soup.find_all('meta')
    title = soup.find('title')
    if(title):
        title=title.text
    else:
        title=url
    desc = [ meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description']
    img = [meta.attrs['content'] for meta in metas if 'content' in meta.attrs and 'property' in meta.attrs and meta.attrs['property'] == 'og:image']
    if(len(desc)>0):
        desc=desc[0]
    else:
        desc=""
    if(len(img)>0):
        img = img[0]
        if("https://" not in img):
            m = re.search('https?://([A-Za-z_0-9.-]+).*', url)
            img = "https://" + m.group(1) + "/" + img.split("/")[-1]
    else:
        img=""
    return (url,title,desc,img)

df = read_data('data.csv')




with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login('Login', 'sidebar')


if authentication_status:
    url = st.sidebar.text_area("Link")
    if st.sidebar.button("Post chat message"):
        url,title,desc,image = get_teaser(url)
        df = pd.DataFrame({"url":[url] + [each for each in df["url"].values],
                            "title":[title] + [each for each in df["title"].values],
                            "description": [desc] + [each for each in df["description"].values],
                            "image":[image] + [each for each in df["image"].values],
                            "timestamp":[time.time()] + [each for each in df["timestamp"].values]
                          })
        update_data(df,'data.csv')
        

    if st.sidebar.button("Reset list"):
        df = pd.DataFrame({"url":[],"title":[],"description":[],"image":[],"timestamp":[]})
        update_data(df,'data.csv')

try:
    for index,row in df.iterrows():
        a,b = get_container()
        if(row["title"] and isinstance(row["title"],str)):
            a.write("## [" + row["title"] + "]("+row["url"] +")")
        if(row["description"] and isinstance(row["description"],str)):
            a.write(row["description"])
        if(row["image"] and isinstance(row["image"],str)):
            b.write("")
            b.markdown('<image src="' + row["image"] + '" style="width:100%;">',unsafe_allow_html=True)
        b.write("")
except ValueError:
    st.title("Enter your name and message into the sidebar, and post!")


