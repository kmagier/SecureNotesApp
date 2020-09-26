from flask import render_template, url_for, current_app
from threading import Thread
from flask_mail import Message
from application.extensions import mail

def send_email(subject, sender, recipients, text_body, html_body, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email, args=[current_app._get_current_object(), msg]).start()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token() 
    #render_template('email/reset_password.txt', user=user, token=token)
    send_email('Reset your password', sender='ja', recipients=[str(user.email)],
                    text_body=render_template('email/reset_password.txt', user=user, token=token),
                    html_body=render_template('email/reset_password.html', user=user, token=token))

def send_registration_email(user): 
    send_email('You have registered successfuly in NoteApp', sender='Administrator', recipients=[str(user.email)],
                    text_body=render_template('email/registration_notification.txt', user=user),
                    html_body=render_template('email/registration_notification.html', user=user))