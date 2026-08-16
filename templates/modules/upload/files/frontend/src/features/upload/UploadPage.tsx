import { useState, type FormEvent } from "react";
import { apiRequest } from "../../lib/api";

type UploadResponse = { filename: string; content_type: string | null; size: number; extension: string };

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null); const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!file) return; setLoading(true); setError(""); setResult(null);
    const body = new FormData(); body.append("file", file);
    try { setResult(await apiRequest<UploadResponse>("/upload", { method: "POST", body })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Upload failed"); }
    finally { setLoading(false); }
  }
  return <section><header className="feature-heading"><h1>File Upload</h1><p>Upload one file to the generic upload endpoint.</p></header><article className="feature-card"><form className="form-stack" onSubmit={submit}><div className="form-field"><label htmlFor="upload-file">Choose a file</label><input id="upload-file" type="file" onChange={(event) => { setFile(event.target.files?.[0] ?? null); setResult(null); setError(""); }} /></div>{file && <p className="status-message">Selected: {file.name}</p>}<button className="button" disabled={!file || loading}>{loading ? "Uploading…" : "Upload"}</button>{error && <p className="status-message error">{error}</p>}{result && <div className="status-message success"><strong>Upload successful</strong><dl className="metadata-list"><dt>Filename</dt><dd>{result.filename}</dd><dt>Type</dt><dd>{result.content_type ?? "Not provided"}</dd><dt>Size</dt><dd>{result.size} bytes</dd><dt>Extension</dt><dd>{result.extension}</dd></dl></div>}</form></article></section>;
}
