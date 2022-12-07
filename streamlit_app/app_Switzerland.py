import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
#check different leafmap backends
import leafmap.foliumap as leafmap
# import leafmap.kepler as leafmap #dark themed
#Config must be first line in script
st.set_page_config(layout="wide")

# TODO styler package

gdf = gpd.read_file("data/geodata/geojson/chf.geojson")

@st.cache
def load_telegram_data():
    df = pd.read_csv("models/BERTopic100CharMin2500CharMax_25Classes_dropDuplicates/df_prep2.csv")
    return df

def create_df_value_counts(df):
    messages_per_week_dict = dict(df.value_counts("week"))
    df_value_counts = df.value_counts(["cluster_names", "week"]).reset_index()
    df_value_counts.columns = ["cluster_names", "week", "occurence_count"]
    # df_value_counts['occurence_count_norm'] = df_value_counts.apply(lambda x: x.occurence_count/list(messages_per_week_dict.values())[list(messages_per_week_dict.keys()).index(x.week)], axis=1)
    return df_value_counts

def modify_df_for_table(df_mod, region_select, cluster_select, week_slider, metric_select=None):
    if region_select!="all Countries analysed":
        df_mod = df_mod[df_mod.region==region_select]
    if not "all found clusters" in cluster_select:
        df_mod = df_mod[df_mod.cluster_names.isin(cluster_select)]
    df_mod = df_mod[df_mod.week.between(week_slider[0], week_slider[1])]
    # if metric_select!='':
    #     df_mod.sort_values(metric_select, ascending=False, inplace=True)
    df_mod.sort_values("reaction_count", ascending=False, inplace=True)
    df_mod = df_mod[["chat", "messageText", "messageTextEnglish", "cluster_names", "messageDatetime", "week", "messageViews", "messageForwards", "reaction_count"]]
    return df_mod

df = load_telegram_data()

st.title('Automatic Identification of Refugee Needs via Telegram')

text_col1, text_col2, text_col3  = st.columns(3)
with text_col1:
    regions = df.region.unique().tolist()
    region_select = st.selectbox(
        "Select a country of interest",
        regions,
        )
with text_col2:
    cluster_names = df.cluster_names.unique().tolist()
    cluster_names = ["all found clusters"] + cluster_names 
    cluster_select = st.multiselect(
        'Choose the topic of interest',
        cluster_names,
        ["all found clusters"]
        )
# with text_col3:    
#     metric_select = st.selectbox(
#         'Choose the metric of interest',
#         ['','messageViews', 'messageForwards', 'reaction_count']
#         )
with text_col3:    
    week_slider = st.slider('Choose calendar week of interest',
        min_value=int(df.week.min()), 
        value=(int(df.week.min()), int(df.week.max())), 
        max_value=int(df.week.max())
        )

df_mod = modify_df_for_table(df_mod=df, region_select=region_select, cluster_select=cluster_select, week_slider=week_slider)
df_value_counts = create_df_value_counts(df=df_mod)    

visual_col1, visual_col2= st.columns(2)
with visual_col1:
    if region_select=="general":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf, layer_name="Cantons", fill_colors=["red"])
        # m.add_gdf(gdf[gdf["NAME_1"].isin(regions)], layer_name="Canton analysed", fill_colors=["red"])
        m.to_streamlit()
    
    if region_select!="general":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf[gdf["NAME_1"]!=region_select], layer_name="Cantons", fill_colors=["blue"])
        m.add_gdf(gdf[gdf["NAME_1"]==region_select], layer_name="Canton choosen for Analysis", fill_colors=["red"])
        m.to_streamlit()


with visual_col2:
    st.text(f'We identified the following clusters within {region_select}')
    fig = px.line(df_value_counts[df_value_counts.cluster_names != "no_class"].sort_values(['week']), x="week", y="occurence_count", color='cluster_names', title='Cluster over time', width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True) 
    
st.dataframe(df_mod)

