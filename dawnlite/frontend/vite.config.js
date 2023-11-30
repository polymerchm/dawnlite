import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import viteTsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
    // depending on your application, base can also be "/"
    // base: '',
    plugins: [react(), viteTsconfigPaths()],
    server: {    
        // this ensures that the browser opens upon server start
        open: true,
        // this sets a default port to 3000  
        port: 3000, 
        // proxy was outside the server block, dummy
        proxy: {
            '/api': {
            target: 'http://127.0.0.1:5000',
            changeOrigin: true,
            secure: false,
            }
        }
    }
})