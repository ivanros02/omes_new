// datosPadron/scraper.js

const axios = require('axios');
const cheerio = require('cheerio');

async function scrapePamiPage(beneficio, parent) {
    try {
        const url = `https://prestadores.pami.org.ar/result.php?c=6-2-1-1&beneficio=${beneficio}&parent=${parent}&vm=2`;
        const response = await axios.get(url);

        if (response.status === 200) {
            const $ = cheerio.load(response.data);

            const nombreApellido = $('.grisClaro').find('p').first().text().trim();
            const fechaBaja = $('td:contains("BAJA:")').next('td').text().trim();
            const ugl = $('td:contains("UGL:")').next('td').text().trim();
            const fecha_nac = $('td:contains("FECHA DE NACIMIENTO:")').next('td').text().trim();

            if (fechaBaja) {
                throw new Error('El beneficiario tiene fecha de baja registrada');
            }

            if (nombreApellido) {
                return {
                    nombreApellido,
                    fecha_nac,
                    ugl
                };
            } else {
                throw new Error('Nombre y apellido no encontrados');
            }
        } else {
            throw new Error('Error en la solicitud: ' + response.status);
        }
    } catch (error) {
        throw new Error('Error al buscar el nombre y apellido: ' + error.message);
    }
}

// Si se ejecuta desde terminal
if (require.main === module) {
    const [beneficio, parent] = process.argv.slice(2);

    scrapePamiPage(beneficio, parent)
        .then(data => {
            console.log(JSON.stringify(data)); // 🔹 Output como JSON
        })
        .catch(err => {
            console.error(JSON.stringify({ error: err.message }));
            process.exit(1);
        });
}

module.exports = { scrapePamiPage };
