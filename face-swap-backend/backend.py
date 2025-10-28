from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2, numpy as np, base64
import insightface
from insightface.app import FaceAnalysis
import os
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import os, requests

MODEL_PATH = "inswapper_128.onnx"
HF_URL = "https://huggingface.co/pewdsxqwerty/inswapper-model/resolve/main/inswapper_128.onnx"

def download_model(url, dest_path):
    print(f"🔽 Downloading model from {url} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"✅ Model downloaded to {dest_path}")

if not os.path.exists(MODEL_PATH):
    download_model(HF_URL, MODEL_PATH)
else:
    print("✅ Model already present locally.")
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0, det_size=(640, 640))
swapper = insightface.model_zoo.get_model("inswapper_128.onnx", download=False)

def read_image(file: UploadFile):
    file_bytes = np.frombuffer(file.file.read(), np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

def enhance_image(img):
    upscaled = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(upscaled, (0, 0), 1.5)
    enhanced = cv2.addWeighted(upscaled, 1.6, blurred, -0.6, 0)
    return enhanced

@app.post("/swap")
async def swap_faces(source: UploadFile = File(...), target: UploadFile = File(...)):
    try:
        src_img = read_image(source)
        tgt_img = read_image(target)
        src_faces = face_app.get(src_img)
        tgt_faces = face_app.get(tgt_img)
        if not src_faces or not tgt_faces:
            return JSONResponse({"error": "No face detected"}, status_code=400)

        swapped = swapper.get(tgt_img.copy(), tgt_faces[0], src_faces[0], paste_back=True)
        enhanced = enhance_image(swapped)

        _, buffer = cv2.imencode(".png", enhanced)
        img_str = base64.b64encode(buffer).decode("utf-8")
        return {"swapped_image": img_str}

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
