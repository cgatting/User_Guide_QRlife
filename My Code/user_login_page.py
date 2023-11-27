import sys
import random
import smtplib
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import md5
from main_page_demo import PromotionsApp


class user_login(QMainWindow):
    def go_to_main_page(self, MainWindow):
            self.main_app_window = PromotionsApp(MainWindow) # Create an instance of the user_login window
    def user_login_message(self, MainWindow):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Congratulations! You have successfully logged in")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        self.go_to_main_page(MainWindow)
    def OTP_Sent_message(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("OTP has been sent to your email")
        msg.setWindowTitle("Inaformation")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
    def update_password(self, user_email, new_password):
        conn = sqlite3.connect('business.db')
        c = conn.cursor()
        new_password_hash = md5(new_password.encode('utf-8')).hexdigest()
        c.execute('UPDATE accounts SET password = ? WHERE email = ?', (new_password_hash, user_email))
        conn.commit()
        conn.close()
    def password_reset_failed(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Temporary password does not match. Please try again.")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
    def error_empty(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("You need to enter a username or password")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
    def no_account(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Either details are incorrect or you do not have an account yet")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
    def OTP_failure(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Your OTP is incorrect")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
    def gen_otp(self):
        otp = f'{random.randint(0, 9999):04d}'
        return otp
    def opt_send(self, otp_code):
        _translate = QtCore.QCoreApplication.translate
        sender_email = 'cgatting@gmail.com'
        recipient_email = self.email_address.text()
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'cgatting@gmail.com'
        smtp_password = 'oytu gdvz jnkt uyjh'
        subject = 'Your OTP'
        message = f'Your OTP is: {otp_code}'
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        self.OTP_Sent_message()
        server.quit()
        
    def send_temp_password(self, to_email, temp_password):
        from_email = 'cgatting@gmail.com'  # Replace with your email
        password = 'oytu gdvz jnkt uyjh'

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = 'Temporary Password'

        body = f'Your temporary password is: {temp_password}'
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
        except Exception as e:
            print('Error sending email:', e)
        
    def gen_new_password(self, user_email):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (user_email,))
        user = c.fetchone()
        if user is None:
            self.no_account()
            return None
        if user_email:
            # Generate a temporary password
            temp_password = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(6))

            # Send the temporary password to the user via email
            self.send_temp_password(user_email, temp_password)

            # Prompt the user to enter the temporary password and set a new password
            temp_password_input, ok = QInputDialog.getText(self, 'Temporary Password', 'Enter the temporary password:')
            if ok:
                if temp_password_input == temp_password:
                    new_password, ok = QInputDialog.getText(self, 'New Password', 'Enter your new password:')
                    if ok:
                        # Update the password in the database
                        self.update_password(user_email, new_password)
                else:
                    self.password_reset_failed()
        else:
            self.no_email_inputted()
    def send_email(self):
        #Write username and password of self into an SQLite database
        _translate = QtCore.QCoreApplication.translate
        username = self.email_address.text()
        password = self.password.text()
        if username == '' or password == '':
            self.error_empty()
        else:
            password = md5(password.encode('utf-8')).hexdigest()
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            ##NEEDS CHANGING TO LOGIN INSTEAD
            c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (username, password))
            user = c.fetchone()
            if user is None:
                self.no_account()
            else:
                self.opt_send(OTP_USER_PASSWORD)
                pass
            conn.commit()
            conn.close()
    
    def opt_verify(self, otp_code, MainWindow):
        print(otp_code, self.opt.text())
        _translate = QtCore.QCoreApplication.translate
        if otp_code == self.opt.text():
            self.user_login_message(MainWindow)
        else:
            self.OTP_failure()

    def __init__(self, MainWindow):
        super().__init__()
        global OTP_USER_PASSWORD
        OTP_USER_PASSWORD = self.gen_otp()
        MainWindow.setObjectName("Login Page")
        MainWindow.resize(300, 472)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(0, 0, 450, 600))
        self.widget.setObjectName("widget")
        self.main_box = QtWidgets.QLabel(self.centralwidget)
        self.main_box.setGeometry(QtCore.QRect(0, 0, 290, 410))
        self.main_box.setStyleSheet("background-color:#79031D;\n"
"border-radius: 10px")
        self.main_box.setText("")
        self.main_box.setObjectName("")
        self.email_address = QtWidgets.QLineEdit(self.centralwidget)
        self.email_address.setGeometry(QtCore.QRect(20, 210, 250, 30))
        self.email_address.setStyleSheet("background-color: rgba(0, 0, 0, 0);\n"
"border: 1px solid rgba(0, 0, 0, 0);\n"
"border-bottom-color: rgba(0, 0, 0, 255);\n"
"padding-bottom: 7px;\n"
"color: #F5F7F7;")
        self.email_address.setText("")
        self.email_address.setCursorPosition(0)
        self.email_address.setObjectName("email_address")
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(20, 260, 250, 30))
        self.password.setStyleSheet("background-color: rgba(0, 0, 0, 0);\n"
"border: 1px solid rgba(0, 0, 0, 0);\n"
"border-bottom-color: rgba(0, 0, 0, 255);\n"
"padding-bottom: 7px;\n"
"color: #F5F7F7;")
        self.password.setText("")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.opt = QtWidgets.QLineEdit(self.centralwidget)
        self.opt.setGeometry(QtCore.QRect(20, 310, 121, 30))
        self.opt.setStyleSheet("background-color: rgba(0, 0, 0, 0);\n"
"border: 1px solid rgba(0, 0, 0, 0);\n"
"border-bottom-color: rgba(0, 0, 0, 255);\n"
"padding-bottom: 7px;\n"
"color: #F5F7F7;")
        self.opt.setInputMask("")
        self.opt.setText("")
        self.opt.setMaxLength(4)
        self.opt.setClearButtonEnabled(False)
        self.opt.setObjectName("opt")
        self.send_email_button = QtWidgets.QPushButton(self.centralwidget)
        self.send_email_button.setGeometry(QtCore.QRect(150, 310, 121, 28))
        self.send_email_button.setStyleSheet("QPushButton{background-color: #000407; color: white;} QPushButton::pressed {background-color: #edb518;}")
        self.send_email_button.setCheckable(False)
        self.send_email_button.setObjectName("send_email_button")
        self.confirmation_button = QtWidgets.QPushButton(self.centralwidget)
        self.confirmation_button.setGeometry(QtCore.QRect(20, 350, 261, 28))
        self.confirmation_button.setStyleSheet("QPushButton{background-color: #000407; color: white;} QPushButton::pressed {background-color: #edb518;}")
        self.confirmation_button.setCheckable(False)
        self.confirmation_button.setObjectName("confirmation_button")
        self.forgot_password_button = QtWidgets.QPushButton(self.centralwidget)
        self.forgot_password_button.setGeometry(QtCore.QRect(20, 380, 261, 28))
        self.forgot_password_button.setStyleSheet("QPushButton{background-color: #000407; color: white;} QPushButton::pressed {background-color: #edb518;}")
        self.forgot_password_button.setCheckable(False)
        self.forgot_password_button.setObjectName("forgot_password_button")
        
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(10, 10, 271, 191))
        self.logo.setText("")
        self.logo.setStyleSheet("QLabel{background-color: #000407;}")
        self.logo.setPixmap(QtGui.QPixmap(r"C:\Users\Clayton\Desktop\Semister1\CT4029 - Principles of Programming\Assigment\Ass-2049\logo.png"))
        self.logo.setObjectName("logo")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.send_email_button.clicked.connect(lambda: self.send_email())
        self.confirmation_button.clicked.connect(lambda: self.opt_verify(OTP_USER_PASSWORD, MainWindow))
        self.forgot_password_button.clicked.connect(lambda: self.gen_new_password(self.email_address.text()))

        global user_email
        user_email = self.email_address.text()
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "This is the Login Page"))
        self.email_address.setPlaceholderText(_translate("MainWindow", "Email Address"))
        self.password.setPlaceholderText(_translate("MainWindow", "Password"))
        self.opt.setPlaceholderText(_translate("MainWindow", "OTP"))
        self.send_email_button.setText(_translate("MainWindow", "Send Email"))
        self.confirmation_button.setText(_translate("MainWindow", "Confirm Login"))
        self.forgot_password_button.setText(_translate("MainWindow", "Forgot Password"))


    