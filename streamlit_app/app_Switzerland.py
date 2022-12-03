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
    df = pd.read_csv("models//BERTopic100CharMin2500CharMax_20/df_prep.csv")
    return df

def create_df_value_counts(df):
    messages_per_week_dict = dict(df.value_counts("week"))
    df_value_counts = df.value_counts(["cluster_names", "week"]).reset_index()
    df_value_counts.columns = ["cluster_names", "week", "occurence_count"]
    # df_value_counts['occurence_count_norm'] = df_value_counts.apply(lambda x: x.occurence_count/list(messages_per_week_dict.values())[list(messages_per_week_dict.keys()).index(x.week)], axis=1)
    return df_value_counts

def modify_df_for_table(df_mod, canton_select, cluster_select, week_slider):
    if canton_select!="all Cantons":
        df_mod = df_mod[df_mod.canton==canton_select]
    if not "all found clusters" in cluster_select:
        df_mod = df_mod[df_mod.cluster_names.isin(cluster_select)]
    df_mod = df_mod[df_mod.week.between(week_slider[0], week_slider[1])]
    # if metric_select!='':
    #     df_mod.sort_values(metric_select, ascending=False, inplace=True)
    df_mod = df_mod[["chat", "messageText", "cluster_names", "messageDatetime", "week", "messageViews", "messageForwards", "reaction_count"]]
    return df_mod

df = load_telegram_data()

st.title('Identification of Refugee Needs via Telegram')

text_col1, text_col2, text_col3 = st.columns(3)
with text_col1:
    cantons = df.canton.unique().tolist()
    cantons.remove("general")
    canton_selection = ["all Cantons"] + cantons
    canton_select = st.selectbox(
        "Select a canton of interest",
        canton_selection,
        )
with text_col2:
    clusters = ['all found clusters', '0_medical', '1_social_service_asylum', '2_education', '3_banking', '4_personal_care', '5_passport_information', '6_advertisement', '7_transport_CHF_UK', '9_train_CHF', '10_accomodation', '13_train_and_bus_travel', '14_transport_UKR_CH', '15_S_Status', '16_dental_services', '17_vet' ]
    # clusters = ["all found clusters"] + df.cluster_names.unique().tolist()
    # print(clusters)    
    cluster_select = st.multiselect(
        'Choose the topic of interest',
        clusters, 
        ["all found clusters"]
        )
# with text_col3:    
#     metric_select = st.selectbox(
#         'Choose the metric of interest',
#         ['','messageViews', 'messageForwards', 'reaction_count']
#         )
with text_col3:    
    week_slider = st.slider('Choose calendar week of interest',
        min_value=df.week.min(), 
        value=(df.week.min(), df.week.max()), 
        max_value=df.week.max()
        )

df_mod = modify_df_for_table(df_mod=df, canton_select=canton_select, cluster_select=cluster_select, week_slider=week_slider)
df_value_counts = create_df_value_counts(df=df_mod)    

visual_col1, visual_col2= st.columns(2)
with visual_col1:
    if canton_select=="all Cantons":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf, layer_name="Swiss Cantons", fill_colors=["red"])
        m.to_streamlit()
    
    if canton_select!="all Cantons":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf[gdf["NAME_1"]!=canton_select], layer_name="Swiss Cantons", fill_colors=["blue"])
        m.add_gdf(gdf[gdf["NAME_1"]==canton_select], layer_name="Canton Choosen", fill_colors=["red"])
        m.to_streamlit()


with visual_col2:
    st.text(f'We identified the following clusters within {canton_select}')
    fig = px.line(df_value_counts[df_value_counts.cluster_names != "no_class"].sort_values(['week']), x="week", y="occurence_count", color='cluster_names', title='Cluster over time')
    st.plotly_chart(fig, use_container_width=True)

    
st.dataframe(df_mod)

