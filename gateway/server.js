const express = require('express');
const app = express();
const port = 3000;

// Middleware to parse JSON
app.use(express.json());

// POST /saveSettings
app.post('/saveSettings', (req, res) => {
  const settingsData = req.body;
  console.log('Received settings data:', settingsData);
  // Process the settings data as needed
  res.status(200).json({ message: 'Settings saved successfully' });
});

// POST /saveSpecificUrl
app.post('/saveSpecificUrl', (req, res) => {
  const urlData = req.body;
  console.log('Received specific URL data:', urlData);
  // Process the specific URL data as needed
  res.status(200).json({ message: 'Specific URL saved successfully' });
});

// GET /initialize
app.get('/initialize', (req, res) => {
  // Fetch or generate initialization data
  const initData = { status: 'initialized' };
  res.status(200).json(initData);
});

// Start the server
app.listen(port, () => {
  console.log(`API gateway is running on port ${port}`);
});