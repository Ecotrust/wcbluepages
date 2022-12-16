const path = require('path');

module.exports = {
    target: 'web',
    entry: {
        index: './src/record_suggestion.js',
    },
    // mode: 'development',
    output: {
        filename: 'record_suggestion.min.js',
        // path: './dist',
        path: path.resolve(__dirname, './dist'),
    }
}