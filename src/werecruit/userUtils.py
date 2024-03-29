
import logging

from click import confirm
import dbUtils
import constants

from dotenv import load_dotenv, find_dotenv
from enum import Enum
import hashlib

from datetime import datetime
from datetime import timezone

_logger = logging.getLogger()


class RoleIDs(Enum):
    ADMIN = 1
    RECRUITER = 2


class Status(Enum):
    active = 1
    suspended = 0
    pending_verification = 2


class RetCodes(Enum):
    success = 'IAM_CRUD_S200'
    missing_ent_attrs_error = "IAM_CRUD_E400"
    empty_ent_attrs_error = "IAM_CRUD_E401"
    save_ent_error = "IAM_CRUD_E403"
    del_ent_error = "IAM_CRUD_E404"
    get_ent_error = "IAM_CRUD_E405"
    server_error = "IAM_CRUD_E500"
    sign_in_failed = "IAM_CRUD_E411"
    reset_password_failed = "IAM_CRUD_E420"


def hashit(plain_text):

    result = hashlib.sha256(plain_text.encode())

    return result.hexdigest()


def do_signUp(user_attrs):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()

        if user_attrs is None or len(user_attrs) <= 0:
            return(RetCodes.missing_ent_attrs_error.value, "user attributes dictionary missing.", None)

        if 'email' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "Email Id is missing.", None)

        if 'name' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "User name is missing.", None)

        if 'status' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "User status is missing.", None)

        if 'password' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "User password is missing.", None)

        if 'tname' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "Company is missing.", None)

        if 'creation_date' not in user_attrs.keys():
            return(RetCodes.missing_ent_attrs_error.value, "Creation date is missing.", None)

        email = user_attrs['email'].strip()
        name = user_attrs['name'].strip()
        status = user_attrs['status']
        password = user_attrs['password'].strip()

        tname = user_attrs['tname'].strip()

        creation_date = user_attrs['creation_date']

        if not email:
            return(RetCodes.empty_ent_attrs_error.value, "Email empty or null.", None)

        if not name:
            return(RetCodes.empty_ent_attrs_error.value, "Name empty or null.", None)

        if not password:
            return(RetCodes.empty_ent_attrs_error.value, "password empty or null.", None)

        if not tname:
            return(RetCodes.empty_ent_attrs_error.value, "Company Name empty or null.", None)
        
        if not creation_date:
            return(RetCodes.empty_ent_attrs_error.value, "Creation date empty or null.", None)

        password = hashit(password)

        # insert a record in user table
        sql = """insert into users ( email, name, status, password,is_deleted,creation_date) 
				values (%s,%s, %s,%s,%s,%s) returning id """
        params = (email, name, status, password, False, creation_date)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        result = cursor.fetchone()
        uid = result[0]
        _logger.debug("user id created is {0}".format(uid))

        # insert a record into tenant
        sql = """insert into tenants ( name,status,is_deleted,creation_date) 
			values (%s, %s, %s, %s) returning id """
        params = (tname, 0, False, creation_date)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."
        result = cursor.fetchone()
        tid = result[0]
        _logger.debug("Tenant id created is %s", tid)

        # insert a record into tenant users table with isadmin field set to true
        sql = """insert into tenant_user_roles ( tid,uid,rid) 
			values (%s,%s, %s)  """
        params = (tid, uid, 1)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        db_con.commit()

        return (RetCodes.success.value, "User sign up successful.", None)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)


def save_user(tenantID, userID, name, email, password, roleID):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()

        if not tenantID:
            return(RetCodes.empty_ent_attrs_error.value, "Tenant ID empty or None.", None)

        if not userID:
            return(RetCodes.empty_ent_attrs_error.value, "User ID empty or None.", None)

        if not name:
            return(RetCodes.empty_ent_attrs_error.value, "Name empty or None.", None)

        if not email:
            return(RetCodes.empty_ent_attrs_error.value, "Email empty or None.", None)

        if not password:
            return(RetCodes.empty_ent_attrs_error.value, "password empty or None.", None)

        if not roleID:
            return(RetCodes.empty_ent_attrs_error.value, "Role ID empty or None.", None)

        password = hashit(password)

        if int(userID) == constants.NEW_ENTITY_ID:
            # insert a record in user table

            creation_date = datetime.now(tz=timezone.utc);

            sql = """insert into users ( email, name, password,is_deleted,status,creation_date) 
				values (%s,%s, %s,%s,%s,%s) returning id """
            params = (email, name, password, False, Status.active.value,creation_date)
            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            result = cursor.fetchone()
            userID = result[0]
            _logger.debug("user id created is {0}".format(userID))

            sql = """insert into tenant_user_roles ( tid,uid,rid) 
				values (%s,%s, %s)  """
            params = (tenantID, userID, roleID)
            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            db_con.commit()

            return (RetCodes.success.value, "User {0} added successful.".format(userID), userID)

        else:

            updation_date = datetime.now(tz=timezone.utc);

            sql = """update users set name = %s, email =%s, password =%s, updation_date =%s
					where id = %s"""
            params = (name, email, password, updation_date, userID)
            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            sql = """update tenant_user_roles set rid = %s where tid =%s and uid =%s """
            params = (roleID, tenantID, userID)
            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            db_con.commit()

            return (RetCodes.success.value, "User {0} record updated successful.".format(userID), userID)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)


def get(id):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """SELECT *,
				(select rid from tenant_user_roles where uid = %s ) as rid,
                (select tid from tenant_user_roles where uid = %s ) as tid
				FROM users 
				where id = %s"""

        params = (id, id, id)
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        user = cursor.fetchone()
        _logger.debug(user.tid)

        return(RetCodes.success.value, "User info for {0} successfully fetched from db".format(id), user)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def delete(userID):
    try:

        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        sql = """UPDATE users SET is_deleted = %s WHERE id = %s"""
        params = (True, userID)

        _logger.debug(sql)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        updated_rows = cursor.rowcount

        db_con.commit()

        if int(updated_rows) != 1:
            return(RetCodes.del_ent_error.value, "DELETE for User ID '{0}' failed. No. of rows updated was {1} instead of 1".format(userID, updated_rows), updated_rows)
        else:
            return(RetCodes.success.value, "DELETE for User ID '{0}' succeeded.".format(userID), updated_rows)

    except Exception as e:
        _logger.error(e)
        return(RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()

        dbUtils.returnToPool(db_con)

def confirm_user(email):
    try:

        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        sql = """UPDATE users SET status = %s WHERE email = %s"""
        params = (Status.active.value, email)

        _logger.debug(sql)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        updated_rows = cursor.rowcount

        if int(updated_rows) != 1:
            return(RetCodes.del_ent_error.value, "Confirmation for User ID '{0}' failed. No. of rows updated was {1} instead of 1".format(email, updated_rows), updated_rows)
        else:
            db_con.commit()
            return(RetCodes.success.value, "Confirmation for User ID '{0}' succeeded.".format(email), updated_rows)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return(RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()

        dbUtils.returnToPool(db_con)

def get_user_by_email(email):

    try:

        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        sql = """SELECT * FROM users WHERE is_deleted = %s and email =%s"""

        params = (False, email)

        _logger.debug(sql)
        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        user = cursor.fetchone()

        return(RetCodes.success.value, "User record with email ID  '{0}' successfully fetched from db".format(email), user)

    except Exception as e:
        _logger.error(e)
        return(RetCodes.server_error.value, str(e), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def list_users(tenant_id, orderBy=None, order=None):
    try:

        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query, params = None, None
        q1 = """SELECT * FROM users WHERE is_deleted = %s and
						id in (select uid from tenant_user_roles where tid =%s)
						order by """
        q2 = """"""
        q3 = """ id"""
        query, params = None, None

        if orderBy == "client":
            q2 = """ client, """
        elif orderBy == "status":
            q2 = """ status, """
        elif orderBy == "title":
            q2 = """ title, """
        elif orderBy == "open_date":
            q2 = """ open_date, """

        query = q1 + q2 + q3
        params = (False, tenant_id)

        _logger.debug(query)
        _logger.debug(cursor.mogrify(query, params))

        cursor.execute(query, params)

        userList = cursor.fetchall()
        if order == "DESC":
            userList = userList[::-1]
        for user in userList:
            _logger.debug(user)

        return (
            RetCodes.success.value,
            "User List successfully fetched from db",
            userList,
        )
    except Exception as e:
        _logger.error(e)
        return (RetCodes.server_error.value, str(e), None)
    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def is_tenant_deleted(tid):

    _logger.debug('Checking if tenant %s is deleted', tid)

    try:
        db_con = dbUtils.getConnFromPool()

        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """SELECT * from tenants where id = %s and is_deleted = %s"""

        data_tuple = (tid, True)

        _logger.debug(cursor.mogrify(query, data_tuple))
        cursor.execute(query, data_tuple)

        tList = cursor.fetchall()
        #_logger.debug ( "user length ",len(userList))

        if (tList is None or len(tList) == 0):
            _logger.debug("Tenant %s  is not deleted.", tid)
            return False
        else:
            _logger.debug("Tenant %s is deleted. ", tid)
            return True

    except Exception as dbe:
        _logger.error(dbe)
        raise

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def do_SignIn(id, password):

    try:
        password = hashit(password)

        try:
            db_con = dbUtils.getConnFromPool()
            cursor = dbUtils.getNamedTupleCursor(db_con)

            query = """SELECT * , 
					(select tid from tenant_user_roles where uid = id),
					(select rid from tenant_user_roles where uid = id) 
					FROM users WHERE
					email = %s and password = %s and is_deleted = %s 
                    and status=%s"""

            data_tuple = (id, password, False,Status.active.value)

            _logger.debug(cursor.mogrify(query, data_tuple))
            cursor.execute(query, data_tuple)

            userList = cursor.fetchall()
            #_logger.debug ( "user length ",len(userList))

            if (userList is None or len(userList) != 1):
                return (RetCodes.sign_in_failed,
                        "Failed to sign in.Please check your credentials and try again",
                        None)

            for user in userList:
                _logger.debug(user)
                if (is_tenant_deleted(user.tid)):
                    return(RetCodes.sign_in_failed, 'Tenant this user belongs to is deleted. Please contact your system administrator', user)

            return(RetCodes.success.value, "User List successfully fetched from db", userList[0])

        except Exception as dbe:
            _logger.error(dbe)
            return (RetCodes.server_error, str(dbe), dbe)
            # db_con.rollback()
            # raise

        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        _logger.error("In the exception block.")
        _logger.error(e)
        return (RetCodes.server_error, str(e),None)

def check_cur_pass_and_newPass(id, email, cur_password, new_password):
	try:
		new_password = hashit(new_password)
		cur_password = hashit(cur_password)
		try:
			db_con = dbUtils.getConnFromPool()
			cursor = dbUtils.getNamedTupleCursor(db_con)

			query = """SELECT * from users WHERE id =%s and email = %s and password =%s
					"""

			data_tuple = (id, email, cur_password)

			_logger.debug ( cursor.mogrify(query, data_tuple))
			u=cursor.execute(query, data_tuple).fetchOne()
			print(u.email)


		except Exception as dbe:
			_logger.error(dbe)
			db_con.rollback()
			return ( RetCodes.server_error, str(dbe), None)

		finally:
			if 'cursor' in locals() and cursor is not None:
				cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		_logger.error ("In the exception block.")
		_logger.error(e)
		return ( RetCodes.server_error, str(e))


def do_reset_password(id, email, cur_password, new_password):

    try:
        new_password = hashit(new_password)
        cur_password = hashit(cur_password)
        try:
            db_con = dbUtils.getConnFromPool()
            cursor = dbUtils.getNamedTupleCursor(db_con)

            query = """UPDATE users set password =%s 
					WHERE id =%s and email = %s and password =%s"""

            data_tuple = (new_password, id, email, cur_password)

            _logger.debug(cursor.mogrify(query, data_tuple))
            cursor.execute(query, data_tuple)

            assert cursor.rowcount == 1, "Failed to find user record. Please contact support"

            db_con.commit()
            return(RetCodes.success.value, "Password reset successfully.", id)

        except Exception as dbe:
            _logger.error(dbe)
            db_con.rollback()
            return (RetCodes.server_error, str(dbe), None)

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        _logger.error("In the exception block.")
        _logger.error(e)
        return (RetCodes.server_error, str(e))


def do_forgot_password(id, email, new_password):
    try:
        new_password = hashit(new_password)
        try:
            db_con = dbUtils.getConnFromPool()
            cursor = dbUtils.getNamedTupleCursor(db_con)

            query = """UPDATE users set password =%s 
					WHERE id =%s and email = %s"""

            data_tuple = (new_password, id, email)

            _logger.debug(cursor.mogrify(query, data_tuple))
            cursor.execute(query, data_tuple)

            assert cursor.rowcount == 1, "Failed to find user record. Please contact support"

            db_con.commit()
            return(RetCodes.success.value, "Password reset successfully.", id)

        except Exception as dbe:
            _logger.error(dbe)
            db_con.rollback()
            return (RetCodes.server_error, str(dbe), None)

        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            dbUtils.returnToPool(db_con)

    except Exception as e:
        _logger.error("In the exception block.")
        _logger.error(e)
        return (RetCodes.server_error, str(e))


def getTenantID( userID):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """select tid from tenant_user_roles where uid = %s"""

        params = (userID,)
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        tid = cursor.fetchone()
        _logger.debug(tid)

        return(RetCodes.success.value, "Tenant ID info for user {0} successfully fetched from db".format(userID), tid)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


# main entry point
if __name__ == "__main__":

    load_dotenv(find_dotenv())
    logging.basicConfig(level=logging.DEBUG)

    '''(retCode, msg, data ) = save_user(1,constants.NEW_ENTITY_ID,'c1_rec','c1_bhavyam@codeelan.com','bhavya',2)
	_logger.debug( retCode)
	_logger.debug ( msg)'''

    '''resultTuple = do_SignIn('c1_admin@gmail.com', '')
    print(resultTuple)'''

    (retCode,msg, data) = get(1)
    print(data)
    print(data.rid)

    #resultTuple = do_SignIn('bhavyam@codeelan.com','bhavya')
    #print(resultTuple)

