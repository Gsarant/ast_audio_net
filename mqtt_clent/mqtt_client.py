import paho.mqtt.client as mqtt
import base64
import json
import os,sys
from datetime import datetime
#from misc.misc import *
sys.path.append("misc/")
from misc import *
import wave
#import soundfile as sd

#import librosa
import numpy as np
from multiprocessing import Process,Pool
import time
import math
import sys
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'mqtt_client'}

class Record:
    def __init__(self,chunks,total_chunks,samplerate,sender_name,topic):
        self.chunks = chunks
        self.total_chunks = total_chunks
        #self.current_recording = None
        self.samplerate=samplerate
        self.sender_name=sender_name
        self.topic=topic

class AudioReceiver:
    def __init__(self,host='127.0.0.1',port=1883,username='rasp4',password='ast-rasp4',save_sound_path=None,threshold_sound=9200):
        start_inf=datetime.now()

        self.save_sound_path=save_sound_path
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.threshold_sound=threshold_sound
        self.client.connect(host, port, 60)
        self.rec=[]
        logger.info(f"Init MQTT time: {datetime.now()-start_inf}",extra=LOG_D)
        try:
            if not os.path.exists(self.save_sound_path):
                os.makedirs(self.save_sound_path)
        except Exception as e:
            logger.error(f"Error create folder : {str(e)} ",extra=LOG_D)
        # self.chunks = {}
        # self.total_chunks = 0
        # self.current_recording = None
        # self.samplerate=None
        # self.sender_name=None

    def __del__(self):
        self.stop()

    def __on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected with result code {rc}",extra=LOG_D)
        client.subscribe("audio/recordings/#")
        
    def __on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            
            if "info" in topic_parts:
                # Νέα εγγραφή ξεκινάει
                info = json.loads(msg.payload)
                # self.total_chunks = info['chunks']
                # self.chunks = {}
                # self.samplerate=info['samplerate']
                # self.sender_name=info['username']
                for r in self.rec:
                    if r.topic==('/').join(topic_parts[:-1]):
                        self.rec.remove(r)
                        del(r)
                        break
                self.rec.append(Record(chunks={},total_chunks=info['chunks'],samplerate=info['samplerate'],sender_name=info['username'],topic=('/').join(topic_parts[:-1])))
                logger.info(f"New recording starting: {info}",extra=LOG_D)
                
            elif "chunk" in topic_parts:
                chunk_num = int(topic_parts[-1])
                #self.chunks[chunk_num] = msg.payload
                for r in self.rec:
                    if r.topic==('/').join(topic_parts[:-2]):
                        r.chunks[chunk_num]= msg.payload
                        if chunk_num==1:
                            logger.info(f"Received chunk {msg.topic}   {chunk_num}/{r.total_chunks-1}",extra=LOG_D)
                        break
                
                #print(f"Received chunk {msg.topic}" )
                
            elif "complete" in topic_parts:
                #print('Complete', msg.payload)
                for r in self.rec:
                    if r.topic==('/').join(topic_parts[:-1]):
                        logger.info(f"Complete {r.sender_name} {msg.payload}",extra=LOG_D)
                        # Ολοκλήρωση εγγραφής
                        info = json.loads(msg.payload)

                        if info['successful_chunks'] == info['total_chunks']:
                            self.__save_recording__(r)
                            self.rec.remove(r)
                            del(r)
                            break
                        #self.sender_name=None
            else:
                logger.info(f"Other topic {topic_parts}",extra=LOG_D)
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}",extra=LOG_D)
    
    def __check_sound_and_reject(self,frames):
        frames=[pow(x,2) for x in frames]
        #energy = np.sum(frames)
        #logger.info(f" Energy :{energy} Threshold {self.threshold_sound}",extra=LOG_D)
        rms_energy= round(math.sqrt(np.mean(frames)),0)
        logger.info(f"RMS: {rms_energy} Threshold {self.threshold_sound}",extra=LOG_D)
        if rms_energy< self.threshold_sound:
            return True
        else:
            return False
        
    def __save_recording__(self,r):
        
        try:
            # Συναρμολόγηση των chunks
            audio_data = bytearray()
            for i in range(r.total_chunks):
                if i in r.chunks:
                    audio_data.extend(r.chunks[i])
                else:
                    logger.warning(f"Missing chunk {i}",extra=LOG_D)
                    #self.chunks = {}
                    #self.total_chunks = 0
                    return 
            int16_data = np.frombuffer(audio_data, dtype=np.int16)
            try:
                sample_rate=r.samplerate
                channels=1
                sample_width=2
                int16_data=int16_data[0:int(math.floor(len(int16_data) / (sample_rate * channels )) * sample_rate * channels)]
                int16_data=self.__apply_fadeout(int16_data,sample_rate,channels,300)
            except:
                pass
            if  r.sender_name is None:
                 #self.sender_name='Unknown'
                logger.warning(f"Missing name ",extra=LOG_D)
                #self.chunks = {}
                #self.total_chunks = 0
                return
            if self.__check_sound_and_reject(int16_data):
                logger.warning(f"Reject sound user {r.sender_name}",extra=LOG_D)
                #self.chunks = {}
                #self.total_chunks = 0
                return
            # Αποθήκευση σε αρχείο
            if not self.save_sound_path is None and os.path.exists(self.save_sound_path):
                filename = os.path.join(self.save_sound_path,f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ r.sender_name}_rec.wav")
            else:
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ r.sender_name}_rec.wav"
           # with open(filename, 'wb') as f:
            #    f.write(audio_data)
            if   r.samplerate is None:
                return
            self.__raw_to_wav(input_raw=int16_data,
                           output_wav=filename,
                            sample_rate=r.samplerate)
           
            
        except Exception as e:
            logger.error(f"Error saving recording: {e}",extra=LOG_D)
        finally:
            pass
            #self.chunks = {}
            #self.total_chunks = 0

    def __apply_fadeout(self,audio_array, sample_rate, channels, fadeout_ms=500):
        
        # Reshape if stereo
        if channels == 2:
            audio_array = audio_array.reshape(-1, 2)
        
        # Calculate number of samples for fadeout
        fadeout_samples = int((fadeout_ms / 1000.0) * sample_rate)
        
        # Create fadeout envelope
        fadeout = np.linspace(1.0, 0.0, fadeout_samples)
        
        # Apply fadeout to the end of the audio
        if channels == 2:
            # For stereo, apply to both channels
            audio_array[-fadeout_samples:, 0] = audio_array[-fadeout_samples:, 0] * fadeout
            audio_array[-fadeout_samples:, 1] = audio_array[-fadeout_samples:, 1] * fadeout
        else:
            # For mono
            audio_array[-fadeout_samples:] = audio_array[-fadeout_samples:] * fadeout
        
        # Convert back to bytes
        return audio_array
    def __align_audio_data(self,input_raw, channels, sample_width):
        """
        Ευθυγραμμίζει τα bytes του ήχου ώστε να ταιριάζουν ακριβώς με τα frames.
        
        Parameters:
        input_raw: bytes object με τα δεδομένα του ήχου
        channels: αριθμός καναλιών (1 για mono, 2 για stereo)
        sample_width: bytes ανά δείγμα (συνήθως 2 για 16-bit)
        
        Returns:
        bytes object με σωστά ευθυγραμμισμένα frames
        """
        # Υπολογισμός μεγέθους frame
        frame_size = channels * sample_width
        
        # Υπολογισμός πόσα ολόκληρα frames έχουμε
        num_frames = len(input_raw) // frame_size
        
        # Κόψιμο σε ακριβές πολλαπλάσιο του frame_size
        aligned_size = num_frames * frame_size
        
        # Μετατροπή σε numpy array για ακριβή χειρισμό
        audio_array = np.frombuffer(input_raw[:aligned_size], dtype=np.int16)
        
        if channels == 2:
            # Αν είναι stereo, επιβεβαίωση ότι έχουμε ζυγό αριθμό δειγμάτων
            if len(audio_array) % 2 != 0:
                audio_array = audio_array[:-1]
            audio_array = audio_array.reshape(-1, 2)
        
        # Εφαρμογή μικρού fadeout στο τέλος για αποφυγή clicks
        fade_samples = min(100, len(audio_array))  # 100 samples fadeout
        fade = np.linspace(1.0, 0.0, fade_samples)
        
        if channels == 2:
            audio_array[-fade_samples:, 0] *= fade
            audio_array[-fade_samples:, 1] *= fade
        else:
                audio_array[-fade_samples:] *= fade
        
        # Προσθήκη μηδενικών στο τέλος για να εξασφαλίσουμε καθαρό τέλος
        padding = np.zeros(100, dtype=np.int16)  # 100 samples padding
        if channels == 2:
            padding = padding.reshape(-1, 2)
            final_array = np.vstack([audio_array, padding])
        else:
            final_array = np.concatenate([audio_array, padding])
        
        return final_array.tobytes()
    
    def __raw_to_wav(self,input_raw, output_wav, channels=1, sample_width=2, sample_rate=16000):
       
        try:
            with wave.open(output_wav, 'wb') as wav_file:
                wav_file.setnchannels(channels)        # mono
                wav_file.setsampwidth(sample_width)        # 2 bytes per sample (16-bit)
                wav_file.setframerate(sample_rate)    # 44.1kHz sample rate
                wav_file.writeframes(input_raw)
            
            #librosa.output.write_wav(path=output_wav,
            #                         y=input_raw,
            #                         sr=sample_rate)
            
            #sd.write(file=output_wav,data=input_raw,samplerate=sample_rate,subtype='FLOAT')
            logger.info(f"Save {output_wav}",extra=LOG_D)    
            logger.info(f"Size of file: {len(input_raw)} bytes",extra=LOG_D)
            logger.info(f"Duration: {len(input_raw) / (sample_rate * channels ):.2f} seconds",extra=LOG_D)
            logger.info(f"Saved recording to {output_wav}",extra=LOG_D)
        except Exception as e:
            logger.error(f"Conversion error : {str(e)}",extra=LOG_D) 

    def __run__(self):
        #self.client.loop_start()
        self.client.loop_forever()
       

    def start(self):
        self.proc_ast_mqtt=Process(target=self.__run__)
        self.proc_ast_mqtt.start()
        #self.proc_ast_mqtt.join()
        
    def stop(self):
        if  not self.proc_ast_mqtt is None:
             self.proc_ast_mqtt.kill()
             self.proc_ast_mqtt.join()
             self.proc_ast_mqtt.close()

    

   
    

def main():
    receiver = AudioReceiver()
    receiver.start()
    while True:
        logger.info('Ok main')
        time.sleep(10)

if __name__ == "__main__":
    logger.info(get_now_str())
    main()