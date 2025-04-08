const express = require('express');
const router = express.Router();
const createDBConnection = require('../db'); // ✅ Importás la función exportada

// Función para obtener una instancia de la base según header o query
function getDBInstance(req) {
  const dbName = req.headers['x-database'] || req.query.db; // Elegí cómo querés pasarlo
  if (!dbName) {
    throw new Error('No se especificó la base de datos');
  }
  return createDBConnection({ database: dbName });
}

// GET para obtener bloques de profesionales
router.get('/bloques', async (req, res) => {
  let db;
  try {
    db = getDBInstance(req);

    const dbName = req.headers['x-database'] || req.query.db;

    const dias = parseInt(req.query.dias, 10) || 0;
    const fecha = new Date();
    fecha.setDate(fecha.getDate() + dias);
    const formattedDate = fecha.toISOString().slice(0, 10);

    // Definimos qué nombre usar o si se usa el campo 'prof_generador'
    let nombreEspecial = null;
    let usarCampoProfGenerador = false;

    if (dbName === 'worldsof_medical_pq0303') {
      nombreEspecial = 'FORBITO AGUSTIN';
    } else if (dbName === 'worldsof_medical_pq0328') {
      nombreEspecial = 'Ramirez Blankenhorst Oscar';
    } else if (dbName === 'worldsof_medical_pq2001') {
      usarCampoProfGenerador = true;
    }

    const [rows] = await db.query(`
      SELECT 
        CONCAT(COALESCE(p.benef, ''), COALESCE(p.parentesco, '')) AS benef,
        a.codigo AS cod_practica,
        CASE WHEN d.codigo IS NULL THEN 'F99' ELSE d.codigo END AS cod_diag,
        CASE 
          WHEN a.codigo = 520101 THEN 
            ${usarCampoProfGenerador ? 'pr.prof_generador' : '?'}
          ELSE pr.nombreYapellido 
        END AS nombre_generador,
        CASE 
          WHEN a.codigo = 520101 THEN 
            (SELECT usuario FROM profesional WHERE nombreYapellido = ${usarCampoProfGenerador ? 'pr.prof_generador' : '?'} LIMIT 1)
          ELSE pr.usuario 
        END AS usuario,
        CASE 
          WHEN a.codigo = 520101 THEN 
            (SELECT contraseña FROM profesional WHERE nombreYapellido = ${usarCampoProfGenerador ? 'pr.prof_generador' : '?'} LIMIT 1)
          ELSE pr.contraseña 
        END AS contraseña
      FROM 
        turnos t
      LEFT JOIN paciente p ON p.id = t.paciente
      LEFT JOIN paci_diag pD ON pD.id_paciente = p.id
      LEFT JOIN diag d ON d.id = pD.codigo
      LEFT JOIN actividades a ON a.id = t.motivo
      LEFT JOIN profesional pr ON t.id_prof = pr.id_prof
      WHERE 
        t.llego = 'SI'
        AND t.atendido = 'SI'
        AND (a.codigo = 521001 OR a.codigo = 520101)
        AND t.generado = 0
        AND t.fecha <= ?
        AND CONCAT(COALESCE(p.benef, ''), COALESCE(p.parentesco, '')) <> ''
        AND p.obra_social = 4
      ORDER BY pr.nombreYapellido, t.fecha ASC
    `,
      usarCampoProfGenerador
        ? [formattedDate] // solo necesita la fecha si usa prof_generador
        : [nombreEspecial, nombreEspecial, nombreEspecial, formattedDate] // los 3 ? del query
    );

    res.json(rows);
  } catch (error) {
    console.error('Error al obtener bloques:', error);
    res.status(500).send('Error al obtener los datos.');
  }
});


// POST para marcar como generado (recibe lista de beneficios)
router.post('/marcar-generado', async (req, res) => {
  const { beneficios, cod_practica } = req.body;
  if (!beneficios || !Array.isArray(beneficios) || !cod_practica) {
    return res.status(400).send('Se requieren los campos: beneficios (array) y cod_practica (string).');
  }

  // Obtener días desde query param (si viene), por defecto 0 (hoy)
  const dias = parseInt(req.query.dias, 10) || 0;
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + dias);
  const fechaObjetivo = fecha.toISOString().slice(0, 10); // formato YYYY-MM-DD

  try {
    const db = getDBInstance(req);
    const placeholders = beneficios.map(() => '?').join(', ');
    const query = `
      UPDATE turnos t
      JOIN paciente p ON p.id = t.paciente
      JOIN actividades a ON a.id = t.motivo
      SET t.generado = 1
      WHERE CONCAT(p.benef, p.parentesco) IN (${placeholders})
      AND a.codigo = ?
      AND t.fecha = ?
    `;

    const [result] = await db.query(query, [...beneficios, cod_practica, fechaObjetivo]);
    res.json({
      mensaje: 'Actualización realizada correctamente',
      fecha_objetivo: fechaObjetivo,
      filas_afectadas: result.affectedRows
    });
  } catch (error) {
    console.error('Error al actualizar:', error);
    res.status(500).send('Error interno al actualizar los turnos.');
  }
});



// POST para marcar como generado y aceptado por práctica
router.post('/marcar-aceptar', async (req, res) => {
  const { beneficios, cod_practica } = req.body;

  if (!beneficios || !Array.isArray(beneficios) || !cod_practica) {
    return res.status(400).send('Se requieren los campos: beneficios (array) y cod_practica (string).');
  }

  // Leer parámetro opcional de días
  const dias = parseInt(req.query.dias, 10) || 0;
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + dias);
  const fechaObjetivo = fecha.toISOString().slice(0, 10);

  try {
    const db = getDBInstance(req);

    const placeholders = beneficios.map(() => '?').join(', ');
    const query = `
      UPDATE turnos t
      JOIN paciente p ON p.id = t.paciente
      JOIN actividades a ON a.id = t.motivo
      SET t.generado = 1, t.aceptado = 1
      WHERE CONCAT(p.benef, p.parentesco) IN (${placeholders})
      AND a.codigo = ?
      AND t.fecha = ?
    `;

    const [result] = await db.query(query, [...beneficios, cod_practica, fechaObjetivo]);

    res.json({
      mensaje: 'Actualización realizada correctamente',
      fecha_objetivo: fechaObjetivo,
      filas_afectadas: result.affectedRows
    });
  } catch (error) {
    console.error('Error al actualizar:', error.message);
    res.status(500).send('Error interno al actualizar los turnos.');
  }
});


// GET para obtner credenciales de clinica
router.get('/credenciales-clinica', async (req, res) => {
  let db;
  try {
    db = getDBInstance(req);
    const [rows] = await db.query(`
      SELECT *
      FROM parametro_sistema
    `);

    res.json(rows);
  } catch (error) {
    console.error('Error al obtener bloques:', error);
    res.status(500).send('Error al obtener los datos.');
  }
});


module.exports = router;
