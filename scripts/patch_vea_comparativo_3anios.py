from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """            // F6.10 — carga inicial adaptativa: móvil/tablet recibe primero el año vigente.\n            // PC/laptop conserva el repositorio histórico completo.\n            const anioCargaInicialVea = veaDispositivoLimitadoF321() ? new Date().getFullYear() : null;\n"""
new = """            // F6.11 — carga inicial comparativa optimizada.\n            // Móvil/tablet conserva 3 años para comparativos por Año, Mes y S.E.;\n            // Individual inicia solo con el año vigente para no saturar memoria.\n            const anioCargaInicialVea = veaDispositivoLimitadoF321() ? new Date().getFullYear() : null;\n            const aniosComparativosVea = veaDispositivoLimitadoF321()\n                ? [anioCargaInicialVea - 2, anioCargaInicialVea - 1, anioCargaInicialVea]\n                : null;\n"""
if old not in s:
    raise SystemExit('No se encontró bloque F6.10')
s = s.replace(old, new, 1)

old2 = """                if (veaDispositivoLimitadoF321()) {\n                    for (const [tabla, destino, tipo] of grupo) {\n                        try {\n                            const filas = await veaSupabaseLeerTablaCompleta(tabla, anioCargaInicialVea);\n                            resultados.push({ tabla, destino, tipo, filas });\n                        } catch (err) {\n                            resultados.push({ tabla, destino, tipo, error: err });\n                        }\n                        await veaCederInterfazF321();\n                    }\n                    return resultados;\n                }\n"""
new2 = """                if (veaDispositivoLimitadoF321()) {\n                    for (const [tabla, destino, tipo] of grupo) {\n                        try {\n                            let filas = [];\n                            if (tipo === 'vigilancia') {\n                                for (const anio of aniosComparativosVea) {\n                                    const parcial = await veaSupabaseLeerTablaCompleta(tabla, anio);\n                                    filas.push(...parcial);\n                                    await veaCederInterfazF321();\n                                }\n                            } else {\n                                filas = await veaSupabaseLeerTablaCompleta(tabla, anioCargaInicialVea);\n                            }\n                            resultados.push({ tabla, destino, tipo, filas });\n                        } catch (err) {\n                            resultados.push({ tabla, destino, tipo, error: err });\n                        }\n                        await veaCederInterfazF321();\n                    }\n                    return resultados;\n                }\n"""
if old2 not in s:
    raise SystemExit('No se encontró descargarGrupo móvil')
s = s.replace(old2, new2, 1)

s = s.replace('<!-- VEA_BUILD: F6_10_CARGA_INICIAL_MOVIL_ANIO_ACTIVO -->','<!-- VEA_BUILD: F6_11_COMPARATIVO_3_ANIOS_MOVIL -->',1)

p.write_text(s, encoding='utf-8')
print('PATCH_OK')
