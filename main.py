import datetime
import re

import cv2
import pytesseract
from PIL import Image
import mysql.connector
harcascade = "model/haarcascade_russian_plate_number.xml"

cap = cv2.VideoCapture(0)

cap.set(3, 640)  # width
cap.set(4, 480)  # height

min_area = 500
count = 0

def connectDB():
    con = mysql.connector.connect(host='localhost', user='root', password='', database='test')
    return con

def createTable():
    con = connectDB()
    cursor = con.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS numberplate (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        number_plate VARCHAR(255) NOT NULL,
        status INT NOT NULL,
        date_in DATETIME NOT NULL,
        date_out DATETIME
    );
    """
    cursor.execute(sql)
    con.commit()
    con.close()
def checkNp(number_plate):
    con = connectDB()
    cursor = con.cursor()
    sql = "SELECT * FROM numberplate WHERE number_plate = %s"
    cursor.execute(sql, (number_plate,))
    cursor.fetchall()
    result = cursor._rowcount
    con.close()
    cursor.close()
    return result

def checkNpStatus(number_plate):
    con = connectDB()
    cursor = con.cursor()
    sql = "SELECT * FROM numberplate WHERE number_plate = %s ORDER BY date_in DESC LIMIT 1"
    cursor.execute(sql, (number_plate,))
    result = cursor.fetchone()
    con.close()
    cursor.close()
    return result



def insertNp(number_plate):
    con = connectDB()
    cursor = con.cursor()
    sql = "INSERT INTO numberplate (number_plate, status, date_in) VALUES (%s, %s, %s)"
    now = datetime.datetime.now()
    date_in = now.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(sql, (number_plate, '1', date_in))
    con.commit()
    con.close()
    cursor.close()
    print("VÀO BÃI GỬI XE")
    print("Ngày giờ vào: " + datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d %H:%M:%S"))


def updataNp(Id):
    con = connectDB()
    cursor = con.cursor()
    sql = "UPDATE numberplate SET status = 0, date_out = %s WHERE Id = %s"
    now = datetime.datetime.now()
    date_out = now.strftime("%Y/%m/%d %H:%M:%S")
    cursor.execute(sql, (date_out, Id))
    con.commit()
    con.close()
    cursor.close()
    print("RA KHOI BAI GUI XE")
    print("Ngay gio ra: " + datetime.datetime.strftime(datetime.datetime.now(), "%Y/%m/%d %H:%M:%S"))
def readnumberplate():
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    plates = Image.open(r"D:\pythonnhandienbansoxe\plates\scaned_img_.jpg")
    text = pytesseract.image_to_string(plates, config='--psm 8')
    text = re.sub(r'[^a-zA-Z0-9-]', '', text)
    number_plate = ''
    for char in str(text):
        if(char.isspace() == False):
            number_plate += char
    print("-----------------------------")
    print("xe co bien so: " + number_plate)
    print("------------------------")
    if(number_plate != ""):
        check = checkNp(number_plate)
        if(check == 0):
            insertNp(number_plate)
        else:
            check2 = checkNpStatus(number_plate)
            if(check2[2] == 1):
                updataNp(check2[0])
            else:
                insertNp(number_plate)
    else:
        print("bien so khong xác dinh")
createTable()

while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(img_gray, 160, 255, cv2.THRESH_BINARY)
    plates = plate_cascade.detectMultiScale(binary_img, 1.1, 4)
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)

        if cv2.contourArea(contour) > 1000:
            approx = cv2.approxPolyDP(contour,0.02*cv2.arcLength(contour,True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)

                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                img_roi = img[y: y + h, x:x + w]
                cv2.imshow("ROI", img_roi)

    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("plates/scaned_img_.jpg", img_roi)

        readnumberplate()