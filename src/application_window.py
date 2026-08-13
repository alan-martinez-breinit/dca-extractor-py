import ctypes
import datetime
import os
import sys
import threading
import time
import tkinter
from tkinter import font as tkinter_font, messagebox

from src.color_palette import COLOR_PALETTE, LOG_TITLE_BAR_INDICATOR_COLORS
from src.canvas_drawing_helpers import (
    draw_rounded_rectangle,
    draw_download_glyph,
    draw_clipboard_glyph,
    draw_check_glyph,
    draw_cabinet_glyph,
    draw_terminal_glyph,
)
from src.configuration_settings import (
    REMOTE_DIRECTORY_PATH,
    LOCAL_BASE_DIRECTORY_PATH,
    LOCAL_CLIENT_SUBDIRECTORY_NAME,
    PROGRESS_LOG_STEP_PERCENTAGE,
    INTERFACE_UPDATE_STEP_PERCENTAGE,
    AI_INSTRUCTIONS_FILE_NAME,
    BUNDLED_DOCUMENTATION_FILE_NAMES,
    AI_INSTRUCTIONS_SEARCH_DIRECTORIES,
)
from src.filesystem_helpers import (
    ensure_base_directory_exists,
    ensure_client_subdirectory_exists,
    local_file_with_matching_name_exists,
    list_text_file_names_in_directory,
    find_first_available_static_file_path,
    copy_first_available_static_file,
)
from src.remote_file_transfer_service import RemoteFileTransferService
from src.schema_ini_generator import generate_schema_ini_file
from src.download_period_filter import (
    DOWNLOAD_PERIOD_BUTTON_SPECS,
    resolve_period_short_label,
    filter_remote_file_names_for_period,
    build_download_context_note,
)
from src.download_run_info import format_duration_message
from src.download_monitoring_log import append_monitoring_entry
from src.error_message_translator import translate_exception_to_spanish_message

SUPPORT_CONTACT_MESSAGE = "Si el problema persiste, comuníquese con DCA Soporte."


# Todos los valores de layout de abajo son "de referencia" (el diseno original,
# pensado para una pantalla comoda). En __init__ se calcula self.ui_scale_factor
# segun el alto de pantalla real disponible, y self.px(valor) devuelve ese valor
# multiplicado por el factor — asi TODO el contenido (fuentes, iconos, altos,
# espaciados) se encoge junto y proporcional en pantallas chicas (ej. 1366x768,
# muy comun entre laptops), en vez de que la ventana se encoja pero el contenido
# fijo se desborde/corte (ese fue el bug original) o de forzar un tamano fijo
# que no cabe en pantallas mas chicas (ese fue el bug de la iteracion anterior).
REFERENCE_WINDOW_WIDTH_PIXELS = 640
REFERENCE_WINDOW_HEIGHT_PIXELS = 894
MINIMUM_UI_SCALE_FACTOR = 0.72
SCREEN_TASKBAR_RESERVE_PIXELS = 60
SCREEN_TITLE_BAR_RESERVE_PIXELS = 32

HERO_CANVAS_HEIGHT_PIXELS = 434
HERO_CANVAS_MARGIN_PIXELS = 30
HERO_CANVAS_MINIMUM_WIDTH_PIXELS = 360
ICON_GLYPH_SIZE_PIXELS = 16
# El icono de descarga (documento + flecha) tiene mas detalle que los demas
# glifos; a 16px sus trazos se funden en un borron. Un tamano propio y mas
# grande solo para los botones lo mantiene legible sin tocar los otros iconos.
DOWNLOAD_BUTTON_ICON_SIZE_PIXELS = 20

DOWNLOAD_ACTION_BUTTONS_TOP_Y_PIXELS = 220
DOWNLOAD_ACTION_BUTTON_HEIGHT_PIXELS = 44
DOWNLOAD_ACTION_BUTTON_GAP_PIXELS = 10
DOWNLOAD_ACTION_BUTTON_HALF_WIDTH_PIXELS = 130
DESTINATION_PATH_ROW_Y_PIXELS = 404


def disable_windows_maximize_button(root_window):
    """resizable(False, False) no siempre engrisa visualmente el boton de
    maximizar en Windows — en algunas versiones/temas queda con apariencia
    normal aunque no haga nada, lo cual confunde al usuario (parece que deberia
    funcionar). Se quita el estilo nativo WS_MAXIMIZEBOX via la API de Windows
    para que el boton se vea y se comporte como realmente deshabilitado.
    """
    if sys.platform != "win32":
        return
    try:
        root_window.update_idletasks()
        GWL_STYLE = -16
        WS_MAXIMIZEBOX = 0x00010000
        SWP_NOMOVE, SWP_NOSIZE, SWP_NOZORDER, SWP_FRAMECHANGED = 0x0002, 0x0001, 0x0004, 0x0020
        window_handle = ctypes.windll.user32.GetParent(root_window.winfo_id())
        current_window_style = ctypes.windll.user32.GetWindowLongW(window_handle, GWL_STYLE)
        ctypes.windll.user32.SetWindowLongW(window_handle, GWL_STYLE, current_window_style & ~WS_MAXIMIZEBOX)
        # SetWindowLongW por si solo no siempre repinta la barra de titulo de
        # inmediato — hay que forzar a Windows a recalcular el frame para que
        # el boton de maximizar se vea (no solo se comporte) como deshabilitado.
        ctypes.windll.user32.SetWindowPos(
            window_handle, 0, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
    except (AttributeError, OSError):
        pass


class DCAExtractorApplicationWindow:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("FTP DCA AUTOPOLIS")
        self.compute_ui_scale_factor()
        self.apply_adaptive_window_size()
        self.root_window.configure(bg=COLOR_PALETTE["background_color"])

        self.is_download_in_progress = False
        self.current_progress_percentage = 0.0
        self.status_message = "Listo para iniciar transferencia segura"
        self.progress_label_message = "En espera"
        self.destination_path_message = None
        self.download_action_button_states = {
            spec["period_key"]: {"label_text": spec["short_label"], "enabled": True}
            for spec in DOWNLOAD_PERIOD_BUTTON_SPECS
        }
        self.copy_icon_mode = "clipboard"
        self.last_rendered_hero_canvas_width = None

        self.application_fonts = {
            "display_font": tkinter_font.Font(
                family="Segoe UI Semibold", size=self.scaled_font_size(22), weight="bold"),
            "title_font": tkinter_font.Font(
                family="Segoe UI Semibold", size=self.scaled_font_size(13), weight="bold"),
            "body_font": tkinter_font.Font(family="Segoe UI", size=self.scaled_font_size(10)),
            "label_font": tkinter_font.Font(
                family="Segoe UI Semibold", size=self.scaled_font_size(8), weight="bold"),
            "code_font": tkinter_font.Font(family="Consolas", size=self.scaled_font_size(9)),
            "code_bold_font": tkinter_font.Font(family="Consolas", size=self.scaled_font_size(9), weight="bold"),
        }

        self.build_header_section()
        self.build_hero_status_card()
        self.build_transfer_log_card()

    def px(self, reference_value_at_scale_1x):
        """Escala un valor de pixeles de referencia segun self.ui_scale_factor,
        calculado una sola vez en compute_ui_scale_factor(). Se usa para que
        TODO el layout se encoja/agrande junto y proporcional, en vez de que
        cada elemento se ajuste (o no) por su cuenta."""
        return round(reference_value_at_scale_1x * self.ui_scale_factor)

    def scaled_font_size(self, reference_point_size, minimum_pixel_size=9):
        """Devuelve un tamano en PIXELES (negativo — convencion de Tk para
        "pixeles, no puntos") en vez de puntos. Los tamanos en puntos los
        reescala Windows solo, segun el DPI del sistema — a 150% de escala el
        texto se renderiza mas grande de lo que este layout (medido en
        pixeles via self.px()) tiene presupuestado, y se desborda de sus
        contenedores aunque la pantalla tenga espacio de sobra. Usando
        pixeles para fuentes y layout por igual, el escalado depende solo de
        self.ui_scale_factor — nunca del DPI de Windows.
        """
        reference_pixel_size = round(reference_point_size * 96 / 72)
        return -max(minimum_pixel_size, self.px(reference_pixel_size))

    def compute_ui_scale_factor(self):
        screen_height_pixels = self.root_window.winfo_screenheight()
        available_height_pixels = (
            screen_height_pixels - SCREEN_TASKBAR_RESERVE_PIXELS - SCREEN_TITLE_BAR_RESERVE_PIXELS)
        raw_scale_factor = min(1.0, available_height_pixels / REFERENCE_WINDOW_HEIGHT_PIXELS)
        self.ui_scale_factor = max(MINIMUM_UI_SCALE_FACTOR, raw_scale_factor)

    def apply_adaptive_window_size(self):
        """El alto de ventana se deriva de self.ui_scale_factor (calculado del
        alto de pantalla real), asi que siempre cabe completo sin cortarse —
        adaptable a cada maquina. Una vez calculado, se bloquea: no
        redimensionable ni maximizable, para que el usuario no lo rompa
        arrastrando bordes."""
        screen_width_pixels = self.root_window.winfo_screenwidth()
        screen_height_pixels = self.root_window.winfo_screenheight()

        self.window_width_pixels = min(REFERENCE_WINDOW_WIDTH_PIXELS, screen_width_pixels - 40)
        window_height_pixels = self.px(REFERENCE_WINDOW_HEIGHT_PIXELS)

        window_position_x = max(0, (screen_width_pixels - self.window_width_pixels) // 2)
        window_position_y = max(
            0, (screen_height_pixels - SCREEN_TASKBAR_RESERVE_PIXELS - window_height_pixels) // 2)

        self.root_window.geometry(
            f"{self.window_width_pixels}x{window_height_pixels}+{window_position_x}+{window_position_y}")
        self.root_window.resizable(False, False)
        disable_windows_maximize_button(self.root_window)

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def build_header_section(self):
        header_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["primary_color"], height=self.px(60))
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        header_content_frame = tkinter.Frame(header_frame, bg=COLOR_PALETTE["primary_color"])
        header_content_frame.pack(expand=True)

        header_icon_size = self.px(ICON_GLYPH_SIZE_PIXELS)
        header_icon_canvas = tkinter.Canvas(header_content_frame, width=header_icon_size,
                                             height=header_icon_size, bg=COLOR_PALETTE["primary_color"],
                                             highlightthickness=0)
        header_icon_canvas.pack(side="left", padx=(0, self.px(8)))
        draw_cabinet_glyph(header_icon_canvas, header_icon_size / 2, header_icon_size / 2,
                            header_icon_size, COLOR_PALETTE["on_primary_color"])

        tkinter.Label(header_content_frame, text="FTP DCA AUTOPOLIS", font=self.application_fonts["title_font"],
                      bg=COLOR_PALETTE["primary_color"], fg=COLOR_PALETTE["on_primary_color"]).pack(side="left")

    def build_hero_status_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="x", padx=self.px(20), pady=(self.px(20), self.px(12)))

        self.destination_directory_path_for_clipboard = os.path.join(
            LOCAL_BASE_DIRECTORY_PATH, LOCAL_CLIENT_SUBDIRECTORY_NAME)
        self.destination_path_message = f"Se guardara en: {self.destination_directory_path_for_clipboard}"

        self.hero_canvas = tkinter.Canvas(wrapper_frame, height=self.px(HERO_CANVAS_HEIGHT_PIXELS),
                                           bg=COLOR_PALETTE["background_color"], highlightthickness=0)
        self.hero_canvas.pack(fill="x")

        for spec in DOWNLOAD_PERIOD_BUTTON_SPECS:
            hitbox_tag = self.download_button_hitbox_tag(spec["period_key"])
            self.hero_canvas.tag_bind(
                hitbox_tag, "<Button-1>",
                lambda event, period_key=spec["period_key"]: self.handle_download_button_click(period_key))
            self.hero_canvas.tag_bind(hitbox_tag, "<Enter>",
                                       lambda event: self.hero_canvas.config(cursor="hand2"))
            self.hero_canvas.tag_bind(hitbox_tag, "<Leave>",
                                       lambda event: self.hero_canvas.config(cursor=""))

        self.hero_canvas.tag_bind("copy_path_hitbox", "<Button-1>", self.handle_copy_path_click)
        self.hero_canvas.tag_bind("copy_path_hitbox", "<Enter>",
                                   lambda event: self.hero_canvas.config(cursor="hand2"))
        self.hero_canvas.tag_bind("copy_path_hitbox", "<Leave>",
                                   lambda event: self.hero_canvas.config(cursor=""))

        self.hero_canvas.bind("<Configure>", self.handle_hero_canvas_resize)

        initial_canvas_width = self.window_width_pixels - 2 * HERO_CANVAS_MARGIN_PIXELS - 10
        self.last_rendered_hero_canvas_width = initial_canvas_width
        self.render_hero_canvas(initial_canvas_width)

    def handle_hero_canvas_resize(self, event):
        if event.width == self.last_rendered_hero_canvas_width:
            return
        self.last_rendered_hero_canvas_width = event.width
        self.render_hero_canvas(event.width)

    @staticmethod
    def download_button_hitbox_tag(period_key):
        return f"download_button_hitbox_{period_key}"

    def render_hero_canvas(self, canvas_width=None):
        if canvas_width is None:
            canvas_width = self.hero_canvas.winfo_width()
        canvas_width = max(canvas_width, HERO_CANVAS_MINIMUM_WIDTH_PIXELS)

        self.hero_canvas.delete("all")

        left_x = HERO_CANVAS_MARGIN_PIXELS
        right_x = canvas_width - HERO_CANVAS_MARGIN_PIXELS
        center_x = canvas_width / 2
        icon_size = self.px(ICON_GLYPH_SIZE_PIXELS)
        destination_path_row_y = self.px(DESTINATION_PATH_ROW_Y_PIXELS)

        draw_rounded_rectangle(
            self.hero_canvas, 0, 0, canvas_width, self.px(HERO_CANVAS_HEIGHT_PIXELS), corner_radius=16,
            fill=COLOR_PALETTE["surface_lowest_color"],
            outline=COLOR_PALETTE["outline_variant_color"])

        security_badge_text = "TRANSFERENCIA SEGURA"
        draw_rounded_rectangle(
            self.hero_canvas, left_x, self.px(20),
            right_x, self.px(42), corner_radius=10,
            fill=COLOR_PALETTE["primary_fixed_color"], outline="")
        self.hero_canvas.create_text(center_x, self.px(31), text=security_badge_text,
                                      font=self.application_fonts["label_font"],
                                      fill=COLOR_PALETTE["primary_container_color"])

        self.hero_canvas.create_text(center_x, self.px(78), text="Descarga de archivos SFTP",
                                      font=self.application_fonts["display_font"], fill=COLOR_PALETTE["primary_color"])
        self.status_text_item_id = self.hero_canvas.create_text(
            center_x, self.px(108), text=self.status_message,
            font=self.application_fonts["body_font"], fill=COLOR_PALETTE["on_surface_variant_color"])

        self.progress_label_item_id = self.hero_canvas.create_text(
            left_x, self.px(160), text=self.progress_label_message, font=self.application_fonts["title_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="w")
        self.progress_percentage_item_id = self.hero_canvas.create_text(
            right_x, self.px(160), text=f"{int(self.current_progress_percentage)}%",
            font=self.application_fonts["code_bold_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="e")

        self.progress_bar_left_x, self.progress_bar_top_y = left_x, self.px(178)
        self.progress_bar_right_x, self.progress_bar_bottom_y = right_x, self.px(190)
        draw_rounded_rectangle(self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
                                self.progress_bar_right_x, self.progress_bar_bottom_y, corner_radius=6,
                                fill=COLOR_PALETTE["surface_container_color"], outline="")
        progress_bar_fill_right_x = self.progress_bar_left_x + (
            self.progress_bar_right_x - self.progress_bar_left_x) * (self.current_progress_percentage / 100.0)
        self.progress_bar_fill_item_id = draw_rounded_rectangle(
            self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
            max(progress_bar_fill_right_x, self.progress_bar_left_x), self.progress_bar_bottom_y, corner_radius=6,
            fill=COLOR_PALETTE["primary_color"], outline="")

        for button_index, spec in enumerate(DOWNLOAD_PERIOD_BUTTON_SPECS):
            self.draw_download_action_button(center_x, button_index, spec["period_key"])

        self.destination_path_text_item_id = self.hero_canvas.create_text(
            left_x, destination_path_row_y, text=self.destination_path_message,
            font=self.application_fonts["body_font"], fill=COLOR_PALETTE["on_surface_variant_color"], anchor="w")

        if self.copy_icon_mode == "check":
            draw_check_glyph(self.hero_canvas, right_x - icon_size / 2, destination_path_row_y,
                              icon_size, COLOR_PALETTE["primary_color"], tags=("copy_path_hitbox",))
        else:
            draw_clipboard_glyph(self.hero_canvas, right_x - icon_size / 2, destination_path_row_y,
                                  icon_size, COLOR_PALETTE["on_surface_variant_color"],
                                  tags=("copy_path_hitbox",))
        self.hero_canvas.create_rectangle(
            right_x - icon_size, destination_path_row_y - icon_size / 2,
            right_x + icon_size / 2, destination_path_row_y + icon_size / 2,
            fill="", outline="", tags=("copy_path_hitbox",))

    def draw_download_action_button(self, center_x, button_index, period_key):
        button_state = self.download_action_button_states[period_key]
        hitbox_tag = self.download_button_hitbox_tag(period_key)

        button_top_y_reference = DOWNLOAD_ACTION_BUTTONS_TOP_Y_PIXELS + button_index * (
            DOWNLOAD_ACTION_BUTTON_HEIGHT_PIXELS + DOWNLOAD_ACTION_BUTTON_GAP_PIXELS)
        button_top_y = self.px(button_top_y_reference)
        button_bottom_y = button_top_y + self.px(DOWNLOAD_ACTION_BUTTON_HEIGHT_PIXELS)
        button_center_y = (button_top_y + button_bottom_y) / 2
        button_half_width = self.px(DOWNLOAD_ACTION_BUTTON_HALF_WIDTH_PIXELS)
        download_button_icon_size = self.px(DOWNLOAD_BUTTON_ICON_SIZE_PIXELS)

        button_fill_color = (COLOR_PALETTE["primary_color"] if button_state["enabled"]
                              else COLOR_PALETTE["outline_variant_color"])
        draw_rounded_rectangle(
            self.hero_canvas, center_x - button_half_width, button_top_y,
            center_x + button_half_width, button_bottom_y, corner_radius=14,
            fill=button_fill_color, outline="", tags=(hitbox_tag,))

        label_text = button_state["label_text"]
        label_text_width = self.application_fonts["title_font"].measure(label_text)
        icon_gap = self.px(8)
        group_width = download_button_icon_size + icon_gap + label_text_width
        group_left_x = center_x - group_width / 2
        icon_center_x = group_left_x + download_button_icon_size / 2
        label_left_x = group_left_x + download_button_icon_size + icon_gap

        draw_download_glyph(self.hero_canvas, icon_center_x, button_center_y, download_button_icon_size,
                             COLOR_PALETTE["on_primary_color"], tags=(hitbox_tag,))
        self.hero_canvas.create_text(
            label_left_x, button_center_y, text=label_text, anchor="w",
            font=self.application_fonts["title_font"], fill=COLOR_PALETTE["on_primary_color"],
            tags=(hitbox_tag,))

    def build_transfer_log_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="both", expand=True, padx=self.px(20), pady=(0, self.px(20)))

        label_row_frame = tkinter.Frame(wrapper_frame, bg=COLOR_PALETTE["background_color"])
        label_row_frame.pack(fill="x", pady=(0, self.px(6)))

        log_icon_size = self.px(12)
        log_icon_canvas = tkinter.Canvas(label_row_frame, width=log_icon_size, height=log_icon_size,
                                          bg=COLOR_PALETTE["background_color"], highlightthickness=0)
        log_icon_canvas.pack(side="left", padx=(0, self.px(6)))
        draw_terminal_glyph(log_icon_canvas, log_icon_size / 2, log_icon_size / 2, log_icon_size,
                             COLOR_PALETTE["on_surface_variant_color"])

        tkinter.Label(label_row_frame, text="REGISTRO DE TRANSFERENCIA", font=self.application_fonts["label_font"],
                      bg=COLOR_PALETTE["background_color"], fg=COLOR_PALETTE["on_surface_variant_color"]).pack(
            side="left")

        log_card_frame = tkinter.Frame(wrapper_frame, bg=COLOR_PALETTE["surface_lowest_color"],
                                        highlightbackground=COLOR_PALETTE["outline_variant_color"],
                                        highlightthickness=1)
        log_card_frame.pack(fill="both", expand=True)

        log_title_bar_frame = tkinter.Frame(log_card_frame, bg=COLOR_PALETTE["surface_container_high_color"],
                                             height=self.px(32))
        log_title_bar_frame.pack(fill="x")
        log_title_bar_frame.pack_propagate(False)

        title_bar_indicators_frame = tkinter.Frame(log_title_bar_frame, bg=COLOR_PALETTE["surface_container_high_color"])
        title_bar_indicators_frame.pack(side="left", padx=self.px(12))
        indicator_diameter = self.px(10)
        for indicator_color in LOG_TITLE_BAR_INDICATOR_COLORS:
            indicator_canvas = tkinter.Canvas(title_bar_indicators_frame, width=indicator_diameter,
                                               height=indicator_diameter,
                                               bg=COLOR_PALETTE["surface_container_high_color"],
                                               highlightthickness=0)
            indicator_canvas.create_oval(1, 1, indicator_diameter - 1, indicator_diameter - 1,
                                          fill=indicator_color, outline="")
            indicator_canvas.pack(side="left", padx=self.px(2))

        log_content_frame = tkinter.Frame(log_card_frame, bg=COLOR_PALETTE["surface_lowest_color"])
        log_content_frame.pack(fill="both", expand=True)

        log_scrollbar = tkinter.Scrollbar(log_content_frame)
        log_scrollbar.pack(side="right", fill="y")

        self.transfer_log_text_widget = tkinter.Text(
            log_content_frame, font=self.application_fonts["code_font"], bg=COLOR_PALETTE["surface_lowest_color"],
            fg=COLOR_PALETTE["on_surface_variant_color"], relief="flat", wrap="word", state="disabled",
            yscrollcommand=log_scrollbar.set, padx=self.px(14), pady=self.px(10))
        self.transfer_log_text_widget.pack(fill="both", expand=True)
        log_scrollbar.config(command=self.transfer_log_text_widget.yview)

        self.transfer_log_text_widget.tag_config("timestamp_tag", foreground=COLOR_PALETTE["primary_color"],
                                                   font=self.application_fonts["code_bold_font"])
        self.transfer_log_text_widget.tag_config("normal_tag", foreground=COLOR_PALETTE["secondary_color"])
        self.transfer_log_text_widget.tag_config(
            "highlight_tag", foreground=COLOR_PALETTE["primary_color"],
            font=self.application_fonts["code_bold_font"], background=COLOR_PALETTE["primary_fixed_color"])
        self.transfer_log_text_widget.tag_config("error_tag", foreground=COLOR_PALETTE["error_color"],
                                                   font=self.application_fonts["code_bold_font"])
        self.transfer_log_text_widget.tag_config("success_tag", foreground=COLOR_PALETTE["primary_color"],
                                                   font=self.application_fonts["code_bold_font"])

    # ------------------------------------------------------------------
    # Utilidades de interfaz
    # ------------------------------------------------------------------
    def append_log_entry(self, log_message, entry_style="normal_tag"):
        current_timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.transfer_log_text_widget.config(state="normal")
        self.transfer_log_text_widget.insert("end", f"[{current_timestamp}]  ", "timestamp_tag")
        self.transfer_log_text_widget.insert("end", f"{log_message}\n", entry_style)
        self.transfer_log_text_widget.see("end")
        self.transfer_log_text_widget.config(state="disabled")

    def update_status_message(self, status_message):
        self.status_message = status_message
        self.hero_canvas.itemconfig(self.status_text_item_id, text=status_message)

    def update_progress_label_message(self, progress_label_message):
        self.progress_label_message = progress_label_message
        self.hero_canvas.itemconfig(self.progress_label_item_id, text=progress_label_message)

    def update_progress_bar(self, new_progress_percentage):
        self.current_progress_percentage = max(0.0, min(100.0, new_progress_percentage))
        progress_bar_total_width = self.progress_bar_right_x - self.progress_bar_left_x
        filled_width_right_edge = self.progress_bar_left_x + progress_bar_total_width * (
            self.current_progress_percentage / 100.0)

        self.hero_canvas.delete(self.progress_bar_fill_item_id)
        if filled_width_right_edge - self.progress_bar_left_x > 2:
            self.progress_bar_fill_item_id = draw_rounded_rectangle(
                self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
                filled_width_right_edge, self.progress_bar_bottom_y, corner_radius=6,
                fill=COLOR_PALETTE["primary_color"], outline="")
        else:
            self.progress_bar_fill_item_id = draw_rounded_rectangle(
                self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
                self.progress_bar_left_x, self.progress_bar_bottom_y, corner_radius=6,
                fill=COLOR_PALETTE["primary_color"], outline="")

        self.hero_canvas.itemconfig(self.progress_percentage_item_id,
                                     text=f"{int(self.current_progress_percentage)}%")

    def update_destination_path_message(self, destination_path_message):
        self.destination_path_message = destination_path_message
        self.hero_canvas.itemconfig(self.destination_path_text_item_id, text=destination_path_message)

    def handle_copy_path_click(self, event=None):
        self.root_window.clipboard_clear()
        self.root_window.clipboard_append(self.destination_directory_path_for_clipboard)
        self.root_window.update()
        self.append_log_entry("Ruta copiada al portapapeles", "success_tag")
        self.copy_icon_mode = "check"
        self.render_hero_canvas()
        self.root_window.after(1200, self.revert_copy_path_icon)

    def revert_copy_path_icon(self):
        self.copy_icon_mode = "clipboard"
        self.render_hero_canvas()

    def set_all_download_buttons_enabled(self, is_enabled):
        for button_state in self.download_action_button_states.values():
            button_state["enabled"] = is_enabled
        self.render_hero_canvas()

    def reset_download_button_labels(self):
        for spec in DOWNLOAD_PERIOD_BUTTON_SPECS:
            self.download_action_button_states[spec["period_key"]]["label_text"] = spec["short_label"]

    def handle_download_button_click(self, period_key, event=None):
        if self.is_download_in_progress:
            return
        self.start_download_process(period_key)

    # ------------------------------------------------------------------
    # Orquestacion de la descarga
    # ------------------------------------------------------------------
    def start_download_process(self, period_key):
        self.is_download_in_progress = True
        self.download_action_button_states[period_key]["label_text"] = "Descargando..."
        self.set_all_download_buttons_enabled(False)
        self.transfer_log_text_widget.config(state="normal")
        self.transfer_log_text_widget.delete("1.0", "end")
        self.transfer_log_text_widget.config(state="disabled")
        self.update_progress_bar(0)

        download_thread = threading.Thread(
            target=self.run_download_workflow, args=(period_key,), daemon=True)
        download_thread.start()

    def run_download_workflow(self, period_key):
        remote_file_transfer_service = RemoteFileTransferService()
        local_destination_directory_path = None
        # Cronometro para "tiempo total"/historial: arranca al inicio de todo
        # el flujo (conexion incluida). El tiempo de descarga de cada archivo
        # se mide por separado, con su propio cronometro (mas abajo).
        overall_workflow_start_time = time.time()
        period_short_label = resolve_period_short_label(period_key)
        try:
            self.append_log_entry("Iniciando conexion...", "normal_tag")
            self.update_status_message("Conectando...")

            remote_file_transfer_service.connect_to_remote_server()

            self.update_status_message("Acceso correcto - Conectado")
            self.append_log_entry(
                f"Conectado al Servidor Correspondiente (protocolo: {remote_file_transfer_service.active_protocol_label})",
                "success_tag")

            self.append_log_entry("Verificando carpeta base local...", "normal_tag")
            base_directory_was_created = ensure_base_directory_exists(LOCAL_BASE_DIRECTORY_PATH)
            if base_directory_was_created:
                self.append_log_entry("Carpeta base creada exitosamente", "success_tag")
            else:
                self.append_log_entry("La carpeta base ya existia, no se realizaron cambios", "normal_tag")

            self.append_log_entry("Verificando subcarpeta del cliente...", "normal_tag")
            local_destination_directory_path, subdirectory_was_created = ensure_client_subdirectory_exists(
                LOCAL_BASE_DIRECTORY_PATH, LOCAL_CLIENT_SUBDIRECTORY_NAME)
            if subdirectory_was_created:
                self.append_log_entry("Subcarpeta del cliente creada exitosamente", "success_tag")
            else:
                self.append_log_entry("La subcarpeta del cliente ya existia, no se realizaron cambios", "normal_tag")

            self.append_log_entry("Accediendo a carpeta de descargas", "success_tag")
            all_remote_text_file_names = remote_file_transfer_service.list_remote_text_file_names(
                REMOTE_DIRECTORY_PATH)
            remote_text_file_names = filter_remote_file_names_for_period(all_remote_text_file_names, period_key)

            if not remote_text_file_names:
                elapsed_seconds = time.time() - overall_workflow_start_time
                self.update_status_message("No hay archivos .txt")
                self.update_progress_label_message("Sin archivos")
                self.append_log_entry(
                    f"No se encontraron archivos .txt para el periodo '{period_short_label}'", "error_tag")
                self.append_log_entry(
                    f"Tiempo transcurrido: {format_duration_message(elapsed_seconds)}", "normal_tag")
                remote_file_transfer_service.disconnect_from_remote_server()
                append_monitoring_entry(period_short_label)
                messagebox.showwarning(
                    "Sin archivos para descargar",
                    f"El servidor DCA no tiene archivos .txt para el periodo '{period_short_label}' "
                    "en este momento.\n\n"
                    f"{SUPPORT_CONTACT_MESSAGE}")
                self.finish_download_process()
                return

            reference_today = datetime.date.today()

            remote_files_with_sizes_ascending = sorted(
                (
                    (remote_file_name, remote_file_transfer_service.get_remote_file_size_in_bytes(remote_file_name))
                    for remote_file_name in remote_text_file_names
                ),
                key=lambda file_name_and_size: file_name_and_size[1],
            )

            total_size_in_bytes_of_all_files = sum(
                file_size_in_bytes for _, file_size_in_bytes in remote_files_with_sizes_ascending)
            self.append_log_entry(
                f"Tamano total: {total_size_in_bytes_of_all_files / 1024 / 1024:.2f} MB", "normal_tag")
            self.append_log_entry(
                f"Encontrados {len(remote_files_with_sizes_ascending)} archivos .txt "
                f"(ordenados del que pesa menos al que pesa mas)", "success_tag")

            total_bytes_downloaded_so_far = 0
            total_file_count = len(remote_files_with_sizes_ascending)

            for current_file_index, (remote_file_name, current_file_size_in_bytes) in enumerate(
                    remote_files_with_sizes_ascending):
                self.update_progress_label_message(
                    f"Descargando {current_file_index + 1}/{total_file_count} archivos...")

                if local_file_with_matching_name_exists(local_destination_directory_path, remote_file_name):
                    self.append_log_entry(
                        f"El archivo ya existe localmente y sera sobrescrito: {remote_file_name}", "normal_tag")
                else:
                    self.append_log_entry(
                        f"El archivo no existe localmente y sera creado: {remote_file_name}", "normal_tag")

                self.append_log_entry(
                    f"Descargando: {remote_file_name} ({current_file_size_in_bytes / 1024 / 1024:.2f} MB)",
                    "highlight_tag")

                last_logged_percentage_for_this_file = -PROGRESS_LOG_STEP_PERCENTAGE
                last_reported_overall_percentage = -INTERFACE_UPDATE_STEP_PERCENTAGE

                def handle_chunk_downloaded(bytes_downloaded_for_current_file, current_file_size_in_bytes,
                                             remote_file_name=remote_file_name):
                    nonlocal last_logged_percentage_for_this_file, last_reported_overall_percentage
                    current_file_progress_percentage = (
                        bytes_downloaded_for_current_file / current_file_size_in_bytes) * 100
                    overall_progress_percentage = (
                        (total_bytes_downloaded_so_far + bytes_downloaded_for_current_file)
                        / total_size_in_bytes_of_all_files) * 100

                    is_file_complete = bytes_downloaded_for_current_file >= current_file_size_in_bytes
                    if (overall_progress_percentage - last_reported_overall_percentage
                            < INTERFACE_UPDATE_STEP_PERCENTAGE and not is_file_complete):
                        return
                    last_reported_overall_percentage = overall_progress_percentage

                    if (current_file_progress_percentage - last_logged_percentage_for_this_file
                            >= PROGRESS_LOG_STEP_PERCENTAGE or current_file_progress_percentage >= 100):
                        last_logged_percentage_for_this_file = current_file_progress_percentage
                        self.append_log_entry(
                            f"{remote_file_name}: {current_file_progress_percentage:.1f}% "
                            f"({bytes_downloaded_for_current_file / 1024 / 1024:.2f}/"
                            f"{current_file_size_in_bytes / 1024 / 1024:.2f} MB)", "normal_tag")

                    self.update_progress_bar(overall_progress_percentage)
                    self.root_window.update_idletasks()

                file_download_start_time = time.time()
                downloaded_file_size_in_bytes = remote_file_transfer_service.download_remote_file_with_progress(
                    remote_file_name, current_file_size_in_bytes, local_destination_directory_path,
                    handle_chunk_downloaded)
                file_elapsed_seconds = time.time() - file_download_start_time

                total_bytes_downloaded_so_far += downloaded_file_size_in_bytes

                # Tiempo y velocidad de ESTE archivo (un hecho ya ocurrido), no una
                # prediccion de cuanto falta. Con archivos que van de 0.1 MB a 86 MB,
                # cualquier "ETA" extrapolado de un promedio acumulado queda muy lejos
                # de la realidad para los archivos chicos que tardan solo segundos.
                file_speed_in_mb_per_second = (
                    (downloaded_file_size_in_bytes / 1024 / 1024) / file_elapsed_seconds
                    if file_elapsed_seconds > 0 else 0.0)

                self.append_log_entry(
                    f"Completado: {remote_file_name} en {format_duration_message(file_elapsed_seconds)} "
                    f"({file_speed_in_mb_per_second:.2f} MB/s)", "success_tag")

            remote_file_transfer_service.disconnect_from_remote_server()

            self.append_log_entry("Generando schema.ini con la descripcion de cada archivo...", "normal_tag")
            all_text_file_names_in_destination = list_text_file_names_in_directory(local_destination_directory_path)
            generate_schema_ini_file(local_destination_directory_path, all_text_file_names_in_destination)
            self.append_log_entry("schema.ini generado exitosamente", "success_tag")

            context_note = build_download_context_note(period_key, reference_today)

            instructions_source_file_path = find_first_available_static_file_path(
                AI_INSTRUCTIONS_SEARCH_DIRECTORIES, AI_INSTRUCTIONS_FILE_NAME)
            if instructions_source_file_path is not None:
                with open(instructions_source_file_path, "r", encoding="utf-8", errors="replace") as source_handle:
                    base_instructions_content = source_handle.read()
                instructions_destination_path = os.path.join(
                    local_destination_directory_path, AI_INSTRUCTIONS_FILE_NAME)
                with open(instructions_destination_path, "w", encoding="utf-8") as destination_handle:
                    destination_handle.write(context_note + "\n---\n\n" + base_instructions_content)
                self.append_log_entry(
                    f"{AI_INSTRUCTIONS_FILE_NAME} actualizado con el contexto de esta descarga", "success_tag")
            else:
                self.append_log_entry(f"{AI_INSTRUCTIONS_FILE_NAME} no encontrado, se omitio", "normal_tag")

            for bundled_documentation_file_name in BUNDLED_DOCUMENTATION_FILE_NAMES:
                documentation_file_was_copied = copy_first_available_static_file(
                    AI_INSTRUCTIONS_SEARCH_DIRECTORIES, bundled_documentation_file_name,
                    local_destination_directory_path)
                if documentation_file_was_copied:
                    self.append_log_entry(f"{bundled_documentation_file_name} copiado exitosamente", "success_tag")
                else:
                    self.append_log_entry(
                        f"{bundled_documentation_file_name} no encontrado, se omitio", "normal_tag")

            elapsed_seconds = time.time() - overall_workflow_start_time

            self.update_status_message("Descarga completada")
            self.update_progress_label_message("Transferencia finalizada")
            self.update_destination_path_message(f"Guardado en: {local_destination_directory_path}")
            self.append_log_entry(
                f"Tiempo total: {format_duration_message(elapsed_seconds)}", "success_tag")
            self.append_log_entry("Completado exitosamente", "success_tag")
            self.update_progress_bar(100)

            append_monitoring_entry(period_short_label)

        except Exception as raised_exception:
            elapsed_seconds = time.time() - overall_workflow_start_time
            error_message_text = translate_exception_to_spanish_message(raised_exception)
            self.update_status_message("Error en la transferencia")
            self.append_log_entry(f"Error: {error_message_text}", "error_tag")
            self.append_log_entry(
                f"Tiempo transcurrido antes del error: {format_duration_message(elapsed_seconds)}", "normal_tag")
            append_monitoring_entry(period_short_label)
            messagebox.showerror(
                "Error de Transferencia",
                "No se pudo completar la descarga de datos DCA.\n\n"
                f"Detalle: {error_message_text}\n\n"
                f"{SUPPORT_CONTACT_MESSAGE}")
        finally:
            self.finish_download_process()

    def finish_download_process(self):
        self.is_download_in_progress = False
        self.reset_download_button_labels()
        self.set_all_download_buttons_enabled(True)
