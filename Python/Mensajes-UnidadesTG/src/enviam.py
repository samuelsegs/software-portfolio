import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import webbrowser
import pyautogui
import time
import threading
import random

# Posición para hacer clic en la caja de mensaje (ajustar según tu pantalla)
CLICK_X = 1123
CLICK_Y = 970

class WhatsAppSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Envío de Mensajes a Operadores WA")
        self.root.geometry("600x400")
        self.df = None

        # Botón cargar Excel
        self.load_btn = tk.Button(root, text="📂 Cargar archivo de Viajes", command=self.load_excel)
        self.load_btn.pack(pady=10)

        # Info de filas cargadas
        self.info_label = tk.Label(root, text="Archivo no cargado.")
        self.info_label.pack()

        # Consola de mensajes
        self.log_text = scrolledtext.ScrolledText(root, height=15, width=70)
        self.log_text.pack(pady=10)

        # Botón enviar
        self.send_btn = tk.Button(root, text="📤 Iniciar envío", state="disabled", command=self.start_sending_thread)
        self.send_btn.pack(pady=5)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("ODS files", "*.ods")])
        if not file_path:
            return

        try:
            self.df = pd.read_excel(file_path, engine="odf")
            self.df.columns = self.df.columns.str.strip().str.upper()
            self.info_label.config(text=f"📄 {len(self.df)} registros cargados.")
            self.send_btn.config(state="normal")
            self.log("✅ Archivo cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            self.log("❌ Error al cargar el archivo.")

    def start_sending_thread(self):
        thread = threading.Thread(target=self.send_messages)
        thread.start()

    def send_messages(self):
        if self.df is None:
            self.log("❌ No hay archivo cargado.")
            return

        total = len(self.df)
        enviados = 0

        for i, row in self.df.iterrows():
            try:
                telefono = str(row.get("TELEFONO", "")).strip()
                unidad = str(row.get("UNIDAD", "")).strip()
                destino = str(row.get("DESTINO", "")).strip()
                servicio = str(row.get("SERVICIOS", "")).strip()
                rutamex = str(row.get("RUTAMEX", "")).strip()

                if not telefono or pd.isna(telefono):
                    self.log(f"⚠️ Fila {i + 2}: sin número.")
                    continue

                if servicio and servicio.lower() != "nan":
                    mensaje = (
                        f"🚨 Unidad {unidad} 🚚, inicialmente te tocó realizar el servicio: {servicio}, "
                        f"y al finalizar realizarás la 📦 paquetería de {destino}," 
                        f"de la siguiente manera: {rutamex}. 👍"
                        f"Para tener mayor información sobre como llegar al servicio comunicate al 807031 dpto de maniobras. "
                        
                    )
                else:
                    mensaje = (
                        f"🚨 Unidad {unidad} 🚚, te tocó realizar la 📦 paquetería de {destino}, "
                        f"de la siguiente manera: {rutamex}. 👍"
                                            )

                mensaje_url = mensaje.replace(" ", "%20")
                url = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje_url}"

                webbrowser.get("chromium").open(url)
                time.sleep(10)  # Esperar a que cargue WhatsApp Web
                pyautogui.moveTo(CLICK_X, CLICK_Y, duration=1)
                pyautogui.click()
                pyautogui.press("enter")
                time.sleep(5)  # Esperar a que se envíe el mensaje
                pyautogui.hotkey('ctrl', 'w')  # 🔥 Cerrar pestaña
                time.sleep(random.uniform(7, 12))  # 🔥 Esperar entre 7 y 12 segundos de forma aleatoria

                enviados += 1
                self.log(f"✅ ({enviados}/{total}) Enviado a {telefono}")
            except Exception as e:
                self.log(f"❌ Error en fila {i + 2}: {e}")

        self.log(f"🎯 Proceso de envío finalizado: {enviados}/{total} mensajes enviados exitosamente.")

# Ejecutar GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppSenderApp(root)
    root.mainloop()
