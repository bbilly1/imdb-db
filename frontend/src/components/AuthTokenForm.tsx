import type { FormEvent } from "react";

interface AuthTokenFormProps {
  tokenInput: string;
  onTokenInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  submitLabel?: string;
  showLogout?: boolean;
  onLogout?: () => void;
  showLabel?: boolean;
}

export function AuthTokenForm({
  tokenInput,
  onTokenInputChange,
  onSubmit,
  submitLabel = "Save Token",
  showLogout = false,
  onLogout,
  showLabel = false,
}: AuthTokenFormProps) {
  return (
    <form onSubmit={onSubmit} className="grid gap-3">
      {showLabel ? (
        <label className="text-sm text-zinc-300" htmlFor="auth-token-input">
          API_TOKEN
        </label>
      ) : null}
      <input
        id="auth-token-input"
        type="password"
        value={tokenInput}
        onChange={(event) => onTokenInputChange(event.target.value)}
        placeholder="paste API_TOKEN"
        className="w-full border border-zinc-700 bg-panelSoft px-3 py-3 text-zinc-100 outline-none transition focus:border-amber-500"
      />
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          className="border border-amber-500 bg-amber-500/10 px-4 py-2 text-sm font-medium uppercase tracking-wide text-amber-300 transition hover:bg-amber-500/20"
        >
          {submitLabel}
        </button>
        {showLogout && onLogout ? (
          <button
            type="button"
            onClick={onLogout}
            className="border border-zinc-600 bg-zinc-900 px-4 py-2 text-sm font-medium uppercase tracking-wide text-zinc-200 transition hover:border-zinc-400"
          >
            Logout
          </button>
        ) : null}
      </div>
    </form>
  );
}
