module.exports = {
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  whatsapp: {
    sessionPath: './.wwebjs_auth',
    puppeteerArgs: ['--no-sandbox', '--disable-setuid-sandbox']
  }
};
