import React, { useState } from "react";
import axios from "axios";
import "./detection.css";

/* =========================
   Grad-CAM Renderer (Overlay)
   ========================= */
function drawGradCAM(canvas, heatmap) {
  if (!canvas || !heatmap) return;

  const ctx = canvas.getContext("2d");
  const SIZE = 384;

  canvas.width = SIZE;
  canvas.height = SIZE;

  const imgData = ctx.createImageData(SIZE, SIZE);

  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      const v = Math.min(1, Math.max(0, heatmap[y][x]));
      const idx = (y * SIZE + x) * 4;

      const r = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 3))));
      const g = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 2))));
      const b = Math.min(255, Math.max(0, 255 * (1.5 - Math.abs(4 * v - 1))));

      imgData.data[idx]     = r;
      imgData.data[idx + 1] = g;
      imgData.data[idx + 2] = b;
      imgData.data[idx + 3] = 180; // transparency
    }
  }

  ctx.putImageData(imgData, 0, 0);
}

/* =========================
      XAI TABLE
   ========================= */
function XaiTable({ table }) {
  if (!table || table.length === 0) return null;

  return (
    <table className="xai-table">
      <thead>
        <tr>
          <th>Region</th>
          <th>Grad-CAM</th>
          <th>LIME</th>
          <th>Combined</th>
          <th>Normalized</th>
        </tr>
      </thead>
      <tbody>
        {table.map((row, idx) => (
          <tr key={idx}>
            <td>{row.Region}</td>
            <td>{row["Grad-CAM Score"].toFixed(6)}</td>
            <td>{row["LIME Score"].toFixed(6)}</td>
            <td>{row["Combined Score"].toFixed(6)}</td>
            <td>{row["Normalized Combined Score"].toFixed(6)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Detection() {
  const [leftFile, setLeftFile] = useState(null);
  const [rightFile, setRightFile] = useState(null);
  const [leftPreview, setLeftPreview] = useState(null);
  const [rightPreview, setRightPreview] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [heatmapLeft, setHeatmapLeft] = useState(null);
  const [heatmapRight, setHeatmapRight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e, side) => {
    const file = e.target.files[0];
    if (!file) return;

    setPrediction(null);
    setHeatmapLeft(null);
    setHeatmapRight(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      side === "left"
        ? setLeftPreview(reader.result)
        : setRightPreview(reader.result);
    };
    reader.readAsDataURL(file);

    side === "left" ? setLeftFile(file) : setRightFile(file);
  };

  const handleUpload = async () => {
    if (!leftFile || !rightFile) {
      setError("Please upload both images.");
      return;
    }

    const formData = new FormData();
    formData.append("left_eye", leftFile);
    formData.append("right_eye", rightFile);

    setLoading(true);
    setError(null);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/predict",
        formData
      );
      setPrediction(res.data);
      setHeatmapLeft(res.data.left_eye.gradcam);
      setHeatmapRight(res.data.right_eye.gradcam);
    } catch {
      setError("Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  const EyeBlock = ({ title, preview, heatmap, data }) => (
    <div className={`eye-card ${data.isGlaucoma ? "glaucoma-detected" : "normal-detected"}`}>
      <div className="image-compare">
        {/* Original */}
        <div className="img-box">
          <span className="img-label">Original</span>
          <img src={preview} className="base-img" />
        </div>

        {/* Grad-CAM */}
        <div className="img-box">
          <span className="img-label">Grad-CAM</span>
          <div className="img-overlay-container">
            <img src={preview} className="base-img" />
            <canvas
              className="gradcam-canvas"
              ref={(c) => c && drawGradCAM(c, heatmap)}
            />
          </div>
        </div>
      </div>

      <div className="prediction-text">
        <h4>{title}</h4>
        <p className={data.isGlaucoma ? "glaucoma" : "no-glaucoma"}>
          {data.isGlaucoma ? "Glaucoma Detected" : "Normal"}
        </p>
        <p className="confidence">Confidence: {(data.confidence * 100).toFixed(2)}%</p>
        <p className="explanation-text">{data.explanation}</p>
        {data.xai_table && <XaiTable table={data.xai_table} />}
      </div>
    </div>
  );

  return (
    <div className="detection-root">
      <div className="card">
        <h2>AI-Powered Glaucoma Detection</h2>

        <div className="upload-box">
          <input type="file" onChange={(e) => handleFileChange(e, "left")} />
          <input type="file" onChange={(e) => handleFileChange(e, "right")} />
          <button onClick={handleUpload} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        {error && <p className="error-message">{error}</p>}

        {prediction && (
          <div className="results-grid">
            <EyeBlock
              title="Left Eye"
              preview={leftPreview}
              heatmap={heatmapLeft}
              data={prediction.left_eye}
            />
            <EyeBlock
              title="Right Eye"
              preview={rightPreview}
              heatmap={heatmapRight}
              data={prediction.right_eye}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default Detection;
