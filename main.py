import tkinter as tk
from tkinter import font as tkfont
import paramiko
import os
from pathlib import Path
import threading
import time
import datetime

# ---------------------------------------------------------------------------
# Paleta (tomada del theme Material entregado)
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#001e40",
    "primary_container": "#003366",
    "on_primary": "#ffffff",
    "secondary": "#505f76",
    "background": "#f7f9fb",
    "surface": "#f7f9fb",
    "surface_lowest": "#ffffff",
    "surface_container": "#eceef0",
    "surface_container_high": "#e6e8ea",
    "outline_variant": "#c3c6d1",
    "on_surface": "#191c1e",
    "on_surface_variant": "#43474f",
    "error": "#ba1a1a",
    "primary_fixed": "#d5e3ff",
}


def round_rectangle(canvas, x1, y1, x2, y2, radius=18, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class DCAExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Breinit DCA Extractor")
        self.root.geometry("640x760")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["background"])

        # Config
        self.SFTP_HOST = "169.62.217.83"
        self.SFTP_PORT = 22
        self.SFTP_USER = "ftpdca"
        self.SFTP_PASS = "ftpDC@2023"
        self.REMOTE_PATH = "/ALANPRUEBAS/FTPIA/Autopolis"
        self.LOCAL_PATH = r"C:\Users\Breinit\Documents\DCA\autopolis"

        self.is_downloading = False
        self.progress_pct = 0.0

        self.fonts = {
            "display": tkfont.Font(family="Segoe UI Semibold", size=22, weight="bold"),
            "title": tkfont.Font(family="Segoe UI Semibold", size=13, weight="bold"),
            "body": tkfont.Font(family="Segoe UI", size=10),
            "label": tkfont.Font(family="Segoe UI Semibold", size=8, weight="bold"),
            "code": tkfont.Font(family="Consolas", size=9),
            "code_bold": tkfont.Font(family="Consolas", size=9, weight="bold"),
        }

        self.build_header()
        self.build_hero_card()
        self.build_log_card()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def build_header(self):
        header = tk.Frame(self.root, bg=COLORS["primary"], height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=COLORS["primary"])
        inner.pack(expand=True)

        tk.Label(inner, text="🗄", font=("Segoe UI Emoji", 16), bg=COLORS["primary"],
                  fg=COLORS["on_primary"]).pack(side="left", padx=(0, 8))
        tk.Label(inner, text="Breinit DCA Extractor", font=self.fonts["title"],
                  bg=COLORS["primary"], fg=COLORS["on_primary"]).pack(side="left")

    def build_hero_card(self):
        wrapper = tk.Frame(self.root, bg=COLORS["background"])
        wrapper.pack(fill="x", padx=20, pady=(20, 12))

        self.hero_canvas = tk.Canvas(wrapper, width=600, height=300, bg=COLORS["background"],
                                      highlightthickness=0)
        self.hero_canvas.pack()

        round_rectangle(self.hero_canvas, 0, 0, 600, 300, radius=16,
                         fill=COLORS["surface_lowest"], outline=COLORS["outline_variant"])

        # Badge
        badge_id = round_rectangle(self.hero_canvas, 230, 20, 370, 42, radius=10,
                                    fill=COLORS["primary_fixed"], outline="")
        self.hero_canvas.create_text(300, 31, text="TRANSFERENCIA SEGURA", font=self.fonts["label"],
                                      fill=COLORS["primary_container"])

        # Headline + subtitle
        self.hero_canvas.create_text(300, 78, text="Descarga de archivos SFTP",
                                      font=self.fonts["display"], fill=COLORS["primary"])
        self.status_text_id = self.hero_canvas.create_text(
            300, 108, text="Listo para iniciar transferencia segura",
            font=self.fonts["body"], fill=COLORS["on_surface_variant"])

        # Progress row labels
        self.progress_label_id = self.hero_canvas.create_text(
            30, 160, text="En espera", font=self.fonts["title"], fill=COLORS["primary"], anchor="w")
        self.progress_pct_id = self.hero_canvas.create_text(
            570, 160, text="0%", font=self.fonts["code_bold"], fill=COLORS["primary"], anchor="e")

        # Progress bar track + fill
        self.bar_x1, self.bar_y1, self.bar_x2, self.bar_y2 = 30, 178, 570, 190
        round_rectangle(self.hero_canvas, self.bar_x1, self.bar_y1, self.bar_x2, self.bar_y2,
                         radius=6, fill=COLORS["surface_container"], outline="")
        self.progress_fill_id = round_rectangle(
            self.hero_canvas, self.bar_x1, self.bar_y1, self.bar_x1, self.bar_y2,
            radius=6, fill=COLORS["primary"], outline="")

        # Action button
        self.btn_x1, self.btn_y1, self.btn_x2, self.btn_y2 = 190, 220, 410, 268
        self.button_bg = round_rectangle(
            self.hero_canvas, self.btn_x1, self.btn_y1, self.btn_x2, self.btn_y2,
            radius=14, fill=COLORS["primary"], outline="")
        self.button_text = self.hero_canvas.create_text(
            300, 244, text="⬇  Descargar Archivos", font=self.fonts["title"], fill=COLORS["on_primary"])

        for item in (self.button_bg, self.button_text):
            self.hero_canvas.tag_bind(item, "<Button-1>", self.on_button_click)
            self.hero_canvas.tag_bind(item, "<Enter>", lambda e: self.hero_canvas.config(cursor="hand2"))
            self.hero_canvas.tag_bind(item, "<Leave>", lambda e: self.hero_canvas.config(cursor=""))

    def build_log_card(self):
        wrapper = tk.Frame(self.root, bg=COLORS["background"])
        wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        label_row = tk.Frame(wrapper, bg=COLORS["background"])
        label_row.pack(fill="x", pady=(0, 6))
        tk.Label(label_row, text="⌨  REGISTRO DE TRANSFERENCIA", font=self.fonts["label"],
                  bg=COLORS["background"], fg=COLORS["on_surface_variant"]).pack(side="left")

        card = tk.Frame(wrapper, bg=COLORS["surface_lowest"], highlightbackground=COLORS["outline_variant"],
                         highlightthickness=1)
        card.pack(fill="both", expand=True)

        title_bar = tk.Frame(card, bg=COLORS["surface_container_high"], height=32)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        dots = tk.Frame(title_bar, bg=COLORS["surface_container_high"])
        dots.pack(side="left", padx=12)
        for color in ("#f2b8b5", "#d3e4fe", "#b7c8e1"):
            dot = tk.Canvas(dots, width=10, height=10, bg=COLORS["surface_container_high"], highlightthickness=0)
            dot.create_oval(1, 1, 9, 9, fill=color, outline="")
            dot.pack(side="left", padx=2)

        self.copy_btn = tk.Label(title_bar, text="Copiar", font=self.fonts["body"],
                                  bg=COLORS["surface_container_high"], fg=COLORS["on_surface_variant"],
                                  cursor="hand2")
        self.copy_btn.pack(side="right", padx=12)
        self.copy_btn.bind("<Button-1>", self.copy_log)

        log_frame = tk.Frame(card, bg=COLORS["surface_lowest"])
        log_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(log_frame, font=self.fonts["code"], bg=COLORS["surface_lowest"],
                                 fg=COLORS["on_surface_variant"], relief="flat", wrap="word",
                                 state="disabled", yscrollcommand=scrollbar.set, padx=14, pady=10)
        self.log_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

        self.log_text.tag_config("timestamp", foreground=COLORS["primary"], font=self.fonts["code_bold"])
        self.log_text.tag_config("normal", foreground=COLORS["secondary"])
        self.log_text.tag_config("highlight", foreground=COLORS["primary"], font=self.fonts["code_bold"],
                                  background=COLORS["primary_fixed"])
        self.log_text.tag_config("error", foreground=COLORS["error"], font=self.fonts["code_bold"])
        self.log_text.tag_config("success", foreground=COLORS["primary"], font=self.fonts["code_bold"])

    # ------------------------------------------------------------------
    # Helpers de UI
    # ------------------------------------------------------------------
    def log(self, message, kind="normal"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{timestamp}]  ", "timestamp")
        self.log_text.insert("end", f"{message}\n", kind)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def copy_log(self, event=None):
        content = self.log_text.get("1.0", "end")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.log("Registro copiado al portapapeles", "highlight")

    def update_status(self, message):
        self.hero_canvas.itemconfig(self.status_text_id, text=message)

    def update_progress_label(self, message):
        self.hero_canvas.itemconfig(self.progress_label_id, text=message)

    def set_progress(self, pct):
        self.progress_pct = max(0.0, min(100.0, pct))
        width = self.bar_x1 + (self.bar_x2 - self.bar_x1) * (self.progress_pct / 100.0)
        self.hero_canvas.delete(self.progress_fill_id)
        if width - self.bar_x1 > 2:
            self.progress_fill_id = round_rectangle(
                self.hero_canvas, self.bar_x1, self.bar_y1, width, self.bar_y2,
                radius=6, fill=COLORS["primary"], outline="")
        else:
            self.progress_fill_id = round_rectangle(
                self.hero_canvas, self.bar_x1, self.bar_y1, self.bar_x1, self.bar_y2,
                radius=6, fill=COLORS["primary"], outline="")
        self.hero_canvas.itemconfig(self.progress_pct_id, text=f"{int(self.progress_pct)}%")

    def set_button_state(self, enabled, text=None):
        color = COLORS["primary"] if enabled else COLORS["outline_variant"]
        self.hero_canvas.itemconfig(self.button_bg, fill=color)
        if text:
            self.hero_canvas.itemconfig(self.button_text, text=text)

    def on_button_click(self, event=None):
        if self.is_downloading:
            return
        self.start_download()

    # ------------------------------------------------------------------
    # Lógica de descarga
    # ------------------------------------------------------------------
    def start_download(self):
        self.is_downloading = True
        self.set_button_state(False, "⬇  Descargando...")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.set_progress(0)

        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

    def download(self):
        try:
            self.log("Iniciando conexión...", "normal")
            self.update_status("Conectando...")

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.SFTP_HOST, self.SFTP_PORT, self.SFTP_USER, self.SFTP_PASS)

            self.update_status("Acceso correcto - Conectado")
            self.log("Conectado al Servidor Correspondiente", "success")

            Path(self.LOCAL_PATH).mkdir(parents=True, exist_ok=True)

            sftp = ssh.open_sftp()
            sftp.chdir(self.REMOTE_PATH)
            self.log("Accediendo a carpeta de descargas", "success")

            files = sftp.listdir()
            jsonl_files = [f for f in files if f.endswith(".jsonl")]

            if not jsonl_files:
                self.update_status("No hay archivos .jsonl")
                self.update_progress_label("Sin archivos")
                self.log("No se encontraron archivos .jsonl", "error")
                sftp.close()
                ssh.close()
                self.finish_download()
                return

            total_size = sum(sftp.stat(f).st_size for f in jsonl_files)
            self.log(f"Tamaño total: {total_size / 1024 / 1024:.2f} MB", "normal")
            self.log(f"Encontrados {len(jsonl_files)} archivos .jsonl", "success")

            start_time = time.time()
            downloaded_size = 0

            for i, filename in enumerate(jsonl_files):
                local_file = os.path.join(self.LOCAL_PATH, filename)
                file_size = sftp.stat(filename).st_size

                self.update_progress_label(f"Descargando {i + 1}/{len(jsonl_files)} archivos...")
                self.log(f"Descargando: {filename} ({file_size / 1024 / 1024:.2f} MB)", "highlight")

                bytes_read = 0
                last_logged_pct = -5

                with open(local_file, "wb") as out_f:
                    with sftp.file(filename, "r") as remote_file:
                        while True:
                            chunk = remote_file.read(1024 * 256)  # 256 KB
                            if not chunk:
                                break
                            out_f.write(chunk)
                            bytes_read += len(chunk)

                            file_progress = (bytes_read / file_size) * 100
                            if file_progress - last_logged_pct >= 5 or file_progress >= 100:
                                last_logged_pct = file_progress
                                self.log(
                                    f"{filename}: {file_progress:.1f}% "
                                    f"({bytes_read / 1024 / 1024:.2f}/{file_size / 1024 / 1024:.2f} MB)",
                                    "normal",
                                )

                            overall = ((downloaded_size + bytes_read) / total_size) * 100
                            self.set_progress(overall)
                            self.root.update_idletasks()

                downloaded_size += file_size
                elapsed = time.time() - start_time
                speed = downloaded_size / elapsed if elapsed > 0 else 0
                remaining = total_size - downloaded_size
                eta = remaining / speed if speed > 0 else 0

                self.log(f"Completado: {filename}", "success")
                self.log(f"Velocidad: {speed / 1024 / 1024:.2f} MB/s | ETA: {int(eta)} seg", "normal")

            sftp.close()
            ssh.close()

            self.update_status("Descarga completada")
            self.update_progress_label("Transferencia finalizada")
            self.log("Completado exitosamente", "success")
            self.set_progress(100)

        except Exception as e:
            self.update_status("Error en la transferencia")
            self.log(f"Error: {str(e)}", "error")
        finally:
            self.finish_download()

    def finish_download(self):
        self.is_downloading = False
        self.set_button_state(True, "⬇  Descargar Archivos")


if __name__ == "__main__":
    root = tk.Tk()
    app = DCAExtractor(root)
    root.mainloop()
