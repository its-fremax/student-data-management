from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QStatusBar, \
    QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create window title and size
        self.setWindowTitle("Student Management system")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/add.png"), "Add student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon("icons/search.png"), "search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        # Create status bar and status bar element
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(search_action)

        # Create cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def about(self):
        about = AboutDialog()
        about.exec()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = Search()
        dialog.exec()

    def cell_clicked(self):
        edit_button = QPushButton("Edit record")
        edit_button.clicked.connect(self.edit)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status.removeWidget(child)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete)
        self.status.addWidget(edit_button)

        self.status.addWidget(delete_button)

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created by Arinze Egwu on the 22nd of August 2023.
        It is part of my personal project for university of port harcourt.
        """
        self.setText(content)




class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update student Data")

        self.setFixedWidth(200)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        index = main.table.currentRow()
        student_name = main.table.item(index, 1).text()
        # Add student name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Get id from selected row
        self.student_id = main.table.item(index, 0).text()

        # Add combo box
        course_name = main.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "maths", "Pyhsics", "Chemistry"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile number
        mobile = main.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("mobile number")
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(), self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete student data")

        grid = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        grid.addWidget(confirmation, 0, 0, 1, 2)
        grid.addWidget(yes, 1, 0)
        grid.addWidget(no, 1, 1)
        self.setLayout(grid)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index = main.table.currentRow()
        student_id = main.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main.load_data()

        self.close()

        confirmation_message = QMessageBox()
        confirmation_message.setWindowTitle("Success")
        confirmation_message.setText("The record was deleted successfully!")
        confirmation_message.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert student Data")

        self.setFixedWidth(200)
        self.setFixedHeight(200)

        layout = QVBoxLayout()
        # Add student name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")

        # Add combo box
        self.course_name = QComboBox()
        courses = ["Biology", "maths", "Pyhsics", "Chemistry"]
        self.course_name.addItems(courses)
        # Add mobile number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("mobile number")

        layout.addWidget(self.student_name)
        layout.addWidget(self.course_name)
        layout.addWidget(self.mobile)

        # Add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        mobile = self.mobile.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, mobile, course) VALUES(?, ?, ?)",
                       (name, mobile, course))
        connection.commit()
        cursor.close()
        connection.close()
        main.load_data()


class Search(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("search student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input text
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("search name")
        layout.addWidget(self.student_name)

        button = QPushButton("search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        output = cursor.execute("SELECT * FROM students WHERE name =?", (name,))
        rows = list(output)
        print(rows)
        items = main.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main = MainWindow()
main.show()
main.load_data()
sys.exit(app.exec())