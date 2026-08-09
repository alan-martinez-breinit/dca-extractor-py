import datetime
import os
import threading
import time
import tkinter
from tkinter import font as tkinter_font

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
    AI_INSTRUCTIONS_SOURCE_FILE_NAME,
    AI_INSTRUCTIONS_SEARCH_DIRECTORIES,
)
from src.filesystem_helpers import (
    ensure_base_directory_exists,
    ensure_client_subdirectory_exists,
    local_file_with_matching_name_exists,
    copy_first_available_static_file,
)
from src.secure_file_transfer_service import SecureFileTransferService
from src.schema_ini_generator import generate_schema_ini_file


DESIGNED_WINDOW_WIDTH_PIXELS = 640
DESIGNED_WINDOW_HEIGHT_PIXELS = 790
SCREEN_TASKBAR_RESERVE_PIXELS = 60
MINIMUM_WINDOW_HEIGHT_PIXELS = 500

HERO_CANVAS_HEIGHT_PIXELS = 330
HERO_CANVAS_MARGIN_PIXELS = 30
HERO_CANVAS_MINIMUM_WIDTH_PIXELS = 360
ICON_GLYPH_SIZE_PIXELS = 16


class DCAExtractorApplicationWindow:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("FTP DCA AUTOPOLIS")
        self.fit_window_to_device_screen()
        self.root_window.configure(bg=COLOR_PALETTE["background_color"])

        self.is_download_in_progress = False
        self.current_progress_percentage = 0.0
        self.status_message = "Listo para iniciar transferencia segura"
        self.progress_label_message = "En espera"
        self.destination_path_message = None
        self.download_button_enabled = True
        self.download_button_label_text = "Descargar Archivos"
        self.copy_icon_mode = "clipboard"
        self.last_rendered_hero_canvas_width = None

        self.application_fonts = {
            "display_font": tkinter_font.Font(family="Segoe UI Semibold", size=22, weight="bold"),
            "title_font": tkinter_font.Font(family="Segoe UI Semibold", size=13, weight="bold"),
            "body_font": tkinter_font.Font(family="Segoe UI", size=10),
            "label_font": tkinter_font.Font(family="Segoe UI Semibold", size=8, weight="bold"),
            "code_font": tkinter_font.Font(family="Consolas", size=9),
            "code_bold_font": tkinter_font.Font(family="Consolas", size=9, weight="bold"),
        }

        self.build_header_section()
        self.build_hero_status_card()
        self.build_transfer_log_card()

    def fit_window_to_device_screen(self):
        screen_width_pixels = self.root_window.winfo_screenwidth()
        screen_height_pixels = self.root_window.winfo_screenheight()

        window_width_pixels = min(DESIGNED_WINDOW_WIDTH_PIXELS, screen_width_pixels)
        window_height_pixels = min(
            DESIGNED_WINDOW_HEIGHT_PIXELS, screen_height_pixels - SCREEN_TASKBAR_RESERVE_PIXELS)
        self.window_width_pixels = window_width_pixels

        window_position_x = (screen_width_pixels - window_width_pixels) // 2
        window_position_y = (screen_height_pixels - window_height_pixels) // 2

        self.root_window.geometry(
            f"{window_width_pixels}x{window_height_pixels}+{window_position_x}+{window_position_y}")
        self.root_window.minsize(window_width_pixels, min(window_height_pixels, MINIMUM_WINDOW_HEIGHT_PIXELS))
        self.root_window.resizable(True, True)

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def build_header_section(self):
        header_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["primary_color"], height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        header_content_frame = tkinter.Frame(header_frame, bg=COLOR_PALETTE["primary_color"])
        header_content_frame.pack(expand=True)

        header_icon_canvas = tkinter.Canvas(header_content_frame, width=ICON_GLYPH_SIZE_PIXELS,
                                             height=ICON_GLYPH_SIZE_PIXELS, bg=COLOR_PALETTE["primary_color"],
                                             highlightthickness=0)
        header_icon_canvas.pack(side="left", padx=(0, 8))
        draw_cabinet_glyph(header_icon_canvas, ICON_GLYPH_SIZE_PIXELS / 2, ICON_GLYPH_SIZE_PIXELS / 2,
                            ICON_GLYPH_SIZE_PIXELS, COLOR_PALETTE["on_primary_color"])

        tkinter.Label(header_content_frame, text="FTP DCA AUTOPOLIS", font=self.application_fonts["title_font"],
                      bg=COLOR_PALETTE["primary_color"], fg=COLOR_PALETTE["on_primary_color"]).pack(side="left")

    def build_hero_status_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="x", padx=20, pady=(20, 12))

        self.destination_directory_path_for_clipboard = os.path.join(
            LOCAL_BASE_DIRECTORY_PATH, LOCAL_CLIENT_SUBDIRECTORY_NAME)
        self.destination_path_message = f"Se guardara en: {self.destination_directory_path_for_clipboard}"

        self.hero_canvas = tkinter.Canvas(wrapper_frame, height=HERO_CANVAS_HEIGHT_PIXELS,
                                           bg=COLOR_PALETTE["background_color"], highlightthickness=0)
        self.hero_canvas.pack(fill="x")

        self.hero_canvas.tag_bind("download_button_hitbox", "<Button-1>", self.handle_download_button_click)
        self.hero_canvas.tag_bind("download_button_hitbox", "<Enter>",
                                   lambda event: self.hero_canvas.config(cursor="hand2"))
        self.hero_canvas.tag_bind("download_button_hitbox", "<Leave>",
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

    def render_hero_canvas(self, canvas_width=None):
        if canvas_width is None:
            canvas_width = self.hero_canvas.winfo_width()
        canvas_width = max(canvas_width, HERO_CANVAS_MINIMUM_WIDTH_PIXELS)

        self.hero_canvas.delete("all")

        left_x = HERO_CANVAS_MARGIN_PIXELS
        right_x = canvas_width - HERO_CANVAS_MARGIN_PIXELS
        center_x = canvas_width / 2

        draw_rounded_rectangle(self.hero_canvas, 0, 0, canvas_width, HERO_CANVAS_HEIGHT_PIXELS, corner_radius=16,
                                fill=COLOR_PALETTE["surface_lowest_color"],
                                outline=COLOR_PALETTE["outline_variant_color"])

        draw_rounded_rectangle(self.hero_canvas, center_x - 70, 20, center_x + 70, 42, corner_radius=10,
                                fill=COLOR_PALETTE["primary_fixed_color"], outline="")
        self.hero_canvas.create_text(center_x, 31, text="TRANSFERENCIA SEGURA",
                                      font=self.application_fonts["label_font"],
                                      fill=COLOR_PALETTE["primary_container_color"])

        self.hero_canvas.create_text(center_x, 78, text="Descarga de archivos SFTP",
                                      font=self.application_fonts["display_font"], fill=COLOR_PALETTE["primary_color"])
        self.status_text_item_id = self.hero_canvas.create_text(
            center_x, 108, text=self.status_message,
            font=self.application_fonts["body_font"], fill=COLOR_PALETTE["on_surface_variant_color"])

        self.progress_label_item_id = self.hero_canvas.create_text(
            left_x, 160, text=self.progress_label_message, font=self.application_fonts["title_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="w")
        self.progress_percentage_item_id = self.hero_canvas.create_text(
            right_x, 160, text=f"{int(self.current_progress_percentage)}%",
            font=self.application_fonts["code_bold_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="e")

        self.progress_bar_left_x, self.progress_bar_top_y = left_x, 178
        self.progress_bar_right_x, self.progress_bar_bottom_y = right_x, 190
        draw_rounded_rectangle(self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
                                self.progress_bar_right_x, self.progress_bar_bottom_y, corner_radius=6,
                                fill=COLOR_PALETTE["surface_container_color"], outline="")
        progress_bar_fill_right_x = self.progress_bar_left_x + (
            self.progress_bar_right_x - self.progress_bar_left_x) * (self.current_progress_percentage / 100.0)
        self.progress_bar_fill_item_id = draw_rounded_rectangle(
            self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
            max(progress_bar_fill_right_x, self.progress_bar_left_x), self.progress_bar_bottom_y, corner_radius=6,
            fill=COLOR_PALETTE["primary_color"], outline="")

        button_half_width = 110
        self.download_button_left_x, self.download_button_top_y = center_x - button_half_width, 220
        self.download_button_right_x, self.download_button_bottom_y = center_x + button_half_width, 268
        button_center_y = (self.download_button_top_y + self.download_button_bottom_y) / 2
        button_fill_color = (COLOR_PALETTE["primary_color"] if self.download_button_enabled
                              else COLOR_PALETTE["outline_variant_color"])
        self.download_button_background_item_id = draw_rounded_rectangle(
            self.hero_canvas, self.download_button_left_x, self.download_button_top_y,
            self.download_button_right_x, self.download_button_bottom_y, corner_radius=14,
            fill=button_fill_color, outline="", tags=("download_button_hitbox",))

        label_text_width = self.application_fonts["title_font"].measure(self.download_button_label_text)
        icon_gap = 8
        group_width = ICON_GLYPH_SIZE_PIXELS + icon_gap + label_text_width
        group_left_x = center_x - group_width / 2
        icon_center_x = group_left_x + ICON_GLYPH_SIZE_PIXELS / 2
        label_left_x = group_left_x + ICON_GLYPH_SIZE_PIXELS + icon_gap

        draw_download_glyph(self.hero_canvas, icon_center_x, button_center_y, ICON_GLYPH_SIZE_PIXELS,
                             COLOR_PALETTE["on_primary_color"], tags=("download_button_hitbox",))
        self.download_button_text_item_id = self.hero_canvas.create_text(
            label_left_x, button_center_y, text=self.download_button_label_text, anchor="w",
            font=self.application_fonts["title_font"], fill=COLOR_PALETTE["on_primary_color"],
            tags=("download_button_hitbox",))

        destination_path_row_y = 300
        self.destination_path_text_item_id = self.hero_canvas.create_text(
            left_x, destination_path_row_y, text=self.destination_path_message,
            font=self.application_fonts["body_font"], fill=COLOR_PALETTE["on_surface_variant_color"], anchor="w")

        if self.copy_icon_mode == "check":
            draw_check_glyph(self.hero_canvas, right_x - ICON_GLYPH_SIZE_PIXELS / 2, destination_path_row_y,
                              ICON_GLYPH_SIZE_PIXELS, COLOR_PALETTE["primary_color"], tags=("copy_path_hitbox",))
        else:
            draw_clipboard_glyph(self.hero_canvas, right_x - ICON_GLYPH_SIZE_PIXELS / 2, destination_path_row_y,
                                  ICON_GLYPH_SIZE_PIXELS, COLOR_PALETTE["on_surface_variant_color"],
                                  tags=("copy_path_hitbox",))
        self.hero_canvas.create_rectangle(
            right_x - ICON_GLYPH_SIZE_PIXELS, destination_path_row_y - ICON_GLYPH_SIZE_PIXELS / 2,
            right_x + ICON_GLYPH_SIZE_PIXELS / 2, destination_path_row_y + ICON_GLYPH_SIZE_PIXELS / 2,
            fill="", outline="", tags=("copy_path_hitbox",))

    def build_transfer_log_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        label_row_frame = tkinter.Frame(wrapper_frame, bg=COLOR_PALETTE["background_color"])
        label_row_frame.pack(fill="x", pady=(0, 6))

        log_icon_size = 12
        log_icon_canvas = tkinter.Canvas(label_row_frame, width=log_icon_size, height=log_icon_size,
                                          bg=COLOR_PALETTE["background_color"], highlightthickness=0)
        log_icon_canvas.pack(side="left", padx=(0, 6))
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
                                             height=32)
        log_title_bar_frame.pack(fill="x")
        log_title_bar_frame.pack_propagate(False)

        title_bar_indicators_frame = tkinter.Frame(log_title_bar_frame, bg=COLOR_PALETTE["surface_container_high_color"])
        title_bar_indicators_frame.pack(side="left", padx=12)
        for indicator_color in LOG_TITLE_BAR_INDICATOR_COLORS:
            indicator_canvas = tkinter.Canvas(title_bar_indicators_frame, width=10, height=10,
                                               bg=COLOR_PALETTE["surface_container_high_color"],
                                               highlightthickness=0)
            indicator_canvas.create_oval(1, 1, 9, 9, fill=indicator_color, outline="")
            indicator_canvas.pack(side="left", padx=2)

        log_content_frame = tkinter.Frame(log_card_frame, bg=COLOR_PALETTE["surface_lowest_color"])
        log_content_frame.pack(fill="both", expand=True)

        log_scrollbar = tkinter.Scrollbar(log_content_frame)
        log_scrollbar.pack(side="right", fill="y")

        self.transfer_log_text_widget = tkinter.Text(
            log_content_frame, font=self.application_fonts["code_font"], bg=COLOR_PALETTE["surface_lowest_color"],
            fg=COLOR_PALETTE["on_surface_variant_color"], relief="flat", wrap="word", state="disabled",
            yscrollcommand=log_scrollbar.set, padx=14, pady=10)
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

    def update_download_button_state(self, is_enabled, button_text=None):
        self.download_button_enabled = is_enabled
        if button_text is not None:
            self.download_button_label_text = button_text
        self.render_hero_canvas()

    def handle_download_button_click(self, event=None):
        if self.is_download_in_progress:
            return
        self.start_download_process()

    # ------------------------------------------------------------------
    # Orquestacion de la descarga
    # ------------------------------------------------------------------
    def start_download_process(self):
        self.is_download_in_progress = True
        self.update_download_button_state(False, "Descargando...")
        self.transfer_log_text_widget.config(state="normal")
        self.transfer_log_text_widget.delete("1.0", "end")
        self.transfer_log_text_widget.config(state="disabled")
        self.update_progress_bar(0)

        download_thread = threading.Thread(target=self.run_download_workflow, daemon=True)
        download_thread.start()

    def run_download_workflow(self):
        secure_file_transfer_service = SecureFileTransferService()
        try:
            self.append_log_entry("Iniciando conexion...", "normal_tag")
            self.update_status_message("Conectando...")

            secure_file_transfer_service.connect_to_remote_server()

            self.update_status_message("Acceso correcto - Conectado")
            self.append_log_entry("Conectado al Servidor Correspondiente", "success_tag")

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
            remote_text_file_names = secure_file_transfer_service.list_remote_text_file_names(REMOTE_DIRECTORY_PATH)

            if not remote_text_file_names:
                self.update_status_message("No hay archivos .txt")
                self.update_progress_label_message("Sin archivos")
                self.append_log_entry("No se encontraron archivos .txt", "error_tag")
                secure_file_transfer_service.disconnect_from_remote_server()
                self.finish_download_process()
                return

            remote_files_with_sizes_ascending = sorted(
                (
                    (remote_file_name, secure_file_transfer_service.get_remote_file_size_in_bytes(remote_file_name))
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

            workflow_start_time = time.time()
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

                downloaded_file_size_in_bytes = secure_file_transfer_service.download_remote_file_with_progress(
                    remote_file_name, current_file_size_in_bytes, local_destination_directory_path,
                    handle_chunk_downloaded)

                total_bytes_downloaded_so_far += downloaded_file_size_in_bytes
                elapsed_time_in_seconds = time.time() - workflow_start_time
                download_speed_in_bytes_per_second = (
                    total_bytes_downloaded_so_far / elapsed_time_in_seconds if elapsed_time_in_seconds > 0 else 0)
                remaining_bytes_to_download = total_size_in_bytes_of_all_files - total_bytes_downloaded_so_far
                estimated_time_remaining_in_seconds = (
                    remaining_bytes_to_download / download_speed_in_bytes_per_second
                    if download_speed_in_bytes_per_second > 0 else 0)

                self.append_log_entry(f"Completado: {remote_file_name}", "success_tag")
                self.append_log_entry(
                    f"Velocidad: {download_speed_in_bytes_per_second / 1024 / 1024:.2f} MB/s | "
                    f"ETA: {int(estimated_time_remaining_in_seconds)} seg", "normal_tag")

            secure_file_transfer_service.disconnect_from_remote_server()

            self.append_log_entry("Generando schema.ini con la descripcion de cada archivo...", "normal_tag")
            downloaded_file_names = [file_name for file_name, _ in remote_files_with_sizes_ascending]
            generate_schema_ini_file(local_destination_directory_path, downloaded_file_names)
            self.append_log_entry("schema.ini generado exitosamente", "success_tag")

            ai_instructions_file_was_copied = copy_first_available_static_file(
                AI_INSTRUCTIONS_SEARCH_DIRECTORIES, AI_INSTRUCTIONS_SOURCE_FILE_NAME,
                local_destination_directory_path)
            if ai_instructions_file_was_copied:
                self.append_log_entry(f"{AI_INSTRUCTIONS_SOURCE_FILE_NAME} copiado exitosamente", "success_tag")
            else:
                self.append_log_entry(
                    f"{AI_INSTRUCTIONS_SOURCE_FILE_NAME} no encontrado, se omitio",
                    "normal_tag")

            self.update_status_message("Descarga completada")
            self.update_progress_label_message("Transferencia finalizada")
            self.update_destination_path_message(f"Guardado en: {local_destination_directory_path}")
            self.append_log_entry("Completado exitosamente", "success_tag")
            self.update_progress_bar(100)

        except Exception as raised_exception:
            self.update_status_message("Error en la transferencia")
            self.append_log_entry(f"Error: {str(raised_exception)}", "error_tag")
        finally:
            self.finish_download_process()

    def finish_download_process(self):
        self.is_download_in_progress = False
        self.update_download_button_state(True, "Descargar Archivos")
