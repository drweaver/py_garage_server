import smtplib
import logging
from threading import Thread

logger = logging.getLogger("garage_notify")
 
class GarageNotify(Thread):
	def __init__(self, config, msg):
		Thread.__init__(self)
		self._config = config
		self._msg = msg
		
	def read_smtp_pwd(self):
		with open(self._config['smtp_pwd_file'], 'r') as f:
			return f.readline()
	
	def run(self):
		self._config.reload()
		c = self._config
		 
		try:
			sender = c['smtp_sender']
			recipient = c['smtp_recipient']
			
			subject = body = self._msg
			body = "" + body + ""
			headers = ["From: " + sender,
			   "Subject: " + subject,
			   "To: " + recipient,
			   "MIME-Version: 1.0",
			   "Content-Type: text/html"]
			headers = "\r\n".join(headers)

			session = smtplib.SMTP(c['smtp_server'], c['smtp_port'])
			session.ehlo()
			session.starttls()
			session.ehlo
			session.login(sender, self.read_smtp_pwd())
			logger.info("SMTP login successful")
			session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
			logger.info("Mail sent successfully to " + recipient + ": " + subject)
			session.quit()
		except smtplib.SMTPException as detail:
			logger.error("Failed to send notification mail! " + detail  )
 


