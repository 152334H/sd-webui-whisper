import launch

''' actual requirements:
scipy = "*"
sounddevice = "*"
numpy = "*"
torch = "*"
tqdm = "*"
more-itertools = "*"
transformers = ">=4.19.0"
ffmpeg-python = "==0.2.0"
whisper = {git = "https://github.com/openai/whisper.git"}
'''

# Many of these print messages even after installation. ???
if not launch.is_installed("sounddevice"):
    launch.run_pip("install sounddevice==0.4.5", "requirements for Whisper extension")
if not launch.is_installed("more-itertools"):
    launch.run_pip("install more-itertools==9.0", "requirements for Whisper")
if not launch.is_installed("ffmpeg-python"):
    launch.run_pip("install ffmpeg-python==0.2.0", "requirements for Whisper")
if not launch.is_installed("whisper"):
    launch.run_pip("install git+https://github.com/openai/whisper.git", "requirements for Whisper")

