export default defineNuxtConfig({
  devtools: { enabled: false },
  ssr: false,

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
  },

  css: [
    'sweetalert2/dist/sweetalert2.min.css',
  ],

  app: {
    head: {
      title: 'Nexo Postural: Kyene\'is Pondyam',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Analizador postural NEXO-POSTURAL' },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap',
        },
      ],
    },
  },

  runtimeConfig: {
    jwtSecret: process.env.JWT_SECRET || 'nexo-postural-secret-key-2024-cesar',
  },

  compatibilityDate: '2026-06-09',
})