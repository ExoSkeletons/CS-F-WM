import yagmail

from config import config


def send_email_from_app(t_email, subject, body):
    email_config = config['email']
    sender = email_config['app_email']
    pwd = email_config['app_password']

    send_email(sender, t_email, pwd, subject, body)


def send_email(s_email, t_email, app_password, subject, body):
    yag = yagmail.SMTP(s_email, app_password)
    yag.send(t_email, subject, body)
