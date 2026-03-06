export function formatPayload(payload: unknown): string {
  return JSON.stringify(payload, null, 2);
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
