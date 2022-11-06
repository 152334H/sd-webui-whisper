'''Modified from github:Nikorasu/LiveWhisper.

The following description is retained verbatim:
# This is my attempt to make psuedo-live transcription of speech using Whisper.
# Since my system can't use pyaudio, I'm using sounddevice instead.
# Currently just a basic terminal implementation.
# by Nik Stromberg - nikorasu85@gmail.com - MIT 2022 - copilot
'''

from modules import safe
import numpy as np
import whisper
import torch
import time
from typing import Callable,Any


model = 'small'     # Whisper model size (tiny, base, small, medium, large)
english = True      # Use english-only model?
translate = False   # Translate non-english to english?
samplerate = 16000  # Stream device recording frequency
blocksize = 30      # Block size in milliseconds
threshold = 0.25    # Minimum volume threshold to activate listening
vocals = [50, 5000] # Frequency range to detect sounds that could be speech
endblocks = 30      # Number of blocks to wait before sending to Whisper

class StreamHandler:
    def __init__(self, upon_message: Callable[[str],Any]=lambda s:None):
        self.running = True
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.filebuffer = None
        self.recorded = None
        
        print("\033[96mLoading Whisper Model..\033[0m", end='', flush=True)
        # wrapper to allow unsafe pickle
        torch.load = safe.unsafe_torch_load
        self.model = whisper.load_model(f'{model}{".en" if english else ""}')
        torch.load = safe.load
        print("\033[90m Done.\033[0m")

    def syncProcess(self):
        import sounddevice as sd
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(samplerate * blocksize / 1000), samplerate=samplerate, dtype=np.float32):
            while self.recorded is None:
                time.sleep(0.5)
        res = self.process(self.recorded)
        self.recorded = None
        return res

    def callback(self, indata, frames, time, status):
        #if status: print(status) # for debugging, prints stream errors.
        if any(indata):
            freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * samplerate / frames
            if indata.max() > threshold and vocals[0] <= freq <= vocals[1]:
                print('.', end='', flush=True)
                if self.padding < 1: self.buffer = self.prevblock.copy()
                self.buffer = np.concatenate((self.buffer, indata))
                self.padding = endblocks
            else:
                self.padding -= 1
                if self.padding > 1:
                    self.buffer = np.concatenate((self.buffer, indata))
                elif self.padding < 1 and 1 < self.buffer.shape[0] > samplerate:
                    self.recorded = self.buffer.astype(np.float32)[:,0]
                    self.buffer = np.zeros((0,1))
                elif self.padding < 1 and 1 < self.buffer.shape[0] < samplerate:
                    self.buffer = np.zeros((0,1))
                    print("\033[2K\033[0G", end='', flush=True)
                else:
                    self.prevblock = indata.copy() #np.concatenate((self.prevblock[-int(samplerate/10):], indata)) # SLOW
        else:
            print("\033[31mNo input or device is muted.\033[0m")
            self.running = False

    def process(self, inputbuffer):
        print("\n\033[90mTranscribing..\033[0m")
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.pad_or_trim(inputbuffer)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        # decode the audio
        options = whisper.DecodingOptions(task='translate' if translate else 'transcribe', language='en')
        result = whisper.decode(self.model, mel, options)
        # print the recognized text
        print(f"\033[1A\033[2K\033[0G{result.text}") # pyright: ignore
        return result.text

