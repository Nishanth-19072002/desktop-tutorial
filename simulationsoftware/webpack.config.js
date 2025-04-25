const path = require('path');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');  // Import the Monaco Editor plugin

module.exports = {
    entry: './simulationsoftware/static/js/codeEditor.js',  // Your entry JS file where Monaco is used
    output: {
        path: path.resolve(__dirname, 'simulationsoftware/static/js'),  // Output path where Monaco Editor will be bundled
        filename: 'bundle.js'  // Output filename
    },
    resolve: {
        alias: {
            'monaco-editor': path.resolve(__dirname, 'node_modules/monaco-editor')
        }
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader'],  // For loading CSS files if necessary
            },
            {
                test: /\.ttf$/, // Handling font files used by Monaco Editor
                type: 'asset/resource',
            },
        ]
    },
    plugins: [
        new MonacoWebpackPlugin({
            languages: ['javascript', 'python', 'css', 'html'], // Add languages you need
            features: ['!accessibilityHelp'], // Remove unused features to optimize the build
        }),
    ],
    // devServer: {
    //     contentBase: path.join(__dirname, 'static'),
    //     compress: true,
    //     port: 9000,
    // },
    mode : 'development'
}