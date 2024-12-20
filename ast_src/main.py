from ast_model import AST
import os,sys
import numpy as np
from rec_audio import Recorder
import time
import glob 
from multiprocessing import Process,Pool
import datetime
#import librosa
from pydub import AudioSegment

from  ast_sql_lite import Ast_Sql_lite
from convert_wav_to_mp3 import  *
from create_spectrogram import *
sys.path.append('./mqtt_clent')
sys.path.append('./misc')
from mqtt_client import AudioReceiver
from log_test import logger
LOG_D={'module_name':'main'}

def check_CPU_temp():
    temp=None
    try:
        with open('/sys/class/thermal/thermal_zone0/temp','r') as f:
            temp=f.readline().replace('\n','')
            temp=float(temp)/1000
    except ValueError:
        logger.error('Error CPU temp',extra=LOG_D) 
    return temp

def proc_check_CPU_temp():
    while True:
       temp=check_CPU_temp
       logger.info(f"CPU Temp {temp}",extra=LOG_D)
       time.sleep(20)
    
def convert_rec_to_float(data):
    if data.dtype == np.uint8:
        data = (data - 128) / 128.
    elif data.dtype == np.int16:
        data = data / 32768.
    elif data.dtype == np.int32:
        data = data / 2147483648.
    data = data - np.mean(data,dtype=np.float32)
    return data

def proc(ast,db):
    while True:
        assets_path='./assets'
        audio_files = glob.glob(f"{assets_path}/audiosuser/*_rec.wav") 
        audio_files.extend(glob.glob(f"{assets_path}/audiosuser/*_rec.mp3"))
        audio_files.extend(glob.glob(f"{assets_path}/audios/*_rec.wav")) 
        audio_files.extend(glob.glob(f"{assets_path}/audios/*_rec.mp3"))
        #Path to save new mp3 files
        mp3_path=os.path.join(assets_path,'audio_mp3')
        #Path to save spectrogrm images
        specrogramm_images=os.path.join(assets_path,'specrogram_images')
        #Create folder for mp3 files
        if not os.path.exists(mp3_path):
            os.makedirs(mp3_path)
            logger.info(f"Create folder {mp3_path}",extra=LOG_D)
        #Create folder for spectrogram images
        if not os.path.exists(specrogramm_images):
            os.makedirs(specrogramm_images)
            logger.info(f"Create folder {specrogramm_images}",extra=LOG_D)
        # Loop for preccessed audio files
        for audio_file in audio_files:
            logger.info(f"Proccess file {audio_file}",extra=LOG_D)
           
            #load audio files
            start_inf=datetime.now()
            try:
                if '.wav' in audio_file:
                    audio = AudioSegment.from_wav(audio_file)
                
                elif '.mp3' in audio_file:
                    audio = AudioSegment.from_mp3(audio_file)
                else:
                    audio=None
                    data=[]
                    logger.error(f"Not Supported audio file")
                if not audio is None:
                    sr=audio.frame_rate
                    channels=audio.channels
                    if sr!=16000 or channels!=1:
                        audio=audio.set_frame_rate(16000)
                        audio=audio.set_channels(1)
                        #(sample_rate_Hz=16000, sample_width=2, channels=1)
                        logger.info(f"Resample data",extra=LOG_D)
                    data=np.array(audio.get_array_of_samples())
                    data=convert_rec_to_float(data)
                   
            except Exception as e:
                audio=None
                data=[]
                logger.error(f"Error Load file: {str(e)} ",extra=LOG_D)

           
            #sr=librosa.get_samplerate(audio_file)
            #data,sr=librosa.load(path=audio_file,sr=16000)
            #data = data - np.mean(data,dtype=np.float32)
            logger.info(f"Load file {audio_file} time: {datetime.now()-start_inf}",extra=LOG_D)

            #Check data len
            if len(data)>0 and not audio is None:
                # inference audio data with AST
                pred_labels=ast.inference(data,sr)
                
                #Get Three max Conf  
                max_conf= max(pred_labels, key=lambda x:x['conf'])
                sound1=pred_labels[0]['sound']
                conf_sound1=pred_labels[0]['conf']
                sound2=pred_labels[1]['sound']
                conf_sound2=pred_labels[1]['conf']
                sound3=pred_labels[2]['sound']
                conf_sound3=pred_labels[2]['conf']
                #Sound category for reject
                #reject_sounds=['Hum','Static','Speech','Rumble','Buzzer','Purr','Burst, pop','Burst,pop']
                reject_sounds=['Hum','Static','Rumble','Buzzer','Purr','Burst, pop','Silence','White noise',"Environmental noise","Whoosh, swoosh, swish","Outside, rural or natural"]
                if 'audiosuser' in audio_file:
                    max_conf_thresh=0.0
                else:
                    max_conf_thresh=0.35
               
                #Reject Sounds 
                if max_conf['conf']>max_conf_thresh and (not sound1 in reject_sounds) :
                    #Path for mp3 files
                    if "rec.wav" in audio_file:
                        mp3_file=os.path.join(mp3_path,os.path.basename(audio_file).replace("rec.wav","rec.mp3"))
                    else:
                        mp3_file=os.path.join(mp3_path,os.path.basename(audio_file))
                    #Convert audio to mp3 with bitrate 192k
                    if not convert_raw_data_to_mp3(data, mp3_file, bitrate='192k') is None:
                        if "rec.wav" in audio_file:
                            spectrogram_image=os.path.join(specrogramm_images,os.path.basename(audio_file).replace("rec.wav","rec.png"))
                        else:
                            spectrogram_image=os.path.join(specrogramm_images,os.path.basename(audio_file).replace("rec.mp3","rec.png"))

                        #Create Spectrogram 
                        #if not create_spectrogram(data,sr,spectrogram_image) is None:
                        if not create_freq_analyzer_spectrogram(data,sr,spectrogram_image) is None:
                            if "_rec.wav" in audio_file:    
                                new_audio_file=audio_file.replace("_rec.wav","_rec_pred.wav")
                            else:
                                new_audio_file=audio_file.replace("_rec.mp3","_rec_pred.mp3")
                            
                            try:
                                os.rename(audio_file,new_audio_file)
                            except Exception as e:
                                logger.error(f"Error converting file: {str(e)} ")
                            
                            start_inf=datetime.now()
                            array_filename=os.path.basename(audio_file).split('_')
                            str_date=array_filename[0][0:4]+"-"+array_filename[0][4:6]+"-"+array_filename[0][6:8]
                            str_time=array_filename[1][0:2]+":"+array_filename[1][2:4]+":"+array_filename[1][4:6]
                            if array_filename[2].startswith('ex'):
                                device_name='ex'
                            else:
                                device_name=array_filename[2]
                            db.insert_rec(date=str_date + " " + str_time ,
                                        device_name=device_name,
                                        file_name=os.path.basename(mp3_file),
                                        spectrogram_image=os.path.basename(spectrogram_image),
                                        sound1=sound1,conf_sound1=round(float(conf_sound1),2),
                                        sound2=sound2,conf_sound2=round(float(conf_sound2),2),
                                        sound3=sound3,conf_sound3=round(float(conf_sound3),2))
                            logger.info(f"Write rec to db time: {datetime.now()-start_inf}",extra=LOG_D)
                        else:
                            logger.error(f"Error create spectrogram",extra=LOG_D)
                            try:    
                                logger.warning(f"Delete file {audio_file}",extra=LOG_D)
                                os.remove(audio_file)
                            except:
                                pass
                            try:
                                logger.warning(f"Delete file {mp3_file}",extra=LOG_D)
                                os.remove(mp3_file)        
                            except:
                                pass
                    else:
                        logger.error(f"Error Convert to mp3")
                        try:
                            logger.warning(f"Delete file {audio_file}",extra=LOG_D)
                            os.remove(audio_file)    
                        except:
                            pass
                else:
                    try:
                        logger.warning(f"Delete file {audio_file}",extra=LOG_D)
                        logger.warning(f"Max conf {max_conf['conf']}",extra=LOG_D)
                        logger.warning(f"Sound1 {sound1}",extra=LOG_D)
                        logger.warning(f"Sound2 {sound2}",extra=LOG_D)
                        os.remove(audio_file)
                    except:
                        pass
            else:
                try:
                    logger.error(f"Zero audio file",extra=LOG_D)
                    logger.warning(f"Delete file {audio_file}",extra=LOG_D)
                    os.remove(audio_file)
                except:
                    pass
            temperature=check_CPU_temp()
            if not temperature  is None:
                logger.info(f"Temperature  {temperature}C",extra=LOG_D)        
            if not temperature  is None and temperature>90:
                logger.warning(f"Warning Hi Temperature {temperature}",extra=LOG_D)
                time.sleep(10)
        #db.show_rec()
        logger.info(f"Nothing in loop wait 10 sec",extra=LOG_D) 
        time.sleep(10)

        

if __name__ == "__main__":
    db=Ast_Sql_lite()
    ast=AST()
    receiver = AudioReceiver(save_sound_path='assets/audios',threshold_sound=800)
    receiver.start()
  #  myrec=Recorder(record_seconds=5,save=True,rec_pause=10,save_path='audios',threshold_sound=250000000)
  #  myrec.start()
    #proc_temp=Process(target=proc_check_CPU_temp,args=())
    #proc_temp.start()
    proc(ast,db)
    #proc_temp.join()
    #proc_ast=Process(target=proc,args=(ast,db))
    #proc_ast.start()
    #proc_ast.join()
    db.close()
    #print('Start proc_ast')
    #time.sleep(360)
    #myrec.stop()
    #print('end')
    