import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        library: {
          cream: "#f7f3eb",
          paper: "#fffdf8",
          ink: "#1c2b2d",
          forest: "#2d4a3e",
          sage: "#5c7a6a",
          amber: "#c17f3a",
          rust: "#a64b2a",
          border: "#ddd5c7",
        },
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["Segoe UI", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
