from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = "const veaDispositivoLimitadoF321 = () => window.innerWidth < 1024 || (navigator.hardwareConcurrency || 8) <= 4;"
new = """const veaDispositivoLimitadoF321 = () => {\n            const ancho = Math.max(window.innerWidth || 0, document.documentElement?.clientWidth || 0);\n            const nucleos = navigator.hardwareConcurrency || 8;\n            const touch = (navigator.maxTouchPoints || 0) > 0 || ('ontouchstart' in window);\n            const punteroTactil = !!window.matchMedia?.('(pointer: coarse)').matches;\n            const tabletPorPantalla = touch && ancho <= 1366;\n            return ancho < 1024 || nucleos <= 4 || punteroTactil || tabletPorPantalla;\n        };"""
if old not in s:
    raise SystemExit('No se encontro la linea objetivo de deteccion de dispositivo')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('PATCH_OK')
