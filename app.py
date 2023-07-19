import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit

st.set_page_config(page_title="Dashboard productos Agricolas", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
@st.cache_data or st.cache_resource
def get_data_from_excel():
    df = pd.read_excel(
        io="Expor_Produc_Cons_Precio.xlsx",
        engine="openpyxl",
        sheet_name="th_produccion_v",
        #skiprows=0,
        usecols="A:E",
        nrows=1000,
    )
    return df
df = get_data_from_excel()


# ---- SIDEBAR ----
st.sidebar.header("Filtra datos aqui:")
Pais = st.sidebar.multiselect(
    "Selecciona el pais:",
    options=df["pais"].unique(),
    default=df["pais"].unique()
)

Anio = st.sidebar.multiselect(
    "Selecciona el año:",
    options=df["anio"].unique(),
    default=df["anio"].unique(),
)

Producto = st.sidebar.multiselect(
    "Selecciona el producto:",
    options=df["producto"].unique(),
    default=df["producto"].unique()
)

df_selection = df.query(
    "pais == @Pais & anio ==@Anio & producto == @Producto"
)

# ---- MAINPAGE ----
st.title(":bar_chart: Dashboard de Analisis de productos agricolas en el mercado mundial ")
st.markdown("##")

# TOP KPI's
total_production = int(df_selection["cantidad_kg"].sum())
type_production = df_selection["tipo_producto"]

left_column, middle_column = st.columns(2)
with left_column:
    st.subheader("Total Produccion:")
    st.subheader(f"{total_production:,} kg")
with middle_column:
    st.subheader("Tipo de producto:")
    st.subheader(f"{type_production}")

st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product_line = (
    df_selection.groupby('producto')['cantidad_kg'].sum()
)
fig_product_sales = px.bar(
    sales_by_product_line,
    x="cantidad_kg",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Cantidad de kg x Producto</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


right_column = st.columns(2)
right_column[0].plotly_chart(fig_product_sales, use_container_width=True)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
