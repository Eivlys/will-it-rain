const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 3001;

// Fetch current weather from Meteomatics
app.post('/api/current-weather', async (req, res) => {
  try {
    const { latitude, longitude } = req.body;
    
    const params = 't_2m:C,precip_1h:mm,relative_humidity_2m:p,wind_speed_10m:ms';
    const now = new Date().toISOString();
    const url = `https://api.meteomatics.com/${now}/${params}/${latitude},${longitude}/json`;

    const response = await axios.get(url, {
      auth: {
        username: process.env.METEOMATICS_USER,
        password: process.env.METEOMATICS_PASS
      }
    });

    const data = response.data.data;
    res.json({
      temperature: data[0]?.coordinates[0]?.dates[0]?.value,
      precipitation: data[1]?.coordinates[0]?.dates[0]?.value || 0,
      humidity: data[2]?.coordinates[0]?.dates[0]?.value,
      wind_speed: data[3]?.coordinates[0]?.dates[0]?.value
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(PORT, () => console.log(`Weather service on port ${PORT}`));