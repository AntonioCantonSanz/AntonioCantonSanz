#!/usr/bin/env python3
"""Genera panel.svg: el panel de desarrollador del perfil de GitHub de Antonio.

Sin dependencias externas. Usa la API pública de GitHub (con GITHUB_TOKEN si existe)
y la página pública de contribuciones. Se ejecuta cada semana desde GitHub Actions.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from xml.sax.saxutils import escape

USUARIO = "AntonioCantonSanz"
INICIO_DAW = dt.date(2025, 9, 15)
FIN_DAW = dt.date(2027, 6, 4)
INICIO_FCT = dt.date(2027, 2, 15)
SEMANAS = 26
SALIDA = sys.argv[1] if len(sys.argv) > 1 else "panel.svg"

PROYECTOS = [
    ("Release Manager", "QA → UAT → producción en Vercel, CI y SemVer", ["Angular", "CI/CD", "Vercel"], "#DD0031"),
    ("Noches de Pesadilla", "Cartelera Angular hecha con un agente de IA", ["Angular", "TypeScript", "IA"], "#3178C6"),
    ("Automatización B2B", "Sheets → Apify → IA → Gmail en un mayorista", ["Make", "Apify", "Notion API"], "#6D00CC"),
]

COLORES_LENGUAJE = {
    "TypeScript": "#3178C6", "JavaScript": "#F7DF1E", "Python": "#3776AB", "HTML": "#E34F26",
    "CSS": "#663399", "PHP": "#777BB4", "Java": "#ED8B00", "SCSS": "#C6538C", "Shell": "#89E051",
}
NIVELES = ["#1a2030", "#4a2418", "#8a3a1e", "#d4542b", "#ff6a3d"]

# Paleta
FONDO_A, FONDO_B = "#0e121b", "#151b29"
BORDE = "#262e42"
TARJETA = "#121826"
TEXTO = "#e8ecf5"
SUAVE = "#8b95ab"
ACENTO = "#ff6a3d"
MONO = "JetBrains Mono, SFMono-Regular, Consolas, Menlo, monospace"
SANS = "Segoe UI, Ubuntu, -apple-system, Helvetica, Arial, sans-serif"


def pedir(url, json_=True):
    req = urllib.request.Request(url, headers={"User-Agent": "panel-perfil", "Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = r.read().decode("utf-8")
    return json.loads(datos) if json_ else datos


def datos_repos():
    repos = pedir(f"https://api.github.com/users/{USUARIO}/repos?per_page=100&type=owner")
    propios = [r for r in repos if not r["fork"] and r["name"] != USUARIO]
    bytes_por_lenguaje = {}
    for r in propios:
        for lenguaje, n in pedir(r["languages_url"]).items():
            bytes_por_lenguaje[lenguaje] = bytes_por_lenguaje.get(lenguaje, 0) + n
    total = sum(bytes_por_lenguaje.values()) or 1
    lenguajes = sorted(bytes_por_lenguaje.items(), key=lambda x: -x[1])
    principales = [(l, n / total) for l, n in lenguajes[:5]]
    resto = 1 - sum(p for _, p in principales)
    if resto > 0.005:
        principales.append(("Otros", resto))
    return len(propios), len(bytes_por_lenguaje), principales


def datos_contribuciones():
    html = pedir(f"https://github.com/users/{USUARIO}/contributions", json_=False)
    total = re.search(r"([\d,.]+)\s+contributions?\s+in the last year", html)
    total = int(re.sub(r"[,.]", "", total.group(1))) if total else 0
    dias = {}
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        fecha = re.search(r'data-date="([\d-]+)"', td)
        nivel = re.search(r'data-level="(\d)"', td)
        if fecha and nivel:
            dias[dt.date.fromisoformat(fecha.group(1))] = int(nivel.group(1))
    return total, dias


def texto(x, y, contenido, tam=13, color=TEXTO, peso=400, fuente=SANS, ancla="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{fuente}" font-size="{tam}" font-weight="{peso}" '
            f'fill="{color}" text-anchor="{ancla}" {extra}>{escape(contenido)}</text>')


def generar():
    hoy = dt.date.today()
    n_repos, n_lenguajes, lenguajes = datos_repos()
    total_contrib, dias = datos_contribuciones()
    dias_fct = max((INICIO_FCT - hoy).days, 0)
    progreso = min(max((hoy - INICIO_DAW).days / (FIN_DAW - INICIO_DAW).days, 0), 1)

    W, H = 860, 612
    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Panel de desarrollador de Antonio Cantón Sanz">')
    p.append(f"""<defs>
  <linearGradient id="fondo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{FONDO_A}"/><stop offset="1" stop-color="{FONDO_B}"/></linearGradient>
  <linearGradient id="acento" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff8a3d"/><stop offset="1" stop-color="#ff3d6a"/></linearGradient>
  <radialGradient id="brillo" cx="0.85" cy="0.1" r="0.6"><stop offset="0" stop-color="{ACENTO}" stop-opacity="0.16"/><stop offset="1" stop-color="{ACENTO}" stop-opacity="0"/></radialGradient>
</defs>
<style>
  .ap {{ opacity: 0; animation: aparecer .6s ease-out forwards; }}
  .crece {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: crecer 1.2s .5s ease-out forwards; }}
  .cursor {{ animation: parpadeo 1s steps(1) infinite; }}
  @keyframes aparecer {{ to {{ opacity: 1; }} }}
  @keyframes crecer {{ to {{ transform: scaleX(1); }} }}
  @keyframes parpadeo {{ 50% {{ opacity: 0; }} }}
</style>""")
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="url(#fondo)" stroke="{BORDE}"/>')
    p.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="url(#brillo)"/>')

    # Barra de terminal
    p.append(f'<path d="M0.5 16.5 a16 16 0 0 1 16 -16 h{W-33} a16 16 0 0 1 16 16 v23 h-{W-1} z" fill="#0a0d14" stroke="{BORDE}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        p.append(f'<circle cx="{24 + i*18}" cy="20" r="5.5" fill="{c}"/>')
    p.append(texto(W/2, 25, "antonio@granada: ~/perfil", 12, SUAVE, fuente=MONO, ancla="middle"))
    p.append(texto(W-20, 25, f"act. {hoy:%d/%m/%Y}", 11, "#5d667c", fuente=MONO, ancla="end"))

    # Cabecera
    p.append(f'<g class="ap">')
    p.append(texto(28, 76, "$ whoami", 13, ACENTO, 600, MONO))
    p.append(texto(28, 106, "Antonio Cantón Sanz", 28, TEXTO, 700))
    p.append(texto(28, 130, "Desarrollador web junior · Angular · automatización con IA", 14, SUAVE))
    p.append("</g>")

    # Cuenta atrás FCT
    p.append(f'<g class="ap" style="animation-delay:.15s">')
    p.append(f'<rect x="{W-218}" y="58" width="190" height="82" rx="12" fill="{TARJETA}" stroke="url(#acento)" stroke-width="1.5"/>')
    p.append(texto(W-200, 80, "CUENTA ATRÁS", 10, SUAVE, 600, MONO, extra='letter-spacing="1.5"'))
    p.append(texto(W-200, 120, str(dias_fct), 38, ACENTO, 800, SANS))
    ancho_num = 23 * len(str(dias_fct))
    p.append(texto(W-200 + ancho_num + 6, 108, "días", 13, TEXTO, 600))
    p.append(texto(W-200 + ancho_num + 6, 124, "para la FCT", 11, SUAVE))
    p.append("</g>")

    # Tarjetas de datos
    tarjetas = [
        ("REPOS PÚBLICOS", str(n_repos), "proyectos propios"),
        ("CONTRIBUCIONES", str(total_contrib), "en el último año"),
        ("LENGUAJES", str(n_lenguajes), "en mis repos"),
        ("CICLO DAW", f"{round(progreso*100)}%", "completado"),
    ]
    tw, gap, ty = 193, 16, 160
    for i, (titulo, valor, sub) in enumerate(tarjetas):
        x = 28 + i * (tw + gap) - (i * 2)
        p.append(f'<g class="ap" style="animation-delay:{.25 + i*.08:.2f}s">')
        p.append(f'<rect x="{x}" y="{ty}" width="{tw-6}" height="84" rx="12" fill="{TARJETA}" stroke="{BORDE}"/>')
        p.append(texto(x+16, ty+24, titulo, 10, SUAVE, 600, MONO, extra='letter-spacing="1.2"'))
        p.append(texto(x+16, ty+58, valor, 26, TEXTO, 700))
        if titulo == "CICLO DAW":
            bw = tw - 6 - 32 - 60
            p.append(f'<rect x="{x+76}" y="{ty+49}" width="{bw}" height="6" rx="3" fill="#232b3d"/>')
            p.append(f'<rect x="{x+76}" y="{ty+49}" width="{bw*progreso:.1f}" height="6" rx="3" fill="url(#acento)" class="crece"/>')
            p.append(texto(x+16, ty+74, sub, 11, SUAVE))
        else:
            p.append(texto(x+16, ty+74, sub, 11, SUAVE))
        p.append("</g>")

    # Actividad (heatmap)
    hy = 272
    p.append(f'<g class="ap" style="animation-delay:.55s">')
    p.append(texto(28, hy, "$ git log --semanas 26", 12, ACENTO, 600, MONO))
    fin = hoy
    inicio = fin - dt.timedelta(days=fin.weekday() + 1 + 7 * (SEMANAS - 1))  # domingo
    celda, sep = 13, 3
    for s in range(SEMANAS):
        for d in range(7):
            dia = inicio + dt.timedelta(days=s*7 + d)
            if dia > fin:
                continue
            nivel = dias.get(dia, 0)
            p.append(f'<rect x="{28 + s*(celda+sep)}" y="{hy + 14 + d*(celda+sep)}" width="{celda}" height="{celda}" rx="3" fill="{NIVELES[nivel]}"/>')
    ly = hy + 14 + 7*(celda+sep) + 14
    p.append(texto(28, ly, "menos", 10, "#5d667c", fuente=MONO))
    for i, c in enumerate(NIVELES):
        p.append(f'<rect x="{70 + i*14}" y="{ly-9}" width="10" height="10" rx="2" fill="{c}"/>')
    p.append(texto(146, ly, "más", 10, "#5d667c", fuente=MONO))
    p.append("</g>")

    # Lenguajes
    lx, lw = 476, W - 476 - 28
    p.append(f'<g class="ap" style="animation-delay:.65s">')
    p.append(texto(lx, hy, "$ cat lenguajes.txt", 12, ACENTO, 600, MONO))
    p.append(f'<clipPath id="barra"><rect x="{lx}" y="{hy+16}" width="{lw}" height="12" rx="6"/></clipPath>')
    p.append(f'<g clip-path="url(#barra)" class="crece">')
    x = lx
    for nombre, pct in lenguajes:
        ancho = lw * pct
        p.append(f'<rect x="{x:.1f}" y="{hy+16}" width="{ancho+0.5:.1f}" height="12" fill="{COLORES_LENGUAJE.get(nombre, "#5d667c")}"/>')
        x += ancho
    p.append("</g>")
    for i, (nombre, pct) in enumerate(lenguajes):
        col, fila = i % 2, i // 2
        x0, y0 = lx + col * (lw/2), hy + 56 + fila * 26
        p.append(f'<circle cx="{x0+5}" cy="{y0-4}" r="5" fill="{COLORES_LENGUAJE.get(nombre, "#5d667c")}"/>')
        p.append(texto(x0+18, y0, nombre, 13, TEXTO, 500))
        p.append(texto(x0 + lw/2 - 16, y0, f"{pct*100:.1f}%", 12, SUAVE, fuente=MONO, ancla="end"))
    p.append("</g>")

    # Proyectos
    py = 446
    p.append(f'<g class="ap" style="animation-delay:.8s">')
    p.append(texto(28, py, "$ ls proyectos/", 12, ACENTO, 600, MONO))
    pw = (W - 56 - 2*16) / 3
    for i, (nombre, desc, chips, color) in enumerate(PROYECTOS):
        x = 28 + i * (pw + 16)
        y = py + 14
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{pw:.1f}" height="104" rx="12" fill="{TARJETA}" stroke="{BORDE}"/>')
        p.append(f'<rect x="{x:.1f}" y="{y+18}" width="3" height="28" rx="1.5" fill="{color}"/>')
        p.append(texto(x+16, y+30, nombre, 15, TEXTO, 700))
        p.append(texto(x+16, y+50, desc, 11, SUAVE))
        cx = x + 16
        for chip in chips:
            ancho = 7 * len(chip) + 16
            p.append(f'<rect x="{cx:.1f}" y="{y+68}" width="{ancho}" height="22" rx="11" fill="none" stroke="{color}" stroke-opacity="0.7"/>')
            p.append(texto(cx + ancho/2, y+83, chip, 10.5, TEXTO, 500, MONO, ancla="middle"))
            cx += ancho + 6
    p.append("</g>")

    # Pie
    p.append(f'<line x1="28" y1="{H-34}" x2="{W-28}" y2="{H-34}" stroke="{BORDE}"/>')
    p.append(texto(28, H-14, "> busco prácticas FCT · 15/02 → 04/06/2027 · Granada · híbrido · remoto", 12, ACENTO, 500, MONO))
    p.append(f'<rect x="{W-40}" y="{H-25}" width="8" height="14" fill="{ACENTO}" class="cursor"/>')
    p.append("</svg>")

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(x for x in p if x))
    print(f"{SALIDA}: repos={n_repos} lenguajes={n_lenguajes} contribuciones={total_contrib} días FCT={dias_fct} DAW={progreso:.0%}")


if __name__ == "__main__":
    generar()
