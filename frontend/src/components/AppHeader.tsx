import type { FormEvent } from "react";
import { AuthTokenForm } from "./AuthTokenForm";

interface NavItem {
  id: string;
  title: string;
}

interface AppHeaderProps {
  apiRequiresAuth: boolean;
  showAuthPanel: boolean;
  token: string;
  tokenInput: string;
  navItems: NavItem[];
  activeEndpointId: string;
  onEndpointSelect: (id: string) => void;
  onToggleAuthPanel: () => void;
  onTokenInputChange: (value: string) => void;
  onLogin: (event: FormEvent<HTMLFormElement>) => void;
  onLogout: () => void;
}

export function AppHeader({
  apiRequiresAuth,
  showAuthPanel,
  token,
  tokenInput,
  navItems,
  activeEndpointId,
  onEndpointSelect,
  onToggleAuthPanel,
  onTokenInputChange,
  onLogin,
  onLogout,
}: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-zinc-800 bg-zinc-950/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[112rem] flex-col gap-3 px-4 py-4 lg:px-6">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold tracking-wide text-zinc-100">
              IMDb DB
            </h1>
            <p className="text-sm text-zinc-400">Your local IMDb Database.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-zinc-400">
              Auth required:{" "}
              <span
                className={
                  apiRequiresAuth ? "text-amber-400" : "text-emerald-400"
                }
              >
                {String(apiRequiresAuth)}
              </span>
            </span>
            <button
              type="button"
              onClick={onToggleAuthPanel}
              className={`border px-3 py-1 text-xs uppercase tracking-wide transition ${
                showAuthPanel
                  ? "border-amber-500 bg-amber-500/10 text-amber-300"
                  : "border-zinc-700 text-zinc-200 hover:border-amber-500 hover:text-amber-300"
              }`}
            >
              {showAuthPanel ? "Hide Auth" : "Auth"}
            </button>
            {token ? (
              <button
                type="button"
                onClick={onLogout}
                className="border border-zinc-600 px-3 py-1 text-xs uppercase tracking-wide text-zinc-200 transition hover:border-zinc-400"
              >
                Logout
              </button>
            ) : null}
          </div>
        </div>

        <section className="border border-zinc-800 bg-panel p-3 shadow-flat">
          <nav className="flex flex-wrap justify-center gap-2">
            {navItems.map((item) => {
              const isActive = item.id === activeEndpointId;
              return (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={() => onEndpointSelect(item.id)}
                  className={`border px-3 py-1 text-xs uppercase tracking-wide transition ${
                    isActive
                      ? "border-amber-500 bg-amber-500/10 text-amber-300"
                      : "border-zinc-700 bg-panel text-zinc-200 hover:border-amber-500 hover:text-amber-300"
                  }`}
                >
                  {item.title}
                </a>
              );
            })}
          </nav>
        </section>

        {showAuthPanel ? (
          <section className="border border-zinc-800 bg-panel p-3 shadow-flat">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-xs uppercase tracking-wide text-zinc-500">
                  Authentication
                </p>
                <p className="text-sm text-zinc-300">
                  Set or rotate API token cookie used for all endpoint requests.
                </p>
              </div>
              <p className="text-xs text-zinc-400">
                Token status: {token ? "set" : "not set"}
              </p>
            </div>
            <div className="mt-3">
              <AuthTokenForm
                tokenInput={tokenInput}
                onTokenInputChange={onTokenInputChange}
                onSubmit={onLogin}
                showLogout={Boolean(token)}
                onLogout={onLogout}
              />
            </div>
          </section>
        ) : null}
      </div>
    </header>
  );
}
