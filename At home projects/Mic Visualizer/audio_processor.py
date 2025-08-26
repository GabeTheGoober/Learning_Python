from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import audioop
import numpy as np

class AudioWorker(QThread):
    """Handles audio input processing in a separate thread."""
    volume_signal = pyqtSignal(int)
    frequency_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    
    def __init__(self, device_index, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self.running = False
        self.threshold = 300
        self.audio_interface = None
        self.stream = None
        self.frequency_analysis = False
        
    def set_frequency_analysis(self, enabled):
        """Enable or disable frequency analysis."""
        self.frequency_analysis = enabled
        
    def run(self):
        """Process audio input and emit volume and frequency signals."""
        self.running = True
        self.audio_interface = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        
        try:
            self.stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=CHUNK
            )
            
            window = np.hanning(CHUNK)
            
            while self.running:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    rms = audioop.rms(data, 2)
                    self.volume_signal.emit(rms)
                    
                    if self.frequency_analysis:
                        audio_data = np.frombuffer(data, dtype=np.int16)
                        windowed = audio_data * window
                        fft = np.fft.rfft(windowed)
                        magnitude = np.abs(fft)
                        magnitude_db = 20 * np.log10(magnitude + 1e-6)
                        self.frequency_signal.emit(magnitude_db)
                        
                except OSError as e:
                    self.error_signal.emit(f"Audio device error: {e}")
                    break
                except Exception as e:
                    self.error_signal.emit(f"Audio processing error: {e}")
        except Exception as e:
            self.error_signal.emit(f"Failed to initialize audio: {e}")
        finally:
            self.cleanup()
                
    def cleanup(self):
        """Clean up audio resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.audio_interface:
            try:
                self.audio_interface.terminate()
            except:
                pass
        
    def stop(self):
        """Stop the audio processing thread."""
        self.running = False
        self.cleanup()
        self.wait()
        
    def set_threshold(self, value):
        """Set the volume threshold for audio processing."""
        self.threshold = value