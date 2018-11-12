const MiniCssExtractTextPlugin = require('mini-css-extract-plugin');
const createElectronReloadWebpackPlugin = require('electron-reload-webpack-plugin');
const ElectronReloadWebpackPlugin = createElectronReloadWebpackPlugin({
    path: './',
    logLevel: 0
});
const HtmlWebpackPlugin = require('html-webpack-plugin');

const path = require('path');
module.exports = {

    watch: true,

    target: 'electron-main',

    entry: ['./src/renderer.js'],

    output: {
        path: __dirname + '/build',
        filename: 'bundle.js'
    },

    module: {
        rules: [
            {
                test: /\.jsx?$/,
                loader: 'babel-loader',
                options: {
                    presets: ['@babel/react']
                }
            },
            {
                test: /\.css$/,
                use: [
                {
                    loader: MiniCssExtractTextPlugin.loader
                },
                'css-loader'
                ]
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                loader: 'file-loader',
                query: {
                    name: '[name].[ext]?[hash]'
                }
            }
        ]
    },

    plugins: [
        new MiniCssExtractTextPlugin({
            filename: 'bundle.css',
        }),
        new ElectronReloadWebpackPlugin(),
        new HtmlWebpackPlugin({
            title: 'TorBot',
            template: 'src/index.html'

        })
    ],

    resolve: {
      extensions: ['.js', '.json', '.jsx']
    }

};
