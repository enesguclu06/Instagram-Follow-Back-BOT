import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont

class InstagramThread(QThread):
    finished = pyqtSignal()
    result_ready = pyqtSignal(list)

    def __init__(self, username, password):   #Initialize and use properties on the object.
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        browser = webdriver.Chrome() # Chrome selecting as a browser
        browser.get("https://www.instagram.com/")   #Entering Instagram adress
        time.sleep(1)
        username = browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[1]/div/label/input") #Username is finding by Xpath
        username.send_keys(self.username)   #Girilen kullanıcı adının kullanıcı adını giriyoruz
        password = browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[2]/div/label/input")
        password.send_keys(self.password)
        browser.find_element(By.XPATH, "//*[@id='loginForm']/div/div[3]").click() #It is finding a login button and click.
        time.sleep(7)  # Waiting 7 seconds to open webpage


        browser.get("https://www.instagram.com/" + self.username + "/followers/") # Entering to followers page with entered username
        time.sleep(5)

        self.js_command(browser) # It does an automatic scroll feature to get the entire list of followers.

        followers = browser.find_elements(By.CLASS_NAME, "x9f619.xjbqb8w.x1rg5ohu.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1n2onr6.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x6s0dn4.x1oa3qoh.x1nhvcw1")
        #It gets the class information of all followers in the followers tab.
        followers_list = []
        for follower in followers:   #It assigns the text version of the data in all follower classes to the list
            followers_list.append(follower.text)

        browser.get("https://www.instagram.com/" + self.username + "/following/") # Entering to following webpage
        time.sleep(5)

        self.js_command(browser) # Enabling the automatic scroll feature to fetch the entire followers list.
        followings = browser.find_elements(By.CLASS_NAME, "x9f619.xjbqb8w.x1rg5ohu.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1n2onr6.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x6s0dn4.x1oa3qoh.x1nhvcw1")
        #Takipçiler sekmesindeki tüm takip edenlerin sınıfının bilgilerini alıyor.
        #It gets the class information off all followings in the followings tab.
        follows_list = []

        for following in followings:  #It takes the textual form of all the data in your following list and puts it into a list
            follows_list.append(following.text)

        followers_set = set(followers_list) #setting them both for comprison
        follow_set = set(follows_list)

        self.youdontfollow = list(followers_set.difference(follow_set)) #

        self.whodontfollowyou = list(follow_set.difference(followers_set)) #It puts the information of users who are in the followers list but not in the list of users you follow into a new list
        browser.quit()

        self.result_ready.emit([self.youdontfollow, self.whodontfollowyou])  #When the informations loaded,it runs this command and ensures that it is loaded properly.
        self.finished.emit()

    def js_command(self, browser):    #Auto scroll function
        jscommand = """
        followers = document.querySelector("._aano")
        followers.scrollTo(0, followers.scrollHeight);
        var lenOfPage=followers.scrollHeight;
        return lenOfPage;
        """

        lenofPage = browser.execute_script(jscommand)
        match = False
        while not match:
            lastCount = lenofPage
            time.sleep(1)
            lenofPage = browser.execute_script(jscommand)
            if lastCount == lenofPage:
                match = True

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instagram Follow Back (Coded By Enes)") #The text at the top when the app opens
        self.showMaximized()

        self.username_label = QLabel("Username")  #A label with username and password.
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")     #Defining the buttons to which we will asign functions.
        self.login_button.clicked.connect(self.login)

        self.extra_button2 = QPushButton("You Don't Follow Backs")
        self.extra_button2.clicked.connect(self.youdontfollowback)
        self.extra_button1 = QPushButton("Who Don't Follow Backs")
        self.extra_button1.clicked.connect(self.whodontfollowyou)

        self.info_output = QTextEdit()   #The text area where the information will appear.
        self.info_output.setFont(QFont("Arial", 16))
        self.info_output.setReadOnly(True)

        layout = QVBoxLayout()  #UI Editing
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.extra_button1)
        layout.addWidget(self.extra_button2)
        layout.addWidget(self.info_output)

        self.thread = None

        self.setLayout(layout)
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:  #opens the application if username and password are entered.
            self.thread = InstagramThread(username, password)
            self.thread.start()

    def youdontfollowback(self): #Sets the functions of the do you dont follow back
        self.info_output.clear() #Clear the info section.
        self.info_output.append("People You Dont Following : ")
        self.info_output.append("\n".join(self.thread.youdontfollow)) #adds the list to the result section

    def whodontfollowyou(self):#Sets the functions of the do who dont follow you.
        self.info_output.clear()
        self.info_output.append("Those People Who Don't Following You Back:")
        self.info_output.append("\n".join(self.thread.whodontfollowyou)) #adds the list to the result section

if __name__ == "__main__": #Functions for launching the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())