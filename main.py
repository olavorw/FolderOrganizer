import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTextEdit, QWidget, QFileDialog, QMessageBox
import random
import shutil
from PyQt5.QtCore import QThread, pyqtSignal

class FolderOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("4934 Folder Organizer")
        self.setGeometry(100, 100, 500, 300)

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout
        layout = QVBoxLayout()

        # Folder input
        self.folder_input = QLineEdit(self)
        self.folder_input.setPlaceholderText("Select Folder...")
        layout.addWidget(self.folder_input)

        # Browse button
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(browse_button)

        # File extension dropdown
        self.organize_method = QComboBox(self)
        self.organize_method.addItems(["File Extension", "Alphanumeric Folders", "Random Folders", "Unorganize..?", "Scramble....?"])  # Add more as needed
        layout.addWidget(self.organize_method)

        # Submit button
        submit_button = QPushButton("Organize", self)
        submit_button.clicked.connect(self.start_organizing)
        layout.addWidget(submit_button)

        # Log display
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Logs will be displayed here...")
        layout.addWidget(self.log_display)

        main_widget.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def start_organizing(self):
        # Verify Organize Method
        organize_method = self.organize_method.currentText()
        if not organize_method:
            self.log("Invalid organize method selected!")
            QMessageBox.information(self, "Invalid Organize Method", "Please select an organize method!")
            return

        # Verify Folder
        folder = self.folder_input.text().strip('"' + "'")
        if not folder or not os.path.isdir(folder):
            self.log("Invalid folder was selected, nothing to organize!")
            QMessageBox.information(self, "Invalid Folder", "Please select a valid folder!")
            return

        self.log(f"Organizing files by: {organize_method}")
        self.log(f"Organizing files in folder: {folder}")

        # Start the organizing in a separate thread
        self.worker = OrganizeWorker(folder, organize_method)
        self.worker.log_signal.connect(self.log)
        self.worker.finished.connect(self.on_organizing_finished)
        self.worker.start()

    def on_organizing_finished(self):
        self.log("Files have been organized!")

    def log(self, message):
        self.log_display.append(message)

class OrganizeWorker(QThread):
    log_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, folder, organize_method):
        super().__init__()
        self.folder = folder
        self.organize_method = organize_method

    def run(self):
        try:
            if self.organize_method == "File Extension":
                self.organize_by_extension(self.folder)
            elif self.organize_method == "Alphanumeric Folders":
                self.organize_alphanumeric(self.folder)
            elif self.organize_method == "Random Folders":
                self.organize_random(self.folder)
            elif self.organize_method == "Unorganize..?":
                self.unorganize(self.folder)
            elif self.organize_method == "Scramble....?":
                self.scramble(self.folder)
        except Exception as e:
            self.log_signal.emit(f"An error occurred: {e}")
        finally:
            self.finished.emit()

    def organize_by_extension(self, folder):
        for root, _, files in os.walk(folder):
            for file in files:
                if file in [".gitattributes", ".gitignore"]:
                    continue

                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path):
                    continue

                _, file_extension = os.path.splitext(file)
                if not file_extension:
                    continue

                extension_folder = os.path.join(folder, file_extension[1:])
                os.makedirs(extension_folder, exist_ok=True)
                dest_path = os.path.join(extension_folder, file)

                if os.path.exists(dest_path):
                    dest_path = self.resolve_conflict(dest_path)

                try:
                    shutil.move(file_path, dest_path)
                    self.log_signal.emit(f"Moved {file} to {extension_folder}")
                except (PermissionError, FileExistsError):
                    self.log_signal.emit(f"Error while moving {file}, skipping.")
                    continue

    def organize_alphanumeric(self, folder):
        for root, _, files in os.walk(folder):
            for file in files:
                if file in [".gitattributes", ".gitignore"]:
                    continue

                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path):
                    continue

                first_char = file[0].upper()
                first_char_folder = os.path.join(folder, first_char)
                os.makedirs(first_char_folder, exist_ok=True)
                dest_path = os.path.join(first_char_folder, file)

                if os.path.exists(dest_path):
                    dest_path = self.resolve_conflict(dest_path)

                try:
                    shutil.move(file_path, dest_path)
                    self.log_signal.emit(f"Moved {file} to {first_char_folder}")
                except (PermissionError, FileExistsError):
                    self.log_signal.emit(f"Error while moving {file}, skipping.")
                    continue

    def organize_random(self, folder):
        for root, _, files in os.walk(folder):
            for file in files:
                if file in [".gitattributes", ".gitignore"]:
                    continue

                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path):
                    continue

                random_folder = os.path.join(folder, str(random.randint(1000, 9999)))
                os.makedirs(random_folder, exist_ok=True)
                dest_path = os.path.join(random_folder, file)

                if os.path.exists(dest_path):
                    dest_path = self.resolve_conflict(dest_path)

                try:
                    shutil.move(file_path, dest_path)
                    self.log_signal.emit(f"Moved {file} to {random_folder}")
                except (PermissionError, FileExistsError):
                    self.log_signal.emit(f"Error while moving {file}, skipping.")
                    continue

    def unorganize(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for file in files:
                if file in [".gitattributes", ".gitignore"]:
                    continue

                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path):
                    continue

                dest_path = os.path.join(folder, file)
                if os.path.exists(dest_path):
                    dest_path = self.resolve_conflict(dest_path)

                try:
                    shutil.move(file_path, dest_path)
                    self.log_signal.emit(f"Moved {file} to root folder")
                except (PermissionError, FileExistsError):
                    self.log_signal.emit(f"Error while moving {file}, skipping.")
                    continue

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        self.log_signal.emit(f"Removed empty folder: {dir}")
                    except PermissionError:
                        self.log_signal.emit(f"Permission error while removing folder {dir}, skipping.")

    def scramble(self, folder):
        self.organize_random(folder)  # Scramble is essentially the same as organizing into random folders.

    def resolve_conflict(self, path):
        base, extension = os.path.splitext(path)
        counter = 1
        new_path = f"{base} ({counter}){extension}"
        while os.path.exists(new_path):
            counter += 1
            new_path = f"{base} ({counter}){extension}"
        return new_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FolderOrganizer()
    window.show()
    window.log("Folder Organizer Initialized!")
    sys.exit(app.exec_())
