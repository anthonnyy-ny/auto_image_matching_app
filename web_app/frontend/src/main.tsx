import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  cancelJob,
  clearCache,
  createProject,
  exportUrl,
  getJob,
  getResults,
  imageUrl,
  importProject,
  listProjects,
  projectFileUrl,
  startMatchJob,
  type MatchResponse,
  type Project,
  type ResultGroup,
  type ResultImage,
  updateResults,
  uploadImages,
} from "./api";
import "./styles.css";

type DragPayload = { groupIndex: number; imageIndex: number };
type PreviewState = { groupName: string; image: ResultImage };
type MatchMode = "strict" | "standard" | "loose" | "fast" | "turbo" | "ann";

const UPLOAD_BATCH_SIZE = 500;
const MATCH_MODES: { value: MatchMode; label: string }[] = [
  { value: "standard", label: "SIFT Match" },
  { value: "strict", label: "Strict SIFT" },
  { value: "loose", label: "Loose SIFT" },
  { value: "fast", label: "Fast SIFT" },
  { value: "turbo", label: "Turbo SIFT" },
  { value: "ann", label: "Vector Grouping" },
];

function cloneGroups(groups: ResultGroup[]) {
  return groups.map((group) => ({ ...group, images: [...group.images] }));
}

function normalizeGroups(groups: ResultGroup[]) {
  const width = Math.max(2, String(groups.length).length);
  return groups
    .filter((group) => group.images.length > 0)
    .map((group, index) => ({
      ...group,
      name: `Group${String(index + 1).padStart(width, "0")}`,
      count: group.images.length,
    }));
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function App() {
  const [projectName, setProjectName] = useState("Web Classification");
  const [project, setProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [status, setStatus] = useState("Backend ready. Create or load a project.");
  const [matchMode, setMatchMode] = useState<MatchMode>("standard");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [liveMetrics, setLiveMetrics] = useState<Record<string, unknown>>({});
  const [filter, setFilter] = useState("");
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [selectedGroups, setSelectedGroups] = useState<Set<string>>(new Set());
  const [preview, setPreview] = useState<PreviewState | null>(null);
  const pollTimer = useRef<number | null>(null);

  useEffect(() => {
    refreshProjects();
    return () => {
      if (pollTimer.current) window.clearInterval(pollTimer.current);
    };
  }, []);

  const totalImages = useMemo(
    () => result?.groups.reduce((sum, group) => sum + group.count, 0) ?? project?.image_count ?? 0,
    [result, project],
  );

  const visibleGroups = useMemo(() => {
    if (!result) return [];
    const keyword = filter.trim().toLowerCase();
    if (!keyword) return result.groups;
    return result.groups.filter(
      (group) => group.name.toLowerCase().includes(keyword) || group.images.some((image) => image.filename.toLowerCase().includes(keyword)),
    );
  }, [result, filter]);

  const dashboard = useMemo(() => {
    const stats = result?.stats ?? {};
    const scan = (stats.scan ?? {}) as Record<string, number>;
    const match = {
      ...((stats.match ?? {}) as Record<string, number>),
      ...(liveMetrics as Record<string, number>),
    };
    const skipped = Array.isArray(stats.skipped) ? stats.skipped.length : 0;
    return [
      ["Match sets", result?.group_count ?? 0],
      ["Images", totalImages],
      ["Backend", match.vector_backend ?? "none"],
      ["Current Img", match.current_image ?? 0],
      ["Processed", match.processed_images ?? 0],
      ["Current", match.current_groups ?? 0],
      ["Cache hits", scan.cache_hits ?? 0],
      ["Cache misses", scan.cache_misses ?? 0],
      ["Vector K", match.embedding_candidates ?? 0],
      ["Hash auto", match.hash_auto_matches ?? 0],
      ["SIFT calls", match.sift_calls ?? 0],
      ["Speed", match.images_per_second ?? 0],
      ["ETA", match.eta_seconds ?? 0],
      ["Limited", match.limited_candidates ?? 0],
      ["Rejected", match.candidate_rejects ?? 0],
      ["Skipped", skipped],
    ];
  }, [result, totalImages, liveMetrics]);

  function setGroups(groups: ResultGroup[]) {
    if (!result) return;
    const normalized = normalizeGroups(groups);
    setResult({ ...result, group_count: normalized.length, groups: normalized });
  }

  async function refreshProjects() {
    try {
      setProjects(await listProjects());
    } catch (error) {
      setStatus(String(error));
    }
  }

  async function loadProject(projectId: string) {
    const selected = projects.find((item) => item.id === projectId);
    if (!selected) return;
    setBusy(true);
    try {
      const results = await getResults(projectId);
      setProject(selected);
      setProjectName(selected.name);
      setSelectedImages(new Set());
      setSelectedGroups(new Set());
      setResult({
        project_id: projectId,
        group_count: results.groups.length,
        elapsed: 0,
        stats: results.stats,
        groups: results.groups,
      });
      setStatus(`Loaded project: ${selected.name}`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleCreate() {
    setBusy(true);
    try {
      const created = await createProject(projectName || "Web Classification");
      setProject(created);
      setResult(null);
      setSelectedImages(new Set());
      setSelectedGroups(new Set());
      setProgress(0);
      setLiveMetrics({});
      setStatus(`Project created: ${created.id}`);
      await refreshProjects();
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleImport(file: File | null) {
    if (!file) return;
    setBusy(true);
    try {
      const imported = await importProject(file);
      setProject(imported);
      setResult(null);
      setStatus(`Project imported: ${imported.id}`);
      await refreshProjects();
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleUpload(files: FileList | null) {
    if (!project || !files?.length) return;
    setBusy(true);
    setProgress(0);
    try {
      const allFiles = Array.from(files);
      let uploaded = 0;
      let imageCount = project.image_count;
      for (let start = 0; start < allFiles.length; start += UPLOAD_BATCH_SIZE) {
        const batch = allFiles.slice(start, start + UPLOAD_BATCH_SIZE);
        const response = await uploadImages(project.id, batch);
        uploaded += response.uploaded;
        imageCount = response.image_count;
        setProgress(Math.round((uploaded / allFiles.length) * 100));
        setStatus(`Uploading ${uploaded}/${allFiles.length} images...`);
      }
      const nextProject = { ...project, image_count: imageCount };
      setProject(nextProject);
      setProjects((items) => items.map((item) => (item.id === nextProject.id ? nextProject : item)));
      setStatus(`Uploaded ${uploaded} images. Total in project: ${imageCount}.`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleMatch() {
    if (!project) return;
    setBusy(true);
    setProgress(0);
    setStatus("Image match job queued...");
    try {
      const job = await startMatchJob(project.id, matchMode);
      setActiveJobId(job.job_id);
      if (pollTimer.current) window.clearInterval(pollTimer.current);
      pollTimer.current = window.setInterval(async () => {
        try {
          const state = await getJob(job.job_id);
          setProgress(state.progress ?? 0);
          setLiveMetrics(state.metrics ?? {});
          setStatus(`${state.message} ${state.progress ?? 0}%`);
          if (state.status === "done" && state.result) {
            if (pollTimer.current) window.clearInterval(pollTimer.current);
            setResult(state.result);
            setLiveMetrics(state.result.stats.match as Record<string, unknown>);
            setBusy(false);
            setActiveJobId(null);
            setProgress(100);
            setStatus(`Done: ${state.result.group_count} match sets, ${state.result.elapsed.toFixed(2)} seconds.`);
            refreshProjects();
          }
          if (state.status === "failed" || state.status === "cancelled") {
            if (pollTimer.current) window.clearInterval(pollTimer.current);
            setBusy(false);
            setActiveJobId(null);
            setStatus(state.error || state.message || "Job stopped.");
          }
        } catch (error) {
          if (pollTimer.current) window.clearInterval(pollTimer.current);
          setBusy(false);
          setActiveJobId(null);
          setStatus(String(error));
        }
      }, 600);
    } catch (error) {
      setBusy(false);
      setActiveJobId(null);
      setStatus(String(error));
    }
  }

  async function handleCancel() {
    if (!activeJobId) return;
    try {
      await cancelJob(activeJobId);
      setStatus("Cancelling job...");
    } catch (error) {
      setStatus(String(error));
    }
  }

  async function handleClearCache() {
    setBusy(true);
    try {
      const response = await clearCache();
      setStatus(`Cache cleared: ${response.removed_files} files, ${formatBytes(response.removed_bytes)}.`);
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function persistEdits() {
    if (!project || !result) return;
    setBusy(true);
    try {
      const response = await updateResults(project.id, normalizeGroups(result.groups));
      setResult({ ...result, groups: response.groups, group_count: response.groups.length });
      setStatus("Corrections saved.");
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  function moveImage(payload: DragPayload, targetGroupIndex: number) {
    if (!result || payload.groupIndex === targetGroupIndex || targetGroupIndex < 0) return;
    const groups = cloneGroups(result.groups);
    const [image] = groups[payload.groupIndex].images.splice(payload.imageIndex, 1);
    if (!image) return;
    groups[targetGroupIndex].images.push(image);
    setGroups(groups);
    setStatus("Image moved. Save corrections when ready.");
  }

  function moveSelectedToNewGroup() {
    if (!result || selectedImages.size === 0) return;
    const groups = cloneGroups(result.groups);
    const moved: ResultImage[] = [];
    groups.forEach((group) => {
      group.images = group.images.filter((image) => {
        if (selectedImages.has(image.source_path)) {
          moved.push(image);
          return false;
        }
        return true;
      });
    });
    if (moved.length) groups.push({ name: "NewGroup", count: moved.length, images: moved });
    setGroups(groups);
    setSelectedImages(new Set());
    setStatus("New group created. Save corrections when ready.");
  }

  function removeSelectedImages() {
    if (!result || selectedImages.size === 0) return;
    const groups = cloneGroups(result.groups);
    groups.forEach((group) => {
      group.images = group.images.filter((image) => !selectedImages.has(image.source_path));
    });
    setGroups(groups);
    setSelectedImages(new Set());
    setStatus("Selected images removed. Save corrections when ready.");
  }

  function mergeSelectedGroups() {
    if (!result || selectedGroups.size < 2) return;
    const selected = result.groups.filter((group) => selectedGroups.has(group.name));
    const rest = result.groups.filter((group) => !selectedGroups.has(group.name));
    const mergedImages = selected.flatMap((group) => group.images);
    setGroups([{ name: "Merged", count: mergedImages.length, images: mergedImages }, ...rest]);
    setSelectedGroups(new Set());
    setStatus("Groups merged. Save corrections when ready.");
  }

  function toggleImage(image: ResultImage) {
    const next = new Set(selectedImages);
    if (next.has(image.source_path)) next.delete(image.source_path);
    else next.add(image.source_path);
    setSelectedImages(next);
  }

  function toggleGroup(groupName: string) {
    const next = new Set(selectedGroups);
    if (next.has(groupName)) next.delete(groupName);
    else next.add(groupName);
    setSelectedGroups(next);
  }

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">AI Image Matching Web</p>
          <h1>Auto Similar Image Organizer</h1>
          <p>Upload images, run SIFT image matching, review matched sets, correct mistakes, and export ordered results.</p>
        </div>
        <div className="stats">
          <span>{project ? "Project Ready" : "No Project"}</span>
          <strong>{totalImages}</strong>
          <small>images</small>
        </div>
      </section>

      <section className="workflow">
        <div className="panel">
          <label>Project</label>
          <div className="row">
            <input value={projectName} onChange={(event) => setProjectName(event.target.value)} />
            <button onClick={handleCreate} disabled={busy}>Create</button>
          </div>
          <select value={project?.id ?? ""} onChange={(event) => loadProject(event.target.value)}>
            <option value="">Project history</option>
            {projects.map((item) => (
              <option key={item.id} value={item.id}>{item.name} ({item.image_count})</option>
            ))}
          </select>
          {project && <p className="meta">ID: {project.id}</p>}
        </div>

        <div className="panel">
          <label>Upload / Restore</label>
          <input className="file" type="file" accept="image/*,.zip" multiple disabled={!project || busy} onChange={(event) => handleUpload(event.target.files)} />
          <input className="file" type="file" accept="application/json" disabled={busy} onChange={(event) => handleImport(event.target.files?.[0] ?? null)} />
          <select value={matchMode} disabled={busy} onChange={(event) => setMatchMode(event.target.value as MatchMode)}>
            {MATCH_MODES.map((mode) => (
              <option key={mode.value} value={mode.value}>{mode.label}</option>
            ))}
          </select>
          <div className="row">
            <button className="wide" onClick={handleMatch} disabled={!project || !project.image_count || busy}>Start Match</button>
            <button className="wide ghost" onClick={handleCancel} disabled={!activeJobId}>Cancel</button>
          </div>
        </div>

        <div className="panel status">
          <label>Status</label>
          <p>{status}</p>
          <div className="progress"><span style={{ width: `${progress}%` }} /></div>
        </div>
      </section>

      <section className="dashboard">
        {dashboard.map(([label, value]) => (
          <div className="metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <section className="toolbar panel">
        <input placeholder="Search group or filename..." value={filter} onChange={(event) => setFilter(event.target.value)} />
        <button onClick={moveSelectedToNewGroup} disabled={!selectedImages.size}>Move to New</button>
        <button onClick={removeSelectedImages} disabled={!selectedImages.size}>Remove</button>
        <button onClick={mergeSelectedGroups} disabled={selectedGroups.size < 2}>Merge</button>
        <button onClick={persistEdits} disabled={!result || busy}>Save</button>
        <button onClick={handleClearCache} disabled={busy}>Clear Cache</button>
        {project && <a className="button" href={projectFileUrl(project.id)}>Project JSON</a>}
        {project && <a className="button" href={exportUrl(project.id)}>Export ZIP</a>}
      </section>

      <section className="results">
        <div className="section-title">
          <h2>Match Results</h2>
          <span>{result ? `${visibleGroups.length}/${result.group_count} match sets` : "Waiting"}</span>
        </div>
        {!result && <div className="empty">After image matching, matched image sets will appear here.</div>}
        {visibleGroups.map((group) => {
          const realGroupIndex = result?.groups.findIndex((item) => item.name === group.name) ?? -1;
          return (
            <article
              className="group"
              key={group.name}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                const payload = JSON.parse(event.dataTransfer.getData("application/json")) as DragPayload;
                moveImage(payload, realGroupIndex);
              }}
            >
              <header>
                <label className="group-check">
                  <input type="checkbox" checked={selectedGroups.has(group.name)} onChange={() => toggleGroup(group.name)} />
                  <span>{group.name}</span>
                </label>
                <span>{group.count} images</span>
              </header>
              <div className="grid">
                {group.images.map((image, imageIndex) => (
                  <figure
                    key={`${group.name}-${image.source_path}`}
                    draggable
                    className={selectedImages.has(image.source_path) ? "selected" : ""}
                    onClick={() => toggleImage(image)}
                    onDoubleClick={() => setPreview({ groupName: group.name, image })}
                    onDragStart={(event) => {
                      event.dataTransfer.setData("application/json", JSON.stringify({ groupIndex: realGroupIndex, imageIndex }));
                    }}
                  >
                    {project && <img src={imageUrl(project.id, image.source_path)} alt={image.filename} loading="lazy" />}
                    <figcaption title={image.filename}>{image.filename}</figcaption>
                  </figure>
                ))}
              </div>
            </article>
          );
        })}
      </section>

      {preview && project && (
        <div className="preview" onClick={() => setPreview(null)}>
          <div className="preview-card" onClick={(event) => event.stopPropagation()}>
            <button className="preview-close" onClick={() => setPreview(null)}>Close</button>
            <img src={imageUrl(project.id, preview.image.source_path)} alt={preview.image.filename} />
            <h3>{preview.groupName}</h3>
            <p>{preview.image.filename}</p>
            <small>{preview.image.source_path}</small>
          </div>
        </div>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
