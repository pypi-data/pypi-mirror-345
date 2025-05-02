// frontend/webpack.config.js
const path = require("path");

module.exports = {
  // 1. 明確指定入口檔案
  entry: path.resolve(__dirname, "src", "index.tsx"),

  // 2. 打包後輸出到 build 資料夾
  output: {
    path: path.resolve(__dirname, "build"),
    filename: "index.js",
    // 讓 Streamlit component 載入時可以直接用全域變數
    libraryTarget: "var",
    library: "stLlmSearchEngine",
  },

  // 3. 告訴 webpack 要處理的副檔名
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },

  // 4. 用 ts-loader 來編譯 TSX/TS
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
};
