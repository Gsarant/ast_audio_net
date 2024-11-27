import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime
import sys
sys.path.append('./misc')
from log_test import logger
LOG_D={'module_name':'create_spectrogram'}


def create_spectrogram(audio_data,audio_sr ,save_path=None):
    try:
        # Create figure and axes
        plt.figure(figsize=(12, 8))
        
        # Create spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
        
        # Display spectrogram
        librosa.display.specshow(
            D,
            y_axis='hz',
            x_axis='time',
            sr=audio_sr,
            cmap='magma_r',  # Similar to the purple-orange colormap in your example
            vmin=-120,  # Adjust these values to match your desired dB range
            vmax=0
        )
        
        # Customize the plot
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        
        # Add frequency axis labels
        plt.ylabel('Frequency (kHz)')
        plt.xlabel('Time (s)')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if path is provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            return None
       
    except Exception as error:
        logger.error(f"Error create spectrogram error {str(error)} ",extra=LOG_D)
        return None
    

def create_freq_analyzer_spectrogram(audio_data, audio_sr, save_path=None):
    try:
        start_inf=datetime.now()

        # Υπολογισμός STFT με συγκεκριμένο μέγεθος παραθύρου
        n_fft = 2048  # Μέγεθος παραθύρου FFT
        D = librosa.stft(audio_data, n_fft=n_fft)
        D_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Υπολογισμός του μέσου φάσματος συχνοτήτων
        freq_spectrum = np.mean(np.abs(D), axis=1)
        freq_db = librosa.amplitude_to_db(freq_spectrum, ref=np.max)
        frequencies = librosa.fft_frequencies(sr=audio_sr, n_fft=n_fft)
        
        # Δημιουργία figure με δύο subplots
        fig = plt.figure(figsize=(12, 10))
        gs = plt.GridSpec(2, 1, height_ratios=[1, 3], hspace=0.3)
        
        # Frequency Analyzer (πάνω subplot)
        ax0 = fig.add_subplot(gs[0])
        ax0.plot(frequencies, freq_db, color='#4682B4', linewidth=1.5)
        ax0.set_xlim(0, audio_sr/2)
        ax0.set_ylim(freq_db.min(), freq_db.max() + 10)
        ax0.set_ylabel('Magnitude (dB)')
        ax0.set_title('Frequency Analyzer', pad=10)
        ax0.grid(True, linestyle='--', alpha=0.7)
        
        # Προσθήκη kHz labels στον άξονα x του analyzer
        ax0.set_xlabel('Frequency (kHz)')
        x_ticks = np.linspace(0, audio_sr/2, 10)
        ax0.set_xticks(x_ticks)
        ax0.set_xticklabels([f'{x/1000:.1f}' for x in x_ticks])
        
        # Spectrogram (κάτω subplot)
        ax1 = fig.add_subplot(gs[1])
        img = librosa.display.specshow(
            D_db,
            y_axis='hz',
            x_axis='time',
            sr=audio_sr,
            ax=ax1,
            cmap='magma_r',
            vmin=D_db.min(),
            vmax=D_db.max()
        )
        
        # Προσαρμογή των ετικετών του spectrogram
        ax1.set_ylabel('Frequency (kHz)')
        ax1.set_xlabel('Time (s)')
        ax1.set_title('Spectrogram', pad=10)
        
        # Μετατροπή των συχνοτήτων σε kHz στον άξονα y
        y_ticks = ax1.get_yticks()
        ax1.set_yticklabels([f'{y/1000:.1f}' for y in y_ticks])
        
        # Προσθήκη colorbar
        cbar = plt.colorbar(img, ax=[ax0, ax1], format='%+2.0f dB')
        cbar.set_label('Magnitude (dB)')
        
        # Ρύθμιση του layout
        plt.tight_layout()
        logger.info(f"Create spectrogram and freq analyzer time: {datetime.now()-start_inf}",extra=LOG_D) 
                            
        # Αποθήκευση ή εμφάνιση
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            return None
            
    except Exception as error:
        logger.error(f"Error create Freq Analyzer error {str(error)} ",extra=LOG_D)
        return None
    

def create_freq_analyzer_spectrogram2(audio_data, audio_sr, save_path=None):
    try:
        start_inf=datetime.now()

        # Υπολογισμός STFT
        n_fft = 2048
        D = librosa.stft(audio_data, n_fft=n_fft)
        D_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Υπολογισμός του μέσου φάσματος συχνοτήτων
        freq_spectrum = np.mean(np.abs(D), axis=1)
        freq_db = librosa.amplitude_to_db(freq_spectrum, ref=np.max)
        
        # Συχνότητες για τον άξονα x
        freq_bands = ['31.5', '63', '125', '250', '500', '1k', '2k', '4k', '8k', '16k']
        frequencies = librosa.fft_frequencies(sr=audio_sr, n_fft=n_fft)
        
        # Ομαδοποίηση συχνοτήτων σε μπάντες
        band_magnitudes = []
        freq_values = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        for i in range(len(freq_values)-1):
            mask = (frequencies >= freq_values[i]) & (frequencies < freq_values[i+1])
            if np.any(mask):
                magnitude = np.mean(freq_db[mask])
                band_magnitudes.append(magnitude)
            else:
                band_magnitudes.append(freq_db.min())

        # Δημιουργία figure
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(12, 6))
        
        # Frequency Analyzer
        ax = plt.gca()
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        # Προσθήκη οριζόντιων γραμμών
        for db in range(-100, 20, 20):
            ax.axhline(y=db, color='green', linestyle='-', alpha=0.3)
        
        # Κάθετες γραμμές πλέγματος
        for x in range(len(freq_bands)):
            ax.axvline(x, color='green', linestyle='-', alpha=0.3)
        
        # Σχεδίαση των μπαρών
        bars = ax.bar(range(len(band_magnitudes)), 
                     band_magnitudes,
                     width=0.8,
                     color='lime')
        
        # Ρύθμιση των αξόνων
        ax.set_ylim(-100, 100)
        ax.set_xlim(-0.5, len(freq_bands) - 0.5)
        
        # Προσθήκη ετικετών στον άξονα x (συχνότητες)
        plt.xticks(range(len(freq_bands)), freq_bands)
        
        # Προσθήκη ετικετών στον άξονα y (dB)
        y_ticks = range(-100, 120, 20)
        plt.yticks(y_ticks, [f'{db}.0' for db in y_ticks])
        
        # Προσθήκη τίτλου και πληροφοριών στο πάνω μέρος
        current_time = "0m 0m 19.22s"  # Προσαρμόστε ανάλογα
        plt.title(f'Ch1  Overall: 82.51 dB  (Time: {current_time})\n'
                 f'Freq: 250.00 Hz  Level: 82.46 dB\n'
                 f'Max: 84.91 dB  Peak: 88.82 dB', 
                 loc='left', pad=10, color='cyan')
        
        # Προσθήκη ετικέτας dB Fast στον άξονα y
        plt.ylabel('dB Fast')
        
        # Προσθήκη ετικέτας Frequency (Hz) στον άξονα x
        plt.xlabel('Frequency (Hz)')
        
        # Ρύθμιση των χρωμάτων για τις ετικέτες και τους άξονες
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(colors='white')
        
        plt.tight_layout()
        logger.info(f"Create spectrogram and freq analyzer time: {datetime.now()-start_inf}",extra=LOG_D) 
                            
        # Αποθήκευση ή εμφάνιση
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
            plt.close()
            return save_path
        else:
            return None
            
    except Exception as error:
        logger.error(f"Error create Freq Analyzer error {str(error)} ",extra=LOG_D)
        return None