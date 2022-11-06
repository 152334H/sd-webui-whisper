from modules import scripts
import main
import gradio as gr

sh = main.StreamHandler()

def process_gradio_audio(fpath: str):
    res = sh.model.transcribe(fpath)
    return res['text']

'''This function is poorly designed for several reasons:
1. it locks gradio in a busy loop
2. it does not use the browser's microphone, but the mic of the machine running Gradio
3. it uses a checkbox
'''
def toggle_whisper_mode(mode: bool):
    if not mode: return False, False
    while 'computer' not in sh.syncProcess().lower(): pass
    return 'click', False

def create_ui():
    with gr.Group():
        with gr.Accordion("Open for Whisper!", open=False):
            with gr.Row():
                # Really bad code
                whisper_mode = gr.Checkbox(label="Wait for command", value=False)
                hidden_mic_activator = gr.Text(visible=False)
                whisper_mode.change(toggle_whisper_mode, [whisper_mode], [hidden_mic_activator, whisper_mode])
                hidden_mic_activator.change(None, [hidden_mic_activator], [], _js='s => doMic(s)')

                # Not so bad code
                hidden_prompt = gr.Text(visible=False)
                whisper_mic = gr.Mic(type='filepath', elem_id="whisper-mic")
                hidden_prompt.change(None, [hidden_prompt], [], _js='s => changePrompt(s)')
                whisper_mic.change(process_gradio_audio, [whisper_mic], [hidden_prompt])

    return whisper_mode

class WhisperScript(scripts.Script):
    def title(self):
        return "Aesthetic embeddings"

    def show(self, _is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if is_img2img: return []
        whisper_mode = create_ui()

        self.infotext_fields = [
            (whisper_mode, "Whisper mode"),
        ]

        return [whisper_mode]

