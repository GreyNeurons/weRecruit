import imaplib
import poplib
import os
import constants
import smtplib

#from userUtils import getUserConfig, get
#import resumeUtils

from imap_tools import MailBox, AND
import userUtils 
import resumeUtils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

from jinja2 import Environment, FileSystemLoader

import _thread
import time
import logging

def readEmails():
	mailbox = None 
	try:
		logging.info("Reading mailbox")
		
		mailserver = os.environ.get("IMAP_MAIL_SERVER")
		email = os.environ.get("IMAP_MAILBOX")
		password = os.environ.get("IMAP_MAILBOX_PWD")
		folder = os.environ.get("IMAP_FOLDER")

		logging.debug( "logging.debuging email configurations")
		logging.debug("Mail server is ",mailserver)
		logging.debug(email)
		#logging.debug(password)
		logging.debug(folder)

		mailbox = MailBox(mailserver)

		mailbox.login(email, password, initial_folder=folder)  

		logging.debug("Logged into mail box")

		logging.debug("start reading emails")
		
		for msg in mailbox.fetch(AND( seen = False )):  #should be False in prod
			logging.debug(msg.subject)
			logging.debug(msg.text)
			for att in msg.attachments:
				logging.debug(os.getcwd(),att.filename, att.content_type)
				cwd = os.getcwd() + "\\";
				logging.debug("working dir is " + cwd)
				
				f = open("./src/werecruit/resume_uploads/" + att.filename,'wb' )
				f.write( att.payload)
				f.close()
				
				(retcode,msg,resumeId) = resumeUtils.save_resume(constants.NEW_ENTITY_ID, att.filename,'Candidate Name',
								'Candidate Email','Candidate phone',1)

				assert retcode == resumeUtils.RetCodes.success.value, "Failed to save resume sent via email. Please contact your sys admin."
				
				file_loader = FileSystemLoader('./conf')
				env = Environment(loader=file_loader)
				template = env.get_template('resume_upload_response.template')
		
				body = template.render(resumeID = resumeId )
				
				sendMail(email,'Resume upload notification',body,'plain')
		#mailbox.logout()
		logging.info("logged out from mailbox")
	
	except Exception as e:
		logging.error( e )
		#mailbox.logout()

	finally:
		if mailbox is not None:
			mailbox.logout()

	#res_dir_path = "./data/"
	#resume_List =  os.listdir(path=res_dir_path)

	#logging.debug("Start processing resumes from folder " + res_dir_path)

	'''for resume_file in resume_List:
		resumeUtils.process_single_resume(userID, str( res_dir_path + resume_file))
		os.remove(str( res_dir_path + resume_file))
	'''

def sendMail_async(ToEmailAddr, subject, body, contentType):
	_thread.start_new_thread ( sendMail,(ToEmailAddr, subject, body, contentType) )


def sendMail(ToEmailAddr, subject, body, contentType):
	
	ToEmailAddr = 'rkanade@gmail.com' #ToEmailAddr -> done purposefully to avoid sending emails to
	
	logging.info("Setting up SMTP server again")

	msg = MIMEMultipart()
	msg['From'] = os.environ.get("SMTP_MAIL_USERNAME")
	msg['To'] = ToEmailAddr
	msg['Subject'] = str(subject)

	msg.attach(MIMEText(body,contentType)) #'plain'

	logging.debug( msg.as_string() )

	with smtplib.SMTP(os.environ.get("SMTP_MAIL_SERVER"), os.environ.get("SMTP_MAIL_PORT")) as server:
		server.login(os.environ.get("SMTP_MAIL_USERNAME"), os.environ.get("SMTP_MAIL_PASSWORD"))
		server.sendmail(os.environ.get("SMTP_MAIL_USERNAME"), ToEmailAddr, msg.as_string())
		server.close()

	logging.info("Mail sent successfully.")


if __name__ == "__main__":
	#processEmailsForApp(constants.APP_CODE_CAMI);
	#processEmails("rrkanade22@yahoo.com","CAMI")
	logging.basicConfig(level=logging.DEBUG)

	sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
	time.sleep(60)
	
	#while True:
	#	readEmails()
	#	time.sleep(60)

