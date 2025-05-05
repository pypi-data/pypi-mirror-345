import sounddevice as sd
import numpy as np
from pynput import keyboard
import threading
import queue
from datetime import datetime
import soundfile as sf
from pathlib import Path

class AudioRecorder:
    def __init__(self, sample_rate=16000, output_dir=None):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_queue = queue.Queue()
        self.recorded_audio = []
        self.output_dir = Path(output_dir) if output_dir else None
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def _on_press(self, key):
        try:
            if key == keyboard.Key.space and not self.recording:
                # Start recording in a separate thread
                self.recording = True
                threading.Thread(target=self._record_audio).start()
        except AttributeError:
            pass

    def _save_audio(self, audio_data):
        """Save audio data to WAV file and return the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_wav = self.output_dir / f"recording_{timestamp}.wav"
        
        # Save as WAV
        sf.write(output_wav, audio_data, self.sample_rate)
        
        return str(output_wav)

    def _on_release(self, key):
        try:
            if key == keyboard.Key.space and self.recording:
                print("Recording stopped...")
                self.recording = False
                # Process the recorded audio
                audio_data = np.concatenate(self.recorded_audio).squeeze()
                # Save audio and get file path
                file_path = self._save_audio(audio_data) if self.output_dir else None
                # Put both audio data and file path in queue
                self.audio_queue.put((audio_data, file_path))
                self.recorded_audio = []
        except AttributeError:
            pass

    def _record_audio(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
            started = False
            while self.recording:
                if not started:
                    started = True
                    print("Recording started...")
                audio_chunk, _ = stream.read(self.sample_rate // 10)  # Read 100ms chunks
                self.recorded_audio.append(audio_chunk.copy())

    def get_last_recording(self):
        """Get the last recorded audio and its file path. Returns (None, None) if no recording is available."""
        try:
            return self.audio_queue.get()
        except queue.Empty:
            return None, None

    def __del__(self):
        self.listener.stop()

if __name__ == "__main__":
    # Example usage
    recorder = AudioRecorder(output_dir="./recorded_audio")
    print("Press and hold SPACE to record audio. Release to stop recording.")
    
    try:
        while True:
            audio, file_path = recorder.get_last_recording()
            if audio is not None:
                print(f"Recorded audio shape: {audio.shape}, dtype: {audio.dtype}")
                print(f"Saved to: {file_path}")
    except KeyboardInterrupt:
        print("\nExiting...") 