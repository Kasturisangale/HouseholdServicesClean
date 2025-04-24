const webpack = require('webpack');

module.exports = {
  transpileDependencies: [], 
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(false),
      }),
    ],
  },
  devServer: {
    host: '0.0.0.0', 
    port: 8080, 
    client: {
      webSocketURL: 'ws://54.242.17.17:8080/ws', 
    },
    proxy: {
      '/api': {
        target: 'http://54.242.17.17:5000', 
        changeOrigin: true, 
        secure: false,
        logLevel: 'debug', 
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
};
