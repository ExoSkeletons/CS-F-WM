import yagmail

from config import config


def send_registration_info_email(user_id, user_email, session_id):
    email_config = config['email']
    sender = email_config['app_email']
    pwd = email_config['app_password']
    receiver = email_config['collection_email']

    subject = f"Watermark Study: registration info for {user_id}"
    contents = f"{user_id}, {user_email}, {session_id}"

    send_email(sender, receiver, pwd, subject, contents)
    print(f"Registration info sent for {user_id}, {user_email}")


def send_email(s_email, t_email, app_password, subject, body):
    yag = yagmail.SMTP(s_email, app_password)
    yag.send(t_email, subject, body)
