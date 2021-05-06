module.exports = {
    apiPath: process.env.NODE_ENV === 'production' ? 'https://live-tda.herokuapp.com/api/' : 'http://localhost:8000/api/',
    publicPath: process.env.NODE_ENV === 'production' ? '/live-tda/' : '/',
}
