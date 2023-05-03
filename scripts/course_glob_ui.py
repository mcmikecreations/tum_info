from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLabel, QLineEdit, QCheckBox, QGridLayout, QPlainTextEdit
import sys
import webbrowser
import json
import course_functions

def logger(message):
  window.log_label.appendPlainText(str(message))
  window.log_label.repaint()
  print(message)

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    self.setWindowTitle('Download grades')
    self.setMinimumSize(QSize(400, 300))

    username_label = QLabel('Username:')
    self.username_label = username_label
    username_entry = QLineEdit()
    self.username_entry = username_entry

    password_label = QLabel('Password:')
    self.password_label = password_label
    password_entry = QLineEdit()
    password_entry.setEchoMode(QLineEdit.Password)
    self.password_entry = password_entry

    advanced_check = QCheckBox('Advanced')
    advanced_check.stateChanged.connect(self.advanced)
    self.advanced_check = advanced_check

    passshow_check = QCheckBox('Show passes')
    passshow_check.stateChanged.connect(self.advanced)
    self.passshow_check = passshow_check

    verbose_check = QCheckBox('Verbose logs')
    self.verbose_check = verbose_check

    button = QPushButton('Download')
    button.setCheckable(True)
    button.clicked.connect(self.download)
    self.button = button

    info_label = QLabel('Press download after entering login info')
    self.info_label = info_label

    log_label = QPlainTextEdit()
    log_label.setLineWrapMode(QPlainTextEdit.NoWrap)
    log_label.setReadOnly(True)
    self.log_label = log_label
    
    source_label = QLabel('<a href="https://github.com/mcmikecreations/tum_info/tree/main/scripts">The app is open-source and doesn\'t steal data! Click here to browse code.</a>')
    source_label.setOpenExternalLinks(True)
    self.source_label = source_label

    layout = QGridLayout()
    layout.addWidget(username_label, 0, 0)
    layout.addWidget(username_entry, 0, 1)
    layout.addWidget(password_label, 1, 0)
    layout.addWidget(password_entry, 1, 1)
    layout.addWidget(advanced_check, 2, 0)
    layout.addWidget(passshow_check, 2, 1)
    layout.addWidget(verbose_check, 3, 0)
    layout.addWidget(button, 3, 1)
    layout.addWidget(info_label, 4, 0, 1, -1)
    layout.addWidget(log_label, 5, 0, 1, -1)
    layout.addWidget(source_label, 6, 0, 1, -1)

    container = QWidget()
    container.setLayout(layout)

    self.setCentralWidget(container)

  def advanced(self):
    if self.advanced_check.checkState() == Qt.Checked:
      self.username_label.setText('Access token:')
      self.password_label.setText('Cookie:')
      self.username_entry.setEchoMode(QLineEdit.Normal if self.passshow_check.checkState() == Qt.Checked else QLineEdit.Password)
      self.password_entry.setEchoMode(QLineEdit.Normal if self.passshow_check.checkState() == Qt.Checked else QLineEdit.Password)
    else:
      self.username_label.setText('Username:')
      self.password_label.setText('Password:')
      self.username_entry.setEchoMode(QLineEdit.Normal)
      self.password_entry.setEchoMode(QLineEdit.Normal if self.passshow_check.checkState() == Qt.Checked else QLineEdit.Password)

  def download(self):
    try:
      filename = 'grades.json'
      self.log_label.setPlainText('')
      verbose = self.verbose_check.checkState() == Qt.Checked
      auth = None
      
      if self.advanced_check.checkState() == Qt.Checked:
        auth = course_functions.AuthModel(self.username_entry.text(), self.password_entry.text())
      else:
        logger('Performing login...')
        auth = course_functions.perform_login(self.username_entry.text(), self.password_entry.text(), logger, verbose)
        logger('Performing profile lookup...')
        auth = course_functions.perform_profile(auth, logger, verbose)
      
      logger('Performing achievements lookup...')
      achievements = course_functions.perform_achievements(auth, logger, verbose)
      logger('Performing grade stats lookup...')
      achievements = list(filter(lambda y: y != None, map(lambda x: course_functions.perform_exam(auth, x, logger, verbose), achievements)))
      with open(filename, 'w') as file_object:
        json.dump(achievements, file_object)
      logger('Finished.')
    except Exception as e:
      self.info_label.setText(str(e))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
