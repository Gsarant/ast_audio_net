import dash
from dash import  html,callback,get_app,Output,Input,State,dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import os, sys
from dash_local_react_components import load_react_component
from flask import request
import json
from sql_to_pandas import SQL_to_Pandas
import pandas as pd
import sys
sys.path.append("..")
from misc.misc import *


app=get_app()


AudioComponent = load_react_component(app, 'react', 'audio_component.js')


dash.register_page(
    __name__,
    #path='/audio_details',
    path='/',
    title='Audio details Dashboard',
    name='Audio details Dashboard'
)

def get_db_rec(str_date_from=None,str_date_to=None):
    sql_to_pandas=SQL_to_Pandas()
    if (str_date_from is None or  str_date_to is None) or str_to_date(str_date_from)>=str_to_date(str_date_to):
        #df=sql_to_pandas.get_last_rec()
        #str_date_to=df['date'].to_string(index=False)
        dt_date_from = get_date_before(get_now_date(),7)
        dt_date_to = get_date_99(get_now_str())
        #dt_date_to = get_date_after(get_now_date(),0)
        
        str_date_from = date_to_str(dt_date_from)
        str_date_to = date_to_str(dt_date_to)
    else:
        dt_date_from = get_date_00(str_date_from)
        dt_date_to = get_date_99(str_date_to) 
        str_date_from = date_to_str(dt_date_from)
        str_date_to = date_to_str(dt_date_to)

    df=sql_to_pandas.get_date_from_to(str_date_from,str_date_to)
    df=sql_to_pandas.rename_columns(df)
    data=df.to_dict('records')
    columns=sql_to_pandas.get_columns(df)
    del(sql_to_pandas)
    return data,columns,str_date_from,str_date_to


_,columns,_,_=get_db_rec()
data=[]

audio_component=html.Div(
    [
        
        AudioComponent(
             id='audio_component', 
            # poster=request.host_url + f"assets/specrogram_images/{df.head(1).T['spectrogram_image']}",
            # src=request.host_url+f"assets/audio_mp3/{df.head(1).T['file_name']}",
            # width = '600px',
             height= '400px',
            # title = df.head(1)['file_name'],
            # sound1=f"{df.head(1)['sound1']}: {df.head(1)['conf_sound1']}",
            # sound2=f"{df.head(1)['sound2']}: {df.head(1)['conf_sound2']}",
            # sound3=f"{df.head(1)['sound3']}: {df.head(1)['conf_sound3']}",
            ),
    ])

date_picker=html.Div([
    dcc.DatePickerRange(
        id='date_picker',
        month_format='M-D-Y',
        #start_date=str_to_date(str_date_from),
       # start_date_placeholder_text=str_date_from,
        #end_date=str_to_date(str_date_to),
       # end_date_placeholder_text=str_date_to,
       #disabled_days=False,
       display_format='YYYY/MM/DD',
    )
])

legend= html.Div([
            
            html.Div([
                html.Div(style={
                    'width': '24px',
                    'height': '24px',
                    'backgroundColor': 'white',
                    'border': '1px solid #000',
                    'display': 'inline-block',
                    'marginRight': '8px'
                }),
                html.Span('Prob. Class < 0.35 ', style={'verticalAlign': 'middle'})
            ], style={
                'display': 'inline-block',
                'marginRight': '24px'
            }),

            html.Div([
                html.Div(style={
                    'width': '24px',
                    'height': '24px',
                    'backgroundColor': 'yellow',
                    'border': '1px solid #ccc',
                    'display': 'inline-block',
                    'marginRight': '8px'
                }),
                html.Span('0.35 <= Prob. Class <0.5 ', style={'verticalAlign': 'middle'})
            ], style={
                'display': 'inline-block',
                'marginRight': '24px'
            }),

            html.Div([
                html.Div(style={
                    'width': '24px',
                    'height': '24px',
                    'backgroundColor': 'pink',
                    'border': '1px solid #ccc',
                    'display': 'inline-block',
                    'marginRight': '8px'
                }),
                html.Span('Prob. Class >= 0.5 ', style={'verticalAlign': 'middle'})
            ], style={
                'display': 'inline-block',
                'marginRight': '24px'
            }),
        ])

modal=dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle(id='modal_title_id')),
                dbc.ModalBody(id='modal_body'),
                dbc.ModalFooter(),
            ],
            id="modal_image",
            is_open=False,
            size='xl',
            centered=True,
            className="mw-100 p-5"
            #style={"max-width": "none", "width": "90%"}
        )

def layout(**kwargs):
    custom_childer=[
        dcc.Location(id='url', refresh=True),
        dbc.Row([
            date_picker]
            ),
        dbc.Row([
                dbc.Col([
                        dbc.Row([
                            dag.AgGrid(
                                id="audio_grid_table",
                                #columnDefs=columns,
                                #rowData=data,
                                columnSize="sizeToFit",
                                columnSizeOptions={
                                    'defaultMinWidth': 120,
                                    'columnLimits': [{'key': 'event_id', 'maxWidth': 130},],
                                },
                                #columnSize="autoSize",
                                defaultColDef={"filter": True},
                                dashGridOptions={"rowSelection": "single", 
                                                "animateRows": False,
                                                "rowHeight": 25
                                                },
                                #selectedRows=[data[0]],
                                style={"height":750, "width": "100%"},
                             )
                        ]),
                        dbc.Row([
                                html.Hr(),
                                dbc.Col(
                                    dbc.Button('Refresh', id='rec_database_refresh_button', n_clicks=0, color="primary", className="me-1"),
                                    width="auto"
                                ),
                                dbc.Col(
                                    dbc.Button(' JSON ', id='rec_database_create_json_button', n_clicks=0, color="warning", className="me-1"),
                                    width="auto"
                                ),
                                dbc.Col(
                                    dbc.Button(' CSV  ', id='rec_database_create_csv_button', n_clicks=0, color="warning", className="me-1"),
                                    width="auto"
                                ),
                                dbc.Col(
                                    legend,
                                    width="auto"
                                ),
                                dbc.Col(
                                    dcc.Download(id="download_json"),
                                    width="auto"
                                ),
                            ], justify="start"),
                ],width=9,
                ),
                dbc.Col([
                            audio_component
                ],width=3),
        ], style={ "height":"100%", "width": "100%"}),
        modal,
    ]
    return html.Div(children=custom_childer)


@callback( Output('audio_grid_table','rowData',allow_duplicate=True),
          Output('audio_grid_table','columnDefs',allow_duplicate=True),
          Output('audio_grid_table','selectedRows',allow_duplicate=True), 

          Output('date_picker','start_date',allow_duplicate=True), 
          Output('date_picker','end_date',allow_duplicate=True),
          Input('url', 'pathname'),
          prevent_initial_call=True
)
def refresh_page(p):
    data,columns,str_date_from,str_date_to=get_db_rec()
    start_date=str_date_from
    end_date=str_date_to
    if len(data)>0:
        ret= [data[0]]
    else:
        ret=None
    return data,columns,ret,start_date,end_date


@callback(Output('audio_grid_table','rowData',allow_duplicate=True), 
         Output('audio_grid_table','selectedRows',allow_duplicate=True), 
         Input('rec_database_refresh_button','n_clicks'),
         State('date_picker','start_date'),
         State('date_picker','end_date'),
         prevent_initial_call=True,
)
def refresh_button_db(n_clicks,start_date,end_date):
    data,columns,str_date_from,str_date_to=get_db_rec(start_date,end_date)   
    try:
        if len(data)>0:
            ret= [data[0]]
        else:
            ret=None
    except:
        ret=None
        data=[]
    return data,ret

@callback(
        Output('modal_image','is_open'),
        Output('modal_title_id','children'),
        Output('modal_body','children'),
        Input('audio_component','n_clicks'),
        State('audio_component','title'),
        State('audio_component','poster'),
        prevent_initial_call=True,
)
def zoom_image(click,title,poster):
    modal_title=[title]
    modal_body=html.Img(src=poster,  
                        #height= "80%", 
                        width='70%',
                        )
    return True,modal_title,modal_body

@callback(       
     Output('audio_component','poster'), 
     Output('audio_component','src'), 
     Output('audio_component','title'), 
     Output('audio_component','sound1'), 
     Output('audio_component','sound2'),
     Output('audio_component','sound3'),  
     Input('audio_grid_table','selectedRows'), 
     prevent_initial_call=True,
)
def update_audio_player(selectedRows):
    poster=None
    src=None
    title=None
    sound1=None
    sound2=None
    sound3=None
    if selectedRows is not None and len(selectedRows)>0:
        for selected_row in selectedRows:
           poster=  request.host_url + f"assets/specrogram_images/{selected_row['spectrogram_image']}"
           src=request.host_url+f"assets/audio_mp3/{selected_row['file_name']}"
           title=f"Event_id: {selected_row['event_id']}"
           sound1=f"{selected_row['Audio class 1']}: {selected_row['prob class 1']}"
           sound2=f"{selected_row['Audio class 2']}: {selected_row['prob class 2']}"
           sound3=f"{selected_row['Audio class 3']}: {selected_row['prob class 3']}"
    return poster,src,title,sound1,sound2,sound3
    

@callback(Output('download_json','data',allow_duplicate=True), 
         Input('rec_database_create_json_button','n_clicks'),
         State('audio_grid_table','virtualRowData'),
         prevent_initial_call=True,
)
def create_json(n_clicks,rowData):
    str_json=None
    
    if len(rowData)>0:
        rowData = sorted(rowData, key=lambda d: d['timestamp'])

        my_events=[]
        for event_item in rowData:
   
            ev={
                "event_id": f"evt_{event_item['event_id']}",
                "timestamp": event_item['timestamp'],
                "audio_events": [
                                    {"class": event_item['Audio class 1'],"probability": event_item['prob class 1']},
                                    {"class": event_item['Audio class 2'],"probability": event_item['prob class 2']},
                                    {"class": event_item['Audio class 3'],"probability": event_item['prob class 3']},
                                ],
                "related_to": my_events[-1]['event_id'] if  len(my_events)>0 else ""
                }
            my_events.append(ev)
            
        _json={"events":my_events}
        return  dict(content=json.dumps(_json), filename="sounds.json")
    else:
        return None,None
    


@callback(Output('download_json','data',allow_duplicate=True), 
         Input('rec_database_create_csv_button','n_clicks'),
         State('audio_grid_table','virtualRowData'),
         prevent_initial_call=True,
)
def create_csv(n_clicks,rowData):
    str_json=None
    
    if len(rowData)>0:
        rowData = sorted(rowData, key=lambda d: d['timestamp'])
        df_rowData = pd.DataFrame(rowData)
        df_rowData.drop(['file_name', 'Device','spectrogram_image'], axis='columns', inplace=True)
        #df_rowData.rename(columns={"id": "event_id", "date": "timestamp"}, errors="raise")
        df_rowData['related_to']=[ df_rowData.iloc[index-1]['event_id'] if index!=0 else '' for index in range(len(df_rowData))]

        
        return  dict(content=df_rowData.to_csv(None, index=False), filename="sounds.csv")
    else:
        return None,None
 
#### for delete
#  for event_item in data:
#             if not prev_dev is None and event_item['device_name']!=prev_dev:
#                 devices.append( {"device":prev_dev,"events": my_events})
#                 my_events=[]
        
#             prev_dev=event_item['device_name']
#             ev={
#                 "event_id": f"evt_{event_item['id']}",
#                 "timestamp": event_item['date'],
#                 "audio_events": [
#                                     {
#                                         "class": event_item['sound1'],
#                                         "probability": event_item['conf_sound1'],
#                                         "related_to": my_events[-1]['event_id'] if  len(my_events)>0 else ""
#                                     }
#                                 ]
#                 }
#             my_events.append(ev)
            
#         if devices[-1]['device']!= prev_dev:
#             devices.append( {"device":prev_dev,"events": my_events})
#         _json={"sounds":devices}
# ###