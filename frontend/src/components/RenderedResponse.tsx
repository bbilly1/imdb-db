import { isRecord } from "../lib/json";

const MAX_NESTED_RENDER_DEPTH = 6;

const DATE_TIME_PATTERN =
  /^(?<date>\d{4}-\d{2}-\d{2})[T ](?<time>\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:(?<z>Z)|(?<offset>[+-]\d{2}:\d{2}))?$/;

function normalizeDateString(value: string): string {
  const match = value.match(DATE_TIME_PATTERN);
  if (!match || !match.groups) {
    return value;
  }

  const datePart = match.groups.date;
  const timePart = match.groups.time;
  const zuluPart = match.groups.z;
  const offsetPart = match.groups.offset;

  if (!datePart || !timePart) {
    return value;
  }

  const parseTarget = `${datePart}T${timePart}${zuluPart ?? offsetPart ?? ""}`;
  const parsed = new Date(parseTarget);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  const isUtc =
    zuluPart === "Z" || offsetPart === "+00:00" || offsetPart === "-00:00";
  if (!offsetPart || isUtc) {
    return `${datePart} ${timePart}`;
  }

  return `${datePart} ${timePart} ${offsetPart}`;
}

function renderPrimitive(value: unknown): string {
  if (value === null) {
    return "null";
  }
  if (value === undefined) {
    return "undefined";
  }
  if (typeof value === "string") {
    return normalizeDateString(value);
  }
  return String(value);
}

function collectColumns(rows: Record<string, unknown>[]): string[] {
  const keySet = new Set<string>();
  rows.forEach((row) => {
    Object.keys(row).forEach((key) => keySet.add(key));
  });
  return Array.from(keySet.values());
}

function RenderedValue({ value, depth }: { value: unknown; depth: number }) {
  if (depth > MAX_NESTED_RENDER_DEPTH) {
    return <p className="text-xs text-zinc-500">Max nested depth reached.</p>;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <p className="text-xs text-zinc-500">Empty array</p>;
    }

    const allObjects = value.every((entry) => isRecord(entry));

    if (allObjects) {
      const rows = value as Record<string, unknown>[];
      const columns = collectColumns(rows);
      return (
        <div className="overflow-x-auto border border-zinc-800 bg-zinc-950">
          <table className="min-w-full border-collapse text-left text-xs text-zinc-200">
            <thead>
              <tr className="border-b border-zinc-700">
                {columns.map((column) => (
                  <th
                    key={column}
                    className="px-2 py-2 font-semibold uppercase tracking-wide text-zinc-400"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`row-${index}`} className="border-b border-zinc-800">
                  {columns.map((column) => (
                    <td
                      key={`${index}-${column}`}
                      className="px-2 py-2 align-top text-zinc-200"
                    >
                      <RenderedValue value={row[column]} depth={depth + 1} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    return (
      <div className="overflow-x-auto border border-zinc-800 bg-zinc-950">
        <table className="min-w-full border-collapse text-left text-xs text-zinc-200">
          <thead>
            <tr className="border-b border-zinc-700">
              <th className="px-2 py-2 font-semibold uppercase tracking-wide text-zinc-400">
                Index
              </th>
              <th className="px-2 py-2 font-semibold uppercase tracking-wide text-zinc-400">
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            {value.map((entry, index) => (
              <tr key={`entry-${index}`} className="border-b border-zinc-800">
                <td className="px-2 py-2 align-top text-zinc-400">{index}</td>
                <td className="px-2 py-2 align-top text-zinc-200">
                  <RenderedValue value={entry} depth={depth + 1} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (isRecord(value)) {
    const rows = Object.entries(value);
    if (rows.length === 0) {
      return <p className="text-xs text-zinc-500">Empty object</p>;
    }

    return (
      <div className="overflow-x-auto border border-zinc-800 bg-zinc-950">
        <table className="min-w-full border-collapse text-left text-xs text-zinc-200">
          <thead>
            <tr className="border-b border-zinc-700">
              <th className="px-2 py-2 font-semibold uppercase tracking-wide text-zinc-400">
                Field
              </th>
              <th className="px-2 py-2 font-semibold uppercase tracking-wide text-zinc-400">
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([key, childValue]) => (
              <tr key={key} className="border-b border-zinc-800">
                <td className="px-2 py-2 align-top text-zinc-400">{key}</td>
                <td className="px-2 py-2 align-top text-zinc-200">
                  <RenderedValue value={childValue} depth={depth + 1} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return <span className="text-zinc-200">{renderPrimitive(value)}</span>;
}

export function RenderedResponse({ payload }: { payload: unknown }) {
  return <RenderedValue value={payload} depth={0} />;
}
