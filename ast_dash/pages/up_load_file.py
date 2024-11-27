import dash
from dash import  html,callback,get_app,Output,Input,State,dcc
import dash_bootstrap_components as dbc
import os, sys
import datetime
import base64
import time 
from flask import request

sys.path.append("..")
from misc.misc import *

app=get_app()

UPLOAD_DIRECTORY = "../assets/audiosuser"

dash.register_page(
    __name__,
    path='/upload_files',
    title='Upload File',
    name='Upload File'
)


def layout(**kwargs):
    custom_childer=[
       html.Div('Upload only wav or mp3 files'),
       html.Div([
                dcc.Upload(
                        id='upload_audio_file',
                        children=html.Div(['Drag and Drop or ',
                                            html.A('Select Files')
                        ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True,
               # accept='audio/wav|audio/mp3',
            ),
            html.Hr(),
            html.Div(id='output_audio_upload'),
        ]),
        html.Hr(),
        html.Div(
            dbc.Button('Upload', id='upload_button' ,n_clicks=0, color="primary", className="me-1"),
        ),
        html.Hr(),
        html.Div(id='results')

    ]
    return html.Div(children=custom_childer)


@callback(Output('output_audio_upload', 'children',allow_duplicate=True),
          Input('upload_audio_file', 'filename'),
         prevent_initial_call=True,
)
def update_output( list_of_names):
    if list_of_names is not None:

        children = [ ',  '.join(list_of_names)]
        return children
    
    
@callback(Output('output_audio_upload', 'children',allow_duplicate=True),
          Output('results','children'),
          Input('upload_button','n_clicks'),
          State('upload_audio_file', 'contents'),
          State('upload_audio_file', 'filename'),
         prevent_initial_call=True,
)
def update_output(n_clicks,list_of_contents, list_of_names):
    try:
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)
    except:
        pass
    output=[]
    if list_of_contents is not None:
        for index,(content,name) in enumerate(zip(list_of_contents, list_of_names)):
            try:
                # Έλεγχος για WAV αρχείο
                if name.lower().endswith('.wav') or name.lower().endswith('.mp3'):
                    username=None
                    try:
                        username = request.authorization['username']
                    except:
                        username='user1'
                    # Δημιουργία ονόματος με timestamp
                    loop_wait=True
                    while loop_wait:
                        if name.lower().endswith('.wav'):
                            rec_file_name=os.path.join(UPLOAD_DIRECTORY,f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{username}_rec.wav")
                        elif name.lower().endswith('.mp3'):
                            rec_file_name=os.path.join(UPLOAD_DIRECTORY,f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{username}_rec.mp3")
                        if not os.path.exists(rec_file_name):
                            loop_wait=False
                        else:
                            time.sleep(1)

                    # Αποκωδικοποίηση και αποθήκευση
                    content_type, content_string = content.split(',')
                    decoded = base64.b64decode(content_string)

                    with open(rec_file_name, 'wb') as fp:
                        fp.write(decoded)
                
                    output.append( html.Div([
                                            html.P(f'File saved as: {rec_file_name}',
                                            style={'color': 'green'}),
                                            ])
                                )
                
            except Exception as e:
                return None, html.Div([
                    'Error saving file:',
                    html.Br(),
                    str(e)
                ], style={'color': 'red'})
    
    return None,[a for a in output]