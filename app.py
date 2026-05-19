import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# 1. 页面配置
st.set_page_config(page_title="Carbon-Heat Digital Twin", layout="wide")

# 2. 读取数据 (使用我们在PyCharm里处理过的压缩包)
@st.cache_data
def load_data():
    # 确保这两个文件和 app.py 在同一个目录下
    df_grid = pd.read_csv("Master_Dataset_Slim.csv.gz")
    df_city = pd.read_csv("Global_200_Cities_Nature_Sample.csv")
    return df_grid, df_city

df_grid, df_city = load_data()

# 3. 侧边栏
st.sidebar.title("🌍 Global Explorer")
target_city = st.sidebar.selectbox("📍 Select Target City", sorted(df_grid['City'].unique()))

# 4. 逻辑分类
LIMIT_SUHII = 607.8
LIMIT_CARBON = 1250.0

city_grids = df_grid[df_grid['City'] == target_city].copy()

def classify_synergy(frac):
    if frac <= LIMIT_SUHII: return "Optimal Zone"
    elif frac <= LIMIT_CARBON: return "Compromise Zone"
    else: return "Critical Zone"

def assign_color(status):
    if "Optimal" in status: return [65, 171, 93, 180]
    elif "Compromise" in status: return [254, 178, 76, 180]
    else: return [227, 26, 28, 180]

city_grids['Synergy_Status'] = city_grids['Build_Fraction'].apply(classify_synergy)
city_grids['Color'] = city_grids['Synergy_Status'].apply(assign_color)

# 5. 网页展示
st.title(f"{target_city} | 1km Grid Carbon-Heat Diagnostics")
col_map, col_data = st.columns([3, 1])

with col_data:
    st.metric("Optimal", f"{len(city_grids[city_grids['Synergy_Status']=='Optimal Zone'])/len(city_grids)*100:.1f}%")
    st.metric("Compromise", f"{len(city_grids[city_grids['Synergy_Status']=='Compromise Zone'])/len(city_grids)*100:.1f}%")
    st.metric("Critical", f"{len(city_grids[city_grids['Synergy_Status']=='Critical Zone'])/len(city_grids)*100:.1f}%")

with col_map:
    layer = pdk.Layer(
        'ColumnLayer', city_grids, get_position=['lon', 'lat'],
        get_elevation='Build_Height', elevation_scale=35, radius=450,
        get_fill_color='Color', pickable=True, auto_highlight=True
    )
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=city_grids['lat'].mean(), longitude=city_grids['lon'].mean(), zoom=10, pitch=50),
        layers=[layer]
    ))