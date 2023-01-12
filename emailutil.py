import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from email.mime.image import MIMEImage

class Email:
    def __init__(self, config:dict):
        self.config = config

    def send(self, html:str, has_errors:bool=False):
        msg = MIMEMultipart()
        msg['Subject'] = self.config.get("subject") if not has_errors else self.config.get("subject-error")
        msg['From'] = self.config.get("from", "noreply@nothing.org")
        msg['To'] = self.config.get("to")
        body = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        msg.attach(body)

        # s = smtplib.SMTP(smtp_server)
        # logging.debug("Sending email to:" + msg['To'])
        # s.sendmail(msg['From'], msg['To'], msg.as_string(), )
        # s.quit()

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.config["server"]["address"], self.config["server"]["port"], context=context) as server:
            server.login(self.config["server"]["user"], self.config["server"]["password"])
            server.sendmail(msg['From'], msg['To'], msg.as_string(), )
            server.quit()
