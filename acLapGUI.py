import modules.acLap as acLap
import modules.driver_championship as driver_championship
import modules.manu_championship as manu_championship
import PySide6.QtCore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView
import sys

class acApp(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Data from drivers and manufacturers (lists of lists)
        self.driver_data = driver_championship.get_drivers_data()
        self.manufacturers_data = manu_championship.get_manufacturers_data()

        # Creates the 2 tables with the data
        self.drivers_table = self.show_data(self.driver_data)
        self.teams_table = self.show_data(self.manufacturers_data)

        # Table styling
        self.drivers_table.setMaximumWidth(500)
        self.teams_table.setMaximumWidth(500)
        self.drivers_table.setMaximumHeight(700)
        self.teams_table.setMaximumHeight(700)
        self.drivers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.teams_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Creates and Setups de main Widget (window)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle('Assetto Corsa Multiclass Championship Tool')
        self.grid_layout = QGridLayout()
        self.main_widget.setLayout(self.grid_layout)

        # Buttons
        self.startBtn = self.create_btn('Start Championship')
        self.resetBtn = self.create_btn('Reset Championship')

        # Add widgets to the main page
        self.grid_layout.addWidget(self.drivers_table)
        self.grid_layout.addWidget(self.teams_table, 0,1)
        self.grid_layout.addWidget(self.startBtn, 1, 0)
        self.grid_layout.addWidget(self.resetBtn, 2, 0)

        #Actions
        self.resetBtn.clicked.connect(self.reset_championship)
        self.startBtn.clicked.connect(self.start_championship)

    # Standard button creation helper function;
    def create_btn(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet('font-size: 20px')
        return btn
    
    def get_data(self):
        return (driver_championship.get_drivers_data(), manu_championship.get_manufacturers_data())
    
    @Slot()
    def start_championship(self):
        acLap.start_championship()
        self.grid_layout.removeWidget(self.drivers_table)
        self.grid_layout.removeWidget(self.teams_table)

        self.delete_tables()

        drivers_upd_data = self.get_data()[0]
        teams_upd_data = self.get_data()[1]

        self.drivers_table = self.show_data(drivers_upd_data)
        self.teams_table = self.show_data(teams_upd_data)

        self.drivers_table.setMaximumWidth(500)
        self.teams_table.setMaximumWidth(500)
        self.drivers_table.setMaximumHeight(700)
        self.teams_table.setMaximumHeight(700)
        self.drivers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.teams_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.grid_layout.addWidget(self.drivers_table, 0, 0)
        self.grid_layout.addWidget(self.teams_table, 0,1)

    def delete_tables(self):
        self.drivers_table.setParent(None)
        self.drivers_table.deleteLater()

        self.teams_table.setParent(None)
        self.teams_table.deleteLater()

    @Slot()
    def reset_championship(self):
        acLap.reset_championships()
        self.drivers_table.clear()
        self.teams_table.clear()

    @Slot()
    def show_data(self, data):
        try:
            rows = len(data)
            cols = len(data[0])
        except (TypeError, IndexError):
            rows = 0
            cols = 0
        else:
            table = QTableWidget(rows, cols)
            if cols == 4:
                table.setHorizontalHeaderLabels(['Name', 'Car', 'Category', 'Points'])
            else:
                table.setHorizontalHeaderLabels(['Name', 'Drivers', 'Points'])
            for row_index, row_data in enumerate(data):
                for col_index, col_data in enumerate(row_data):
                    tb_item = QTableWidgetItem(str(col_data))
                    table.setItem(row_index, col_index, tb_item)
            return table
        return QTableWidget(0, 0)

def main():
    app = QApplication(sys.argv)
    window = acApp()
    window.show()
    app.exec()
if __name__ == '__main__':
    main()