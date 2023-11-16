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
        to = self.config.get("to")
        if not isinstance(to, list):
            to = [to]
        msg['To'] = ",".join(to)
        body = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        msg.attach(body)

        # s = smtplib.SMTP(smtp_server)
        # logging.debug("Sending email to:" + msg['To'])
        # s.sendmail(msg['From'], msg['To'], msg.as_string(), )
        # s.quit()

        context = ssl.create_default_context()

        if "transport" in self.config["server"] and self.config["server"]["transport"].lower() == "tls":
            with smtplib.SMTP(self.config["server"]["address"], self.config["server"]["port"]) as server:
                server.starttls(context=context)
                server.login(self.config["server"]["user"], self.config["server"]["password"])
                server.sendmail(msg['From'],to, msg.as_string(), )
                server.quit()
        elif "transport" not in self.config["server"] or self.config["server"]["transport"].lower() == "ssl":
            with smtplib.SMTP_SSL(self.config["server"]["address"], self.config["server"]["port"], context=context) as server:
                server.login(self.config["server"]["user"], self.config["server"]["password"])
                server.sendmail(msg['From'], to, msg.as_string(), )
                server.quit()
        else:
            raise ValueError("The transport must be either SSL (default) or TLS")

