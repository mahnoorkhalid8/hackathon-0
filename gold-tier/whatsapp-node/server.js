const express = require('express');
const cors = require('cors');
const config = require('./src/config');
const whatsappService = require('./src/services/whatsappService');
const whatsappRoutes = require('./src/routes/whatsapp');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({
    service: 'WhatsApp API Service',
    version: '1.0.0',
    status: 'running'
  });
});

app.use('/api/whatsapp', whatsappRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error occurred:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
    details: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});

// Initialize WhatsApp client
whatsappService.initialize();

// Start server
app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
  console.log(`Environment: ${config.nodeEnv}`);
  console.log('Waiting for WhatsApp authentication...');
});
