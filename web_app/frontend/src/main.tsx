import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { createProject, imageUrl, matchProject, type MatchResponse, type Project, uploadImages } from "./api";
import "./styles.css";

function App() {
  const [projectName, setProjectName] = useState("Web Classification");
  const [project, setProject] = useState<Project | null>(null);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [status, setStatus] = useState("後端已準備，先建立一個專案。");
  const [busy, setBusy] = useState(false);

  const totalImages = useMemo(() => result?.groups.reduce((sum, group) => sum + group.count, 0) ?? project?.image_count ?? 0, [result, project]);

  async function handleCreate() {
    setBusy(true);
    try {
      const created = await createProject(projectName || "Web Classification");
      setProject(created);
      setResult(null);
      setStatus(`專案已建立：${created.id}`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleUpload(files: FileList | null) {
    if (!project || !files?.length) return;
    setBusy(true);
    try {
      const response = await uploadImages(project.id, files);
      setProject({ ...project, image_count: response.image_count });
      setStatus(`已上傳 ${response.uploaded} 張圖片。`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleMatch() {
    if (!project) return;
    setBusy(true);
    setStatus("分類中，正在使用後端演算法與快取...");
    try {
      const matched = await matchProject(project.id, "fast");
      setResult(matched);
      setStatus(`完成：${matched.group_count} 組，${matched.elapsed.toFixed(2)} 秒。`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">AI Image Matching Web</p>
          <h1>相似系列圖片自動整理系統</h1>
          <p>桌面版核心演算法已接入 Web API。建立專案、上傳圖片、分類、檢視分組，先把主流程跑順。</p>
        </div>
        <div className="stats">
          <span>{project ? "Project Ready" : "No Project"}</span>
          <strong>{totalImages}</strong>
          <small>images</small>
        </div>
      </section>

      <section className="workflow">
        <div className="panel">
          <label>專案名稱</label>
          <div className="row">
            <input value={projectName} onChange={(event) => setProjectName(event.target.value)} />
            <button onClick={handleCreate} disabled={busy}>建立專案</button>
          </div>
          {project && <p className="meta">ID: {project.id}</p>}
        </div>

        <div className="panel">
          <label>上傳圖片</label>
          <input className="file" type="file" accept="image/*" multiple disabled={!project || busy} onChange={(event) => handleUpload(event.target.files)} />
          <button className="wide" onClick={handleMatch} disabled={!project || !project.image_count || busy}>開始分類</button>
        </div>

        <div className="panel status">
          <label>狀態</label>
          <p>{status}</p>
        </div>
      </section>

      <section className="results">
        <div className="section-title">
          <h2>分組結果</h2>
          <span>{result ? `${result.group_count} groups` : "等待分類"}</span>
        </div>
        {!result && <div className="empty">分類完成後，圖片會依 Group 顯示在這裡。</div>}
        {result?.groups.map((group) => (
          <article className="group" key={group.name}>
            <header>
              <h3>{group.name}</h3>
              <span>{group.count} images</span>
            </header>
            <div className="grid">
              {group.images.map((image) => (
                <figure key={`${group.name}-${image.source_path}`}>
                  <img src={imageUrl(result.project_id, image.source_path)} alt={image.filename} loading="lazy" />
                  <figcaption>{image.filename}</figcaption>
                </figure>
              ))}
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
