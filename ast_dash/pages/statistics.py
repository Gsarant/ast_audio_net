import dash
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pandas as pd
from datetime import datetime
import numpy as np
from dash import  html,callback,get_app,Output,Input,State,dcc
import dash_bootstrap_components as dbc
import os, sys
from sql_to_pandas import SQL_to_Pandas
import sys
sys.path.append("..")
from misc.misc import *
from sql_to_pandas import SQL_to_Pandas


app=get_app()



dash.register_page(
    __name__,
    path='/statistics',
    title='Statistics Dashboard',
    name='Statistics Dashboard'
)
# Συνάρτηση για φόρτωση δεδομένων από τη βάση
def load_data(str_date_from=None, str_date_to=None):
    sql_to_pandas=SQL_to_Pandas()
    if (str_date_from is None or  str_date_to is None) or str_to_date(str_date_from)>=str_to_date(str_date_to):
        dt_date_from = get_date_before(get_now_date(),7)
        dt_date_to = get_date_after(get_now_date(),0)
        str_date_from = date_to_str(dt_date_from)
        str_date_to = date_to_str(dt_date_to)
    else:
        dt_date_from = get_date_00(str_date_from)
        dt_date_to = get_date_99(str_date_to) 
        str_date_from = date_to_str(dt_date_from)
        str_date_to = date_to_str(dt_date_to)
    df=sql_to_pandas.get_date_from_to(str_date_from,str_date_to)
    del(sql_to_pandas)
    df['date'] = pd.to_datetime(df['date'])
    return df,str_date_from,str_date_to

_,str_date_from,str_date_to=load_data()


# Styles
CONTROLS_STYLE = {
    'backgroundColor': '#f8f9fa',
    'padding': '20px',
    'borderRight': '1px solid #ddd',
    #'minHeight': '100vh',
    #'width': '250px'
}

CONTENT_STYLE = {
    'margin-left': '10px',
    'padding': '10px'
}

# Layout της εφαρμογής
def layout(**kwargs):
    custom_childer=[
            dbc.Row([
                    dbc.Col([
                    # Left Controls Panel
                            html.Div([
                              
                                # Date Range
                                html.Div([
                                    html.Label('Date Range'),
                                    dcc.DatePickerRange(
                                        id='date_picker',
                                        month_format='M-D-Y',
                                        display_format='YYYY/MM/DD',

                                        #min_date_allowed=str_to_date(str_date_from),
                                        #max_date_allowed=str_to_date(str_date_to),
                                        start_date=str_to_date(str_date_from),
                                        end_date=str_to_date(str_date_to),
                                        style = {
                                                'fontSize': '6px','display': 'inline-block', 'border-radius' : '2px', 
                                                'border' : '1px solid #ccc', 'color': '#333', 
                                                'border-spacing' : '0', 'border-collapse' :'separate'
                                                    } 
                                    )
                                ]),
        
                                # # Resample Resolution
                                # html.Div([
                                #     html.Label('Resample Resolution'),
                                #     dcc.RadioItems(
                                #         options=[
                                #             {'label': 'Raw', 'value': 'raw'},
                                #             {'label': '15 minutes', 'value': '15min'},
                                #             {'label': 'Hourly', 'value': 'hourly'},
                                #             {'label': 'DAILY', 'value': 'daily'}
                                #         ],
                                #         value='raw',
                                #         id='resample_resolution',
                                #         style={'marginBottom': '20px'}
                                #     )
                                # ]),
                                

                                html.Div([
                                    html.Label(children=['Select #Audio classes to show'], id='label_sounds_slider'),
                                    dcc.Slider(
                                        id='sounds_slider',
                                        min=1,
                                        max=100,
                                        value=10,
                                        marks={1: '1', 25: '25', 50: '50', 75: '75', 100: '100'},
                                        step=1
                                    )
                                ])
                            ], ),
                    ],width=2,style=CONTROLS_STYLE),
                    dbc.Col([
                            # Main Content
                               dbc.Row([
        
                                    dcc.Dropdown(
                                        id='sounds_selector',
                                        options=[{'label': 'All', 'value': 'All'}],
                                        value='All',
                                        style={'marginBottom': '10px'}
                                    ),
                                ]),
                                dbc.Row([
                                    dbc.Col([
                                            # Charts
                                                # Top Species Chart
                                                dcc.Graph(
                                                    id='top_species_chart',
                                                ),
                                    ],width=6),
                                    dbc.Col([
                                        # Daily Pattern Chart
                                        dcc.Graph(
                                            id='daily_pattern',
                                        )
                                    ],width=6)
                                ]),
                                   
                                    # Timeline Chart
                                dbc.Row([    
                                    dcc.Graph(id='timeline'),
                                ]),
                                dbc.Row([
                                    # Total Detections
                                    html.Div(id='total_detections', style={'textAlign': 'center'})
                                ]),
                              
                    ],width=10)
            ])
       
    ]
    return html.Div(children=custom_childer,style={'width':'100%', 'height':'80%'})

# Callbacks
@callback(
    Output('top_species_chart', 'figure'),
     Output('daily_pattern', 'figure'),
     Output('timeline', 'figure'),
     Output('sounds_selector', 'options'),
     Output('total_detections', 'children'),
     Output('label_sounds_slider','children'),
     Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('sounds_selector', 'value'),
     #Input('resample_resolution', 'value'),
     Input('sounds_slider', 'value'),
     #prevent_initial_call=True,
)
def update_graphs(start_date, end_date, selected_sound,  num_sounds):
    df,_,_ = load_data(start_date, end_date)
   
     
    # Calculate total detections
    valid_sounds = len(df)
    
    # Filter for specific bird if selected
    if selected_sound != 'All':
        mask = (df['sound1'] == selected_sound) 
              # (df['sound2'] == selected_bird) | \
              # (df['sound3'] == selected_bird)
        df = df[mask]
    
    # Apply resampling if needed
    #if resolution != 'raw':
    #    df = resample_data(df, resolution)
    
    # Create figures
    if selected_sound != 'All':
        top_species_fig = create_top_species_chart(df.iloc[0:0], 1)
    else:    
        top_species_fig = create_top_species_chart(df, num_sounds)
    daily_pattern_fig = create_daily_pattern(df)
    timeline_fig = create_timeline(df,start_date,end_date)
    
    # Update bird options
    sounds_options = update_sound_options(df)
    
    return (
        top_species_fig,
        daily_pattern_fig,
        timeline_fig,
        sounds_options,
        f'Total Detections: {valid_sounds:,}',
        [f"Select {num_sounds} Audio classes to show"]
        

    )

def resample_data(df, resolution):
    """Resample data based on selected resolution"""
    if resolution == '15min':
        return df.resample('15T', on='date').count()
    elif resolution == 'hourly':
        return df.resample('H', on='date').count()
    elif resolution == 'daily':
        return df.resample('D', on='date').count()
    return df

def create_top_species_chart(df, num_sounds):
    """Δημιουργία γραφήματος top species"""
    all_sounds = pd.concat([
        df[['sound1', 'conf_sound1']].rename(columns={'sound1': 'sound', 'conf_sound1': 'confidence'}),
       # df[['sound2', 'conf_sound2']].rename(columns={'sound2': 'sound', 'conf_sound2': 'confidence'}),
        #df[['sound3', 'conf_sound3']].rename(columns={'sound3': 'sound', 'conf_sound3': 'confidence'})
    ])
    
    species_counts = all_sounds['sound'].dropna().value_counts().head(num_sounds)
    
    fig = go.Figure(go.Bar(
        x=species_counts.values,
        y=species_counts.index,
        orientation='h',
        marker_color='#2E8B57'
    ))
    
    fig.update_layout(
        title=f'Top {num_sounds} Audio classes in Date Range',
        xaxis_title='Number of Detections',
        yaxis_title='Audio classes',
        #height=550,
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')
    
    return fig

def create_daily_pattern(df):
    """Δημιουργία γραφήματος ημερήσιου μοτίβου"""
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    hourly_counts = df.groupby('hour').size()
    
    for hour in range(24):
        if hour not in hourly_counts.index:
            hourly_counts[hour] = 0
    hourly_counts = hourly_counts.sort_index()
    
    fig = go.Figure(go.Barpolar(
        r=hourly_counts.values,
        theta=np.linspace(0, 360, 24, endpoint=False),
        marker_color='#2E8B57',
        opacity=0.8,
        width=360/24
    ))
    
    fig.update_layout(
        title='Daily Activity Pattern',
        polar=dict(
            radialaxis=dict(showticklabels=True, ticks=''),
            angularaxis=dict(
                ticktext=['12am','1am','2am','3am','4am','5am','6am','7am',
                         '8am','9am','10am','11am','12pm','1pm','2pm','3pm',
                         '4pm','5pm','6pm','7pm','8pm','9pm','10pm','11pm'],
                tickvals=list(range(0, 360, 15)),
                direction='clockwise',
                period=24
            )
        ),
        #height=550,
        margin=dict(l=10, r=30, t=30, b=20)
    )
    
    return fig

def create_timeline(df, start_date=None, end_date=None):
    # Μετατροπή της στήλης date σε datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Μετατροπή των ημερομηνιών σε datetime και προσθήκη ώρας
    if start_date is None:
        start = df['date'].min()
    else:
        start = pd.to_datetime(start_date + ' 00:00:00')
    if end_date is None:
        end_date = df['date'].max()
    else:
        end = pd.to_datetime(end_date + ' 23:59:59')
    
    # Φιλτράρισμα για το επιλεγμένο εύρος
    mask = (df['date'] >= start) & (df['date'] <= end)
    df_filtered = df.loc[mask].copy()
    
    # Ομαδοποίηση ανά ώρα
    hourly_counts = df_filtered.groupby(df_filtered['date'].dt.floor('H')).size().reset_index(name='count')
    
    # Δημιουργία πλήρους χρονοσειράς με μηδενικά για τις κενές ώρες
    full_range = pd.date_range(start=start, end=end, freq='H')
    hourly_counts = hourly_counts.set_index('date').reindex(full_range, fill_value=0).reset_index()
    hourly_counts.columns = ['date', 'count']
    
    # Δημιουργία του γραφήματος
    fig = go.Figure()
    
    # Προσθήκη της κύριας γραμμής
    fig.add_trace(go.Scatter(
        x=hourly_counts['date'],
        y=hourly_counts['count'],
        mode='lines+markers',  # Προσθήκη markers για κάθε ώρα
        name='Detections',
        line=dict(color='#2E8B57', width=1.5),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(70, 130, 180, 0.2)'
    ))
    
    # Ενημέρωση της διάταξης
    fig.update_layout(
        title={
            'text': 'Hourly Detections' ,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=16)
        },
        xaxis_title='Date/Time',
        yaxis_title='Number of Detections',
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
        yaxis=dict(
            gridcolor='lightgrey',
            rangemode='tozero',
            zeroline=True,
            zerolinecolor='lightgrey',
            tickformat='d',  # Ακέραιοι αριθμοί
            dtick=10  # Διάστημα μεταξύ των τιμών στον άξονα y
        ),
        xaxis=dict(
            gridcolor='lightgrey',
            rangeslider=dict(visible=True),
            type='date',
            #tickformat='%d/%m %H:00',  # Μορφή ημερομηνίας/ώρας
            tickformat='%d/%m',  # Μορφή ημερομηνίας/ώρας
            dtick='H1'  # Εμφάνιση κάθε ώρας
        )
    )
    
    # Προσαρμογή του hover
    fig.update_traces(
        hovertemplate="<b>Date/Time</b>: %{x|%d/%m/%Y %H:00}<br>" +
                      "<b>Number of Detections</b>: %{y}<br>" +
                      "<extra></extra>"
    )
    
    return fig

def update_sound_options(df):
    """Ενημέρωση επιλογών πουλιών για το dropdown"""
    all_sounds = pd.unique(pd.concat([
        df['sound1'].dropna(),
        #df['sound2'].dropna(),
        #df['sound3'].dropna()
    ]))
    
    options = [{'label': 'All', 'value': 'All'}]
    options.extend([
        {'label': bird, 'value': bird}
        for bird in sorted(all_sounds)
        if bird is not None and str(bird).strip() != ''
    ])
    
    return options
