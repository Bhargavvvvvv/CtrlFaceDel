import React, { useState } from "react";
import {
  Upload,
  Sparkles,
  ArrowLeftRight,
  Download,
  RefreshCw,
  Loader2,
} from "lucide-react";

export default function FaceSwapApp() {
  const [source, setSource] = useState(null);
  const [target, setTarget] = useState(null);
  const [sourcePreview, setSourcePreview] = useState(null);
  const [targetPreview, setTargetPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      if (type === "source") {
        setSource(file);
        setSourcePreview(URL.createObjectURL(file));
      } else {
        setTarget(file);
        setTargetPreview(URL.createObjectURL(file));
      }
    }
  };

  const handleSwap = async () => {
    if (!source || !target) {
      alert("Please upload both source and target images");
      return;
    }

    const formData = new FormData();
    formData.append("source", source);
    formData.append("target", target);

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/swap", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.swapped_image) {
        setResult(`data:image/png;base64,${data.swapped_image}`);
      } else {
        alert("Error: " + (data.error || "Something went wrong"));
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSource(null);
    setTarget(null);
    setSourcePreview(null);
    setTargetPreview(null);
    setResult(null);
  };

  const handleDownload = () => {
    if (result) {
      const link = document.createElement("a");
      link.href = result;
      link.download = "face-swap-result.png";
      link.click();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #4f46e5, #7c3aed, #a855f7)",
        padding: "40px 20px",
        fontFamily: "'Inter', sans-serif",
        color: "white",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* ===== Loading Overlay ===== */}
      {loading && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.6)",
            backdropFilter: "blur(6px)",
            zIndex: 9999,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            animation: "fadeIn 0.3s ease-in-out",
          }}
        >
          <Loader2
            size={64}
            style={{
              color: "#c084fc",
              animation: "spin 1s linear infinite",
              marginBottom: "20px",
            }}
          />
          <h2 style={{ fontSize: "1.5rem", fontWeight: "600" }}>
            Swapping faces... please wait ✨
          </h2>

          {/* CSS keyframes */}
          <style>
            {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }
            `}
          </style>
        </div>
      )}

      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            <Sparkles size={40} color="#facc15" />
            <h1 style={{ fontSize: "2.8rem", fontWeight: "700" }}>
              AI Face Swap Studio
            </h1>
            <Sparkles size={40} color="#facc15" />
          </div>
          <p style={{ color: "#bfdbfe", fontSize: "1.1rem" }}>
            Transform faces with cutting-edge AI technology
          </p>
        </div>

        <div
          style={{
            background: "rgba(255, 255, 255, 0.1)",
            borderRadius: "20px",
            padding: "40px",
            boxShadow: "0 10px 40px rgba(0, 0, 0, 0.25)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          {!result ? (
            <div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "40px",
                }}
              >
                {/* Source Upload */}
                <UploadCard
                  title="Source Face"
                  color="rgba(147,197,253,0.7)"
                  preview={sourcePreview}
                  onChange={(e) => handleFileChange(e, "source")}
                  hint="The face you want to use"
                />

                {/* Target Upload */}
                <UploadCard
                  title="Target Image"
                  color="rgba(192,132,252,0.7)"
                  preview={targetPreview}
                  onChange={(e) => handleFileChange(e, "target")}
                  hint="The image to swap onto"
                />
              </div>

              {/* Action Buttons */}
              <div style={{ textAlign: "center", marginTop: "40px" }}>
                <button
                  onClick={handleSwap}
                  disabled={loading || !source || !target}
                  style={{
                    background: "linear-gradient(90deg, #3b82f6, #8b5cf6)",
                    color: "white",
                    padding: "14px 40px",
                    fontSize: "1.1rem",
                    borderRadius: "12px",
                    border: "none",
                    fontWeight: "600",
                    cursor: loading ? "not-allowed" : "pointer",
                    marginRight: "10px",
                    transition: "0.3s",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  <ArrowLeftRight size={18} style={{ marginRight: "8px" }} />
                  Swap Faces
                </button>
                <button
                  onClick={handleReset}
                  style={{
                    background: "rgba(255,255,255,0.15)",
                    color: "white",
                    padding: "14px 30px",
                    fontSize: "1.1rem",
                    borderRadius: "12px",
                    border: "none",
                    fontWeight: "600",
                    cursor: "pointer",
                  }}
                >
                  Reset
                </button>
              </div>
            </div>
          ) : (
            <ResultSection
              result={result}
              handleDownload={handleDownload}
              handleReset={handleReset}
            />
          )}
        </div>

        {/* Footer */}
        <p
          style={{
            textAlign: "center",
            color: "#c7d2fe",
            marginTop: "30px",
            fontSize: "0.9rem",
          }}
        >
          Powered by advanced AI face swapping technology
        </p>
      </div>
    </div>
  );
}

/* ===== Helper Components ===== */

function UploadCard({ title, color, preview, onChange, hint }) {
  return (
    <div>
      <h3
        style={{
          fontSize: "1.25rem",
          fontWeight: 600,
          marginBottom: "12px",
          textAlign: "center",
        }}
      >
        {title}
      </h3>
      <label
        style={{
          display: "block",
          border: `2px dashed ${color}`,
          borderRadius: "16px",
          padding: "10px",
          textAlign: "center",
          cursor: "pointer",
          background: "rgba(255, 255, 255, 0.05)",
          transition: "0.3s",
          height: "320px", // consistent height
          overflow: "hidden",
        }}
      >
        <input
          type="file"
          accept="image/*"
          onChange={onChange}
          style={{ display: "none" }}
        />

        {preview ? (
          <div
            style={{
              width: "100%",
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "rgba(0,0,0,0.3)",
              borderRadius: "12px",
            }}
          >
            <img
              src={preview}
              alt={title}
              style={{
                maxWidth: "100%",
                maxHeight: "100%",
                objectFit: "contain", // ✅ show full image
                borderRadius: "12px",
              }}
            />
          </div>
        ) : (
          <div
            style={{
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color,
            }}
          >
            <Upload size={60} />
            <p style={{ marginTop: "10px" }}>Click to upload</p>
            <small>{hint}</small>
          </div>
        )}
      </label>
    </div>
  );
}

function ResultSection({ result, handleDownload, handleReset }) {
  return (
    <div style={{ textAlign: "center" }}>
      <h2
        style={{
          fontSize: "2rem",
          fontWeight: "700",
          marginBottom: "20px",
          color: "white",
        }}
      >
        ✨ Face Swap Complete! ✨
      </h2>

      {/* Same frame as UploadCard */}
      <div
        style={{
          display: "inline-block",
          border: "2px dashed rgba(255,255,255,0.3)",
          borderRadius: "16px",
          background: "rgba(255,255,255,0.05)",
          height: "320px",
          width: "100%",
          maxWidth: "480px",
          overflow: "hidden",
          marginBottom: "25px",
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(0,0,0,0.2)",
          }}
        >
          <img
            src={result}
            alt="Result"
            style={{
              maxWidth: "100%",
              maxHeight: "100%",
              objectFit: "contain",
              borderRadius: "12px",
            }}
          />
        </div>
      </div>

      <div style={{ marginTop: "10px" }}>
        <button
          onClick={handleDownload}
          style={{
            background: "linear-gradient(90deg, #22c55e, #16a34a)",
            color: "white",
            padding: "12px 35px",
            fontSize: "1rem",
            borderRadius: "12px",
            border: "none",
            fontWeight: "600",
            cursor: "pointer",
            marginRight: "10px",
          }}
        >
          <Download size={18} style={{ marginRight: "6px" }} />
          Download
        </button>
        <button
          onClick={handleReset}
          style={{
            background: "linear-gradient(90deg, #3b82f6, #8b5cf6)",
            color: "white",
            padding: "12px 35px",
            fontSize: "1rem",
            borderRadius: "12px",
            border: "none",
            fontWeight: "600",
            cursor: "pointer",
          }}
        >
          <RefreshCw size={18} style={{ marginRight: "6px" }} />
          Create Another
        </button>
      </div>
    </div>
  );
}

