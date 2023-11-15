const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log("in create proxy")
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
    })
  );
};