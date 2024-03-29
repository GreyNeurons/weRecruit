import logging
import os

import emailUtils
import jdUtils
import resumeUtils
import constants

import schedule
import time

from dotenv import load_dotenv,find_dotenv
load_dotenv(find_dotenv())
logging.basicConfig(filename=constants.LOG_FILENAME_SCHED, format=constants.LOG_FORMAT, level=int(os.environ.get("LOG_LEVEL",20)))

_logger = logging.getLogger()

def read_email_job():

	_logger.info("Start read email job")
	emailUtils.readEmails()
	_logger.info("read email job completed")


def update_job_stats_job():
	_logger.info("Start update job stats job")
	jdUtils.update_job_stats()
	_logger.info("Completed update job stats job")

def parse_resumes_job():
	_logger.info("Start parse resume job")
	resumeUtils.populate_json_resumes()
	_logger.info("Completed parse resume job")

def auto_shortlist_resumes():
	_logger.info("Start auto shortlisting job")
	resumeUtils.auto_shortlist_resumes()
	_logger.info("Completed auto shortlisting job")

if __name__ == "__main__":	
	
	#load_dotenv(find_dotenv())
	#logging.basicConfig(filename=constants.LOG_FILENAME_SCHED, format=constants.LOG_FORMAT, level=int(os.environ.get("LOG_LEVEL",20)))

	try:

		schedule.every(1).minutes.do(read_email_job)
		schedule.every(1).minutes.do(update_job_stats_job)
		#schedule.every(1).minutes.do(parse_resumes_job)
		schedule.every(1).minutes.do(auto_shortlist_resumes)

		_logger.info("scheduler started")

		while 1:
			try:
				schedule.run_pending()
				time.sleep(1)
			except Exception as innerExc:
				_logger.error("Exception occured during running scheduled jobs.",exc_info=1)
				_logger.error(innerExc)

		_logger.info("Scheduler stopped normally.")

	except KeyboardInterrupt:
		_logger.warning("Scheduler stopped bcas of keyboard interrupt.")
		
	except Exception as e:
		_logger.error("Exception occured during running scheduled jobs.",exc_info=1)
		_logger.error(e)
		_logger.warning("Scheduler stopped with errors.",exc_info=1)

	finally:
		schedule.clear()