import sys, sqlite3, csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog
)

class BukuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku - Week 10")
        self.setGeometry(100, 100, 720, 500)

        self.conn = sqlite3.connect("katalog.db")
        self.c = self.conn.cursor()
        self.create_table()

        self.init_ui()
        self.load_data()

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS buku (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            pengarang TEXT,
            tahun INTEGER
        )''')
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout()

        # Identitas
        self.identity_label = QLabel("Nama: Kayla Mizanti | NIM: F1D022127")
        self.identity_label.setStyleSheet("font-weight: bold; color: gray;")
        layout.addWidget(self.identity_label)

        # Input fields
        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("📘 Judul Buku")
        self.pengarang_input = QLineEdit()
        self.pengarang_input.setPlaceholderText("✍️ Pengarang")
        self.tahun_input = QLineEdit()
        self.tahun_input.setPlaceholderText("📅 Tahun")

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.judul_input)
        form_layout.addWidget(self.pengarang_input)
        form_layout.addWidget(self.tahun_input)
        layout.addLayout(form_layout)

        pink_style = """
        QPushButton {
            background-color: #d63384;
            color: white;
            border-radius: 5px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #e3b6ca;
        }
        """

        self.save_button = QPushButton("💾 Simpan")
        self.save_button.setStyleSheet(pink_style)
        self.save_button.clicked.connect(self.save_data)

        self.delete_button = QPushButton("🗑️ Hapus")
        self.delete_button.setStyleSheet(pink_style)
        self.delete_button.clicked.connect(self.delete_data)

        self.export_button = QPushButton("📤 Export CSV")
        self.export_button.setStyleSheet(pink_style)
        self.export_button.clicked.connect(self.export_csv)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addWidget(self.export_button)
        layout.addLayout(btn_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Cari judul buku...")
        self.search_input.textChanged.connect(self.search_data)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellChanged.connect(self.update_data)
        self.table.itemDoubleClicked.connect(self.edit_mode)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def save_data(self):
        judul = self.judul_input.text()
        pengarang = self.pengarang_input.text()
        tahun = self.tahun_input.text()

        if not judul or not pengarang or not tahun:
            QMessageBox.warning(self, "Input Error", "Semua field harus diisi.")
            return

        try:
            tahun_int = int(tahun)
            self.c.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)",
                           (judul, pengarang, tahun_int))
            self.conn.commit()
            self.clear_inputs()
            self.load_data()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Tahun harus berupa angka.")

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM buku")
        for row_idx, row_data in enumerate(self.c.fetchall()):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)
        self.table.blockSignals(False)

    def update_data(self, row, col):
        id_item = self.table.item(row, 0)
        if id_item is None:
            return
        record_id = int(id_item.text())
        new_value = self.table.item(row, col).text()
        column = ["id", "judul", "pengarang", "tahun"][col]

        try:
            if column == "tahun":
                new_value = int(new_value)
            self.c.execute(f"UPDATE buku SET {column} = ? WHERE id = ?", (new_value, record_id))
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Update Error", str(e))

    def edit_mode(self, item):
        self.table.editItem(item)

    def delete_data(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Hapus", "Pilih baris yang ingin dihapus.")
            return
        id_item = self.table.item(selected, 0)
        if id_item:
            record_id = int(id_item.text())
            self.c.execute("DELETE FROM buku WHERE id = ?", (record_id,))
            self.conn.commit()
            self.load_data()

    def search_data(self, text):
        self.table.setRowCount(0)
        self.c.execute("SELECT * FROM buku WHERE judul LIKE ?", ('%' + text + '%',))
        for row_idx, row_data in enumerate(self.c.fetchall()):
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path:
            self.c.execute("SELECT * FROM buku")
            rows = self.c.fetchall()
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(rows)
            QMessageBox.information(self, "Export Berhasil", "Data berhasil diekspor ke CSV.")

    def clear_inputs(self):
        self.judul_input.clear()
        self.pengarang_input.clear()
        self.tahun_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BukuApp()
    window.show()
    sys.exit(app.exec_())
