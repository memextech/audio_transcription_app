import sys  
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel  
from PyQt5.QtCore import Qt  
class MainWindow(QMainWindow):  
    def __init__(self):  
        super().__init__()  
        self.setWindowTitle("Test App")  
        self.setMinimumSize(400, 300)  
        central_widget = QWidget()  
        self.setCentralWidget(central_widget)  
        layout = QVBoxLayout(central_widget)  
        label = QLabel("This is a test app")  
        layout.addWidget(label)  
        button = QPushButton("Click Me")  
        button.clicked.connect(lambda: label.setText("Button clicked!"))  
        layout.addWidget(button)  
def main():  
    app = QApplication(sys.argv)  
    window = MainWindow()  
    window.show()  
    return app.exec_()  
if __name__ == "__main__":  
    sys.exit(main()) 
