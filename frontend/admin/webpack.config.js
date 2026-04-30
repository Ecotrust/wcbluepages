const path = require('path');

module.exports = {
    target: 'web',
    entry: {
        index: './src/bluepages_admin.js',
    },
    // mode: 'development',
    output: {
        filename: 'bluepages_admin.min.js',
        // path: './dist',
        path: path.resolve(__dirname, './dist'),
    }
}