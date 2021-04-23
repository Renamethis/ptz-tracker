import smtplib
import base64

smtpObj = smtplib.SMTP('smtp.gmail.com', 587)

smtpObj.starttls()

smtpObj.login('tensorflow21@gmail.com', base64.b64decode('VGVuc29yNTUyMQ=='))

smtpObj.sendmail("tensorflow21@gmail.com","prostepm21@gmail.com","test")