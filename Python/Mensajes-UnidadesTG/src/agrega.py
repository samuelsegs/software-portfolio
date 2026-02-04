import sys
import os
import subprocess
import pandas as pd
import pdfplumber
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QShortcut,
    QComboBox, QLabel, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
from weasyprint import HTML, CSS

# ---- botones ----
class BotonPersonalizado(QPushButton):
    def __init__(self, texto, icono_path=None, parent=None):
        super().__init__(texto, parent)
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        if icono_path and os.path.exists(icono_path):
            self.setIcon(QIcon(icono_path))
            self.setIconSize(QSize(24, 24))

# ---- celda editable para Servicios ----
class ServiceCellWidget(QWidget):
    def __init__(self, parent=None):
        super(ServiceCellWidget, self).__init__(parent)
        layout = QHBoxLayout(self)
        self.serviceEdit = QLineEdit(self)
        self.serviceEdit.setPlaceholderText("Ingrese servicio")
        layout.addWidget(self.serviceEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def get_service_data(self):
        return self.serviceEdit.text().strip()

# ---- Clase ventana principal ----
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.df = pd.DataFrame()
        self.servicios = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Asignación de Servicios a Paquetería")
        self.resize(1500, 600)
        if os.path.exists("logo2.png"):
            self.setWindowIcon(QIcon("logo2.png"))

        layout = QVBoxLayout()

        if os.path.exists("logo3.png"):
            logo_label = QLabel(self)
            pixmap = QPixmap("logo3.png").scaled(300, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        self.sheet_selector = QComboBox()
        self.sheet_selector.addItems(['LUNES', 'MAR-VIE', 'SAB-TRN', 'SAB-VAL'])
        self.sheet_selector.setFixedWidth(250)
        layout.addWidget(self.sheet_selector, alignment=Qt.AlignCenter)

        self.loadButton = BotonPersonalizado("Cargar Asignación")
        self.loadButton.clicked.connect(self.load_pdfs)
        layout.addWidget(self.loadButton, alignment=Qt.AlignCenter)

        self.searchLineEdit = QLineEdit(self)
        self.searchLineEdit.setPlaceholderText("Buscar destino...")
        self.searchLineEdit.hide()
        self.searchLineEdit.textChanged.connect(self.search_destinations)
        layout.addWidget(self.searchLineEdit)

        self.shortcutFind = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcutFind.activated.connect(self.toggle_search)

        button_layout = QHBoxLayout()

        self.exportExcelButton = BotonPersonalizado("Exportar ODS")
        self.exportExcelButton.clicked.connect(self.export_to_ods)

        self.exportPdfButton = BotonPersonalizado("Exportar PDF")
        self.exportPdfButton.clicked.connect(self.export_to_pdf)

        self.addPhoneButton = BotonPersonalizado("Agregar Tel")
        self.addPhoneButton.clicked.connect(self.agregar_telefonos)

        self.whatsappButton = BotonPersonalizado("WhatsApp", "w.png")
        self.whatsappButton.clicked.connect(self.run_whatsapp_sender)

        button_layout.addWidget(self.exportExcelButton)
        button_layout.addWidget(self.exportPdfButton)
        button_layout.addWidget(self.addPhoneButton)
        button_layout.addWidget(self.whatsappButton)

        layout.addLayout(button_layout)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        self.table = QTableWidget(self)
        self.table.setShowGrid(True)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # ---- Funciones de buscar ctrl+B ----

    def toggle_search(self):
        if self.searchLineEdit.isVisible():
            self.searchLineEdit.hide()
            self.clear_search()
        else:
            self.searchLineEdit.show()
            self.searchLineEdit.setFocus()

    def search_destinations(self):
        query = self.searchLineEdit.text().lower().strip()
        if query == "":
            self.clear_search()
            return
        num_rows = self.table.rowCount()
        for row in range(num_rows):
            found = any(
                self.table.item(row, col) and query in self.table.item(row, col).text().lower()
                for col in range(self.table.columnCount() - 2)
            )
            self.table.setRowHidden(row, not found)

    def clear_search(self):
        num_rows = self.table.rowCount()
        for row in range(num_rows):
            self.table.setRowHidden(row, False)
        self.searchLineEdit.clear()

    def load_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecciona archivos de Asignación", "", "PDF Files (*.pdf)")
        if files:
            dataframes = []
            for f in files:
                with pdfplumber.open(f) as pdf:
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            header = [h.replace("\n", " ").strip() if isinstance(h, str) else h for h in table[0]]
                            rows = table[1:]
                            df_pdf = pd.DataFrame(rows, columns=header)
                            df_pdf = df_pdf.applymap(lambda x: x.replace("\n", " ").strip() if isinstance(x, str) else x)
                            df_pdf["Fuente"] = os.path.basename(f)
                            dataframes.append(df_pdf)
            self.df = pd.concat(dataframes, ignore_index=True)

            selected_sheet = self.sheet_selector.currentText()
            if "ORI." in self.df.columns and "DESTINO" in self.df.columns:
                self.df["RutaMex"] = self.df.apply(
                    lambda row: self.obtener_ruta_sugerida(str(row["ORI."]), str(row["DESTINO"]), selected_sheet), axis=1
                )
                self.df["Horario"] = selected_sheet

            self.populate_table()

    def obtener_ruta_sugerida(self, ori, destino, hoja, archivo='inicioV.ods'):
        try:
            df = pd.read_excel(archivo, engine='odf', sheet_name=hoja, usecols="B:I")
            df.columns = df.columns.str.strip()
            resultado = df[
                (df["IniciaV"].str.upper().str.strip() == ori.upper().strip()) &
                (df["Destino"].str.upper().str.strip() == destino.upper().strip())
            ]
            if not resultado.empty:
                fila = resultado.iloc[0]
                tramos = [fila["Inicia"]] + [fila[f"FIN{i}"] for i in range(1, 5) if pd.notna(fila.get(f"FIN{i}"))]
                return " → ".join([str(tramo).strip() for tramo in tramos if tramo])
            return "Ruta no encontrada"
        except Exception as e:
            return f"Error buscando ruta: {e}"

    def populate_table(self):
        if self.df.empty:
            return
        num_rows = self.df.shape[0]
        num_cols = self.df.shape[1] + 1  # esta agrega una columna extra para colocar servicios
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        headers = list(self.df.columns) + ["Servicios"]
        self.table.setHorizontalHeaderLabels(headers)

        self.servicios = []
        for row in range(num_rows):
            for col in range(self.df.shape[1]):
                item = QTableWidgetItem(str(self.df.iat[row, col]))
                self.table.setItem(row, col, item)
            service_widget = ServiceCellWidget(self)
            self.table.setCellWidget(row, num_cols - 1, service_widget)
            self.servicios.append(service_widget)

    def actualizar_dataframe(self):
        if self.df.empty:
            return
        num_rows = self.table.rowCount()
        num_cols = self.df.shape[1]
        for row in range(num_rows):
            for col in range(num_cols):
                item = self.table.item(row, col)
                value = item.text() if item else ""
                try:
                    self.df.iloc[row, col] = value
                except:
                    pass
        # Agregar columna de servicios
        self.df["Servicios"] = [widget.get_service_data() for widget in self.servicios]

    def export_to_ods(self):
        self.actualizar_dataframe()
        output_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo ODS", "", "ODS files (*.ods)")
        if not output_path:
            return
        self.df.to_excel(output_path, index=False, engine='odf')
        QMessageBox.information(self, "Éxito", f"Archivo exportado a:\n{output_path}")

    def export_to_pdf(self):
        self.actualizar_dataframe()
        output_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo PDF", "", "PDF files (*.pdf)")
        if not output_path:
            return
        df_pdf = self.df.copy()
        cols_to_drop = [col for col in df_pdf.columns if "cliente" in col.lower() or "utilidad" in col.lower()]
        if cols_to_drop:
            df_pdf.drop(columns=cols_to_drop, inplace=True)
        html_table = df_pdf.to_html(index=False)
        logo_abs = os.path.abspath("logo3.png") if os.path.exists("logo3.png") else ""
        html = f"""
        <html><body>
        <img src='file://{logo_abs}' width='200'/><br><br>
        {html_table}
        </body></html>
        """
        HTML(string=html).write_pdf(output_path, stylesheets=[CSS(string='@page { size: A4; margin: 1cm; }')])
        QMessageBox.information(self, "Éxito", f"Archivo exportado a:\n{output_path}")

    def agregar_telefonos(self):
        try:
            df_viajes = pd.read_excel("Viajes.ods", engine="odf", header=6)
            df_numeros = pd.read_excel("numeros.ods", engine="odf")
            df_viajes.columns = df_viajes.columns.str.strip().str.upper()
            df_numeros.columns = df_numeros.columns.str.strip().str.upper()
            df_merge = pd.merge(df_viajes, df_numeros[["UNIDAD", "NUMERO"]], on="UNIDAD", how="left")
            df_merge.rename(columns={"NUMERO": "TELEFONO"}, inplace=True)
            df_merge.to_excel("viajes_con_telefonos.xlsx", index=False)
            QMessageBox.information(self, "Éxito", "Se generó 'viajes_con_telefonos.xlsx' correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def run_whatsapp_sender(self):
        try:
            subprocess.Popen(["python3", "enviam.py"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar WhatsApp Sender:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
