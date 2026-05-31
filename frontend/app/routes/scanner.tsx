import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Camera,
  CheckCircle2,
  Cpu,
  Gauge,
  Maximize2,
  Play,
  RefreshCw,
  ScanLine,
  Server,
  Settings,
  X,
  Zap,
} from "lucide-react";
import Navbar from "~/components/navbar";
import { Protect } from "~/features/auth/components/protect";

type ScannerStatus = {
  camera_url: string;
  status: string;
  frames_processed: number;
  defects_detected: number;
  last_latency_ms: number;
  last_fps: number;
  last_seen: number | null;
  last_error: string | null;
  model: string;
  confidence_threshold: number;
};

type DetectionEvent = {
  id: string;
  label: string;
  confidence: number;
  severity: "critical" | "warning";
  timestamp: number;
};

type ModelCatalog = {
  models: string[];
  active: string;
};

const SCANNER_API_URL =
  import.meta.env.VITE_SCANNER_URL ?? "http://localhost:8012";

const initialStatus: ScannerStatus = {
  camera_url: "http://192.168.1.15:8080/video",
  status: "connecting",
  frames_processed: 0,
  defects_detected: 0,
  last_latency_ms: 0,
  last_fps: 0,
  last_seen: null,
  last_error: null,
  model: "textile_defect_model.pt",
  confidence_threshold: 0.5,
};

export default function Scanner() {
  const [status, setStatus] = useState<ScannerStatus>(initialStatus);
  const [events, setEvents] = useState<DetectionEvent[]>([]);
  const [cameraUrl, setCameraUrl] = useState(initialStatus.camera_url);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState(initialStatus.model);
  const [feedKey, setFeedKey] = useState(Date.now());
  const [isUpdating, setIsUpdating] = useState(false);
  const [isModelUpdating, setIsModelUpdating] = useState(false);
  const [serviceReachable, setServiceReachable] = useState(false);
  const [feedOnline, setFeedOnline] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);

  const streamUrl = useMemo(
    () => `${SCANNER_API_URL}/video_feed?key=${feedKey}`,
    [feedKey],
  );
  const serviceState = normalizeState(status.status, serviceReachable);
  const cameraOffline =
    serviceReachable && (status.status === "offline" || Boolean(status.last_error));
  const streamAvailable = feedOnline && serviceReachable && !cameraOffline;

  useEffect(() => {
    let mounted = true;

    async function refreshTelemetry() {
      try {
        const [statusResponse, eventsResponse, modelsResponse] = await Promise.all([
          fetch(`${SCANNER_API_URL}/status`),
          fetch(`${SCANNER_API_URL}/events?limit=6`),
          fetch(`${SCANNER_API_URL}/models`),
        ]);

        if (!statusResponse.ok || !eventsResponse.ok || !modelsResponse.ok) {
          throw new Error("Scanner telemetry unavailable");
        }

        const nextStatus = (await statusResponse.json()) as ScannerStatus;
        const nextEvents = (await eventsResponse.json()) as { events: DetectionEvent[] };
        const nextModels = (await modelsResponse.json()) as ModelCatalog;

        if (!mounted) return;
        setStatus(nextStatus);
        setCameraUrl((current) => current || nextStatus.camera_url);
        setSelectedModel((current) => current || nextStatus.model);
        setEvents(nextEvents.events ?? []);
        setModels(nextModels.models ?? []);
        setServiceReachable(true);
      } catch {
        if (!mounted) return;
        setServiceReachable(false);
      }
    }

    refreshTelemetry();
    const interval = window.setInterval(refreshTelemetry, 1500);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  async function handleUpdateCamera() {
    setIsUpdating(true);
    try {
      const response = await fetch(`${SCANNER_API_URL}/source`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: cameraUrl }),
      });

      if (!response.ok) {
        throw new Error("Camera source update failed");
      }

      const nextStatus = (await response.json()) as ScannerStatus;
      setStatus(nextStatus);
      setEvents([]);
      setFeedOnline(true);
      setFeedKey(Date.now());
    } catch {
      setServiceReachable(false);
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleUpdateModel() {
    setIsModelUpdating(true);
    try {
      const response = await fetch(`${SCANNER_API_URL}/model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: selectedModel }),
      });

      if (!response.ok) {
        throw new Error("Model update failed");
      }

      const nextStatus = (await response.json()) as ScannerStatus;
      setStatus(nextStatus);
      setEvents([]);
      setFeedKey(Date.now());
    } catch {
      setServiceReachable(false);
    } finally {
      setIsModelUpdating(false);
    }
  }

  return (
    <Protect>
      <div className="min-h-screen bg-black text-neutral-200 selection:bg-emerald-500/30">
        <Navbar />

        <main className="mx-auto flex max-w-[1600px] flex-col gap-5 px-5 py-5">
          <section className="flex flex-col gap-4 border-b border-neutral-900 pb-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-2xl">
              <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-emerald-400">
                <ScanLine className="h-4 w-4" />
                Vision microservice
              </div>
              <h1 className="text-3xl font-semibold text-white">
                Textile quality scanner
              </h1>
              <p className="mt-2 text-sm leading-6 text-neutral-500">
                A dedicated AI inspection cell connected to the production pipeline,
                processing the phone camera stream through the trained YOLO defect model.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <Metric icon={Server} label="Service" value={serviceState.label} tone={serviceState.tone} />
              <Metric icon={Activity} label="Throughput" value={`${status.last_fps || 0} fps`} />
              <Metric icon={Gauge} label="Latency" value={`${status.last_latency_ms || 0} ms`} />
              <Metric icon={ScanLine} label="Defects" value={`${status.defects_detected}`} tone={status.defects_detected > 0 ? "amber" : "emerald"} />
            </div>
          </section>

          <section className="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
            <div className="flex flex-col gap-4">
              <div className="relative aspect-video overflow-hidden rounded-[8px] border border-neutral-800 bg-neutral-950 shadow-2xl">
                <div className="pointer-events-none absolute inset-0 z-10 bg-[linear-gradient(180deg,rgba(16,185,129,0.08),transparent_24%,transparent_76%,rgba(20,184,166,0.08))]" />
                <div className="pointer-events-none absolute inset-x-0 top-0 z-20 h-16 bg-gradient-to-b from-black/80 to-transparent" />
                <div className="pointer-events-none absolute inset-x-0 bottom-0 z-20 h-20 bg-gradient-to-t from-black/85 to-transparent" />

                <div className={`absolute left-4 top-4 z-30 flex items-center gap-2 rounded-[8px] border px-3 py-1.5 backdrop-blur ${cameraOffline ? "border-amber-500/30 bg-amber-950/70" : "border-red-500/20 bg-black/70"}`}>
                  <span className={`h-2 w-2 rounded-full ${cameraOffline ? "bg-amber-400" : "bg-red-500 shadow-[0_0_16px_rgba(239,68,68,0.8)]"}`} />
                  <span className="font-mono text-xs text-neutral-200">
                    {cameraOffline ? "CAMERA OFFLINE" : "LIVE INSPECTION"}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={() => setIsExpanded(true)}
                  className="absolute right-4 top-4 z-30 flex h-9 w-9 items-center justify-center rounded-[8px] border border-neutral-800 bg-black/70 text-neutral-300 transition hover:border-neutral-600 hover:text-white"
                  title="Open larger scanner view"
                >
                  <Maximize2 className="h-4 w-4" />
                </button>

                {streamAvailable ? (
                  <img
                    src={streamUrl}
                    alt="Live textile scanner feed"
                    className="relative z-0 h-full w-full object-cover"
                    onLoad={() => setFeedOnline(true)}
                    onError={() => setFeedOnline(false)}
                  />
                ) : (
                  <div className="flex h-full flex-col items-center justify-center gap-4 bg-neutral-950 px-6 text-center">
                    <div className={`flex h-16 w-16 items-center justify-center rounded-full border ${cameraOffline ? "border-amber-500/30 bg-amber-500/10" : "border-neutral-800 bg-black"}`}>
                      <Camera className={`h-8 w-8 ${cameraOffline ? "text-amber-400" : "text-neutral-700"}`} />
                    </div>
                    <div className="max-w-md">
                      <p className={`text-sm font-semibold ${cameraOffline ? "text-amber-300" : "text-neutral-300"}`}>
                        {cameraOffline ? "Phone camera feed is offline" : "Waiting for scanner stream"}
                      </p>
                      <p className="mt-2 text-xs leading-5 text-neutral-500">
                        {status.last_error ?? "Start the scanner container and keep the phone camera online."}
                      </p>
                      <p className="mt-2 font-mono text-[11px] text-neutral-600">
                        {status.camera_url}
                      </p>
                    </div>
                  </div>
                )}

                {streamAvailable && (
                <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center">
                  <div className="h-[42%] w-[42%] rounded-[8px] border border-emerald-400/25">
                    <div className="h-full w-full animate-[scanner-sweep_2.8s_ease-in-out_infinite] border-t border-emerald-400/70" />
                  </div>
                </div>
                )}

                <div className="absolute bottom-4 left-4 right-4 z-30 grid gap-2 sm:grid-cols-3">
                  <PipelineBadge icon={ScanLine} label="Inspection stage" value="Vision Gate" />
                  <PipelineBadge icon={Cpu} label="Model" value={status.model} />
                  <PipelineBadge icon={Zap} label="Threshold" value={`${Math.round(status.confidence_threshold * 100)}%`} />
                </div>
              </div>

              <div className="flex flex-col gap-3 rounded-[8px] border border-neutral-800 bg-neutral-950 p-4 lg:flex-row lg:items-center">
                <div className="flex min-w-48 items-center gap-3 text-neutral-400">
                  <Settings className="h-5 w-5 text-emerald-400" />
                  <div>
                    <p className="text-sm font-medium text-white">Camera source</p>
                    <p className="text-xs text-neutral-600">Saved by the scanner service after Connect</p>
                  </div>
                </div>

                <input
                  type="text"
                  value={cameraUrl}
                  onChange={(event) => setCameraUrl(event.target.value)}
                  className="min-h-10 flex-1 rounded-[8px] border border-neutral-800 bg-black px-3 text-sm text-white outline-none transition focus:border-emerald-500"
                  placeholder="http://192.168.1.15:8080/video"
                />

                <button
                  type="button"
                  onClick={handleUpdateCamera}
                  disabled={isUpdating}
                  className="flex min-h-10 items-center justify-center gap-2 rounded-[8px] bg-emerald-500 px-4 text-sm font-semibold text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isUpdating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                  Connect
                </button>
              </div>
              <div className="rounded-[8px] border border-neutral-900 bg-black px-3 py-2 font-mono text-xs text-neutral-500">
                Active source: <span className="text-neutral-300">{status.camera_url}</span>
              </div>

              <div className="flex flex-col gap-3 rounded-[8px] border border-neutral-800 bg-neutral-950 p-4 lg:flex-row lg:items-center">
                <div className="flex min-w-48 items-center gap-3 text-neutral-400">
                  <Cpu className="h-5 w-5 text-emerald-400" />
                  <div>
                    <p className="text-sm font-medium text-white">Detection model</p>
                    <p className="text-xs text-neutral-600">Choose a .pt model from the scanner service</p>
                  </div>
                </div>

                <select
                  value={selectedModel}
                  onChange={(event) => setSelectedModel(event.target.value)}
                  className="min-h-10 flex-1 rounded-[8px] border border-neutral-800 bg-black px-3 text-sm text-white outline-none transition focus:border-emerald-500"
                >
                  {models.length > 0 ? (
                    models.map((modelName) => (
                      <option key={modelName} value={modelName}>
                        {modelName}
                      </option>
                    ))
                  ) : (
                    <option value={status.model}>{status.model}</option>
                  )}
                </select>

                <button
                  type="button"
                  onClick={handleUpdateModel}
                  disabled={isModelUpdating || selectedModel === status.model}
                  className="flex min-h-10 items-center justify-center gap-2 rounded-[8px] border border-neutral-700 px-4 text-sm font-semibold text-white transition hover:border-emerald-500 hover:text-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isModelUpdating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Cpu className="h-4 w-4" />}
                  Apply model
                </button>
              </div>
            </div>

            <aside className="flex flex-col gap-4">
              <div className="rounded-[8px] border border-neutral-800 bg-neutral-950 p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-semibold text-white">Inspection queue</h2>
                    <p className="mt-1 text-xs text-neutral-600">Latest model decisions from the scanner service</p>
                  </div>
                  <span className="rounded-[8px] border border-neutral-800 px-2 py-1 font-mono text-xs text-neutral-500">
                    {status.frames_processed} frames
                  </span>
                </div>

                <div className="flex flex-col gap-2">
                  {events.length > 0 ? (
                    events.map((event) => <DetectionRow key={event.id} event={event} />)
                  ) : (
                    <div className="flex items-start gap-3 rounded-[8px] border border-neutral-800 bg-black p-3">
                      <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                      <div>
                        <p className="text-xs font-medium text-white">No defects in current window</p>
                        <p className="mt-1 text-xs text-neutral-600">The line is passing the active quality gate.</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </aside>
          </section>
        </main>

        {isExpanded && (
          <div className="fixed inset-0 z-[80] flex flex-col bg-black">
            <div className="flex h-12 items-center justify-between border-b border-neutral-800 bg-neutral-950 px-5">
              <div className="flex items-center gap-3">
                <div className={`h-2.5 w-2.5 rounded-full ${cameraOffline ? "bg-amber-400" : "bg-emerald-400"}`} />
                <div>
                  <p className="text-sm font-semibold text-white">Expanded scanner view</p>
                  <p className="text-xs text-neutral-500">{status.model} - {status.camera_url}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsExpanded(false)}
                className="flex h-9 w-9 items-center justify-center rounded-[8px] border border-neutral-800 text-neutral-300 transition hover:border-neutral-600 hover:text-white"
                title="Close scanner view"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="relative min-h-0 flex-1 bg-neutral-950">
              {streamAvailable ? (
                <img
                  src={streamUrl}
                  alt="Expanded live textile scanner feed"
                  className="h-full w-full object-contain"
                  onLoad={() => setFeedOnline(true)}
                  onError={() => setFeedOnline(false)}
                />
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-4 px-6 text-center">
                  <div className={`flex h-20 w-20 items-center justify-center rounded-full border ${cameraOffline ? "border-amber-500/30 bg-amber-500/10" : "border-neutral-800 bg-black"}`}>
                    <Camera className={`h-10 w-10 ${cameraOffline ? "text-amber-400" : "text-neutral-700"}`} />
                  </div>
                  <div className="max-w-xl">
                    <p className={`text-base font-semibold ${cameraOffline ? "text-amber-300" : "text-neutral-300"}`}>
                      {cameraOffline ? "Phone camera feed is offline" : "Waiting for scanner stream"}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-neutral-500">
                      {status.last_error ?? "Start the scanner container and keep the phone camera online."}
                    </p>
                    <p className="mt-3 font-mono text-xs text-neutral-600">{status.camera_url}</p>
                  </div>
                </div>
              )}

              {streamAvailable && (
                <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                  <div className="h-[50%] w-[50%] rounded-[8px] border border-emerald-400/25">
                    <div className="h-full w-full animate-[scanner-sweep_2.8s_ease-in-out_infinite] border-t border-emerald-400/70" />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes scanner-sweep {
          0% { transform: translateY(0); opacity: 0.25; }
          50% { transform: translateY(100%); opacity: 0.95; }
          100% { transform: translateY(0); opacity: 0.25; }
        }
      `}</style>
    </Protect>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  tone = "neutral",
}: {
  icon: typeof Activity;
  label: string;
  value: string;
  tone?: "neutral" | "emerald" | "amber" | "red";
}) {
  const toneClass = {
    neutral: "text-neutral-300",
    emerald: "text-emerald-400",
    amber: "text-amber-400",
    red: "text-red-400",
  }[tone];

  return (
    <div className="min-w-32 rounded-[8px] border border-neutral-800 bg-neutral-950 px-3 py-2">
      <div className="mb-1 flex items-center gap-1.5 text-[11px] text-neutral-600">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      <p className={`text-sm font-semibold ${toneClass}`}>{value}</p>
    </div>
  );
}

function PipelineBadge({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[8px] border border-neutral-800/80 bg-black/75 px-3 py-2 backdrop-blur">
      <div className="flex items-center gap-1.5 text-[11px] text-neutral-500">
        <Icon className="h-3.5 w-3.5 text-emerald-400" />
        {label}
      </div>
      <p className="mt-1 truncate text-xs font-medium text-white">{value}</p>
    </div>
  );
}

function DetectionRow({ event }: { event: DetectionEvent }) {
  const isCritical = event.severity === "critical";

  return (
    <div className={`flex items-start gap-3 rounded-[8px] border p-3 ${isCritical ? "border-red-500/25 bg-red-500/10" : "border-amber-500/25 bg-amber-500/10"}`}>
      <AlertTriangle className={`mt-0.5 h-4 w-4 shrink-0 ${isCritical ? "text-red-400" : "text-amber-400"}`} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs font-medium text-white">
          {event.label} detected
        </p>
        <p className="mt-1 text-xs text-neutral-500">
          Confidence {Math.round(event.confidence * 100)}% - {formatEventTime(event.timestamp)}
        </p>
      </div>
    </div>
  );
}

function normalizeState(status: string, reachable: boolean) {
  if (!reachable) return { label: "Offline", tone: "red" as const };
  if (status === "detecting") return { label: "Detecting", tone: "amber" as const };
  if (status === "offline" || status === "error") return { label: "Offline", tone: "red" as const };
  return { label: "Online", tone: "emerald" as const };
}

function formatEventTime(timestamp: number) {
  const secondsAgo = Math.max(0, Math.round((Date.now() - timestamp * 1000) / 1000));
  if (secondsAgo < 2) return "just now";
  if (secondsAgo < 60) return `${secondsAgo}s ago`;
  return `${Math.round(secondsAgo / 60)}m ago`;
}
