import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Singapore Trade Visualisation")

st.title("Singapore Trade Visualisation")

df = pd.read_csv("/Users/gojek/Downloads/trade-in-services-by-services-category-annual/exports-and-imports-of-services-by-detailed-services-category-annual.csv")
st.subheader("Exports and imports (detailed services annual")
st.write(df, width = 550)
df.drop("level_1", axis = 1, inplace = True)

st.subheader("Services imports detailed")
df_imports = df[df["level_2"] == "Imports Of Services"]
df_imports["detailed_service"] = df_imports["level_3"] + ": "+  df_imports["level_4"]
df_imports.drop(["level_3", "level_4"], axis = 1, inplace = True)
st.write(df_imports)

base = alt.Chart(df_imports).properties(width = 1000)

line = base.mark_line().encode(
    x = 'year',
    y = 'value',
    color = 'detailed_service'
)

rule = base.mark_rule().encode(
    y='sum(value)',
    color='detailed_service',
    size=alt.value(2)
)

base = line + rule

st.altair_chart(base, use_container_width=True)

# df_exports = df[df["level_2"] == "Exports Of Services"]

