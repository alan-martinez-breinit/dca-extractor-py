import tkinter as tk
from tkinter import messagebox, scrolledtext
import paramiko
import os
import json
from pathlib import Path
import threading
import time

class DCAExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Breinit DCA Extractor")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Config
        self.SFTP_HOST = "169.62.217.83"
        self.SFTP_PORT = 22
        self.SFTP_USER = "ftpdca"
        self.SFTP_PASS = "ftpDC@2023"
        self.REMOTE_PATH = "/ALANPRUEBAS/FTPIA/Autopolis"
        self.LOCAL_PATH = r"C:\Users\Breinit\Documents\DCA\autopolis"

        self.setup_ui()

    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="Breinit DCA Extractor", font=("Arial", 24, "bold"), fg="#003366")
        title.pack(pady=20)

        # Subtitle
        subtitle = tk.Label(self.root, text="Descarga de archivos SFTP", font=("Arial", 12), fg="#666666")
        subtitle.pack()

        # Status
        self.status_label = tk.Label(self.root, text="Listo para descargar", font=("Arial", 10), fg="#333333", wraplength=500)
        self.status_label.pack(pady=15)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Canvas(self.root, width=400, height=20, bg="#E0E0E0", highlightthickness=0)
        self.progress_bar.pack(pady=10)

        # Button
        self.button = tk.Button(self.root, text="Descargar Archivos", font=("Arial", 12, "bold"),
                                bg="#003366", fg="white", height=2, width=30, command=self.start_download)
        self.button.pack(pady=15)

        # Log
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, width=50, font=("Courier", 9), state="disabled")
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def update_status(self, message):
        self.status_label.config(text=message)

    def start_download(self):
        self.button.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.progress_var.set(0)

        thread = threading.Thread(target=self.download)
        thread.start()

    def download(self):
        try:
            self.log("Iniciando conexión...")
            self.update_status("Conectando...")

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.SFTP_HOST, self.SFTP_PORT, self.SFTP_USER, self.SFTP_PASS)

            self.update_status("✓ Acceso correcto - Conectado")
            self.log("✓ Conectado al Servidor Correspondiente")

            Path(self.LOCAL_PATH).mkdir(parents=True, exist_ok=True)

            sftp = ssh.open_sftp()
            sftp.chdir(self.REMOTE_PATH)
            self.log("✓ Accediendo a carpeta de descargas")

            files = sftp.listdir()
            txt_files = [f for f in files if f.endswith(".txt")]

            if not txt_files:
                self.update_status("⚠ No hay archivos .txt")
                self.log("No se encontraron archivos .txt")
                sftp.close()
                ssh.close()
                self.button.config(state="normal")
                return

            # Calcular tamaño total
            total_size = sum(sftp.stat(f).st_size for f in txt_files)
            self.log(f"✓ Tamaño total: {total_size / 1024 / 1024:.2f} MB")

            self.update_status(f"Descargando {len(txt_files)} archivos...")
            self.log(f"✓ Encontrados {len(txt_files)} archivos .txt")

            start_time = time.time()
            downloaded_size = 0

            for i, filename in enumerate(txt_files):
                jsonl_name = Path(filename).stem + ".jsonl"
                local_file = os.path.join(self.LOCAL_PATH, jsonl_name)
                file_size = sftp.stat(filename).st_size

                self.log(f"↓ Descargando: {filename} ({file_size / 1024 / 1024:.2f} MB)")

                bytes_read = 0
                headers = None
                buffer = ""
                rows_written = 0

                with open(local_file, "w", encoding="utf-8") as out_f:
                    with sftp.file(filename, "r") as remote_file:
                        while True:
                            chunk = remote_file.read(1024 * 256)  # 256 KB chunks
                            if not chunk:
                                break
                            bytes_read += len(chunk)
                            buffer += chunk.decode("utf-8", errors="replace")

                            lines = buffer.split("\n")
                            buffer = lines.pop()  # línea incompleta, se conserva para el próximo chunk

                            for line in lines:
                                line = line.rstrip("\r")
                                if not line:
                                    continue
                                if headers is None:
                                    headers = line.split("|")
                                    continue
                                values = line.split("|")
                                row = dict(zip(headers, values))
                                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                                rows_written += 1

                            # Progreso en tiempo real
                            file_progress = (bytes_read / file_size) * 100
                            self.log(f"  {filename}: {file_progress:.1f}% ({bytes_read / 1024 / 1024:.2f}/{file_size / 1024 / 1024:.2f} MB)")
                            self.root.update()

                    # Procesar última línea si quedó pendiente en el buffer
                    if buffer.strip() and headers is not None:
                        values = buffer.rstrip("\r").split("|")
                        row = dict(zip(headers, values))
                        out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                        rows_written += 1

                downloaded_size += file_size
                elapsed = time.time() - start_time
                speed = downloaded_size / elapsed if elapsed > 0 else 0
                remaining_size = total_size - downloaded_size
                eta = remaining_size / speed if speed > 0 else 0

                self.log(f"✓ Completado: {jsonl_name} ({rows_written} registros)")
                self.log(f"  Velocidad: {speed / 1024 / 1024:.2f} MB/s | ETA: {int(eta)} seg\n")

                progress = ((i + 1) / len(txt_files)) * 100
                self.progress_var.set(progress)
                self.draw_progress()
                self.update_status(f"Descargando {i + 1}/{len(txt_files)} archivos...")

            sftp.close()
            ssh.close()

            self.update_status("✓ Descarga completada")
            self.log("\n✓ Completado exitosamente")
            self.progress_var.set(100)
            self.draw_progress()

        except Exception as e:
            self.update_status("✗ Error")
            self.log(f"✗ Error: {str(e)}")
        finally:
            self.button.config(state="normal")

    def draw_progress(self):
        self.progress_bar.delete("progress")
        progress = self.progress_var.get()
        width = (progress / 100) * 400
        self.progress_bar.create_rectangle(0, 0, width, 20, fill="#003366", tags="progress")
        self.progress_bar.create_text(200, 10, text=f"{int(progress)}%", fill="white", tags="progress")

if __name__ == "__main__":
    root = tk.Tk()
    app = DCAExtractor(root)
    root.mainloop()
