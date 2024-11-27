from pydub import AudioSegment
import os
from datetime import datetime
import sys
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'convert_wav_to_mp3'}

def convert_wav_to_mp3(wav_path, mp3_path=None, bitrate='192k'):
    """
    Convert WAV file to MP3.
    
    Parameters:
    wav_path (str): Path to input WAV file
    mp3_path (str): Path for output MP3 file (optional)
    bitrate (str): Audio bitrate for MP3 (default: '192k')
    
    Returns:
    str: Path to the created MP3 file
    """
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

# Example usage
if __name__ == "__main__":
    # Single file conversion
    wav_file = "assets/55.wav"
    mp3_file = "assets/552.mp3"
    convert_wav_to_mp3(wav_file, mp3_file, bitrate='192k')#320k
    
   