const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: './src/index.ts',
  output: {
    filename: 'worker.js',
    path: path.join(__dirname, 'dist'),
  },
  mode: 'production',
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.html'],  // Added .html
    alias: {
      '@': path.resolve(__dirname, 'src'),  // Add this for easier imports
    }
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        loader: 'ts-loader',
        options: {
          transpileOnly: true,
        },
      },
      {
        test: /\.html$/,
        type: 'asset/source',
        generator: {
          filename: '[name][ext]'
        }
      }
    ],
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        {
          from: 'public',
          to: 'public'
        },
        {
          from: 'src/index.html',
          to: 'index.html'
        }
      ],
    }),
  ],
};