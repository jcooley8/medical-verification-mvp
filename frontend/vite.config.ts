import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Enable code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'react-vendor': ['react', 'react-dom'],
          'pdf-vendor': ['pdfjs-dist', 'react-pdf'],
          'ui-vendor': ['lucide-react', 'framer-motion'],
        },
      },
    },
    // Increase chunk size warning limit (we've optimized chunks)
    chunkSizeWarningLimit: 600,
  },
  // Optimize dependency pre-bundling
  optimizeDeps: {
    include: ['react', 'react-dom', 'pdfjs-dist', 'react-pdf'],
  },
})
