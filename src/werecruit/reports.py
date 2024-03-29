import dbUtils
import logging

from enum import Enum
_logger = logging.getLogger()

class RetCodes(Enum):
	success = 'RPT_CRUD_S200'
	missing_ent_attrs_error = "RPT_CRUD_E400"
	empty_ent_attrs_error = "RPT_CRUD_E401"
	save_ent_error = "RPT_CRUD_E403"
	del_ent_error = "RPT_CRUD_E404"
	get_ent_error = "RPT_CRUD_E405"
	server_error = "RPT_CRUD_E500"

def get_client_wise_summary_report(tenantID,orderBy=None, order=None):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		if not orderBy:
			query = """select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, count(*) from wr_jds 
				where status = 0 and recruiter_id in ( select uid from tenant_user_roles where tid = %s) 
				group by client_id order by count ASC"""
		if orderBy == 'client':
			query = """select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, count(*) from wr_jds 
				where status = 0 and recruiter_id in ( select uid from tenant_user_roles where tid = %s) 
				group by client_id order by client ASC"""
		elif orderBy == 'count':
			query = """select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, count(*) from wr_jds 
				where status = 0 and recruiter_id in ( select uid from tenant_user_roles where tid = %s) 
				group by client_id order by count ASC"""
		

		params = (int(tenantID),)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()
		if order == 'DESC':
			clientSummaryList = clientSummaryList[::-1]
		return(RetCodes.success.value, "Client wise summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	


def get_client_wise_job_application_status_summary_report(tenantID, orderBy=None, order=None, limit=1000):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		query, params = None, None
		if not orderBy:
			query ="""
			select id, (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, title,
				(jd_stats->'0') as shortlisted,
				(jd_stats->'1') as Initial_Screening_Interviews_scheduled,
				(jd_stats->'2') as Initial_Screening_Interviews_cleared,
				(jd_stats->'3') as Initial_Screening_Interviews_rejected,
				(jd_stats->'10') as R1_Interview_Scheduled,
				(jd_stats->'20') as R1_Interview_Cleared,
				(jd_stats->'30') as R1_Interview_Failed,
				(jd_stats->'31') as R1_Interview_No_Show,
				(jd_stats->'40') as R2_Interview_Scheduled,
				(jd_stats->'50') as R2_Interview_Cleared,
				(jd_stats->'60') as R2_Interview_Failed,
				(jd_stats->'61') as R2_Interview_No_Show,
				(jd_stats->'70') as HM_Interview_Scheduled,
				(jd_stats->'80') as HM_Interview_Cleared,
				(jd_stats->'90') as HM_Interview_Failed,
				(jd_stats->'91') as HM_Interview_No_Show,
				(jd_stats->'100') as HR_Interview_Scheduled,
				(jd_stats->'110') as HR_Interview_Cleared,
				(jd_stats->'120') as HR_Interview_Failed,
				(jd_stats->'121') as HR_Interview_No_Show,
				(jd_stats->'130') as Offer_Pending,
				(jd_stats->'140') as Offer_Released,
				(jd_stats->'150') as Offer_Accepted,
				(jd_stats->'160') as Joined,
				(jd_stats->'170') as No_show
				from wr_jds 
				where status = 0
				and recruiter_id in ( select uid from tenant_user_roles where tid = %s)
				order by id DESC limit %s
			"""
		if orderBy == 'client':
			query = """
			select id, (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, title,
				(jd_stats->'0') as shortlisted,
				(jd_stats->'1') as Initial_Screening_Interviews_scheduled,
				(jd_stats->'2') as Initial_Screening_Interviews_cleared,
				(jd_stats->'3') as Initial_Screening_Interviews_rejected,
				(jd_stats->'10') as R1_Interview_Scheduled,
				(jd_stats->'20') as R1_Interview_Cleared,
				(jd_stats->'30') as R1_Interview_Failed,
				(jd_stats->'31') as R1_Interview_No_Show,
				(jd_stats->'40') as R2_Interview_Scheduled,
				(jd_stats->'50') as R2_Interview_Cleared,
				(jd_stats->'60') as R2_Interview_Failed,
				(jd_stats->'61') as R2_Interview_No_Show,
				(jd_stats->'70') as HM_Interview_Scheduled,
				(jd_stats->'80') as HM_Interview_Cleared,
				(jd_stats->'90') as HM_Interview_Failed,
				(jd_stats->'91') as HM_Interview_No_Show,
				(jd_stats->'100') as HR_Interview_Scheduled,
				(jd_stats->'110') as HR_Interview_Cleared,
				(jd_stats->'120') as HR_Interview_Failed,
				(jd_stats->'121') as HR_Interview_No_Show,
				(jd_stats->'130') as Offer_Pending,
				(jd_stats->'140') as Offer_Released,
				(jd_stats->'150') as Offer_Accepted,
				(jd_stats->'160') as Joined,
				(jd_stats->'170') as No_show
				from wr_jds 
				where status = 0
				and recruiter_id in ( select uid from tenant_user_roles where tid = %s)
				order by client , id DESC limit %s 
			"""
		elif orderBy == 'title':
			query ="""
			select id, (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, title,
				(jd_stats->'0') as shortlisted,
				(jd_stats->'1') as Initial_Screening_Interviews_scheduled,
				(jd_stats->'2') as Initial_Screening_Interviews_cleared,
				(jd_stats->'3') as Initial_Screening_Interviews_rejected,
				(jd_stats->'10') as R1_Interview_Scheduled,
				(jd_stats->'20') as R1_Interview_Cleared,
				(jd_stats->'30') as R1_Interview_Failed,
				(jd_stats->'31') as R1_Interview_No_Show,
				(jd_stats->'40') as R2_Interview_Scheduled,
				(jd_stats->'50') as R2_Interview_Cleared,
				(jd_stats->'60') as R2_Interview_Failed,
				(jd_stats->'61') as R2_Interview_No_Show,
				(jd_stats->'70') as HM_Interview_Scheduled,
				(jd_stats->'80') as HM_Interview_Cleared,
				(jd_stats->'90') as HM_Interview_Failed,
				(jd_stats->'91') as HM_Interview_No_Show,
				(jd_stats->'100') as HR_Interview_Scheduled,
				(jd_stats->'110') as HR_Interview_Cleared,
				(jd_stats->'120') as HR_Interview_Failed,
				(jd_stats->'121') as HR_Interview_No_Show,
				(jd_stats->'130') as Offer_Pending,
				(jd_stats->'140') as Offer_Released,
				(jd_stats->'150') as Offer_Accepted,
				(jd_stats->'160') as Joined,
				(jd_stats->'170') as No_show
				from wr_jds 
				where status = 0
				and recruiter_id in ( select uid from tenant_user_roles where tid = %s)
				order by title, id DESC limit %s
			"""
		

		params = (tenantID,limit)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()
		if order == 'DESC':
			clientSummaryList = clientSummaryList[::-1]
		return(RetCodes.success.value, "Client wise job application summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


def get_client_wise_revenue_opportunity_report(tenantID, orderBy= None, order=None, limit=1000):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		query, params = None, None
		if orderBy == 'ctc_currency':
			query = """
				select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client,id, title, positions, 
				ctc_currency, 
				sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
				where status = 0  
					and ctc_max is not NULL
					and recruiter_id in ( select uid from tenant_user_roles where tid = %s) group by client_id ,id
					order by ctc_currency, id DESC limit %s
				"""
		elif orderBy == 'client':
			query = """
				select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client,id, title, positions, 
				ctc_currency, 
				sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
				where status = 0  
					and ctc_max is not NULL
					and recruiter_id in ( select uid from tenant_user_roles where tid = %s) group by client_id ,id
					order by client, id DESC limit %s
				"""
		elif orderBy == 'title':
			query = """
				select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client,id, title, positions, 
				ctc_currency, 
				sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
				where status = 0  
					and ctc_max is not NULL
					and recruiter_id in ( select uid from tenant_user_roles where tid = %s) group by client_id ,id
					order by title, id DESC limit %s
				"""
		elif orderBy == 'positions':
			query = """
				select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client,id, title, positions, 
				ctc_currency, 
				sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
				where status = 0  
					and ctc_max is not NULL
					and recruiter_id in ( select uid from tenant_user_roles where tid = %s) group by client_id ,id
					order by positions, id DESC limit %s
				"""
		else:
			query = """
				select (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client,id, title, positions, 
				ctc_currency, 
				sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
				where status = 0  
					and ctc_max is not NULL
					and recruiter_id in ( select uid from tenant_user_roles where tid = %s) group by client_id ,id
					order by id DESC limit %s
				"""
		params = (tenantID,limit)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()
		if order == 'DESC':
			clientSummaryList = clientSummaryList[::-1]
		return(RetCodes.success.value, "Client wise revenue opportunity summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


def get_jd_wise_application_status_report(jd_id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """
		select id, (select client_name from wr_clients where  wr_clients.client_id = wr_jds.client_id) as client, title,
			(jd_stats->'0') as shortlisted,
			(jd_stats->'1') as Initial_Screening_Interviews_scheduled,
			(jd_stats->'2') as Initial_Screening_Interviews_cleared,
			(jd_stats->'3') as Initial_Screening_Interviews_rejected,
			(jd_stats->'10') as R1_Interview_Scheduled,
			(jd_stats->'20') as R1_Interview_Cleared,
			(jd_stats->'30') as R1_Interview_Failed,
			(jd_stats->'31') as R1_Interview_No_Show,
			(jd_stats->'40') as R2_Interview_Scheduled,
			(jd_stats->'50') as R2_Interview_Cleared,
			(jd_stats->'60') as R2_Interview_Failed,
			(jd_stats->'61') as R2_Interview_No_Show,
			(jd_stats->'70') as HM_Interview_Scheduled,
			(jd_stats->'80') as HM_Interview_Cleared,
			(jd_stats->'90') as HM_Interview_Failed,
			(jd_stats->'91') as HM_Interview_No_Show,
			(jd_stats->'100') as HR_Interview_Scheduled,
			(jd_stats->'110') as HR_Interview_Cleared,
			(jd_stats->'120') as HR_Interview_Failed,
			(jd_stats->'121') as HR_Interview_No_Show,
			(jd_stats->'130') as Offer_Pending,
			(jd_stats->'140') as Offer_Released,
			(jd_stats->'150') as Offer_Accepted,
			(jd_stats->'160') as Joined,
			(jd_stats->'170') as No_show
		from wr_jds 
		where 	id=%s
		"""
		# and status = 0

		params = (jd_id,)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		job_summary = cursor.fetchall()

		return(RetCodes.success.value, "JD wise summary report fetched successfully from db for jd_id {0}".format(jd_id), job_summary)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)
		
def get_clients_by_tenant_id(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """
				select * from wr_clients
				where tenant_id = %s
				order by client_name
				"""

		params = (int(tenantID),)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		clientList = cursor.fetchall()

		return(RetCodes.success.value, "Client List fetched successfully from db for tenant ID {0}".format(tenantID), clientList)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

def get_jds_by_client_id(clientID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """
				select * from wr_jds
				where client_id = %s and status=0
				order by title ASC
				"""
		params = (clientID,)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		jdList = cursor.fetchall()

		return(RetCodes.success.value, "JD List fetched successfully from db for client {}".format(clientID), jdList)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

if __name__ == "__main__":

	#(code,msg,resumeList) = get_resumes_not_associated_with_job(18)
	#_logger.debug (code)
	(code,msg,result) = get_client_wise_revenue_opportunity_report(1)
	_logger.debug(code)
	_logger.debug(msg)
	_logger.debug(result)

