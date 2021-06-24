#!usr/bin/python3.6

# import required libraries
from bs4 import BeautifulSoup
from getpass import getpass
import requests
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date
from datetime import datetime
import time
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import sys
import schedule

# constants
ENV_PATH = Path('.') / '.env'

load_dotenv(dotenv_path=ENV_PATH)  # load the environment file

# global variables
html = ''
mealDetails = {
}  # global variable to store menu details using a python dictionary


def main():
    messageBody = ''
    # ensure that the page is retrieved well
    print("-----------INSIDE MAIN--------------")
    mealTime = ''  # will store the values BREAKFAST, LUNCH or DINNER based on current hour of the day
    BASE_URL = "https://dining.postech.ac.kr/"
    PAGE = requests.get(BASE_URL)
    global mealDetails
    if (PAGE.status_code == 200):
        html = PAGE.text
        soup = BeautifulSoup(html, 'html.parser')

        # card class div element from the page source
        dailyCard = soup.find_all('div', {'class': 'card-content'})
        for card in dailyCard:

            # mealHour stores the type of meal; BREAKFAST, LUNCH, DINNER, BLUE HILL RESTAURANT
            menuTiming = card.find('p', attrs={'class': 'subtitle'})
            mealHour = menuTiming.text

            # menu stores details for the particular meal
            menuDetails = card.find('div', attrs={'class': 'content'})
            menu = menuDetails

            # store the menu details in a dictionary with the mealHour as its keys
            mealDetails[mealHour] = menu 

        # identify meal timings
        currentHour = datetime.now().hour

        if (currentHour < 10 and currentHour >= 8):
            mealTime = 'BREAKFAST'

        elif (currentHour <= 13 and currentHour >= 10):
            mealTime = 'LUNCH'

        elif (currentHour <= 19 and currentHour >= 17):
            mealTime = 'DINNER'

        else:
            mealTime = 'WISDOM'  # setting a value for else condition, won't really be used

        # based on value of mealTime, fetch the menu from the mealDetails dictionary
        #for (k, v) in mealDetails.items():
        menuDetails="<br><h3>1. Cafeteria</h3><br>"+str(mealDetails[mealTime])+"<br><h3>2. WISDOM</h3><br>"+str(mealDetails["WISDOM"])+"<h3>3. THE BLUE HILL</h3><br>"+str(mealDetails["THE BLUE HILL"])
        messageBody = formatBodyMessage(mealHour=mealTime,
                                        mealDetails=menuDetails)
        print(menuDetails)
        sendEmail("Meal Menu", messageBody)
        mealDetails.clear()

    else:  # outer if's else condition
        print("URL could not be retrieved.")


def formatBodyMessage(mealHour, mealDetails):
    formattedBodyMsg = ''
    today = date.today()
    nowdate = today.strftime("%Y-%m-%d")
    formattedBodyMsg += 'Hi!<br> {mealHour} menu for the date {tday} is as follows:<br><br> {menu}<br><br>Enjoy your meal!!!'.format(
        mealHour=mealHour, tday=nowdate, menu=mealDetails)
    return formattedBodyMsg


def sendEmail(subject, body):
    # get u/n, p/w and email server details from .env file
    emailsender = os.environ['SENDER_EMAIL']
    emailpw = os.environ['SENDER_EMAIL_PASSWORD']
    recipientString = os.environ['RECIPIENTS_EMAIL_LIST']
    recipientList = recipientString.split(',')

    for recipient in recipientList:
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf-8')
        msg['From'] = emailsender
        msg['Subject'] = subject
        msg['To'] = recipient
        _attach = MIMEText(body.encode('utf-8'), 'html', 'UTF-8')
        msg.attach(_attach)

        server = smtplib.SMTP(os.environ['SERVER'])
        server.ehlo()
        server.starttls()
        server.login(emailsender, emailpw)
        server.sendmail(emailsender, recipient, msg.as_string())
        server.quit()

schedule.every().day.at("08:10").do(main)
schedule.every().day.at("11:15").do(main)
schedule.every().day.at("17:30").do(main)

while True:
    schedule.run_pending()
    time.sleep(30)
