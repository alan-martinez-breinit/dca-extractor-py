def draw_rounded_rectangle(canvas_widget, top_left_x, top_left_y, bottom_right_x, bottom_right_y,
                            corner_radius=18, **style_options):
    polygon_points = [
        top_left_x + corner_radius, top_left_y,
        bottom_right_x - corner_radius, top_left_y,
        bottom_right_x, top_left_y,
        bottom_right_x, top_left_y + corner_radius,
        bottom_right_x, bottom_right_y - corner_radius,
        bottom_right_x, bottom_right_y,
        bottom_right_x - corner_radius, bottom_right_y,
        top_left_x + corner_radius, bottom_right_y,
        top_left_x, bottom_right_y,
        top_left_x, bottom_right_y - corner_radius,
        top_left_x, top_left_y + corner_radius,
        top_left_x, top_left_y,
    ]
    return canvas_widget.create_polygon(polygon_points, smooth=True, **style_options)


# Los iconos se dibujan como vectores (lineas/poligonos) en vez de caracteres emoji:
# el glifo emoji depende de que el dispositivo tenga la fuente de color instalada y de
# como Windows resuelva el fallback de fuente en el contexto de Tk, lo cual varia por
# equipo y produce cajas "tofu" o iconos monocromos. Un icono vectorial se ve identico
# en cualquier dispositivo.

def draw_download_glyph(canvas_widget, center_x, center_y, glyph_size, color, tags=()):
    """Documento con esquina doblada, flecha hacia abajo y linea base — icono de
    "descargar archivo", en el mismo estilo de trazo (outline) que los demas iconos."""
    half_size = glyph_size / 2
    page_left = center_x - half_size * 0.55
    page_right = center_x + half_size * 0.55
    page_top = center_y - half_size * 0.95
    page_bottom = center_y + half_size * 0.95
    fold = half_size * 0.4

    canvas_widget.create_line(
        page_left, page_top,
        page_right - fold, page_top,
        page_right, page_top + fold,
        page_right, page_bottom,
        page_left, page_bottom,
        page_left, page_top,
        fill=color, width=1.1, capstyle="round", joinstyle="round", tags=tags)
    canvas_widget.create_line(
        page_right - fold, page_top,
        page_right - fold, page_top + fold,
        page_right, page_top + fold,
        fill=color, width=1.1, capstyle="round", joinstyle="round", tags=tags)

    arrow_top_y = center_y - half_size * 0.35
    arrow_bottom_y = center_y + half_size * 0.32
    canvas_widget.create_line(
        center_x, arrow_top_y, center_x, arrow_bottom_y,
        fill=color, width=1.1, capstyle="round", tags=tags)
    canvas_widget.create_line(
        center_x - half_size * 0.28, arrow_bottom_y - half_size * 0.28,
        center_x, arrow_bottom_y,
        center_x + half_size * 0.28, arrow_bottom_y - half_size * 0.28,
        fill=color, width=1.1, capstyle="round", joinstyle="round", tags=tags)

    base_y = page_bottom - half_size * 0.22
    canvas_widget.create_line(
        page_left + half_size * 0.22, base_y, page_right - half_size * 0.22, base_y,
        fill=color, width=1.1, capstyle="round", tags=tags)


def draw_clipboard_glyph(canvas_widget, center_x, center_y, glyph_size, color, tags=()):
    half_width = glyph_size * 0.35
    half_height = glyph_size * 0.5
    left_x, right_x = center_x - half_width, center_x + half_width
    top_y, bottom_y = center_y - half_height, center_y + half_height
    canvas_widget.create_rectangle(left_x, top_y, right_x, bottom_y, outline=color, width=1.5, tags=tags)
    tab_half_width = half_width * 0.5
    canvas_widget.create_rectangle(
        center_x - tab_half_width, top_y - glyph_size * 0.12,
        center_x + tab_half_width, top_y + glyph_size * 0.1,
        fill=color, outline=color, tags=tags)
    for line_fraction in (0.15, 0.45, 0.75):
        line_y = top_y + (bottom_y - top_y) * line_fraction + glyph_size * 0.08
        canvas_widget.create_line(
            left_x + half_width * 0.4, line_y, right_x - half_width * 0.4, line_y,
            fill=color, width=1.2, tags=tags)


def draw_check_glyph(canvas_widget, center_x, center_y, glyph_size, color, tags=()):
    half_size = glyph_size / 2
    canvas_widget.create_line(
        center_x - half_size * 0.7, center_y,
        center_x - half_size * 0.15, center_y + half_size * 0.5,
        center_x + half_size * 0.75, center_y - half_size * 0.5,
        fill=color, width=2.2, capstyle="round", joinstyle="round", tags=tags)


def draw_cabinet_glyph(canvas_widget, center_x, center_y, glyph_size, color, tags=()):
    half_width = glyph_size * 0.4
    half_height = glyph_size * 0.5
    left_x, right_x = center_x - half_width, center_x + half_width
    top_y, bottom_y = center_y - half_height, center_y + half_height
    canvas_widget.create_rectangle(left_x, top_y, right_x, bottom_y, outline=color, width=1.5, tags=tags)
    canvas_widget.create_line(left_x, center_y, right_x, center_y, fill=color, width=1.5, tags=tags)
    handle_radius = glyph_size * 0.05
    for handle_center_y in (top_y + half_height * 0.5, bottom_y - half_height * 0.5):
        canvas_widget.create_oval(
            center_x - handle_radius, handle_center_y - handle_radius,
            center_x + handle_radius, handle_center_y + handle_radius,
            fill=color, outline="", tags=tags)


def draw_terminal_glyph(canvas_widget, center_x, center_y, glyph_size, color, tags=()):
    half_width = glyph_size * 0.5
    half_height = glyph_size * 0.4
    left_x, right_x = center_x - half_width, center_x + half_width
    top_y, bottom_y = center_y - half_height, center_y + half_height
    canvas_widget.create_rectangle(left_x, top_y, right_x, bottom_y, outline=color, width=1.5, tags=tags)
    for line_fraction in (-0.35, 0, 0.35):
        line_y = center_y + half_height * line_fraction
        canvas_widget.create_line(
            left_x + half_width * 0.3, line_y, right_x - half_width * 0.3, line_y,
            fill=color, width=1.2, tags=tags)
