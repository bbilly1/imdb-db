import type { FormEvent, ReactNode } from "react";
import { AuthTokenForm } from "./AuthTokenForm";

interface BootErrorScreenProps {
  message: string;
}

interface AuthRequiredScreenProps {
  tokenInput: string;
  onTokenInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

function StartupContainer({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full min-h-[40vh] items-center justify-center px-4 py-10 text-zinc-200">
      {children}
    </div>
  );
}

export function LoadingScreen() {
  return (
    <StartupContainer>
      <div className="w-full max-w-xl border border-zinc-800 bg-panel p-6 text-center shadow-flat">
        <p className="text-sm uppercase tracking-wide text-zinc-500">Startup</p>
        <h1 className="mt-2 text-xl font-semibold">
          Checking API requirements...
        </h1>
      </div>
    </StartupContainer>
  );
}

export function BootErrorScreen({ message }: BootErrorScreenProps) {
  return (
    <StartupContainer>
      <div className="w-full max-w-xl border border-orange-500/50 bg-panel p-6 shadow-flat">
        <p className="text-sm uppercase tracking-wide text-orange-300">
          Startup Error
        </p>
        <p className="mt-2 text-sm text-zinc-300">{message}</p>
        <p className="mt-2 text-xs text-zinc-500">
          Ensure backend API is reachable at /api and reload.
        </p>
      </div>
    </StartupContainer>
  );
}

export function AuthRequiredScreen({
  tokenInput,
  onTokenInputChange,
  onSubmit,
}: AuthRequiredScreenProps) {
  return (
    <StartupContainer>
      <div className="w-full max-w-3xl border border-zinc-800 bg-panel p-6 text-zinc-100 shadow-flat">
        <p className="text-xs uppercase tracking-wide text-amber-400">
          Authentication Required
        </p>
        <h1 className="mt-2 text-2xl font-semibold">
          Enter API token to continue
        </h1>
        <p className="mt-2 text-sm text-zinc-400">
          The backend reports `has_auth=true`. Save your `API_TOKEN` to use this
          frontend.
        </p>
        <div className="mt-6">
          <AuthTokenForm
            tokenInput={tokenInput}
            onTokenInputChange={onTokenInputChange}
            onSubmit={onSubmit}
            submitLabel="Save Token and Continue"
            showLabel
          />
        </div>
      </div>
    </StartupContainer>
  );
}
