import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import plotly.express as px
import pycountry


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title='DASHBOARD DE CLASSIFICAÇÃO DE VINHOS',
    page_icon='🍷',
    layout='wide',
    initial_sidebar_state='expanded',
    
    menu_items={
        'About': "Esse app foi desenvolvido por Fábio Dantas Cardoso e Lucas Cavalcante para a disciplina de Análise e Visualização de Dados."
    }
)
# DATASET
@st.cache_data
def busca_df():
    df = pd.read_csv('./data/Vinhos.csv')
    return df

df = busca_df()

#CRIANDO UMA COLUNA COM O ISO_ALPHA_3 PARA O GRÁFICO DP MAPA
input_countries = df['Country']

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_3

codes = [countries.get(country, 'Unknown code') for country in input_countries]
df['Codes'] = codes

#CONFIGURANDO O SIDEBAR
with st.sidebar:
    logo_teste = Image.open('./assets/logo_novo_novo.jpg')
    st.image(logo_teste, width=300)

    #CRIANDO O STREAMLIT_OPTION_MENU
    selected = option_menu(
    menu_title = "Menu Principal",
    options=["Dashboard","Busca por Vinho","Lojas Virtuais"],
    icons=["bar-chart", "funnel","shop-window"],
    menu_icon="house",
    default_index=0,
    orientation="vertical",
    styles={
    "container": {"padding": "0!important", "background-color": "#c1a2a0"},
    "icon": {"color": "black", "font-size": "25px"},
    "nav-link": {
        "font-size": "15px",
        "text-align": "left",
        "margin": "0px",
        "--hover-color": "#e8caaf",
    },
    "nav-link-selected": {"background-color": "#7d3f60"},
},
)
#CONFIGURANDO A PAGINA DO 'DASHBOARD'
if selected == "Dashboard":
    with st.container():       

        tab1, tab2 = st.tabs(["Custo x Benefício (todos os países)", "Custo x Benefício (por País)"])
#GRÁFICO DE SCATTER COM BOXPLOT PARA O EIXO X E RUG PARA O EIXO Y
        with tab1:   
            graf1_2 =px.scatter(df,
                      x='Rating',
                      y='Price',
                      
                      marginal_x='box',
                      marginal_y='rug',
                      color='Type',color_discrete_sequence= px.colors.qualitative.Set1,
                      #color='Type',color_discrete_sequence= ['#52173a','#a305a2', '#a208e0','#e93e92'],
                      symbol='Type',
                      hover_name='Country',
                      hover_data='Year'
                      
                      #size='NumberOfRatings'
                      )
            graf1_2.update_layout({
            'plot_bgcolor': '#f6e8f2',  # Cor de fundo
            'paper_bgcolor': '#f6e8f2', # Cor do papel
            'title':'Gráfico de custo-benefício' ,
            'title_font' :{'size': 30},
            })   
            
            st.plotly_chart(graf1_2, theme=None, use_container_width=True)
            
        
#GRAFICO SCATTER COM UM SELECTBOX PARA FILTRAR POR PAÍS
        with tab2:
            fPais = st.selectbox(
            "Selecione o País:",
            options=df['Country'].sort_values().unique()
            )

            tbl_scatter_pais = df.loc[df['Country']==fPais]
        
            graf1_1 =px.scatter(tbl_scatter_pais,
                      x='Rating',
                      y='Price',
                      #marginal_x='box',
                      #marginal_y='rug',
                      color='Type',color_discrete_sequence= px.colors.qualitative.Set1,
                      symbol='Type',
                      hover_name = 'Winery',
                      hover_data=['Year','Region']
                      
                      #size='NumberOfRatings'
                      )
            graf1_1.update_layout({
            'plot_bgcolor': '#f6e8f2',  # Cor de fundo
            'paper_bgcolor': '#f6e8f2', # Cor do papel
            'title':'Gráfico de custo-benefício' ,
            'title_font' :{'size': 30},
            })
            
            st.plotly_chart(graf1_1, theme=None, use_container_width=True)
        

    st.markdown('---')
#GRÁFICO DE GEO CHOROPLETH
    with st.container():
        st.header("Gráfico de países com maiores Ratings")
        graf2 = px.choropleth(df,locations='Codes',color='Rating',color_continuous_scale='YlOrRd')
        st.plotly_chart(graf2)
        
#CONFIGURANDO A PAGINA DO FILTRO DA BUSCA DE VINHOS
if selected == "Busca por Vinho":     
    col1, col2,col3 = st.columns([1,0.3,1])  

    with col1:
        
        fPais = st.selectbox(
            "Selecione o País:",
            options=df['Country'].sort_values().unique()
            )

        tbl_sidebar_pais = df.loc[df['Country'] == fPais]        
        

        fRegiao = st.selectbox(
            "Selecione a Região:",
            options = tbl_sidebar_pais['Region'].sort_values().unique()
            )
        tbl_sidebar_regiao = df.loc[df['Region'] == fRegiao]

        fTipo = st.radio(
            "Selecione o tipo de Vinho:",
            options=tbl_sidebar_regiao['Type'].sort_values().unique()
            )
        
        fPreco = st.slider(
            'Selecione o valor do vinho',
            tbl_sidebar_pais['Price'].min(), 
            tbl_sidebar_pais['Price'].max(), 
            (tbl_sidebar_regiao['Price'].min(), tbl_sidebar_regiao['Price'].max()),
            step=0.1
            
            )
        fRating = st.slider(
            'Selecione o rating do vinho',
            tbl_sidebar_pais['Rating'].min(), 
            tbl_sidebar_pais['Rating'].max(), 
            (tbl_sidebar_regiao['Rating'].min(), tbl_sidebar_regiao['Rating'].max()),
            step=0.1
            )
        
    st.markdown("---")

    #sAÍDA DO RESULTADO DA BUSCA FEITA NO FILTRO
    with col3:

        st.title("Vinho desejado:")
        tbl_dinamica = df.loc[
                (df['Country'] == fPais) &
                (df['Region'] == fRegiao) &
                (df['Type'] == fTipo) &
                (df['Price'] >= fPreco[0]) &
                (df['Price'] <= fPreco[1]) &
                (df['Rating'] >= fRating[0]) &
                (df['Rating'] <= fRating[1]) 
                #(df['NumberOfRatings'] >= fNum_Rating)
                ]
        vinho_desejado = tbl_dinamica.sort_values(by="NumberOfRatings")
        nome_vinho_desejado = vinho_desejado.to_numpy()[0][1]
        vinicula_vinho_desejado = vinho_desejado.to_numpy()[0][4]

             
        st.write('**NOME DO RÓTULO:**')
        st.info(f"{nome_vinho_desejado}")

        st.write('**NOME DA VINÍCULA:**')
        st.info(f"{vinicula_vinho_desejado}")
#CONFIGURANDO A PAGINA DOS LINKS DAS LOJAS VIRTUAIS DE VINHO
if selected == "Lojas Virtuais":
    st.title("Sites de lojas virtuais:")
    st.subheader("VIVINO")
    st.write("www.vivino.com.br")
    st.subheader("MEU VINHO")
    st.write("www.meuvinho.com.br")
    st.subheader("WINE LOVERS")
    st.write("www.winelovers.com.br")
    st.subheader("EVINO")
    st.write("www.evino.com.br")

