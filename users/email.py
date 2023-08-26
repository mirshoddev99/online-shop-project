import smtplib
from config.secret import SENDER, email_password


def sending_email(receiver, username):
    sender = f'{SENDER}'
    password = f'{email_password}'
    receiver = f"{receiver}"
    subject = 'Welcome to our Ecommerce website!!!'
    body = f""" Hi {username}, Welcome to our Online shopping site. Have a good shopping!!! """

    message = f"""
                    From: Ecommerce Admin   {sender}
                    To: {username}   {receiver}
                    Subject: {subject}\n
                    {body}
                """

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender, password)
        print("Logged in...")
        server.sendmail(sender, receiver, message)
        print("Email has been sent!")

    except smtplib.SMTPAuthenticationError:
        print("Failed")


def sending_code(receiver, code):
    sender = f'{SENDER}'
    password = f'{email_password}'
    receiver = f"{receiver}"
    subject = 'Verification code'
    body = f"This is your verification code - {code}"

    message = f"""
                    From: Ecommerce Admin   {sender}
                    To:   {receiver}
                    Subject: {subject}\n
                    {body}
                """

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender, password)
        print("Logged in...")
        server.sendmail(sender, receiver, message)
        print("Email has been sent!")

    except smtplib.SMTPAuthenticationError:
        print("Failed")


def resetting_email(receiver, username, subject, body):
    sender = f'{SENDER}'
    password = f'{email_password}'
    receiver = f"{receiver}"
    subject = subject
    body = body

    message = f"""
                    From: Ecommerce Admin   {sender}
                    To: {username}   {receiver}
                    Subject: {subject}\n
                    {body}
                """

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    try:
        server.login(sender, password)
        print("Logged in...")
        server.sendmail(sender, receiver, message)
        print("Email has been sent!")

    except smtplib.SMTPAuthenticationError:
        print("Failed")
