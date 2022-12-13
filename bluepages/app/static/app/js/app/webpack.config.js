const path = require('path');

module.exports = {
    target: 'web',
    entry: {
        index: './src/app.js',
    },
    // mode: 'development',
    output: {
        filename: 'app.min.js',
        // path: './dist',
        path: path.resolve(__dirname, './dist'),
    }
}