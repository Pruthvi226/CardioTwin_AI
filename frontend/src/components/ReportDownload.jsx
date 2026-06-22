import { Download } from "lucide-react";

export default function ReportDownload({ disabled, onDownload }) {
  return (
    <button className="primary-button" onClick={onDownload} disabled={disabled} title="Download health report">
      <Download size={18} aria-hidden="true" />
      Download Health Report
    </button>
  );
}

