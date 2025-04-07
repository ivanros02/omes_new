const express = require('express');
const app = express();
const ordenesRoutes = require('./routes/ordenes');

app.use(express.json()); // middleware para JSON

// Rutas
app.use('/api', ordenesRoutes);

// Arrancar el servidor
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
