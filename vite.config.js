import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Tell Vite that the "root" folder is src/
// so it knows to look for src/index.html.
export default defineConfig({
  root: 'src',
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true  // ensures it won't jump to a different port
  }
})
