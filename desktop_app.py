import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_BASE = 'http://127.0.0.1:8000/api/'

class ChartWidget(QWidget):
    def __init__(self, summary, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.plot(summary)

    def plot(self, summary):
        self.figure.clear()
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        # Bar chart for averages
        avg = summary.get('averages', {})
        if avg:
            ax1.bar(avg.keys(), avg.values(), color='#4caf50')
            ax1.set_title('Averages')
            ax1.tick_params(axis='x', rotation=30)
        # Pie chart for type distribution
        dist = summary.get('type_distribution', {})
        if dist:
            ax2.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', startangle=140)
            ax2.set_title('Type Distribution')
        self.canvas.draw()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chemical Equipment Visualizer (Desktop)')
        self.resize(900, 600)
        self.username = ''
        self.password = ''
        self.history = []
        self.summary = None
        self.selected_id = None
        self.chart_scroll = None  # For chart scroll area
        self.table_scroll = None  # For table scroll area
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        # Login
        login_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Username')
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Password')
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.login)
        login_layout.addWidget(self.user_input)
        login_layout.addWidget(self.pass_input)
        login_layout.addWidget(self.login_btn)
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setVisible(False)
        login_layout.addWidget(self.logout_btn)
        layout.addLayout(login_layout)
        # Upload
        upload_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Upload CSV')
        self.upload_btn.clicked.connect(self.upload_csv)
        self.upload_btn.setEnabled(False)
        upload_layout.addWidget(self.upload_btn)
        layout.addLayout(upload_layout)
        # Summary
        self.summary_label = QLabel('')
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
        self.chart_widget = None
        self.chart_scroll = QScrollArea()
        self.chart_scroll.setWidgetResizable(True)
        layout.addWidget(self.chart_scroll)
        # History Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'File', 'Date', 'Summary', 'PDF'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        self.table_scroll.setMinimumHeight(200)
        self.table_scroll.setWidget(self.table)
        layout.addWidget(self.table_scroll)
        self.setLayout(layout)

    def login(self):
        self.username = self.user_input.text().strip()
        self.password = self.pass_input.text().strip()
        if not self.username or not self.password:
            QMessageBox.warning(self, 'Error', 'Enter username and password')
            return
        try:
            r = requests.get(API_BASE + 'history/', auth=(self.username, self.password))
            r.raise_for_status()
            self.history = r.json()
            self.update_table()
            self.upload_btn.setEnabled(True)
            self.login_btn.setVisible(False)
            self.logout_btn.setVisible(True)
            QMessageBox.information(self, 'Success', 'Login successful!')
        except Exception as e:
            QMessageBox.critical(self, 'Login Failed', 'Invalid credentials or server error.')

    def logout(self):
        self.username = ''
        self.password = ''
        self.history = []
        self.summary = None
        self.selected_id = None
        self.user_input.setText('')
        self.pass_input.setText('')
        self.upload_btn.setEnabled(False)
        self.login_btn.setVisible(True)
        self.logout_btn.setVisible(False)
        self.summary_label.setText('')
        self.table.setRowCount(0)
        if self.chart_widget:
            self.chart_scroll.takeWidget()
            self.chart_widget.deleteLater()
            self.chart_widget = None

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if not file_path:
            return
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                r = requests.post(API_BASE + 'upload/', files=files, auth=(self.username, self.password))
                r.raise_for_status()
                data = r.json()
                self.summary = data['summary']
                self.show_summary(self.summary)
                self.fetch_history()
                QMessageBox.information(self, 'Success', 'CSV uploaded and processed!')
        except Exception as e:
            QMessageBox.critical(self, 'Upload Failed', 'Failed to upload or process CSV.')

    def fetch_history(self):
        try:
            r = requests.get(API_BASE + 'history/', auth=(self.username, self.password))
            r.raise_for_status()
            self.history = r.json()
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Failed to fetch history.')

    def show_summary(self, summary):
        # Compact summary UI: single line for each section, less vertical space
        html = (
            f"<b>Total Count:</b> <span style='color:#1976d2;font-size:16px;'>{summary.get('total_count', '-')}</span> | "
            f"<b>Averages:</b> " + ', '.join([f"{k}: <b style='color:#388e3c'>{v}</b>" for k, v in summary.get('averages', {}).items()]) + " | "
            f"<b>Type Distribution:</b> " + ', '.join([f"{k}: <b style='color:#d84315'>{v}</b>" for k, v in summary.get('type_distribution', {}).items()])
        )
        self.summary_label.setText(html)
        if self.chart_widget:
            self.chart_scroll.takeWidget()
            self.chart_widget.deleteLater()
            self.chart_widget = None
        self.chart_widget = ChartWidget(summary)
        self.chart_widget.setMinimumHeight(350)
        self.chart_widget.setMinimumWidth(700)
        self.chart_scroll.setWidget(self.chart_widget)
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(850)

    def update_table(self):
        self.table.setRowCount(0)
        for row, h in enumerate(self.history):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(h['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(h['filename']))
            self.table.setItem(row, 2, QTableWidgetItem(h['uploaded_at'].replace('T', ' ').split('.')[0]))
            btn_summary = QPushButton('View')
            btn_summary.clicked.connect(lambda _, s=h['summary']: self.show_summary(s))
            self.table.setCellWidget(row, 3, btn_summary)
            btn_pdf = QPushButton('PDF')
            btn_pdf.clicked.connect(lambda _, id=h['id']: self.download_pdf(id))
            self.table.setCellWidget(row, 4, btn_pdf)

    def download_pdf(self, id):
        try:
            r = requests.get(API_BASE + f'report/{id}/', auth=(self.username, self.password), stream=True)
            r.raise_for_status()
            fname = f'report_{id}.pdf'
            with open(fname, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            QMessageBox.information(self, 'Downloaded', f'PDF report saved as {fname}')
        except Exception as e:
            QMessageBox.critical(self, 'Download Failed', 'Failed to download PDF report.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
