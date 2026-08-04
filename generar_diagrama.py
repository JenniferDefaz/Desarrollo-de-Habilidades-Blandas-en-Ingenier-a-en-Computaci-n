from PIL import Image, ImageDraw, ImageFont
import os

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1600, 2000
img = Image.new("RGB", (W, H), "#F8F9FA")
d   = ImageDraw.Draw(img)

# ── Intentar fuente del sistema, si no existe usar default ───────────────────
def get_font(size, bold=False):
    candidates_bold   = ["arialbd.ttf","Arial Bold.ttf","calibrib.ttf","DejaVuSans-Bold.ttf"]
    candidates_normal = ["arial.ttf","Arial.ttf","calibri.ttf","DejaVuSans.ttf"]
    candidates = candidates_bold if bold else candidates_normal
    dirs = [
        r"C:\Windows\Fonts",
        r"C:\Windows\fonts",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts",
    ]
    for fname in candidates:
        for d_ in dirs:
            path = os.path.join(d_, fname)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    pass
    return ImageFont.load_default()

fT   = get_font(34, bold=True)   # título grande
fH   = get_font(26, bold=True)   # cabecera de capa
fSub = get_font(20, bold=True)   # sub-título de caja
fB   = get_font(17)              # body text
fBb  = get_font(17, bold=True)   # body bold
fSm  = get_font(15)              # small
fXs  = get_font(13)              # extra small

# ── Colores ───────────────────────────────────────────────────────────────────
C_BG        = "#F8F9FA"
C_TITLE_BG  = "#0D47A1"
C_TITLE_FG  = "#FFFFFF"

# capas
C_L1_BG  = "#1565C0";  C_L1_HDR = "#0D47A1";  C_L1_FG = "#FFFFFF"  # Presentación — azul oscuro
C_L2_BG  = "#1976D2";  C_L2_HDR = "#0D47A1";  C_L2_FG = "#FFFFFF"  # Negocio      — azul medio
C_L3_BG  = "#FF8F00";  C_L3_HDR = "#E65100";  C_L3_FG = "#FFFFFF"  # Persistencia — naranja
C_L4_BG  = "#2E7D32";  C_L4_HDR = "#1B5E20";  C_L4_FG = "#FFFFFF"  # Base Datos   — verde
C_SH_BG  = "#6A1B9A";  C_SH_HDR = "#4A148C";  C_SH_FG = "#FFFFFF"  # Shared       — violeta

C_BOX_BG  = "#FFFFFF"
C_BOX_BD  = "#BBDEFB"
C_BOX_FG  = "#0D1B2A"
C_ARROW   = "#37474F"
C_RULE    = "#90A4AE"

MARGIN  = 60
PAD     = 14
RADIUS  = 12

# ── Helpers ───────────────────────────────────────────────────────────────────
def rrect(draw, x0, y0, x1, y1, r, fill, outline=None, width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                           outline=outline, width=width)

def center_text(draw, text, x, y, font, fill="#FFFFFF"):
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text((x - tw//2, y), text, font=font, fill=fill)

def wrap_text(draw, text, x, y, max_w, font, fill, line_h=20):
    words = text.split()
    line  = ""
    yy    = y
    for w in words:
        test = (line + " " + w).strip()
        bb   = draw.textbbox((0,0), test, font=font)
        if bb[2] - bb[0] <= max_w:
            line = test
        else:
            if line:
                draw.text((x, yy), line, font=font, fill=fill)
                yy += line_h
            line = w
    if line:
        draw.text((x, yy), line, font=font, fill=fill)
    return yy + line_h

def arrow_down(draw, cx, y_top, y_bot, color=C_ARROW, label=""):
    draw.line([(cx, y_top), (cx, y_bot-10)], fill=color, width=3)
    draw.polygon([(cx-8, y_bot-12),(cx+8, y_bot-12),(cx, y_bot)], fill=color)
    if label:
        bb = draw.textbbox((0,0), label, font=fXs)
        tw = bb[2]-bb[0]
        draw.text((cx - tw//2, (y_top+y_bot)//2 - 10), label, font=fXs, fill=color)

# ══════════════════════════════════════════════════════════════════════════════
# TÍTULO
# ══════════════════════════════════════════════════════════════════════════════
rrect(d, 0, 0, W, 80, 0, C_TITLE_BG)
center_text(d, "ARQUITECTURA EN CAPAS HORIZONTALES — MONOLITO MODULAR", W//2, 14, fT)
center_text(d, "Sistema Integral de Desarrollo de Habilidades Blandas", W//2, 50, fB)

# ══════════════════════════════════════════════════════════════════════════════
# USUARIO  (parte superior)
# ══════════════════════════════════════════════════════════════════════════════
ux, uy = W//2, 130
# figura usuario
r_cabeza = 20
d.ellipse([ux-r_cabeza, uy-r_cabeza, ux+r_cabeza, uy+r_cabeza], fill="#1565C0", outline="#0D47A1", width=2)
d.line([(ux, uy+r_cabeza),(ux, uy+r_cabeza+30)], fill="#1565C0", width=4)
d.line([(ux-25, uy+r_cabeza+10),(ux+25, uy+r_cabeza+10)], fill="#1565C0", width=4)
d.line([(ux, uy+r_cabeza+30),(ux-18, uy+r_cabeza+58)], fill="#1565C0", width=4)
d.line([(ux, uy+r_cabeza+30),(ux+18, uy+r_cabeza+58)], fill="#1565C0", width=4)
center_text(d, "USUARIOS (8 roles)", ux, uy+r_cabeza+65, fBb, "#1565C0")
center_text(d, "Estudiante · Docente · Tutor · Coordinador", ux, uy+r_cabeza+88, fXs, "#546E7A")
center_text(d, "Empresa · Graduado · Bienestar · Administrador", ux, uy+r_cabeza+104, fXs, "#546E7A")

# flecha usuario → capa 1
arrow_down(d, ux, uy+r_cabeza+120, 250, label="HTTPS/TLS · JWT")

# ══════════════════════════════════════════════════════════════════════════════
# Definir capas
# ══════════════════════════════════════════════════════════════════════════════
LX0 = MARGIN
LX1 = W - MARGIN
layers = [
    # (y_top, height, bg, hdr_bg, fg, número, nombre, subtítulo)
    (250,  230, C_L1_BG, C_L1_HDR, C_L1_FG, "CAPA 1", "PRESENTACIÓN",  "Controllers REST"),
    (520,  230, C_L2_BG, C_L2_HDR, C_L2_FG, "CAPA 2", "NEGOCIO",       "Services"),
    (790,  230, C_L3_BG, C_L3_HDR, C_L3_FG, "CAPA 3", "PERSISTENCIA",  "Repositories + ORM"),
    (1060, 200, C_L4_BG, C_L4_HDR, C_L4_FG, "CAPA 4", "BASE DE DATOS", "PostgreSQL 15"),
]

# Cajas internas por capa
boxes = {
    0: [  # CAPA 1 — Controllers
        ("DiagnosticoController",        "POST /api/evaluaciones/diagnostico\nRF03 — Diagnóstico inicial"),
        ("EvaluacionParesController",     "POST /api/evaluaciones/pares\nRF09 — Evaluación entre pares"),
        ("EvaluacionDocenteController",   "POST /api/evaluaciones/docente\nRF10 — Evaluación docente"),
        ("EvaluacionEmpleadorController", "POST /api/evaluaciones/empleador\nRF11 — Empresa colaboradora"),
        ("HistorialController",           "GET /api/evaluaciones/historial\nRF19 — Historial auditable"),
    ],
    1: [  # CAPA 2 — Services
        ("EvaluacionService",   "calcularPromedio()\nvalidarRubricas()"),
        ("ValidacionService",   "validarPermisos()\nvalidarDTO()  RBAC"),
        ("HistorialService",    "registrarHistorial()\nfiltrosPrivacidad()"),
        ("NotificacionService", "enviarNotificacion()\ndelegarModulo()"),
    ],
    2: [  # CAPA 3 — Repositories
        ("EvaluacionRepository",  "save()  findById()\nfindByEstudianteId()\nORM — JPA/TypeORM"),
        ("HistorialRepository",   "registrar()  ← SOLO INSERTAR\npreventUpdate()  🔒\npreventDelete()  🔒\nAPPEND-ONLY / INMUTABLE"),
    ],
    3: [  # CAPA 4 — PostgreSQL
        ("usuarios",        "roles, contraseñas\nhash, cifrado"),
        ("evaluaciones",    "calificacion, tipo\nfecha, activo"),
        ("historial_auditoria","INMUTABLE\nAPPEND-ONLY"),
        ("competencias",    "niveles, rúbricas\nconfigurables"),
        ("evidencias",      "referencia a\nMinIO/FileSystem"),
        ("analitica",       "dashboard\nreportes"),
    ],
}

layer_y_bottoms = []

for i, (yt, lh, bg, hdr_bg, fg, num, name, sub) in enumerate(layers):
    yb = yt + lh
    layer_y_bottoms.append(yb)

    # fondo de capa
    rrect(d, LX0, yt, LX1, yb, RADIUS, bg, outline=hdr_bg, width=3)

    # etiqueta izquierda (número + nombre)
    label_w = 130
    rrect(d, LX0, yt, LX0 + label_w, yb, RADIUS, hdr_bg)
    # texto vertical en la etiqueta izquierda
    lbl_cx = LX0 + label_w//2
    lbl_cy = yt + lh//2
    center_text(d, num,  lbl_cx, lbl_cy - 28, fBb, fg)
    center_text(d, name, lbl_cx, lbl_cy - 4,  fH,  fg)
    center_text(d, f"[{sub}]", lbl_cx, lbl_cy + 28, fXs, "#BBDEFB")

    # cajas internas
    inner_x0 = LX0 + label_w + 16
    inner_x1 = LX1 - 16
    inner_w   = inner_x1 - inner_x0
    box_items = boxes[i]
    n         = len(box_items)
    gap       = 10
    bw        = (inner_w - gap*(n-1)) // n
    bh        = lh - 30

    for j, (title, desc) in enumerate(box_items):
        bx0 = inner_x0 + j*(bw + gap)
        bx1 = bx0 + bw
        by0 = yt + 15
        by1 = by0 + bh

        rrect(d, bx0, by0, bx1, by1, 8, C_BOX_BG, outline=C_BOX_BD, width=2)

        # header de la caja
        rrect(d, bx0, by0, bx1, by0+28, 8, hdr_bg)
        # corregir esquinas inferiores del header (hacerlo rect)
        d.rectangle([bx0, by0+14, bx1, by0+28], fill=hdr_bg)

        bb = d.textbbox((0,0), title, font=fXs)
        tw = bb[2]-bb[0]
        tx = bx0 + (bw - tw)//2
        d.text((tx, by0+6), title, font=fXs, fill="#FFFFFF")

        # descripción
        lines = desc.split("\n")
        ty = by0 + 36
        for ln in lines:
            bb2 = d.textbbox((0,0), ln, font=fXs)
            lw2 = bb2[2]-bb2[0]
            lx2 = bx0 + (bw - lw2)//2
            d.text((lx2, ty), ln, font=fXs, fill=C_BOX_FG)
            ty += 18

# ── Flechas entre capas ───────────────────────────────────────────────────────
arrow_labels = ["llama a →", "delega a →", "queries ORM →"]
for i in range(len(layers)-1):
    yb = layer_y_bottoms[i]
    yt_next = layers[i+1][0]
    lbl = arrow_labels[i] if i < len(arrow_labels) else ""
    arrow_down(d, W//2, yb, yt_next, label=lbl)
