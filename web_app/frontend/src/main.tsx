import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  askAssistant,
  cancelJob,
  clearCache,
  createProject,
  exportUrl,
  getJob,
  getAiStatus,
  getResults,
  imageUrl,
  importProject,
  listProjects,
  projectFileUrl,
  startMatchJob,
  reloadAi,
  type AiStatus,
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
type MatchMode = "strict" | "standard" | "loose" | "fast" | "hybrid" | "turbo" | "ann" | "ai" | "ai-hybrid" | "ai-trained";
type ChatMessage = { role: "assistant" | "user"; text: string };
type SpotlightItem = {
  title: string;
  creator: string;
  category: string;
  viewers: string;
  description: string;
  tone: string;
};
type FooterLinkGroup = {
  title: string;
  links: { label: string; href: string; external?: boolean }[];
};
type MotionWallItem = {
  title: string;
  text: string;
  tag: string;
  metric: string;
  tone: string;
};
type FaqItem = {
  question: string;
  answer: string;
};

const UPLOAD_BATCH_SIZE = 500;
const MATCH_MODES: { value: MatchMode; label: string }[] = [
  { value: "ai-hybrid", label: "AI Hybrid" },
  { value: "ai-trained", label: "Trained AI" },
  { value: "ai", label: "AI Vector" },
  { value: "hybrid", label: "Classic Hybrid" },
  { value: "standard", label: "SIFT Match" },
  { value: "strict", label: "Strict SIFT" },
  { value: "loose", label: "Loose SIFT" },
  { value: "fast", label: "Fast SIFT" },
  { value: "turbo", label: "Turbo SIFT" },
  { value: "ann", label: "Vector Grouping" },
];

const SPOTLIGHT_ITEMS: SpotlightItem[] = [
  {
    title: "Duplicate discovery live run",
    creator: "AI Matching Studio",
    category: "Image Intelligence",
    viewers: "1.8K reviewing",
    description: "Watch incoming images separate into confident match sets while the model keeps near-duplicates within reach.",
    tone: "sunrise",
  },
  {
    title: "Visual cluster audit",
    creator: "Guardian Workspace",
    category: "Quality Control",
    viewers: "924 checking",
    description: "Flip through groups, inspect edge cases, and move uncertain images without breaking your project flow.",
    tone: "mint",
  },
  {
    title: "AI vector comparison",
    creator: "Hybrid Matcher",
    category: "Neural Search",
    viewers: "2.4K matching",
    description: "Classic features and AI embeddings work side by side for faster, cleaner image organization.",
    tone: "violet",
  },
  {
    title: "Export-ready results",
    creator: "Project Delivery",
    category: "Batch Workflow",
    viewers: "638 exporting",
    description: "Confirm your final sets, save corrections, and package matched files for handoff in one place.",
    tone: "coral",
  },
];

const FOOTER_LINK_GROUPS: FooterLinkGroup[] = [
  {
    title: "Product",
    links: [
      { label: "Projects", href: "#projects" },
      { label: "Matched Sets", href: "#results" },
      { label: "Exports", href: "#exports" },
      { label: "AI Status", href: "#home" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About AI Matcher", href: "#home" },
      { label: "Brand Assets", href: "#home" },
      { label: "Terms", href: "#home" },
      { label: "Privacy", href: "#home" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Documentation", href: "#projects" },
      { label: "Beginner Guide", href: "#home" },
      { label: "Model Notes", href: "#projects" },
      { label: "Support", href: "#home" },
    ],
  },
];

const SOCIAL_LINKS = [
  { label: "GitHub", logo: "GH", href: "https://github.com/" },
  { label: "X", logo: "X", href: "https://x.com/" },
  { label: "LinkedIn", logo: "in", href: "https://www.linkedin.com/" },
  { label: "Discord", logo: "DC", href: "https://discord.com/" },
];

const MOTION_WALL_ITEMS: MotionWallItem[] = [
  {
    title: "Upload folders or ZIPs",
    text: "Bring in a full image batch and let the workspace keep progress visible while files are processed.",
    tag: "Input",
    metric: "500/file batch",
    tone: "sunrise",
  },
  {
    title: "AI-assisted grouping",
    text: "Hybrid matching blends classic image features with embeddings for cleaner duplicate discovery.",
    tag: "Matching",
    metric: "AI Hybrid",
    tone: "violet",
  },
  {
    title: "Drag corrections",
    text: "Move images between sets, merge groups, and remove outliers before saving the final project state.",
    tag: "Review",
    metric: "Manual QA",
    tone: "mint",
  },
  {
    title: "Export results",
    text: "Package corrected match sets into a ZIP or keep the project JSON for future review.",
    tag: "Delivery",
    metric: "ZIP + JSON",
    tone: "coral",
  },
  {
    title: "Model visibility",
    text: "Check backend, framework, model source, cache hits, and live job metrics without leaving the page.",
    tag: "Ops",
    metric: "Live status",
    tone: "sunrise",
  },
  {
    title: "Beginner support",
    text: "The assistant panel keeps common workflow questions close while the user learns the matching process.",
    tag: "Help",
    metric: "Guided",
    tone: "mint",
  },
];

const FAQ_ITEMS: FaqItem[] = [
  {
    question: "What kind of images can I upload?",
    answer: "You can upload individual image files or ZIP archives. For larger projects, the app processes files in batches so the interface stays responsive.",
  },
  {
    question: "Which matching mode should I start with?",
    answer: "AI Hybrid is the best first choice because it balances neural similarity with classic feature matching. You can switch to faster or stricter modes when your dataset needs it.",
  },
  {
    question: "Can I fix groups after the AI finishes?",
    answer: "Yes. Select images, drag them between groups, create new sets, merge selected groups, remove outliers, and then save the corrected result.",
  },
  {
    question: "Where does my project data go?",
    answer: "Projects are stored in the local workspace for this app. You can export results as a ZIP or download the project JSON for backup and review.",
  },
  {
    question: "Why does the AI status say fallback?",
    answer: "Fallback means the AI model is not currently available, so the app relies on classic matching. Use Refresh AI or Reload model after checking the backend environment.",
  },
];

const PROMPT_SUGGESTIONS = [
  "Create a new image classification project and prepare upload",
  "Upload images, then run AI Hybrid matching",
  "Review duplicate groups and help me fix mistakes",
  "Show model status, cache metrics, and run progress",
  "Export corrected match sets as ZIP and project JSON",
  "Explain this workflow step by step for a beginner",
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
  const [projectName, setProjectName] = useState("AI Matching Studio");
  const [commandPrompt, setCommandPrompt] = useState("");
  const [commandSubmitted, setCommandSubmitted] = useState(false);
  const [project, setProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [status, setStatus] = useState("Backend ready. Create or load a project.");
  const [matchMode, setMatchMode] = useState<MatchMode>("ai-hybrid");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(0);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [liveMetrics, setLiveMetrics] = useState<Record<string, unknown>>({});
  const [aiStatus, setAiStatus] = useState<AiStatus | null>(null);
  const [filter, setFilter] = useState("");
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [selectedGroups, setSelectedGroups] = useState<Set<string>>(new Set());
  const [preview, setPreview] = useState<PreviewState | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatBusy, setChatBusy] = useState(false);
  const [activeSpotlight, setActiveSpotlight] = useState(0);
  const [footerLanguage, setFooterLanguage] = useState("zh-Hant");
  const [footerRegion, setFooterRegion] = useState("TW");
  const [openFaq, setOpenFaq] = useState(0);
  const [chatSuggestions, setChatSuggestions] = useState(["怎么上传图片？", "为什么 AI 是 Fallback？", "怎么导出分组结果？"]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "你好，我是网站守护女神。第一次用的话，问我上传、AI 匹配、修正分组、导出结果都可以。",
    },
  ]);
  const pollTimer = useRef<number | null>(null);

  useEffect(() => {
    refreshProjects();
    refreshAiStatus();
    return () => {
      if (pollTimer.current) window.clearInterval(pollTimer.current);
    };
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveSpotlight((index) => (index + 1) % SPOTLIGHT_ITEMS.length);
    }, 6500);
    return () => window.clearInterval(timer);
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
      ["Sets", result?.group_count ?? 0],
      ["Images", totalImages],
      ["AI", scan.ai_backend ?? match.ai_backend ?? aiStatus?.ai_backend ?? "ready"],
      ["Model", scan.ai_model ?? match.ai_model ?? aiStatus?.ai_model ?? match.vector_backend ?? "classic"],
      ["Framework", scan.ai_framework ?? aiStatus?.ai_framework ?? "classic"],
      ["Current", match.current_image ?? 0],
      ["Processed", match.processed_images ?? 0],
      ["Groups", match.current_groups ?? 0],
      ["Cache hits", scan.cache_hits ?? 0],
      ["AI cache", scan.embedding_cache_hits ?? scan.ai_cache_hits ?? 0],
      ["Vector hits", match.embedding_candidates ?? 0],
      ["Auto", match.hash_auto_matches ?? 0],
      ["SIFT calls", match.sift_calls ?? 0],
      ["Speed", match.images_per_second ?? 0],
      ["ETA", match.eta_seconds ?? 0],
      ["Limited", match.limited_candidates ?? 0],
      ["Rejected", match.candidate_rejects ?? 0],
      ["Skipped", skipped],
    ];
  }, [result, totalImages, liveMetrics, aiStatus]);

  function setGroups(groups: ResultGroup[]) {
    if (!result) return;
    const normalized = normalizeGroups(groups);
    setResult({ ...result, group_count: normalized.length, groups: normalized });
  }

  function submitCommand(prompt = commandPrompt) {
    const text = prompt.trim();
    if (!text) return;
    setCommandPrompt(text);
    setCommandSubmitted(true);
    setProjectName(text.slice(0, 64));
    setStatus("Instruction received. Create or load a project, upload images, then run matching.");
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
      setCommandSubmitted(true);
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
      setCommandSubmitted(true);
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
    setCommandSubmitted(true);
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
    setCommandSubmitted(true);
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

  async function refreshAiStatus() {
    try {
      setAiStatus(await getAiStatus());
    } catch (error) {
      setAiStatus({
        ai_backend: "unavailable",
        ai_model: "unknown",
        ai_status: String(error),
        ai_ready: false,
      });
    }
  }

  async function handleReloadAi() {
    setBusy(true);
    try {
      const response = await reloadAi();
      setAiStatus(response);
      setStatus(response.ai_status || "AI model reloaded.");
    } catch (error) {
      setStatus(String(error));
    } finally {
      setBusy(false);
    }
  }

  async function sendChat(message = chatInput) {
    const text = message.trim();
    if (!text || chatBusy) return;
    setChatInput("");
    setChatOpen(true);
    setChatMessages((items) => [...items, { role: "user", text }]);
    setChatBusy(true);
    try {
      const response = await askAssistant(text, {
        project: project?.name,
        image_count: totalImages,
        mode: matchMode,
        ai_backend: aiStatus?.ai_backend,
        ai_ready: aiStatus?.ai_ready,
      });
      setChatMessages((items) => [...items, { role: "assistant", text: response.answer }]);
      setChatSuggestions(response.suggestions);
    } catch (error) {
      setChatMessages((items) => [...items, { role: "assistant", text: "我这边暂时连不上助手 API。你可以先刷新页面，或检查后端服务是否在 8000 端口运行。" }]);
    } finally {
      setChatBusy(false);
    }
  }

  const currentModeLabel = MATCH_MODES.find((mode) => mode.value === matchMode)?.label ?? "AI Hybrid";
  const recentProjects = projects.slice(0, 6);
  const spotlight = SPOTLIGHT_ITEMS[activeSpotlight];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img className="brand-mark" src="/guardian-logo.png" alt="AI Matcher guardian logo" />
          <div>
            <strong>AI Matcher</strong>
            <small>Guardian workspace</small>
          </div>
        </div>
        <nav className="nav">
          <a className="active" href="#home">Home</a>
          <a href="#projects">Projects</a>
          <a href="#results">Results</a>
          <a href="#exports">Exports</a>
        </nav>
        <div className="side-section">
          <span>Projects</span>
          <button className="side-link" onClick={handleCreate} disabled={busy}>New project</button>
          {recentProjects.map((item) => (
            <button className={project?.id === item.id ? "side-link selected" : "side-link"} key={item.id} onClick={() => loadProject(item.id)}>
              <span>{item.name}</span>
              <small>{item.image_count}</small>
            </button>
          ))}
        </div>
        <div className="side-card">
          <span>{currentModeLabel}</span>
          <strong>{totalImages}</strong>
          <small>images in scope</small>
        </div>
      </aside>

      <section className="main-area" id="home">
        <header className="topbar">
          <div className="title-block">
            <span className="crumb">Dashboard</span>
            <h1>What should AI organize today?</h1>
            <p className="guardian-line">Your guardian goddess watches over every image match, correction, and AI model run.</p>
          </div>
          <div className="guardian-card" aria-label="Website guardian goddess logo">
            <img src="/guardian-logo.png" alt="Website guardian goddess" />
            <div>
              <span>Guardian Goddess</span>
              <strong>AI Matching Studio</strong>
            </div>
          </div>
          <div className="top-actions">
            <select value={project?.id ?? ""} onChange={(event) => loadProject(event.target.value)}>
              <option value="">Project history</option>
              {projects.map((item) => (
                <option key={item.id} value={item.id}>{item.name} ({item.image_count})</option>
              ))}
            </select>
            <button onClick={handleClearCache} disabled={busy}>Clear cache</button>
          </div>
        </header>

        <section className="spotlight" aria-label="Featured video carousel">
          <button
            className="spotlight-arrow"
            aria-label="Previous featured video"
            onClick={() => setActiveSpotlight((index) => (index + SPOTLIGHT_ITEMS.length - 1) % SPOTLIGHT_ITEMS.length)}
          >
            {"<"}
          </button>
          <div className={`spotlight-stage tone-${spotlight.tone}`}>
            <div className="spotlight-video" aria-hidden="true">
              <div className="video-window">
                <span className="live-pill">LIVE</span>
                <div className="scan-line" />
                <div className="video-grid-preview">
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
            <article className="spotlight-copy">
              <span className="spotlight-kicker">{spotlight.category}</span>
              <h2>{spotlight.title}</h2>
              <strong>{spotlight.creator}</strong>
              <p>{spotlight.description}</p>
              <div className="spotlight-meta">
                <span>{spotlight.viewers}</span>
                <span>{currentModeLabel}</span>
              </div>
            </article>
          </div>
          <button
            className="spotlight-arrow"
            aria-label="Next featured video"
            onClick={() => setActiveSpotlight((index) => (index + 1) % SPOTLIGHT_ITEMS.length)}
          >
            {">"}
          </button>
          <div className="spotlight-rail">
            {SPOTLIGHT_ITEMS.map((item, index) => (
              <button
                className={index === activeSpotlight ? "spotlight-thumb active" : "spotlight-thumb"}
                key={item.title}
                onClick={() => setActiveSpotlight(index)}
              >
                <span className={`thumb-art tone-${item.tone}`} />
                <span>
                  <strong>{item.title}</strong>
                  <small>{item.category}</small>
                </span>
              </button>
            ))}
          </div>
        </section>

        <section className={commandSubmitted ? "prompt-console compact" : "prompt-console"} aria-label="AI command prompt">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              submitCommand();
            }}
          >
            <label htmlFor="command-prompt">What do you want AI Matcher to do?</label>
            <div className="prompt-box">
              <textarea
                id="command-prompt"
                value={commandPrompt}
                onChange={(event) => setCommandPrompt(event.target.value)}
                placeholder="Describe the image classification task, matching mode, export goal, or review workflow..."
              />
              <button className="primary" disabled={!commandPrompt.trim()}>Start</button>
            </div>
          </form>
          <div className="prompt-suggestions" aria-label="Recommended functions">
            {PROMPT_SUGGESTIONS.map((item) => (
              <button key={item} type="button" onClick={() => submitCommand(item)}>
                {item}
              </button>
            ))}
          </div>
        </section>

        {commandSubmitted && (
          <>
            <section className="composer workflow-controls">
              <input value={projectName} onChange={(event) => setProjectName(event.target.value)} />
              <div className="composer-actions">
                <input className="file" type="file" accept="image/*,.zip" multiple disabled={!project || busy} onChange={(event) => handleUpload(event.target.files)} />
                <select value={matchMode} disabled={busy} onChange={(event) => setMatchMode(event.target.value as MatchMode)}>
                  {MATCH_MODES.map((mode) => (
                    <option key={mode.value} value={mode.value}>{mode.label}</option>
                  ))}
                </select>
                <button onClick={handleCreate} disabled={busy}>Create</button>
                <button className="primary" onClick={handleMatch} disabled={!project || !project.image_count || busy}>Run</button>
                <button onClick={handleCancel} disabled={!activeJobId}>Cancel</button>
              </div>
            </section>

        <section className="status-strip">
          <div>
            <span>Run state</span>
            <strong>{status}</strong>
          </div>
          <div className="progress"><span style={{ width: `${progress}%` }} /></div>
        </section>

        <section className="dashboard">
          {dashboard.map(([label, value]) => (
            <div className="metric" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </section>

        <section className="project-grid" id="projects">
          <article className="project-panel">
            <div className="section-title">
              <h2>Current project</h2>
              <span>{project ? project.name : "No project"}</span>
            </div>
            <p className="meta">{project ? project.id : "Create or load a project to start matching."}</p>
            <div className="panel-actions">
              <input className="file" type="file" accept="application/json" disabled={busy} onChange={(event) => handleImport(event.target.files?.[0] ?? null)} />
              {project && <a className="button" href={projectFileUrl(project.id)}>Project JSON</a>}
              {project && <a className="button" href={exportUrl(project.id)}>Export ZIP</a>}
            </div>
          </article>

          <article className="project-panel">
            <div className="section-title">
              <h2>AI solution</h2>
              <span>{aiStatus?.ai_ready ? "Neural" : "Fallback"}</span>
            </div>
            <div className="ai-card">
              <strong>{aiStatus?.ai_model ?? "Loading model status..."}</strong>
              <span>{aiStatus?.ai_framework ?? "framework pending"}</span>
              <p>{aiStatus?.ai_status ?? "Checking Hugging Face encoder."}</p>
              {aiStatus?.ai_last_error && <small>{aiStatus.ai_last_error}</small>}
            </div>
            <div className="panel-actions">
              <button onClick={refreshAiStatus} disabled={busy}>Refresh AI</button>
              <button onClick={handleReloadAi} disabled={busy}>Reload model</button>
            </div>
          </article>

          <article className="project-panel">
            <div className="section-title">
              <h2>Recent projects</h2>
              <span>{projects.length}</span>
            </div>
            <div className="recent-list">
              {recentProjects.length === 0 && <div className="empty compact">No projects yet.</div>}
              {recentProjects.map((item) => (
                <button className="project-row" key={item.id} onClick={() => loadProject(item.id)}>
                  <span>{item.name}</span>
                  <small>{item.image_count} images</small>
                </button>
              ))}
            </div>
          </article>
        </section>

        <section className="toolbar panel" id="exports">
          <input placeholder="Search group or filename..." value={filter} onChange={(event) => setFilter(event.target.value)} />
          <button onClick={moveSelectedToNewGroup} disabled={!selectedImages.size}>New Set</button>
          <button onClick={removeSelectedImages} disabled={!selectedImages.size}>Remove</button>
          <button onClick={mergeSelectedGroups} disabled={selectedGroups.size < 2}>Merge</button>
          <button onClick={persistEdits} disabled={!result || busy}>Save</button>
        </section>

        <section className="results" id="results">
          <div className="section-title">
            <h2>Matched Sets</h2>
            <span>{result ? `${visibleGroups.length}/${result.group_count} match sets` : "Waiting"}</span>
          </div>
          {!result && <div className="empty">Run AI to generate grouped image sets.</div>}
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

        <section className="motion-wall-section" aria-label="Dynamic workflow wall">
          <div className="section-title">
            <h2>Workflow Wall</h2>
            <span>Auto-scrolling product moments</span>
          </div>
          <div className="motion-wall">
            <div className="motion-track motion-track-forward">
              {[...MOTION_WALL_ITEMS, ...MOTION_WALL_ITEMS].map((item, index) => (
                <article className={`motion-card tone-${item.tone}`} key={`forward-${item.title}-${index}`}>
                  <span>{item.tag}</span>
                  <strong>{item.title}</strong>
                  <p>{item.text}</p>
                  <small>{item.metric}</small>
                </article>
              ))}
            </div>
            <div className="motion-track motion-track-reverse">
              {[...MOTION_WALL_ITEMS.slice().reverse(), ...MOTION_WALL_ITEMS.slice().reverse()].map((item, index) => (
                <article className={`motion-card tone-${item.tone}`} key={`reverse-${item.title}-${index}`}>
                  <span>{item.tag}</span>
                  <strong>{item.title}</strong>
                  <p>{item.text}</p>
                  <small>{item.metric}</small>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="faq-section" aria-label="Frequently asked questions">
          <div className="faq-intro">
            <span>FAQ</span>
            <h2>Questions before your next match run</h2>
            <p>Short answers for the workflow details users usually need before uploading, reviewing, and exporting.</p>
          </div>
          <div className="faq-list">
            {FAQ_ITEMS.map((item, index) => {
              const isOpen = openFaq === index;
              return (
                <article className={isOpen ? "faq-item open" : "faq-item"} key={item.question}>
                  <button onClick={() => setOpenFaq(isOpen ? -1 : index)} aria-expanded={isOpen}>
                    <span>{item.question}</span>
                    <strong>{isOpen ? "-" : "+"}</strong>
                  </button>
                  {isOpen && <p>{item.answer}</p>}
                </article>
              );
            })}
          </div>
        </section>
          </>
        )}

        <footer className="site-footer">
          <div className="footer-brand">
            <div className="footer-logo">
              <img src="/guardian-logo.png" alt="AI Matcher logo" />
              <div>
                <strong>AI Matcher</strong>
                <span>Guardian workspace</span>
              </div>
            </div>
            <p>Professional image matching, correction, and export tools for focused visual datasets.</p>
            <div className="locale-row">
              <label>
                <span>Language</span>
                <select value={footerLanguage} onChange={(event) => setFooterLanguage(event.target.value)}>
                  <option value="zh-Hant">繁體中文</option>
                  <option value="en">English</option>
                  <option value="ja">日本語</option>
                  <option value="ko">한국어</option>
                </select>
              </label>
              <label>
                <span>Region</span>
                <select value={footerRegion} onChange={(event) => setFooterRegion(event.target.value)}>
                  <option value="TW">Taiwan</option>
                  <option value="US">United States</option>
                  <option value="JP">Japan</option>
                  <option value="KR">Korea</option>
                </select>
              </label>
            </div>
          </div>
          <div className="footer-links">
            {FOOTER_LINK_GROUPS.map((group) => (
              <nav className="footer-column" key={group.title} aria-label={group.title}>
                <strong>{group.title}</strong>
                {group.links.map((link) => (
                  <a key={link.label} href={link.href}>
                    {link.label}
                  </a>
                ))}
              </nav>
            ))}
            <nav className="footer-column social-column" aria-label="Social media">
              <strong>Social</strong>
              <div className="social-links">
                {SOCIAL_LINKS.map((link) => (
                  <a key={link.label} href={link.href} target="_blank" rel="noreferrer" aria-label={link.label} title={link.label}>
                    <span>{link.logo}</span>
                  </a>
                ))}
              </div>
            </nav>
          </div>
          <div className="footer-bottom">
            <span>© 2026 AI Matcher Studio</span>
            <span>{footerLanguage} · {footerRegion}</span>
          </div>
        </footer>
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

      <section className={chatOpen ? "chat-widget open" : "chat-widget"}>
        {chatOpen && (
          <div className="chat-panel">
            <header>
              <img src="/guardian-logo.png" alt="Guardian assistant" />
              <div>
                <strong>Guardian Goddess</strong>
                <span>Beginner tech support</span>
              </div>
              <button onClick={() => setChatOpen(false)}>Close</button>
            </header>
            <div className="chat-messages">
              {chatMessages.map((message, index) => (
                <div className={message.role === "assistant" ? "chat-bubble assistant" : "chat-bubble user"} key={`${message.role}-${index}`}>
                  {message.text}
                </div>
              ))}
              {chatBusy && <div className="chat-bubble assistant">我正在帮你看...</div>}
            </div>
            <div className="chat-suggestions">
              {chatSuggestions.map((item) => (
                <button key={item} onClick={() => sendChat(item)} disabled={chatBusy}>{item}</button>
              ))}
            </div>
            <form
              className="chat-input"
              onSubmit={(event) => {
                event.preventDefault();
                sendChat();
              }}
            >
              <input value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder="问我怎么使用这个网站..." />
              <button className="primary" disabled={chatBusy || !chatInput.trim()}>Send</button>
            </form>
          </div>
        )}
        <button className="chat-launcher" onClick={() => setChatOpen((value) => !value)}>
          <img src="/guardian-logo.png" alt="Open guardian assistant" />
          <span>技术支援</span>
        </button>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
