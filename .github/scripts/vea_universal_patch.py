from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
original = s


def extract_span(text, signature):
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f'No encontrado: {signature}')
    brace = text.find('{', start)
    if brace < 0:
        raise SystemExit(f'Sin apertura: {signature}')
    depth = 0
    quote = None
    esc = False
    i = brace
    while i < len(text):
        c = text[i]
        if quote:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == quote:
                quote = None
        else:
            if c in ('"', "'", '`'):
                quote = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return start, i + 1
        i += 1
    raise SystemExit(f'Función incompleta: {signature}')


def replace_function(signature, new_text):
    global s
    a, b = extract_span(s, signature)
    s = s[:a] + new_text + s[b:]
    print('OK', signature)


replace_function('async function veaSupabaseLeerPaginaRestMovil', '''async function veaSupabaseLeerPaginaRestMovil(tabla, desde, hasta) {
            const limite = Math.max(1, (hasta - desde) + 1);
            const url = `/api/vea-data?table=${encodeURIComponent(tabla)}&offset=${desde}&limit=${limite}`;
            const controlador = new AbortController();
            const timer = setTimeout(() => controlador.abort(), 25000);
            try {
                const respuesta = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'apikey': VEA_SUPABASE_PUBLISHABLE_KEY,
                        'Authorization': `Bearer ${VEA_SUPABASE_PUBLISHABLE_KEY}`,
                        'Accept': 'application/json'
                    },
                    cache: 'no-store',
                    signal: controlador.signal
                });
                if (!respuesta.ok) throw new Error(`VEA API ${tabla}: HTTP ${respuesta.status}`);
                const data = await respuesta.json();
                return { data: Array.isArray(data) ? data : [], error: null };
            } catch (error) {
                return { data: null, error };
            } finally {
                clearTimeout(timer);
            }
        }''')

replace_function('async function veaSupabaseLeerTablaCompleta', '''async function veaSupabaseLeerTablaCompleta(tabla) {
            const lote = 300;
            const concurrencia = 2;
            const maxIntentos = 4;
            const salida = [];
            let desdeBase = 0;
            let terminado = false;
            while (!terminado) {
                const paginas = await Promise.all(Array.from({ length: concurrencia }, (_, i) => {
                    const desde = desdeBase + (i * lote);
                    return (async () => {
                        let ultimoError = null;
                        for (let intento = 1; intento <= maxIntentos; intento++) {
                            const respuesta = await veaSupabaseLeerPaginaRestMovil(tabla, desde, desde + lote - 1);
                            if (!respuesta.error) return respuesta;
                            ultimoError = respuesta.error;
                            if (intento < maxIntentos) {
                                const espera = Math.min(5000, 650 * (2 ** (intento - 1)));
                                await new Promise(resolve => setTimeout(resolve, espera));
                            }
                        }
                        return { data: null, error: ultimoError || new Error(`No se pudo leer ${tabla}`) };
                    })();
                }));
                for (const respuesta of paginas) {
                    if (respuesta.error) throw respuesta.error;
                    const filas = Array.isArray(respuesta.data) ? respuesta.data : [];
                    salida.push(...filas);
                    if (filas.length < lote) {
                        terminado = true;
                        break;
                    }
                }
                desdeBase += lote * concurrencia;
            }
            return salida;
        }''')

replace_function('window.onload = async function()', '''window.onload = async function() {
            aplicarEstadoVeaSidebar();
            cambiarTab('dashboard');
            cargarFiltrosPersistidos();
            restaurarEstadoFiltrosEvento(selectedEvent);
            aplicarTemaGraficoYBotones();
            actualizarCalculosYGraficos();
            renderizarModulosDinamicosVea();

            const txt = document.getElementById('textoProgresoVea');
            const barra = document.getElementById('barraProgresoVea');
            const cacheVeaDisponible = await veaCacheRestaurarProcesado();
            if (cacheVeaDisponible) {
                if (txt) txt.textContent = 'Base local disponible · verificando actualización…';
                if (barra) barra.style.width = '90%';
                await veaCederInterfazF321();
            } else {
                if (txt) txt.textContent = 'Sincronizando base VEA…';
                if (barra) barra.style.width = '15%';
            }

            try {
                const resultadoSupabase = await cargarRepositorioVeaDesdeSupabase();
                if (!resultadoSupabase.totalRemoto && resultadoSupabase.errores?.length) {
                    console.error('[VEA Universal] Sincronización sin datos:', resultadoSupabase.errores);
                }
            } catch (err) {
                if (txt) txt.textContent = cacheVeaDisponible
                    ? 'Sincronización pendiente · usando la última base válida'
                    : 'Error de sincronización: ' + (err?.message || err);
                if (barra && cacheVeaDisponible) barra.style.width = '100%';
                console.error('[VEA Universal] Error de inicialización:', err);
            }
        }''')

# Unificar el cargador remoto y evitar limpiar una base válida antes de tiempo.
a, b = extract_span(s, 'async function cargarRepositorioVeaDesdeSupabase')
body = s[a:b]
body, n = re.subn(
    r"\s*const modoRestMovil = veaDispositivoLimitadoF321\(\);.*?if \(!modoRestMovil\) veaSupabaseClient \|\|= window\.supabase\.createClient\(VEA_SUPABASE_URL, VEA_SUPABASE_PUBLISHABLE_KEY\);",
    "\n            const modoRestMovil = true; // F6.00 motor universal same-origin vía Vercel",
    body,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f'Bloque cliente navegador no reemplazado: {n}')
body = body.replace(
    "if (txtEstadoSupabase) txtEstadoSupabase.textContent = modoRestMovil ? 'Cargando datos móviles vía Vercel…' : 'Cargando Dashboard desde Supabase…';",
    "if (txtEstadoSupabase) txtEstadoSupabase.textContent = 'Cargando datos vía Vercel…';",
)
body = body.replace(
    "if (txtEstadoSupabase) txtEstadoSupabase.textContent = modoRestMovil ? 'Cargando datos en modo móvil seguro…' : 'Cargando Dashboard desde Supabase…';",
    "if (txtEstadoSupabase) txtEstadoSupabase.textContent = 'Cargando datos vía Vercel…';",
)
body = body.replace(
    '            limpiarRepositorioVeaEnMemoria();\n',
    '            // F6.00 conservar la última base válida hasta validar cada tabla nueva.\n',
)
s = s[:a] + body + s[b:]

# Responsive seguro para teléfono/tablet sin tocar cálculos.
if 'id="veaResponsiveUniversalF600"' not in s:
    css = """
    <style id="veaResponsiveUniversalF600">
      @media (max-width: 1023px) {
        html, body { max-width: 100%; overflow-x: hidden; }
        #veaAppShell > main { width: 100% !important; max-width: 100% !important; padding-left: .75rem !important; padding-right: .75rem !important; }
        #contentDashboard,#contentDatos,#contentCasos,#contentCanal,#contentTabla,#contentHospitalizados,#contentSoat,#contentVih,#contentTbc,#contentConfiguracion { min-width: 0 !important; max-width: 100% !important; }
        #resumenAnualDatosAcumuladosV6B,#panelCabeceraDatosAcumuladosV6B { width: 100% !important; max-width: 100% !important; margin-left: 0 !important; margin-right: 0 !important; transform: none !important; }
        canvas { max-width: 100% !important; }
        [class*="grid-cols-5"],[class*="grid-cols-4"],[class*="grid-cols-3"] { grid-template-columns: repeat(2,minmax(0,1fr)) !important; }
      }
      @media (max-width: 640px) {
        #veaAppShell > main { padding-left: .5rem !important; padding-right: .5rem !important; }
        [class*="grid-cols-5"],[class*="grid-cols-4"],[class*="grid-cols-3"],[class*="grid-cols-2"] { grid-template-columns: minmax(0,1fr) !important; }
        #resumenAnualDatosAcumuladosV6B .vea-matriz-wrap { overflow-x: auto !important; -webkit-overflow-scrolling: touch; }
        #resumenAnualDatosAcumuladosV6B .vea-matriz-tabla { min-width: 760px !important; }
        button, select, input { max-width: 100%; }
      }
    </style>
"""
    s = s.replace('</head>', css + '\n</head>', 1)

if s == original:
    raise SystemExit('No se aplicaron cambios')
p.write_text(s, encoding='utf-8')
print('PATCH_OK')
