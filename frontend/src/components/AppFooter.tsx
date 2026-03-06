export function AppFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-zinc-800 bg-zinc-950">
      <div className="mx-auto flex w-full max-w-[112rem] flex-wrap items-center justify-between gap-2 px-4 py-4 text-xs text-zinc-400 lg:px-6">
        <span>&copy; {year} IMDb DB</span>
        <a
          href="https://github.com/bbilly1/imdb-db"
          target="_blank"
          rel="noreferrer"
          className="text-amber-300 transition hover:text-amber-200"
        >
          https://github.com/bbilly1/imdb-db
        </a>
      </div>
    </footer>
  );
}
