import { formatPayload } from "../lib/json";
import type { EndpointResponse, RenderMode } from "../types/api";
import { RenderedResponse } from "./RenderedResponse";

interface ReturnAreaProps {
  renderMode: RenderMode;
  onRenderModeChange: (mode: RenderMode) => void;
  response?: EndpointResponse;
}

export function ReturnArea({
  renderMode,
  onRenderModeChange,
  response,
}: ReturnAreaProps) {
  return (
    <section className="min-w-0 border border-zinc-800 bg-panel p-4 shadow-flat">
      <div className="flex flex-wrap justify-end gap-2">
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => onRenderModeChange("json")}
            className={`border px-3 py-1 text-xs uppercase tracking-wide ${
              renderMode === "json"
                ? "border-amber-500 bg-amber-500/10 text-amber-300"
                : "border-zinc-700 text-zinc-300 hover:border-amber-500 hover:text-amber-300"
            }`}
          >
            JSON
          </button>
          <button
            type="button"
            onClick={() => onRenderModeChange("rendered")}
            className={`border px-3 py-1 text-xs uppercase tracking-wide ${
              renderMode === "rendered"
                ? "border-amber-500 bg-amber-500/10 text-amber-300"
                : "border-zinc-700 text-zinc-300 hover:border-amber-500 hover:text-amber-300"
            }`}
          >
            Rendered
          </button>
        </div>
      </div>

      <div className="mt-4 min-w-0 overflow-x-auto border border-zinc-800 bg-zinc-950 p-3">
        {response ? (
          <div className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs text-zinc-500">{response.url}</p>
              <span
                className={`text-xs ${response.ok ? "text-emerald-400" : "text-orange-400"}`}
              >
                {String(response.status)}
              </span>
            </div>
            {renderMode === "json" ? (
              <pre className="overflow-x-auto whitespace-pre text-xs text-zinc-200">
                {formatPayload(response.response)}
              </pre>
            ) : (
              <RenderedResponse payload={response.response} />
            )}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">
            No response yet for this endpoint.
          </p>
        )}
      </div>
    </section>
  );
}
