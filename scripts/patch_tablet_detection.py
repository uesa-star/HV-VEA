from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = """        function tresAniosMasRecientesVea(anios) {
            return normalizarListaAniosVea(anios).sort((a, b) => b - a).slice(0, 3).sort((a, b) => a - b);
        }
"""

new = """        function tresAniosMasRecientesVea(anios) {
            const disponibles = normalizarListaAniosVea(anios).sort((a, b) => a - b);
            const aprobados = [2024, 2025, 2026].filter(anio => disponibles.includes(anio));
            if (aprobados.length === 3) return aprobados;
            return [...disponibles].sort((a, b) => b - a).slice(0, 3).sort((a, b) => a - b);
        }
"""

if new in s:
    print('PATCH_OK_ALREADY')
elif old in s:
    p.write_text(s.replace(old, new, 1), encoding='utf-8')
    print('PATCH_OK')
else:
    raise SystemExit('No se encontro el bloque esperado de tresAniosMasRecientesVea')
