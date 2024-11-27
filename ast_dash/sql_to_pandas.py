import pandas as pd
import sqlite3

class SQL_to_Pandas():
    def __init__(self,db_file='../ast_audio.db'):
        self.conn=  sqlite3.connect(db_file)
        self.df=None
    def __del__(self):
        self.conn.close()
    def rename_columns(self,df):
        return df.rename(columns={"id": "event_id", 
                                "date": "timestamp",
                                "device_name":"Device",
                                "sound1":"Audio class 1",
                                "conf_sound1":"prob class 1",
                                "sound2":"Audio class 2",
                                "conf_sound2":"prob class 2",
                                "sound3":"Audio class 3",
                                "conf_sound3":"prob class 3",
                                 })
    def get_columns(self,df):
        def fun_cellStyle(field):
            if field=='prob class 1' or field=='prob class 2' or  field=='prob class 3':
               return{
                    "styleConditions": [
                                             {
                                                 "condition": "params.value >= 0.5",
                                                 "style": {"backgroundColor": "pink"},
                                             },
                                             {
                                                 "condition": "params.value > 0.3 && params.value < 0.5 ",
                                                 "style": {"backgroundColor": "yellow"},
                                             }
                                         ],
                   # "defaultStyle": {"backgroundColor": "white"},
                }
            else:
                return {
                    #"defaultStyle": {"backgroundColor": "white"}
                    }
        
        
        
        if df is None:
            df = pd.read_sql_query("SELECT * FROM ast_table ORDER BY  date ASC LIMIT 1", self.conn)
        columns= []
        #columns= [{"field": i} for i in df.columns ]
        for i in df.columns:
            if i=='spectrogram_image' or i=='file_name':
                tmp_field={"field": i, 'hide': True, 'cellStyle':fun_cellStyle(i)}
                #tmp_field={"field": i, 'hide': True}
            else:
                tmp_field={"field": i, 'hide': False,  'cellStyle':fun_cellStyle(i)}
                #tmp_field={"field": i, 'hide': False}
            columns.append(tmp_field)
                
        return columns
    

    def get_all_rec(self):
        self.df = pd.read_sql_query("SELECT * FROM ast_table ORDER BY  date DESC", self.conn)
        return self.df
    def get_first_rec(self):
        self.df = pd.read_sql_query("SELECT  * FROM ast_table ORDER BY  date ASC LIMIT 1", self.conn)
        return self.df
    def get_last_rec(self):
        self.df = pd.read_sql_query("SELECT  * FROM ast_table ORDER BY  date DESC LIMIT 1", self.conn)
        return self.df
    def get_date_from_to(self,date_from=None,date_to=None):
        if (not date_from is None and not date_to is None) and date_to>date_from:
            self.df = pd.read_sql_query(f"SELECT * FROM ast_table WHERE date BETWEEN '{date_from}' AND '{date_to}' ORDER BY  date DESC", self.conn)
        else:
            self.df = pd.read_sql_query("SELECT * FROM ast_table ORDER BY  date DESC", self.conn)
        return self.df

