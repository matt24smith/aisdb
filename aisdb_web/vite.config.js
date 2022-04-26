import { defineConfig } from 'vite';
import { resolve } from 'path';
import { VitePWA } from 'vite-plugin-pwa';

const root = resolve(__dirname, 'dist_sphinx');
const outDir = resolve(__dirname, 'dist');

export default defineConfig({
  root: root,
  build: {
    outDir: outDir,
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(root, 'index.html'),
        map: resolve(root, 'map', 'index.html'),
        // rust: resolve(root, 'rust', 'doc', 'aisdb', 'index.html'),
      }
    }
  },
  plugins: [
    VitePWA({
      includeAssets: [ 'favicon.svg', 'robots.txt' ],
      manifest: {
        short_name: 'AISDB',
        name: 'AISDB: Ship Tracking Database',
        description: 'Web Interface for AIS Ship Tracking Database',
        icons: [
          {
            src: '/favicon.svg',
            sizes: 'any 192x192 256x256 512x512',
            type: 'image/svg+xml',
            purpose: 'monochrome any maskable'
          },
          {
            src: '/favicon.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        start_url: '/map',
        scope: '/map',
        background_color : '#282c34',
        theme_color: '#282c34',
        display: 'fullscreen',
        orientation: 'landscape',
        shortcuts: [
          {
            name: 'Ecoregions Shortcut',
            short_name: 'Ecoregions',
            description: 'Display map with ecoregion polygons overlay',
            url: '/map/index.html?ecoregions',
            icons: [
              {
                src: '/favicon.svg',
                purpose: 'monochrome any',
                sizes: 'any 192x192 256x256 512x512',
                type: 'image/svg+xml'
              }
            ]
          }
        ]
      }
    })
  ],
});