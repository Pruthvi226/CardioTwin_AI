import { ImageUp } from "lucide-react";
import { useEffect, useState } from "react";

export default function ImageUpload({ file, onFileChange, result }) {
  const [preview, setPreview] = useState("");

  useEffect(() => {
    if (!file || !file.type.startsWith("image/")) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  return (
    <section className="panel">
      <div className="panel-title-row">
        <h3>ECG / Report Image</h3>
        <span>{result?.demo_mode ? "Demo OCR" : result?.risk_category || "Optional"}</span>
      </div>
      <label className="file-control">
        <ImageUp size={18} aria-hidden="true" />
        <input
          type="file"
          accept=".png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff,.pdf"
          onChange={(event) => onFileChange(event.target.files?.[0] || null)}
        />
        <span>{file?.name || "Choose report image"}</span>
      </label>
      {preview ? (
        <img className="image-preview" src={preview} alt="Uploaded report preview" />
      ) : (
        <div className="image-placeholder">ECG / report preview</div>
      )}
      <p className="small-muted">{result?.summary || "OCR findings appear here after analysis."}</p>
    </section>
  );
}

