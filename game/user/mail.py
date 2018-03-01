import smtplib

from credentials import credentials


def send_mail_using_g_mail(user, pwd, recipient, subject, body):

    to = recipient if type(recipient) is list else [recipient]

    # Prepare actual message
    message = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(user, ", ".join(to), subject, body)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to, message)
        server.close()
        return True

    except Exception:
        return False


def send(email, password):

    subject = '[Mechanical Turk] Duopoly Registration'
    message = "Hi,\n\nThanks for joining our experiment.\n\n" \
              "Your username to join the game is the email you used for register: " + email + \
              "\nYour password is: " + password + \
              "\n\nPlease come back to login on Duopoly in order to play the game!"

    return send_mail_using_g_mail(
        user=credentials.username,
        pwd=credentials.pwd,
        recipient=email,
        subject=subject,
        body=message
    )
