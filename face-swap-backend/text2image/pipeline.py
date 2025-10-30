import onnxruntime as ort
import numpy as np
from transformers import CLIPTokenizer
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize tokenizer
MODEL_URLS = {
    "text_encoder.onnx": "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/text_encoder.onnx",
    "unet.onnx": "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/unet.onnx",
    "vae_decoder.onnx": "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/vae_decoder.onnx"
}

def download_model(name, url):
    """Download model if not already present."""
    local_path = os.path.join(MODEL_DIR, name)
    if not os.path.exists(local_path):
        print(f"⬇️ Downloading {name} from Hugging Face...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ {name} downloaded.")
    else:
        print(f"✔️ {name} already exists.")
    return local_path

# Ensure models are present
text_encoder_path = download_model("text_encoder.onnx", MODEL_URLS["text_encoder.onnx"])
unet_path = download_model("unet.onnx", MODEL_URLS["unet.onnx"])
vae_path = download_model("vae_decoder.onnx", MODEL_URLS["vae_decoder.onnx"])

# Load sessions
providers = ["CPUExecutionProvider"]
text_sess = ort.InferenceSession(text_encoder_path, providers=providers)
unet_sess = ort.InferenceSession(unet_path, providers=providers)
vae_sess  = ort.InferenceSession(vae_path, providers=providers)





def generate_image(prompt: str, steps: int = 15):
    """
    Simplified ONNX text-to-image (mock for now)
    """
    # Tokenize text → embeddings
    tokens = tokenizer(prompt, return_tensors="np", padding="max_length", truncation=True, max_length=77)
    text_embeds = text_sess.run(None, {"input_ids": tokens["input_ids"]})[0]

    # Create dummy latent (replace this with real diffusion loop later)
    latent = np.random.randn(1, 4, 64, 64).astype(np.float32)

    for _ in range(steps):
        latent = unet_sess.run(None, {"latent": latent, "encoder_hidden_states": text_embeds})[0]

    # Decode latent → image
    image = vae_sess.run(None, {"latent": latent / 0.18215})[0]
    image = np.clip((image.transpose(0, 2, 3, 1) + 1) / 2, 0, 1)
    img = Image.fromarray((image[0] * 255).astype(np.uint8))
    return img

# from PIL import Image, ImageDraw

# def generate_image(prompt: str, steps: int = 15):
#     img = Image.new("RGB", (512, 512), (20, 20, 20))
#     draw = ImageDraw.Draw(img)
#     draw.text((30, 250), f"Mock: {prompt}", fill=(255, 255, 255))
#     return img