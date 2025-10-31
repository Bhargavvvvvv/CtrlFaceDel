import streamlit as st
import os
import requests
from tqdm import tqdm
import onnxruntime as ort
from PIL import Image, ImageDraw

# ------------------------------
# App Config
# ------------------------------
st.set_page_config(page_title="CtrlFaceDel AI Suite", layout="wide")
st.title("🎨 CtrlFaceDel — AI Suite")
st.caption("AI Face Swap • Text-to-Image • More coming soon...")

# ------------------------------
# Model URLs (replace with yours)
# ------------------------------
HF_BASE_URL = "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/"
# https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/text_encoder.onnx
MODEL_FILES = {
    "text_encoder": "text_encoder.onnx",
    "unet": "unet.onnx",
    "vae_decoder": "vae_decoder.onnx",
    "face_swap": "inswapper_128.onnx"
}

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


# ------------------------------
# Helper: download with progress
# ------------------------------
def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 8192
    with open(dest_path, "wb") as file, tqdm(
        desc=f"Downloading {os.path.basename(dest_path)}",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            file.write(data)
            bar.update(len(data))


# ------------------------------
# Cached model loader
# ------------------------------
@st.cache_resource
def load_models():
    sessions = {}
    for key, fname in MODEL_FILES.items():
        model_path = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(model_path):
            st.info(f"Downloading {fname} from Hugging Face...")
            url = HF_BASE_URL + fname
            download_file(url, model_path)
        # Load ONNX model session
        st.info(f"Loading {fname} ...")
        try:
            sessions[key] = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        except Exception as e:
            st.warning(f"Could not load {fname}: {e}")
    return sessions


# ------------------------------
# Sidebar Navigation
# ------------------------------
page = st.sidebar.radio("Choose a feature", ["Face Swap", "Text to Image"])

# Load models once per session
with st.spinner("Loading AI models..."):
    models = load_models()


# ------------------------------
# FACE SWAP
# ------------------------------
if page == "Face Swap":
    st.header("🤖 AI Face Swap")
    src_file = st.file_uploader("Upload Source Face", type=["jpg", "png"])
    tgt_file = st.file_uploader("Upload Target Image", type=["jpg", "png"])

    if src_file and tgt_file:
        col1, col2 = st.columns(2)
        with col1:
            st.image(src_file, caption="Source Face", use_column_width=True)
        with col2:
            st.image(tgt_file, caption="Target Image", use_column_width=True)

        if st.button("🔄 Swap Faces"):
            # placeholder output
            img = Image.open(tgt_file).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text((20, 20), "Swapped!", fill=(255, 0, 0))
            st.image(img, caption="Swapped Result", use_column_width=True)
            st.success("Swap complete!")


# ------------------------------
# TEXT TO IMAGE
# ------------------------------
elif page == "Text to Image":
    st.header("🖌️ AI Text-to-Image")

    prompt = st.text_area("Enter a prompt:", "a cyberpunk cat wearing sunglasses")

    if st.button("🎨 Generate Image"):
        st.write(f"Generating for: {prompt}")

        # placeholder output
        img = Image.new("RGB", (512, 512), (40, 40, 40))
        draw = ImageDraw.Draw(img)
        draw.text((40, 240), f"Prompt: {prompt}", fill=(255, 255, 255))
        st.image(img, caption="Generated Image", use_column_width=True)
