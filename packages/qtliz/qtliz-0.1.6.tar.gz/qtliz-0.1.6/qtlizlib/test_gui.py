import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu

from qtlizlib.domain.menuActionTool import ActionItem
from qtlizlib.handler.menuActionTool import MenuMasterHandler


class TestMainWindow(QMainWindow):


    signal_action_1 = Signal()
    signal_action_2 = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Main Window")
        self.setGeometry(100, 100, 800, 600)

        action_1 = ActionItem("test_action_1", "Test Action 1")
        action_2 = ActionItem("test_action_2", "Test Action 2")
        action_3 = ActionItem("test_action_3", "Test Action 3")

        handler = MenuMasterHandler(
            menu=QMenu("Test Menu"),
            menu_bar=self.menuBar(),
            parent=self,
            enable_logs=True
        )
        handler.install_menu()
        handler.install_action(action_1, self.signal_action_1)
        handler.install_action(action_2, self.signal_action_2)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())