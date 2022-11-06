// Thank you to a1111-sd-webui-tagcomplete
function changePrompt(newPrompt) {
  let textArea = gradioApp().querySelector('#txt2img_prompt > label > textarea');
  textArea.value = newPrompt;
  // Since we've modified a Gradio Textbox component manually, we need to simulate an `input` DOM event to ensure its
  // internal Svelte data binding remains in sync.
  textArea.dispatchEvent(new Event("input", { bubbles: true }));

  let genButton = gradioApp().getElementById('txt2img_generate')
  genButton.click()
}

function doMic(mode) {
  if (mode === 'click') {
    let mic_button = gradioApp().querySelector('#whisper-mic > div > button')
    mic_button.click()
  }
}

