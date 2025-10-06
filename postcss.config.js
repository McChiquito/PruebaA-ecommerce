// postcss.config.js (corregido)
const purgecss = require('@fullhuman/postcss-purgecss');

module.exports = {
  plugins: [
    purgecss.default({
      content: [
        './templates/**/*.html',
        './productos/templates/**/*.html',
        './static/js/**/*.js',
      ],
      safelist: [
        /^modal(-|$)/,
        /^product(-|$)/,
        /^col-details$/,
        /^texto-existencia$/,
        /^close-button$/,
        /^btn(-|$)/,
        /^btn-secondary$/,
        /^hidden$/, /^show$/, /^active$/,
      ],
      defaultExtractor: (content) =>
        content.match(/[\w-/:]+(?<!:)/g) || []
    }),
    require('cssnano')({ preset: 'default' }),
  ],
};
