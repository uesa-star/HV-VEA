from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
original = s

# 1) Permitir filtro year en la lectura REST del navegador.
old = '''        async function veaSupabaseLeerPaginaRestMovil(tabla, desde, hasta) {
            const limite = Math.max(1, (hasta - desde) + 1);
            const url = `/api/vea-data?table=${encodeURIComponent(tabla)}&offset=${desde}&limit=${limite}`;'''
new = '''        async function veaSupabaseLeerPaginaRestMovil(tabla, desde, hasta, year = null) {
            const limite = Math.max(1, (hasta - desde) + 1);
            let url = `/api/vea-data?table=${encodeURIComponent(tabla)}&offset=${desde}&limit=${limite}`;
            if (year !== null && year !== undefined && String(year).trim() !== '') {
                url += `&year=${encodeURIComponent(String(year).trim())}`;
            }'''
if old not in s:
    raise SystemExit('No se encontró veaSupabaseLeerPaginaRestMovil esperado')
s = s.replace(old, new, 1)

# 2) Pasar year por el paginador completo.
s = s.replace('        async function veaSupabaseLeerTablaCompleta(tabla) {',
              '        async function veaSupabaseLeerTablaCompleta(tabla, year = null) {', 1)
s = s.replace('const respuesta = await veaSupabaseLeerPaginaRestMovil(tabla, desde, desde + lote - 1);',
              'const respuesta = await veaSupabaseLeerPaginaRestMovil(tabla, desde, desde + lote - 1, year);', 1)

# 3) En el cargador remoto: año activo solo para dispositivo limitado.
needle = "            const modoRestMovil = true; // F6.00 motor universal same-origin vía Vercel\n"
insert = "            const modoRestMovil = true; // F6.00 motor universal same-origin vía Vercel\n            // F6.10 — carga inicial adaptativa: móvil/tablet recibe primero el año vigente.\n            // PC/laptop conserva el repositorio histórico completo.\n            const anioCargaInicialVea = veaDispositivoLimitadoF321() ? new Date().getFullYear() : null;\n"
if needle not in s:
    raise SystemExit('No se encontró punto de inserción anioCargaInicialVea')
s = s.replace(needle, insert, 1)

# 4) Reemplazar descarga concurrente de grupo por secuencial en móvil/tablet.
old_group = '''            const descargarGrupo = grupo => Promise.all(grupo.map(async ([tabla, destino, tipo]) => {
                try {
                    const filas = await veaSupabaseLeerTablaCompleta(tabla);
                    return { tabla, destino, tipo, filas };
                } catch (err) {
                    return { tabla, destino, tipo, error: err };
                }
            }));'''
new_group = '''            const descargarGrupo = async grupo => {
                const resultados = [];
                if (veaDispositivoLimitadoF321()) {
                    for (const [tabla, destino, tipo] of grupo) {
                        try {
                            const filas = await veaSupabaseLeerTablaCompleta(tabla, anioCargaInicialVea);
                            resultados.push({ tabla, destino, tipo, filas });
                        } catch (err) {
                            resultados.push({ tabla, destino, tipo, error: err });
                        }
                        await veaCederInterfazF321();
                    }
                    return resultados;
                }
                return Promise.all(grupo.map(async ([tabla, destino, tipo]) => {
                    try {
                        const filas = await veaSupabaseLeerTablaCompleta(tabla, null);
                        return { tabla, destino, tipo, filas };
                    } catch (err) {
                        return { tabla, destino, tipo, error: err };
                    }
                }));
            };'''
if old_group not in s:
    raise SystemExit('No se encontró descargarGrupo esperado')
s = s.replace(old_group, new_group, 1)

# 5) Mensajes de progreso claros.
s = s.replace("if (txtEstadoSupabase) txtEstadoSupabase.textContent = 'Cargando datos vía Vercel…';",
              "if (txtEstadoSupabase) txtEstadoSupabase.textContent = anioCargaInicialVea ? `Cargando datos ${anioCargaInicialVea} · modo móvil optimizado…` : 'Cargando datos vía Vercel…';", 1)

# 6) Marcar build para auditoría.
s = s.replace('<!-- VEA_BUILD: MARCA_UNICA_SEPTIEMBRE_2026_V2 -->',
              '<!-- VEA_BUILD: F6_10_CARGA_INICIAL_MOVIL_ANIO_ACTIVO -->', 1)

if s == original:
    raise SystemExit('No se aplicaron cambios')
p.write_text(s, encoding='utf-8')
print('PATCH_OK')
