import datetime
import os
import threading
import time
import tkinter
from tkinter import font as tkinter_font

from color_palette import COLOR_PALETTE, LOG_TITLE_BAR_INDICATOR_COLORS
from canvas_drawing_helpers import draw_rounded_rectangle
from configuration_settings import (
    REMOTE_DIRECTORY_PATH,
    LOCAL_BASE_DIRECTORY_PATH,
    LOCAL_CLIENT_SUBDIRECTORY_NAME,
    PROGRESS_LOG_STEP_PERCENTAGE,
    INTERFACE_UPDATE_STEP_PERCENTAGE,
)
from filesystem_helpers import (
    ensure_base_directory_exists,
    ensure_client_subdirectory_exists,
    local_file_with_matching_name_exists,
)
from secure_file_transfer_service import SecureFileTransferService


class DCAExtractorApplicationWindow:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Breinit DCA Extractor")
        self.root_window.geometry("640x760")
        self.root_window.resizable(False, False)
        self.root_window.configure(bg=COLOR_PALETTE["background_color"])

        self.is_download_in_progress = False
        self.current_progress_percentage = 0.0

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

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def build_header_section(self):
        header_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["primary_color"], height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        header_content_frame = tkinter.Frame(header_frame, bg=COLOR_PALETTE["primary_color"])
        header_content_frame.pack(expand=True)

        tkinter.Label(header_content_frame, text="🗄", font=("Segoe UI Emoji", 16),
                      bg=COLOR_PALETTE["primary_color"], fg=COLOR_PALETTE["on_primary_color"]).pack(
            side="left", padx=(0, 8))
        tkinter.Label(header_content_frame, text="Breinit DCA Extractor", font=self.application_fonts["title_font"],
                      bg=COLOR_PALETTE["primary_color"], fg=COLOR_PALETTE["on_primary_color"]).pack(side="left")

    def build_hero_status_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="x", padx=20, pady=(20, 12))

        self.hero_canvas = tkinter.Canvas(wrapper_frame, width=600, height=300,
                                           bg=COLOR_PALETTE["background_color"], highlightthickness=0)
        self.hero_canvas.pack()

        draw_rounded_rectangle(self.hero_canvas, 0, 0, 600, 300, corner_radius=16,
                                fill=COLOR_PALETTE["surface_lowest_color"],
                                outline=COLOR_PALETTE["outline_variant_color"])

        draw_rounded_rectangle(self.hero_canvas, 230, 20, 370, 42, corner_radius=10,
                                fill=COLOR_PALETTE["primary_fixed_color"], outline="")
        self.hero_canvas.create_text(300, 31, text="TRANSFERENCIA SEGURA", font=self.application_fonts["label_font"],
                                      fill=COLOR_PALETTE["primary_container_color"])

        self.hero_canvas.create_text(300, 78, text="Descarga de archivos SFTP",
                                      font=self.application_fonts["display_font"], fill=COLOR_PALETTE["primary_color"])
        self.status_text_item_id = self.hero_canvas.create_text(
            300, 108, text="Listo para iniciar transferencia segura",
            font=self.application_fonts["body_font"], fill=COLOR_PALETTE["on_surface_variant_color"])

        self.progress_label_item_id = self.hero_canvas.create_text(
            30, 160, text="En espera", font=self.application_fonts["title_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="w")
        self.progress_percentage_item_id = self.hero_canvas.create_text(
            570, 160, text="0%", font=self.application_fonts["code_bold_font"],
            fill=COLOR_PALETTE["primary_color"], anchor="e")

        self.progress_bar_left_x, self.progress_bar_top_y = 30, 178
        self.progress_bar_right_x, self.progress_bar_bottom_y = 570, 190
        draw_rounded_rectangle(self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
                                self.progress_bar_right_x, self.progress_bar_bottom_y, corner_radius=6,
                                fill=COLOR_PALETTE["surface_container_color"], outline="")
        self.progress_bar_fill_item_id = draw_rounded_rectangle(
            self.hero_canvas, self.progress_bar_left_x, self.progress_bar_top_y,
            self.progress_bar_left_x, self.progress_bar_bottom_y, corner_radius=6,
            fill=COLOR_PALETTE["primary_color"], outline="")

        self.download_button_left_x, self.download_button_top_y = 190, 220
        self.download_button_right_x, self.download_button_bottom_y = 410, 268
        self.download_button_background_item_id = draw_rounded_rectangle(
            self.hero_canvas, self.download_button_left_x, self.download_button_top_y,
            self.download_button_right_x, self.download_button_bottom_y, corner_radius=14,
            fill=COLOR_PALETTE["primary_color"], outline="")
        self.download_button_text_item_id = self.hero_canvas.create_text(
            300, 244, text="⬇  Descargar Archivos", font=self.application_fonts["title_font"],
            fill=COLOR_PALETTE["on_primary_color"])

        for clickable_item_id in (self.download_button_background_item_id, self.download_button_text_item_id):
            self.hero_canvas.tag_bind(clickable_item_id, "<Button-1>", self.handle_download_button_click)
            self.hero_canvas.tag_bind(clickable_item_id, "<Enter>",
                                       lambda event: self.hero_canvas.config(cursor="hand2"))
            self.hero_canvas.tag_bind(clickable_item_id, "<Leave>", lambda event: self.hero_canvas.config(cursor=""))

    def build_transfer_log_card(self):
        wrapper_frame = tkinter.Frame(self.root_window, bg=COLOR_PALETTE["background_color"])
        wrapper_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        label_row_frame = tkinter.Frame(wrapper_frame, bg=COLOR_PALETTE["background_color"])
        label_row_frame.pack(fill="x", pady=(0, 6))
        tkinter.Label(label_row_frame, text="⌨  REGISTRO DE TRANSFERENCIA", font=self.application_fonts["label_font"],
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
        self.hero_canvas.itemconfig(self.status_text_item_id, text=status_message)

    def update_progress_label_message(self, progress_label_message):
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

    def update_download_button_state(self, is_enabled, button_text=None):
        button_fill_color = COLOR_PALETTE["primary_color"] if is_enabled else COLOR_PALETTE["outline_variant_color"]
        self.hero_canvas.itemconfig(self.download_button_background_item_id, fill=button_fill_color)
        if button_text is not None:
            self.hero_canvas.itemconfig(self.download_button_text_item_id, text=button_text)

    def handle_download_button_click(self, event=None):
        if self.is_download_in_progress:
            return
        self.start_download_process()

    # ------------------------------------------------------------------
    # Orquestacion de la descarga
    # ------------------------------------------------------------------
    def start_download_process(self):
        self.is_download_in_progress = True
        self.update_download_button_state(False, "⬇  Descargando...")
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

            total_size_in_bytes_of_all_files = sum(
                secure_file_transfer_service.get_remote_file_size_in_bytes(remote_file_name)
                for remote_file_name in remote_text_file_names
            )
            self.append_log_entry(
                f"Tamano total: {total_size_in_bytes_of_all_files / 1024 / 1024:.2f} MB", "normal_tag")
            self.append_log_entry(
                f"Encontrados {len(remote_text_file_names)} archivos .txt", "success_tag")

            workflow_start_time = time.time()
            total_bytes_downloaded_so_far = 0

            for current_file_index, remote_file_name in enumerate(remote_text_file_names):
                self.update_progress_label_message(
                    f"Descargando {current_file_index + 1}/{len(remote_text_file_names)} archivos...")

                if local_file_with_matching_name_exists(local_destination_directory_path, remote_file_name):
                    self.append_log_entry(
                        f"El archivo ya existe localmente y sera sobrescrito: {remote_file_name}", "normal_tag")
                else:
                    self.append_log_entry(
                        f"El archivo no existe localmente y sera creado: {remote_file_name}", "normal_tag")

                current_file_size_in_bytes = secure_file_transfer_service.get_remote_file_size_in_bytes(
                    remote_file_name)
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
                    remote_file_name, local_destination_directory_path, handle_chunk_downloaded)

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

            self.update_status_message("Descarga completada")
            self.update_progress_label_message("Transferencia finalizada")
            self.append_log_entry("Completado exitosamente", "success_tag")
            self.update_progress_bar(100)

        except Exception as raised_exception:
            self.update_status_message("Error en la transferencia")
            self.append_log_entry(f"Error: {str(raised_exception)}", "error_tag")
        finally:
            self.finish_download_process()

    def finish_download_process(self):
        self.is_download_in_progress = False
        self.update_download_button_state(True, "⬇  Descargar Archivos")
