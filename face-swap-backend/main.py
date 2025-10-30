# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import base64
from io import BytesIO
import cv2, numpy as np, base64
from fastapi.middleware.cors import CORSMiddleware

from faceswap.pipeline import read_image,face_app,swapper,enhance_image
from text2image.pipeline import generate_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🧠 Face Swap endpoint (already exists)
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


# 🎨 New Text-to-Image endpoint
@app.post("/generate")
async def generate_endpoint(prompt: str = Form(...)):
    try:
        img = generate_image(prompt)
        buf = BytesIO()
        img.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"generated_image": encoded}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
