from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtSql
from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from sense_hat import SenseHat
import atexit
import time

class pollingThread(QThread):
    def __init__(self):
        super().__init__()
        
    def run(self):
        self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName("3.34.124.67")
        self.db.setDatabaseName("16_3")
        self.db.setUserName("16_3")
        self.db.setPassword("1234")
        ok = self.db.open()
        print(ok)
        if ok == False:
            return
        
        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.dcMotor = self.mh.getMotor(2)
        self.speed = 100
        self.adjust = 0
        self.moveTime = 0
        
        self.dcMotor.setSpeed(self.speed)
        self.query = QtSql.QSqlQuery();
        
        self.servo = self.mh._pwm
        self.servo.setPWMFreq(60)
        
        self.sense = SenseHat()
        gyro = self.sense.get_gyroscope()
        self.prev_roll = gyro["roll"]
        accel = self.sense.get_accelerometer_raw()
        self.init_y = accel["y"]
        
        while True:
            time.sleep(0.1)
            self.getQuery()
            self.setQuery()
            
    def setQuery(self):
        pressure = self.sense.get_pressure()
        temp = self.sense.get_temperature()
        humidity = self.sense.get_humidity()
        gyro = self.sense.get_gyroscope()
        accel = self.sense.get_accelerometer_raw()
        
        p = round((pressure - 1000.0) / 100.0, 3)
        t = round(temp / 100.0, 3)
        h = round(humidity / 100.0, 3)
        
        roll = gyro["roll"]
        y = accel["y"]
        self.speed = int(100 + (100 * (self.init_y - y)))
            
        roll_diff = self.prev_roll - roll
        
        if (roll_diff < -90):
            roll_diff += 360
        if (roll_diff > 90):
            roll_diff -= 360
            
        if (roll_diff >= 10 or roll_diff <= -10):
            self.adjust = int(100 * (roll_diff / 180))
            
        self.dcMotor.setSpeed(self.speed + self.adjust)
        self.prev_roll = roll
        
        self.query.prepare("insert into SENSING1 (TIME, NUM1, NUM2, NUM3, META_STRING, IS_FINISH) values (:time, :num1, :num2, :num3, :meta, :finish)");
        time = QDateTime().currentDateTime()
        met = str(round(gyro["pitch"], 3)) + "|" + str(round(gyro["roll"], 3)) + "|" + str(round(gyro["yaw"], 3))
        self.query.bindValue(":time", time)
        self.query.bindValue(":num1", p)
        self.query.bindValue(":num2", t)
        self.query.bindValue(":num3", h)
        self.query.bindValue(":meta", met)
        self.query.bindValue(":finish", 0)
        self.query.exec()
        
        a = int((p * 1271) % 256)
        b = int((t * 1271) % 256)
        c = int((h * 1271) % 256)
        self.sense.clear(a, b, c)
        
    def getQuery(self):
        query = QtSql.QSqlQuery("select * from COMMAND1 order by TIME desc limit 1");
        query.next()
        cmdTime = query.record().value(0)
        cmdType = query.record().value(1)
        cmdArg = query.record().value(2)
        is_finish = query.record().value(3)
            
        if is_finish == 0:
            print(cmdTime.toString(), cmdType, cmdArg)
            args = cmdArg.split()
            if len(args) == 2 and args[1] == "sec":
                self.moveTime = int(args[0])
            query = QtSql.QSqlQuery("update COMMAND1 set IS_FINISH = 1 where IS_FINISH = 0");
            
            if cmdType == "go":
                self.go()
                
            if cmdType == "back":
                self.back()
                
            if cmdType == "left":
                self.left()
                
            if cmdType == "right":
                self.right()
                
            if cmdType == "mid":
                self.middle()
                
            if cmdType == "front" and cmdArg == "press":
                self.middle()
                self.forward()
            if cmdType == "leftside" and cmdArg == "press":
                self.left()
                self.forward()
            if cmdType == "rightside" and cmdArg == "press":
                self.right()
                self.forward()
                
            if cmdType == "front" and cmdArg == "release":
                self.stop()
            if cmdType == "leftside" and cmdArg == "release":
                self.stop()
            if cmdType == "rightside" and cmdArg == "release":
                self.stop()
                
    def stop(self):
        print("MOTOR STOP")
        self.dcMotor.run(Raspi_MotorHAT.RELEASE)
        
    def forward(self):
        print("FORWARD")
        self.dcMotor.run(Raspi_MotorHAT.FORWARD)
                
    def go(self):
        print("GO")
        self.dcMotor.run(Raspi_MotorHAT.FORWARD)
        time.sleep(self.moveTime)
        self.dcMotor.run(Raspi_MotorHAT.RELEASE)
        
    def back(self):
        print("BACK")
        self.dcMotor.run(Raspi_MotorHAT.BACKWARD)
        time.sleep(self.moveTime)
        self.dcMotor.run(Raspi_MotorHAT.RELEASE)
        
    def steer(self, angle=0):
        if angle <= -60:
            angle = -60
        if angle >= 60:
            angle = 60
        pulse_time = 200 + (614 - 200) // 180 * (angle + 90)
        
        self.servo.setPWM(0, 0, pulse_time)
        
    def left(self):
        print("LEFT")
        self.steer(-30)
        
    def right(self):
        print("RIGHT")
        self.steer(30)
        
    def middle(self):
        print("MIDDLE")
        self.steer(0)
            
th = pollingThread()
th.start()

app = QApplication([])

while True:
    pass
