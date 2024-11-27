import dash
from dash import  Dash, dcc, html
from dash.dependencies import Output
from dash.dependencies import Input
import dash_bootstrap_components as dbc
import os
import dash_auth




# def check_CPU_temp():
#     try:
#         with open('/sys/class/thermal/thermal_zone0/temp','r') as f:
#             temp=f.readline()
#             print('CPU Temp',temp)
#             return str(temp)
#     except ValueError:
#         print('Error CPU temp') # catch only error needed
#         return 'Error'
 

USER_PASS_MAPPING={ 'user1':'user1',
                    'user2':'user2',

                    }
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
def create_assets_folder():
    try:
        if not os.path.exists('../assets'):
            os.makedirs('../assets')
    except:
        pass

app = Dash(__name__, 
           use_pages=True, 
           external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],
           #serve_locally=False,
           assets_folder='../assets',
           
           #assets_url_path='assets'
           )


app.server.secret_key = os.urandom(24) 

auth=dash_auth.BasicAuth(app,USER_PASS_MAPPING)

menus_array=[]
for page in dash.page_registry.values():
    menus_array.append(dbc.DropdownMenuItem(page['name'], href=page["relative_path"]))


navbar=dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=menus_array,
            nav=True,
            in_navbar=True,
            right=True,
            #label="More Pages",
        ),
    ],
    brand="Audio Surveillance",
    #brand_href="/",
    color="primary",
    brand_style={"align":"left"},
    dark=True,
    )

def MyNavBar():
    
    navitems=[]
    for page in dash.page_registry.values():
        #if page['name']=='Audio details Dashboard':
        #    active=True
        #else:
        #    active=False
        navitems.append(dbc.NavItem(dbc.NavLink(page['name'], 
                                                href=page["relative_path"],
                                                #active=active,
                                                ),
                                    style={'display': 'flex','color':'white','font-size':'15px','font-weight': 'bold',  'border': '1px solid white', 'border-radius': '25px', 'margin':'5px'}))
    row=html.Div([
          dbc.NavItem(dbc.NavbarBrand("Audio Surveillance", className="ms-4",style={'justify-content':'flex-start','font-size':'35px','font-weight': 'bold'})),
          dbc.Nav(children=navitems,
                  style={'display': 'flex','color':'white','width':'100%','justify-content': 'flex-end','marginRight': '20px'},
                  pills=True, 
                 
                  ),

    ],style={'display': 'flex','width':'100%'})
    return dbc.Navbar(children=row,
                      color="primary",
                      dark=True,
                    )



app.layout=html.Div(children=[
    MyNavBar(),
    dash.page_container
    ]
)

# @app.callback(
#     [Output('live_update_temperature','children'), Input('temperature_interval','n_intervals'),]
# )
# def update_temperature(n):
#     temp=check_CPU_temp()
#     if int(temp) > 70000:
#         return [html.Span([dbc.Badge('Temperature is '+ temp + 'Celsus', pill=True, color="danger", className="me-1"),]),]
#     else:
#         return [html.Span([dbc.Badge('Temperature is '+ temp + 'Celsus', pill=True, color="primary", className="me-1"),]),]
        

if __name__ == '__main__':
    create_assets_folder()
    app.run(
            host='0.0.0.0',
            debug=True,
            dev_tools_hot_reload=False,
            )