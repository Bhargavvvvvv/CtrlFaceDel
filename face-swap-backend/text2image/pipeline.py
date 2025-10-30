import os, onnxruntime as ort, requests
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def _download(name, url):
    p = os.path.join(MODEL_DIR, name)
    if not os.path.exists(p):
        r = requests.get(url, stream=True); r.raise_for_status()
        with open(p, "wb") as f:
            for c in r.iter_content(8192): f.write(c)
    return p

HF = "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main"

def generate_image(prompt: str, steps: int = 15):
    """Loads models only when called; unloads afterwards to save RAM."""
    try:
        text = _download("text_encoder.onnx", f"{HF}/text_encoder.onnx")
        unet = _download("unet.onnx", f"{HF}/unet.onnx")
        vae  = _download("vae_decoder.onnx", f"{HF}/vae_decoder.onnx")
        providers = ["CPUExecutionProvider"]
        text_sess = ort.InferenceSession(text, providers=providers)
        unet_sess = ort.InferenceSession(unet, providers=providers)
        vae_sess  = ort.InferenceSession(vae,  providers=providers)

        tokens = tokenizer(prompt, return_tensors="np", padding="max_length", truncation=True, max_length=77)
        text_embeds = text_sess.run(None, {"input_ids": tokens["input_ids"]})[0]

        latent = np.random.randn(1, 4, 64, 64).astype(np.float32)

        for _ in range(steps):
            latent = unet_sess.run(None, {"latent": latent, "encoder_hidden_states": text_embeds})[0]

        image = vae_sess.run(None, {"latent": latent / 0.18215})[0]
        image = np.clip((image.transpose(0, 2, 3, 1) + 1) / 2, 0, 1)
        img = Image.fromarray((image[0] * 255).astype(np.uint8))
        return img
    finally:
        del text_sess, unet_sess, vae_sess
