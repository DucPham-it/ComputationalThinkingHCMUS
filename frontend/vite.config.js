import { fileURLToPath, URL } from "node:url";
import fs from "node:fs";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const httpsKeyPath = process.env.VITE_DEV_HTTPS_KEY;
const httpsCertPath = process.env.VITE_DEV_HTTPS_CERT;
const httpsConfig =
  httpsKeyPath && httpsCertPath
    ? {
        key: fs.readFileSync(httpsKeyPath),
        cert: fs.readFileSync(httpsCertPath),
      }
    : undefined;

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
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: true,
    https: httpsConfig,
    proxy: {
      "/api/v1": {
        target: process.env.VITE_DEV_API_TARGET || "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  }
});
