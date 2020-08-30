from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5 import QtSql
from time import sleep

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("hi.ui", self)
    
        self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName("3.34.124.67")
        self.db.setDatabaseName("16_3")
        self.db.setUserName("16_3")
        self.db.setPassword("1234")
        while True:
            ok = self.db.open()
            print(ok)
            sleep(1)
            if ok == True : break
        
        self.query = QtSql.QSqlQuery()
        
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.pollingQuery)
        self.timer.start()
        
    def pollingQuery(self):
        self.query = QtSql.QSqlQuery("select * from command2 order by time desc limit 15");
        str = ""
        while (self.query.next()):
            self.record = self.query.record()
            str += "%s | %10s | %10s | %4d\n" % (self.record.value(0).toString(), self.record.value(1), self.record.value(2), self.record.value(3))
            
        self.text.setPlainText(str)

        self.query = QtSql.QSqlQuery("select * from sensing2 order by time desc limit 15");
        str = ""
        while (self.query.next()):
            self.record = self.query.record()
            str += "%s | %10s | %10s | %10s\n" % (self.record.value(0).toString(), self.record.value(1), self.record.value(2), self.record.value(3))
        self.text2.setPlainText(str)
        
    
    def commandQuery(self, cmd, arg):
        self.query.prepare("insert into command2 (time, cmd_string, arg_string, is_finish) values (:time, :cmd, :arg, :finish)");
        time = QDateTime().currentDateTime()
        self.query.bindValue(":time", time)
        self.query.bindValue(":cmd", cmd)
        self.query.bindValue(":arg", arg)
        self.query.bindValue(":finish", 0)
        self.query.exec()
    
    def clickedRight(self):
        self.commandQuery("right", "1 sec")
    
    def clickedLeft(self):
        self.commandQuery("left", "1 sec")
    
    def clickedGo(self):
        self.commandQuery("go", "1 sec")
    
    def clickedBack(self):
        self.commandQuery("back", "1 sec")
        
    def clickedMid(self):
        self.commandQuery("mid", "1 sec")

    #add func
    def frontPress(self):
        self.commandQuery("front", "press")

    def frontRelease(self):
        self.commandQuery("front", "release")

    def rightPress(self):
        self.commandQuery("rightside", "press")
        
    def rightRelease(self):
        self.commandQuery("rightside", "release")

    def leftPress(self):
        self.commandQuery("leftside", "press")

    def leftRelease(self):
        self.commandQuery("leftside", "release")


        
app = QApplication([])
win = MyApp()
win.show()
app.exec()
