from pydub import AudioSegment
import os
from datetime import datetime
import sys
from io import BytesIO
import numpy as np
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'convert_wav_to_mp3'}

def convert_wav_to_mp3(wav_path, mp3_path=None, bitrate='192k'):
   
    try:
        # If mp3_path is not provided, create it from wav_path
        # Load WAV file
        start_inf=datetime.now()
        if '.wav' in wav_path:
            audio = AudioSegment.from_wav(wav_path)
        elif '.mp3' in wav_path:
            audio = AudioSegment.from_mp3(wav_path)
        else:
            logger.error(f"Not Supported audio file")
            return None
        
        # Export as MP3
        audio.export(
            mp3_path,
            format='mp3',
            bitrate=bitrate,
            tags={
                'artist': 'Converted with Python',
                'title': os.path.basename(mp3_path)
            }
        )
        logger.info(f"Successfully converted {wav_path} to {mp3_path}",extra=LOG_D)
        logger.info(f"Convert to mp3 time: {datetime.now()-start_inf}",extra=LOG_D)
        return mp3_path
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)} ",extra=LOG_D)
        return None
    

def convert_raw_data_to_mp3(data, mp3_path=None, bitrate='192k'):
    
    try:
        start_inf=datetime.now()
        data = np.int16(data * 2 ** 15)
        audio = AudioSegment.from_raw(BytesIO(data),
                                    sample_width=2, 
                                    channels=1,
                                    frame_rate=16000
                                    )
        # Export as MP3
        audio.export(
            mp3_path,
            format='mp3',
            bitrate=bitrate,
            tags={
                'title': os.path.basename(mp3_path)
            }
        )
        logger.info(f"Convert to mp3 time: {datetime.now()-start_inf}",extra=LOG_D)
        return mp3_path
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)} ",extra=LOG_D)
        return None
    
def convert_audio_to_mp3(audio, mp3_path=None, bitrate='192k'):
   
    try:
        
        start_inf=datetime.now()
        # Export as MP3
        audio.export(
            mp3_path,
            format='mp3',
            bitrate=bitrate,
            tags={
                'artist': 'Converted with Python',
                'title': os.path.basename(mp3_path)
            }
        )
        logger.info(f"Successfully converted  to {mp3_path}",extra=LOG_D)
        logger.info(f"Convert to mp3 time: {datetime.now()-start_inf}",extra=LOG_D)
        return mp3_path
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)} ",extra=LOG_D)
        return None

# Example usage
if __name__ == "__main__":
    # Single file conversion
    wav_file = "assets/55.wav"
    mp3_file = "assets/552.mp3"
    convert_wav_to_mp3(wav_file, mp3_file, bitrate='192k')#320k
    
   