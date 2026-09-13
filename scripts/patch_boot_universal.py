from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

start = s.find('        window.onload = async function() {')
if start < 0:
    raise SystemExit('No se encontró window.onload')
end_marker = '        };\n    \n        \n        // F4.43'
end = s.find(end_marker, start)
if end < 0:
    raise SystemExit('No se encontró cierre de window.onload')
end += len('        };')

nuevo = r'''        window.onload = async function() {
            // F6.01 — ARRANQUE UNIVERSAL ROBUSTO
            // Ningún fallo visual puede impedir la sincronización de datos.
            const veaPasoSeguroF601 = (nombre, fn) => {
                try { return fn(); }
                catch (err) {
                    console.warn(`[VEA F6.01] Paso inicial ${nombre} no bloqueante:`, err);
                    return null;
                }
            };

            veaPasoSeguroF601('sidebar', () => aplicarEstadoVeaSidebar());
            veaPasoSeguroF601('tab inicial', () => cambiarTab('dashboard'));
            veaPasoSeguroF601('filtros persistidos', () => cargarFiltrosPersistidos());
            veaPasoSeguroF601('estado filtros', () => restaurarEstadoFiltrosEvento(selectedEvent));
            veaPasoSeguroF601('tema', () => aplicarTemaGraficoYBotones());

            const txt = document.getElementById('textoProgresoVea');
            const barra = document.getElementById('barraProgresoVea');
            if (txt) txt.textContent = 'Iniciando sincronización VEA…';
            if (barra) barra.style.width = '10%';

            let cacheVeaDisponible = null;
            try {
                cacheVeaDisponible = await veaCacheRestaurarProcesado();
            } catch (err) {
                console.warn('[VEA F6.01] Caché no disponible; continúa sincronización remota:', err);
            }

            if (cacheVeaDisponible) {
                if (txt) txt.textContent = 'Base local disponible · sincronizando actualización…';
                if (barra) barra.style.width = '35%';
                await veaCederInterfazF321();
            } else {
                if (txt) txt.textContent = 'Descargando base VEA…';
                if (barra) barra.style.width = '20%';
            }

            try {
                const resultado = await cargarRepositorioVeaDesdeSupabase();
                if (!resultado.totalRemoto && resultado.errores?.length && !cacheVeaDisponible) {
                    throw new Error(resultado.errores.join(' | '));
                }

                // Render únicamente después de que exista base válida en memoria.
                veaPasoSeguroF601('cálculos y gráficos', () => actualizarCalculosYGraficos());
                veaPasoSeguroF601('módulos dinámicos', () => renderizarModulosDinamicosVea());
                veaPasoSeguroF601('KPIs', () => actualizarKpisVigilancia());
                veaPasoSeguroF601('cabecera', () => actualizarCabeceraDinamicaVeaF483());

                if (txt && resultado.totalRemoto > 0) {
                    txt.textContent = `Carga actualizada · ${resultado.totalRemoto.toLocaleString('es-PE')} registros`;
                }
                if (barra) barra.style.width = '100%';
                console.info('[VEA F6.01] Arranque universal completado', resultado);
            } catch (err) {
                const mensaje = String(err?.message || err || 'Error desconocido');
                if (txt) txt.textContent = cacheVeaDisponible
                    ? `Sincronización pendiente · usando última base válida · ${mensaje}`
                    : `Error de sincronización · ${mensaje}`;
                if (barra) barra.style.width = cacheVeaDisponible ? '100%' : '0%';
                console.error('[VEA F6.01] Fallo de sincronización:', err);
            }
        };'''

s2 = s[:start] + nuevo + s[end:]
if s2 == s:
    raise SystemExit('Sin cambios')
p.write_text(s2, encoding='utf-8')
print('OK: window.onload reordenado para sincronizar antes de render pesado')
