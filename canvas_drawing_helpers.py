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
