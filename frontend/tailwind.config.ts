import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#151515",
        panelSoft: "#1d1d1d",
        accent: "#f59e0b",
        accentSoft: "#fb923c",
      },
      boxShadow: {
        flat: "0 0 0 1px rgba(255,255,255,0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
