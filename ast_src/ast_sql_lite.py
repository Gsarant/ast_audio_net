import sqlite3
import sys
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'ast_sql_lite'}

class Ast_Sql_lite():
    def __init__(self,db_file='ast_audio_db/ast_audio.db'):
        logger.info(f"Init Ast sql lite",extra=LOG_D)  
        try:
            self.conn = sqlite3.connect(db_file)
            self.cursor = self.conn.cursor()
            self.__create_tables__()
        except Exception as e:
            logger.error(f"Error Init Ast sql lite {str(e)} ",extra=LOG_D)

    
    def __del__(self):
        try:
            self.conn.close()
            logger.info(f"Close Ast sql lite",extra=LOG_D)
        except Exception as e:
            logger.error(f"Error close Ast sql lite {str(e)} ",extra=LOG_D)    
    
    def __check_exit_table__(self,table_name):
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = self.cursor.fetchone()
            logger.info(f"Table {table_name} table exist {result}",extra=LOG_D)
        except Exception as e:
            result=None
            logger.error(f"Error checkexist table {str(e)} ",extra=LOG_D)
        return result is not None
    
    def __create_tables__(self):
        if not self.__check_exit_table__('devices'):
            try:
                self.cursor.execute('''CREATE TABLE devices (
                                                            device_name TEXT PRIMARY KEY,
                                                            latitude REAL,
                                                            longitude REAL,
                                                            description TEXT
                                                        );

                                    ''')
                self.conn.commit()
                logger.info(f"Create  device table",extra=LOG_D)
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('raspberry', 35.518915, 24.042270, 'Raspberry Pi located in ELMEPA');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('ex', 40.7128, -74.0060, 'Experimental device in New York');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('esp32s3-1',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('esp32s3-2',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('esp32s3-3',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('esp32s3-4',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('giannis',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('hlias',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                self.cursor.execute('''INSERT INTO devices (device_name, latitude, longitude, description)
                                        VALUES ('herc',35.507127, 23.968207, 'ESP32 device located in Irinis Chania');
                                    ''')
                self.conn.commit()
                logger.info(f"Add records to  device table",extra=LOG_D)
            except Exception as e:
                logger.error(f"Error create devices table {str(e)} ",extra=LOG_D)
        if not self.__check_exit_table__('ast_table'):
            try:
                self.cursor.execute('''CREATE TABLE ast_table (
                                                                    id INTEGER PRIMARY KEY,
                                                                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                                    file_name TEXT NOT NULL,
                                                                    device_name TEXT,
                                                                    spectrogram_image TEXT,
                                                                    sound1 TEXT,
                                                                    conf_sound1 FLOAT,
                                                                    sound2 TEXT,
                                                                    conf_sound2 FLOAT,
                                                                    sound3 TEXT,
                                                                    conf_sound3 FLOAT,
                                                                    FOREIGN KEY (device_name) REFERENCES devices(device_name)
                                                                );
                                    '''
                                    )
                self.conn.commit()
                logger.info(f"Create  ast_table table",extra=LOG_D)
            except Exception as e:
                logger.error(f"Error create ast_table table {str(e)} ",extra=LOG_D)
    def insert_rec(self,date=None,device_name=None,file_name=None,spectrogram_image=None,sound1=None,conf_sound1=None,sound2=None,conf_sound2=None,sound3=None,conf_sound3=None):
        try:
            if  not file_name is None and  not spectrogram_image is None and not sound1 is None and not conf_sound1 is None and not sound2 is None and not conf_sound2 is None and not sound3 is None and not conf_sound3 is None:
                if device_name is None:
                    device_name='raspberry'
                if date is None:
                    sql_query=f"INSERT INTO ast_table ( file_name, device_name, spectrogram_image, sound1, conf_sound1, sound2, conf_sound2,sound3, conf_sound3 ) VALUES (\"{file_name}\", \"{device_name}\", \"{spectrogram_image}\", \"{sound1}\", {conf_sound1}, \"{sound2}\", {conf_sound2}, \"{sound3}\", {conf_sound3});"
                else:
                    sql_query= f"INSERT INTO ast_table ( date,file_name, device_name, spectrogram_image, sound1, conf_sound1, sound2, conf_sound2,sound3, conf_sound3 ) VALUES (\"{date}\", \"{file_name}\", \"{device_name}\", \"{spectrogram_image}\", \"{sound1}\", {conf_sound1}, \"{sound2}\", {conf_sound2}, \"{sound3}\", {conf_sound3});"
               
                self.cursor.execute(sql_query)
                self.conn.commit()
                logger.info(f"DB Insert {sql_query}",extra=LOG_D)
        except Exception as e:
            logger.error(f"Error DB Insert {sql_query}",extra=LOG_D)
            
    
    def show_rec(self):
        result= self.cursor.execute(f"SELECT * FROM  ast_table ;")
        logger.info(f"db fetch {result.fetchall()}",extra=LOG_D)
    
    def close(self):
        self.__del__()
        