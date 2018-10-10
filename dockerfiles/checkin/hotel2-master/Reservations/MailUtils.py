import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

def send_mail(conf, fro, to, subject, text, headers = None, files=[],cc=[], server="localhost"):
    if not conf["startSSL"]:
        print 'conf["server"]:',conf["server"],'conf["port"]:',conf["port"]
        conn = smtplib.SMTP(conf["server"], conf["port"])

    else:
        conn = smtplib.SMTP_SSL(conf["server"], conf["port"])
    if conf["username"] and conf["password"]:
        conn.starttls()
        conn.login(conf["username"], conf["password"])
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Cc'] = COMMASPACE.join(cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach( MIMEText(text,'html'))
    if files:
        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(file,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'% os.path.basename(file))
            msg.attach(part)

#    smtp = smtplib.SMTP(server)
#    smtp.sendmail(fro, to+cc, msg.as_string() )
#    smtp.close()
    conn.sendmail(fro, to+cc, msg.as_string())
    print "Sent Mail"
    conn.quit()

