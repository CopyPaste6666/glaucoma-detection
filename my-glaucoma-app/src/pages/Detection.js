import React, { useState } from "react";
import axios from "axios";

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

  const handleFileChange = (event, type) => {
    const file = event.target.files[0];
    if (type === "left") {
      setLeftFile(file);
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => setLeftPreview(reader.result);
        reader.readAsDataURL(file);
      }
    } else {
      setRightFile(file);
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => setRightPreview(reader.result);
        reader.readAsDataURL(file);
      }
    }
    setPrediction(null);
    setError(null);
    setHeatmapLeft(null);
    setHeatmapRight(null);
  };

  const handleUpload = async () => {
    if (!leftFile || !rightFile) {
      setError("Please select both left and right eye images.");
      return;
    }

    const formData = new FormData();
    formData.append("left_eye", leftFile);
    formData.append("right_eye", rightFile);

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setPrediction(response.data);
      setHeatmapLeft(response.data.left_heatmap);
      setHeatmapRight(response.data.right_heatmap);
    } catch (err) {
      setError("Failed to get prediction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <section className="detection-section">
        <h2>AI-Powered Glaucoma Detection</h2>
        <div className="upload-box">
          <div>
            <label>Upload Left Eye Image:</label>
            <input type="file" onChange={(e) => handleFileChange(e, "left")} accept="image/*" />
          </div>
          <div>
            <label>Upload Right Eye Image:</label>
            <input type="file" onChange={(e) => handleFileChange(e, "right")} accept="image/*" />
          </div>
          <button onClick={handleUpload} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Images"}
          </button>
        </div>
        {error && <p className="error-message">{error}</p>}

        {prediction && (
          <div className="result-box">
            <div className="prediction-text">
              <h3>Prediction Results:</h3>
              <p className={prediction.left_eye.isGlaucoma ? "glaucoma" : "no-glaucoma"}>
                Left Eye: {prediction.left_eye.isGlaucoma ? "Glaucoma Detected" : "No Glaucoma Detected"}
              </p>
              <p>Confidence: {(prediction.left_eye.confidence * 100).toFixed(2)}%</p>

              <p className={prediction.right_eye.isGlaucoma ? "glaucoma" : "no-glaucoma"}>
                Right Eye: {prediction.right_eye.isGlaucoma ? "Glaucoma Detected" : "No Glaucoma Detected"}
              </p>
              <p>Confidence: {(prediction.right_eye.confidence * 100).toFixed(2)}%</p>
            </div>
          </div>
        )}
      </section>

      {(leftPreview && heatmapLeft) || (rightPreview && heatmapRight) ? (
        <section className="xai-section">
          <h2>Explainable AI (XAI)</h2>
          <div className="xai-explanation">
            {leftPreview && heatmapLeft && (
              <div className="eye-result">
                <h3>Left Eye</h3>
                <img src={leftPreview} alt="Left Eye" />
                <img src={`data:image/png;base64,${heatmapLeft}`} alt="Left Eye Heatmap" />
              </div>
            )}
            {rightPreview && heatmapRight && (
              <div className="eye-result">
                <h3>Right Eye</h3>
                <img src={rightPreview} alt="Right Eye" />
                <img src={`data:image/png;base64,${heatmapRight}`} alt="Right Eye Heatmap" />
              </div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}

export default Detection;
