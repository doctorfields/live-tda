module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? '/live-tda/' : '/',
  "transpileDependencies": [
    "vuetify"
  ],
  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: false
    }
  },
}
