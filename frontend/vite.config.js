import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  resolve: {
    alias: {
      "@react-login-page/page1": fileURLToPath(
        new URL("./src/vendor/react-login-page-page1/index.jsx", import.meta.url)
      )
    }
  },
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts: true
  }
});
