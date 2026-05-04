const path = require('path');

module.exports = {
    target: 'web',
    entry: {
        index: './src/region_picker.js',
    },
    // mode: 'development',
    output: {
        filename: 'region_picker.min.js',
        // path: './dist',
        path: path.resolve(__dirname, './dist'),
    }
}