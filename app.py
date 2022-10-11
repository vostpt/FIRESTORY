# -*- coding: utf-8 -*-
# author: Jorge Gomes for VOST Portugal

# ------------------------------
#      VERSIONS
# ------------------------------

# V 0.1 25 AGO 2022 - The basics

# FIRESTORY 

# ------------------------------
#       IMPORT LIBRARIES
# ------------------------------

# ---------- IMPORT BASIC LIBRARIES ------------

import json
import requests
import pandas as pd 
import datetime as dt 
from datetime import datetime, timedelta, date 

# ---------- IMPORT PLOTLY LIBRARIES ------------
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# ---------- IMPORT DASH LIBRARIES ------------
import dash
import dash_daq as daq
from dash import Input, Output, dcc, html
import dash_mantine_components as dmc


# ------------------------------
#      START DASH APP
# ------------------------------

app = dash.Dash(__name__,title='VOST PORTUGAL',suppress_callback_exceptions=True,update_title=None,
    external_stylesheets=[
        # include google fonts
        "https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;900&display=swap"
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )

app.css.config.serve_locally = False 
app.scripts.config.serve_locally = False 

# Define Arrays

csv_git = [2013,2014,2015,2016,2017,2018]
csv_fogos = [2019,2020,2021]

years = [2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]


# -------------------------------------
#     DATA INGESTION AND TREATMENT
# -------------------------------------


# GET DATA FOR 2022 - CALLING FOGOS.API TO GET THE LATEST VALUES
url_bar_2022 = "https://api.fogos.pt/v2/incidents/search?after=2022-01-01&limit=1000000"
# Get response from URL 
response_2022 = requests.get(url_bar_2022)
json_2022 = response_2022.json()
# Create dataframe for 2022 and treat the data 
df_in_2022 = pd.json_normalize(json_2022,'data')
df_in_2022.loc[:,'date'] = pd.to_datetime(df_in_2022['date'],format='%d-%m-%Y')
df_in_2022['month'] = pd.DatetimeIndex(df_in_2022['date']).month
df_in_2022 = df_in_2022.sort_values(by='district', ascending=True)

print("GOT DATA FROM 2022")

# GET ICNF DATA FROM GITHUB FOR 2013 to 2018

for i in csv_git:
    globals()[f"df_in_{i}"] = pd.read_csv(f'https://raw.githubusercontent.com/vostpt/ICNF_DATA/main/icnf_{i}_raw.csv')

print("GOT DATA FROM 2013 TO 2018")

# GET FOGOS DATA FROM LOCAL CSV FOR 2019 to 2021
    
for i in csv_fogos:
    globals()[f"df_in_{i}"] = pd.read_csv(f'assets/fogos_{i}.csv')

print("GOT DATA FROM 2019 TO 2021")

# RENAME COLUMNS FOR ICNF DATA YEARS TO HARMONIZE WITH FOGOS.PT DATA
for i in csv_git:
    globals()[f"df_in_{i}"] = globals()[f"df_in_{i}"].rename(columns={"Unnamed: 0": "id","MES":"month","DISTRITO":"district","ANO":"year","CONCELHO":"concelho","AREATOTAL":"icnf.burnArea.total"})

print("RENAMED COLUMNS")

# CREATE TOTAL RECORDS VARIABLE FOR EACH YEAR

for i in years:
    globals()[f"total_records_{i}"] = globals()[f"df_in_{i}"]['id'].nunique()


print("CALCULATED TOTAL RECORDS PER YEAR")

# CALCULATE BURNT AREA FOR EACH YEAR AND ASSIGN TO A UNIQUE VARIABLE

total_burn_area_measure = " ha"

for i in years:
    globals()[f"df_in_{i}_reset_burntarea"] = globals()[f"df_in_{i}"]['icnf.burnArea.total'].fillna(0)
    globals()[f"total_burnt_area_{i}_number_full"] = globals()[f"df_in_{i}"]['icnf.burnArea.total'].sum()
    globals()[f"total_burnt_area_{i}_number"] = "{:.2f}".format(globals()[f"total_burnt_area_{i}_number_full"])
    globals()[f"total_burnt_area_{i}"] = globals()[f"total_burnt_area_{i}_number"] + total_burn_area_measure

print("CALCULATED BURNT AREA FOR EACH YEAR AND ASSIGNED TO A UNIQUE VARIABLE")


# INITIAL DROPDOWN SETTINGS AND VALUES

district_value = "Aveiro"
county_value = "Aveiro"

print("Created initial dropdown settings")

for i in years:
    print(i)
    globals()[f"df_dropdown_county_{i}"] =  globals()[f"df_in_{i}"][globals()[f"df_in_{i}"]['district']== district_value]
    globals()[f"df_county_records_{i}_final"] =  globals()[f"df_dropdown_county_{i}"][ globals()[f"df_dropdown_county_{i}"]['concelho']== county_value]


#df_dropdown_county_2013 = df_in_2013[df_in_2013['district']== district_value]
# df_county_records_2013_final = df_dropdown_county_2013[df_dropdown_county_2013['concelho']== county_value]

for i in years:
    globals()[f"total_district_records_{i}"] = globals()[f"df_dropdown_county_{i}"]["id"].nunique()
    globals()[f"total_county_records_{i}"] = globals()[f"df_county_records_{i}_final"]["id"].nunique()

#total_district_records_2022 = df_dropdown_county_2022['id'].nunique()
#total_county_records_2022 = df_county_records_2022_final['id'].nunique()



# ------------------------------
#      START APP LAYOUT
# ------------------------------

app.layout = html.Div(
    [
        dmc.Grid(
            children=[
                
                dmc.Col(
                        dmc.Text(
                            "VOST Portugal",
                            weight=700,
                            variant="gradient",
                            gradient={"from":"green", "to":"orange","deg":45},
                            style={"fontSize":24},
                            align="left",
                        ),
                span=1,xs=12,
                ),
                dmc.Col(
                        dmc.Text(
                            "INCÊNDIOS 2022",
                            variant="gradient",
                            gradient={"from":"orange", "to":"red","deg":45},
                            style={"fontSize":24},
                            align="right",
                        ),
                span=2,xs=12,offset=6,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Total 2022",style={'color':'white','font-family':'sans-serif'}),
                            html.H1(total_records_2022,id="total_fires_2022", style={'color':'white','font-family':'sans-serif'}),
                            html.H3("Área Ardida",style={'color':'white','font-family':'sans-serif'}),
                            html.H1(total_burnt_area_2022,id="total_burnt_2022", style={'color':'white','font-family':'sans-serif'}),

                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#ED2939'},
                    ),
                span=3,offset=0,xs=12,xl=3,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Total 2021",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_records_2021,id="total_fires_2021", style={'color':'white','font-family':'sans-serif'}),
                            html.H3("Área Ardida",style={'color':'white','font-family':'sans-serif'}),
                            html.H1(total_burnt_area_2021,id="total_burnt_2021", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#e03c3c'},
                    ),
                span=3,offset=0,xs=12,xl=3,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Total 2020",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_records_2020,id="total_fires_2020", style={'color':'white','font-family':'sans-serif'}),
                            html.H3("Área Ardida",style={'color':'white','font-family':'sans-serif'}),
                            html.H1(total_burnt_area_2020,id="total_burnt_2020", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#e03c3c'},
                    ),
                span=3,offset=0,xs=12,xl=3,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Total 2019",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_records_2019,id="total_fires_2019", style={'color':'white','font-family':'sans-serif'}),
                            html.H3("Área Ardida",style={'color':'white','font-family':'sans-serif'}),
                            html.H1(total_burnt_area_2019,id="total_burnt_2019", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#e03c3c'},
                    ),
                span=3,offset=0,xs=12,xl=3,
                ),
            ],
        ),
        dmc.Grid(
            children=[

                dmc.Col(
                    dmc.Select(
                                id="dropdown_district",
                                data=[
                                    {"label": i, "value": i}
                                    for i in df_in_2022['district'].unique()
                                ],
                                searchable=True,
                                clearable=True,
                                label='Distrito',
                                required=True,
                                value="Aveiro",
                                nothingFound="Esse Distrito Não Existe"
                            ),
                span=6,    
                ),
                dmc.Col(
                    dmc.Select(
                                id="dropdown_county",
                                data=[
                                    {"label": i, "value": i}
                                    for i in df_in_2022['concelho'].unique()
                                ],
                                searchable=True,
                                clearable=True,
                                label='Concelho',
                                value="Aveiro",
                                required=True,
                                nothingFound="Esse Concelho Não Existe"
                            ),
                span=6,    
                ),
            ],            
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Incêndios Registados no Distrito 2022",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_district_records_2022,id="total_district_2022", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#8e0e18'},
                    ),
                    span=6,offset=0,xs=12,xl=6,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("Incêndios Registados no Concelho 2022",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_county_records_2022,id="total_county_2022", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#F17800'},
                    ),
                    span=6,offset=0,xs=12,xl=6,
                ),
            ]
        ),
        dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2021",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_district_records_2021,id="total_district_2021", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#bc5e66'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2020",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_district_records_2020,id="total_district_2020", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#bc5e66'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2019",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_district_records_2019,id="total_district_2019", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#bc5e66'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),

                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2021",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_county_records_2021,id="total_county_2021", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#F9A144'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2020",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_county_records_2020,id="total_county_2020", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#F9A144'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),
                dmc.Col(
                    dmc.Paper(
                        children=[
                            html.H3("2019",style={'color':'white',"font-family":"sans-serif"}),
                            html.H1(total_county_records_2019,id="total_county_2019", style={'color':'white','font-family':'sans-serif'}),
                        ],
                        shadow="md",
                        p="xs",
                        radius="md",
                        withBorder=True,
                        style={'background-color':'#F9A144'},
                    ),
                    span=2,offset=0,xs=12,xl=2,
                ),
            ]
        ),
    ],
)


@app.callback(
    Output(component_id="dropdown_county", component_property="data"),
    Output(component_id="dropdown_county",component_property="value"),
    Output(component_id="total_district_2022",component_property="children"),
    Input(component_id="dropdown_district", component_property="value"),
    #prevent_initial_call=True
)

def update_county(value):

    url_bar_2022 = "https://api.fogos.pt/v2/incidents/search?after=2022-01-01&limit=1000000"

    url_bar_2021 = "https://api.fogos.pt/v2/incidents/search?before=2022-01-01&after=2021-01-01&limit=1000000"

    # Get response from URL 
    response_2022 = requests.get(url_bar_2022)
    response_2021 = requests.get(url_bar_2021)

    # Get the json content from the response
    json_2022 = response_2022.json()
    json_2021 = response_2021.json()
    df_in = pd.json_normalize(json_2022,'data')
    df_in_2021 = pd.json_normalize(json_2021,'data')
    df_in.loc[:,'date'] = pd.to_datetime(df_in['date'],format='%d-%m-%Y')
    df_in['month'] = pd.DatetimeIndex(df_in['date']).month
    df_dropdown_county = df_in[df_in['district']== value]
    df_dropdown_county = df_dropdown_county.sort_values(by='concelho', ascending=True)

    total_district_2022 = df_dropdown_county['id'].nunique()
    return [{'label': i, 'value': i} for i in df_dropdown_county['concelho'].unique()],df_dropdown_county['concelho'].iloc[0], total_district_2022


@app.callback(
    Output(component_id="total_county_2022", component_property="children"),
    Output(component_id="total_district_2021", component_property="children"),
    Output(component_id="total_district_2020", component_property="children"),
    Output(component_id="total_district_2019", component_property="children"),
    Output(component_id="total_county_2021", component_property="children"),
    Output(component_id="total_county_2020", component_property="children"),
    Output(component_id="total_county_2019", component_property="children"),
    Input(component_id="dropdown_district", component_property="value"),
    Input(component_id="dropdown_county", component_property="value"),
    #prevent_initial_call=True
)


def upddate_cards(district_value,county_value):

    url_bar_2022 = "https://api.fogos.pt/v2/incidents/search?after=2022-01-01&limit=1000000"
    # Get response from URL 
    response_2022 = requests.get(url_bar_2022)
    # Get the json content from the response
    json_2022 = response_2022.json()
    df_in_2022 = pd.json_normalize(json_2022,'data')

    # -------------------------------------
    #     GET INITIAL DATA - ALL FOR 2021
    # -------------------------------------

    url_bar_2021 = "https://api.fogos.pt/v2/incidents/search?after=2021-01-01&before=2022-01-01&limit=1000000"
    # Get response from URL 
    response_2021 = requests.get(url_bar_2021)
    json_2021 = response_2021.json()
    # Create dataframe for 2022 and treat the data 
    df_in_2021 = pd.json_normalize(json_2021,'data')
    df_in_2021.loc[:,'date'] = pd.to_datetime(df_in_2021['date'],format='%d-%m-%Y')
    df_in_2021['month'] = pd.DatetimeIndex(df_in_2021['date']).month
    df_in_2021 = df_in_2021.sort_values(by='district', ascending=True)

    # -------------------------------------
    #     GET INITIAL DATA - ALL FOR 2020
    # -------------------------------------

    url_bar_2020 = "https://api.fogos.pt/v2/incidents/search?after=2020-01-01&before=2021-01-01&limit=1000000"
    # Get response from URL 
    response_2020 = requests.get(url_bar_2020)
    json_2020 = response_2020.json()
    # Create dataframe for 2022 and treat the data 
    df_in_2020 = pd.json_normalize(json_2020,'data')
    df_in_2020.loc[:,'date'] = pd.to_datetime(df_in_2020['date'],format='%d-%m-%Y')
    df_in_2020['month'] = pd.DatetimeIndex(df_in_2020['date']).month
    df_in_2020 = df_in_2020.sort_values(by='district', ascending=True)

    # -------------------------------------
    #     GET INITIAL DATA - ALL FOR 2019
    # -------------------------------------

    url_bar_2019 = "https://api.fogos.pt/v2/incidents/search?after=2019-01-01&before=2020-01-01&limit=1000000"
    # Get response from URL 
    response_2019 = requests.get(url_bar_2019)
    json_2019 = response_2019.json()
    # Create dataframe for 2022 and treat the data 
    df_in_2019 = pd.json_normalize(json_2019,'data')
    df_in_2019.loc[:,'date'] = pd.to_datetime(df_in_2019['date'],format='%d-%m-%Y')
    df_in_2019['month'] = pd.DatetimeIndex(df_in_2019['date']).month
    df_in_2019 = df_in_2019.sort_values(by='district', ascending=True)


    # -------------------------------------
    #            LET'S FILTER
    # -------------------------------------

    df_dropdown_county_2022 = df_in_2022[df_in_2022['district']== district_value]
    df_county_records_2022_final = df_dropdown_county_2022[df_dropdown_county_2022['concelho']== county_value]

    df_dropdown_county_2021 = df_in_2021[df_in_2021['district'] == district_value]
    df_county_records_2021_final = df_dropdown_county_2021[df_dropdown_county_2021['concelho']== county_value]

    df_dropdown_county_2020 = df_in_2020[df_in_2020['district'] == district_value]
    df_county_records_2020_final = df_dropdown_county_2020[df_dropdown_county_2020['concelho']== county_value]

    df_dropdown_county_2019 = df_in_2019[df_in_2019['district'] == district_value]
    df_county_records_2019_final = df_dropdown_county_2019[df_dropdown_county_2019['concelho']== county_value]



    total_county_records_2022 = df_county_records_2022_final['id'].nunique()

    total_district_records_2021 = df_dropdown_county_2021['id'].nunique()
    total_district_records_2020 = df_dropdown_county_2020['id'].nunique()
    total_district_records_2019 = df_dropdown_county_2019['id'].nunique()

    total_county_records_2021 = df_county_records_2021_final['id'].nunique()
    total_county_records_2020 = df_county_records_2020_final['id'].nunique()
    total_county_records_2019 = df_county_records_2019_final['id'].nunique()

    return total_county_records_2022, total_district_records_2021,total_district_records_2020,total_district_records_2019,total_county_records_2021, total_county_records_2020, total_county_records_2019




# -------------------------------------------------------------------------------------
# --------------------------------  START THE APP -------------------------------------
# -------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug=True)


# The End
