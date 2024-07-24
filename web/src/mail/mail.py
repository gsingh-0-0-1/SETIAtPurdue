import yagmail
import os

yag = yagmail.SMTP(os.getenv("CSETI_EMAIL_USER"), oauth2_file='/usr/gmail/oauth2_creds.json')

def send_confirmation_email(fullname, email, token):

    firstname = fullname.split(" ")[0]

    contents = f'''Hi {firstname},

Welcome to Citizen SETI! Please confirm your account creation by clicking on this link:

http://34.29.165.122/confirmaccount/{token}

    '''

    yag.send(subject = f"Welcome to Citizen SETI, {firstname}!",
             to = email,
             contents = contents)
