import dbUtils
import json
from datetime import datetime
from datetime import timezone 
from dataclasses import dataclass
from typing import List

# importing enum for enumerations

CART_STATUS_INACTIVE = 0
CART_STATUS_SHOPPING = 1
CART_STATUS_CHECKEDOUT = 2

PRODUCT_STATUS_INACTIVE = 0
PRODUCT_STATUS_ACTIVE = 1

PRODUCT_BF_MONTHLY = 1

@dataclass(frozen=True)
class Product:
	id: str
	unit_price: float
	desc: str
	currency : str
	billing_frequency : int = PRODUCT_BF_MONTHLY
	status : int =  PRODUCT_STATUS_ACTIVE

@dataclass( frozen = True)
class Cart:
	id : str
	productList : List[Product] #ProductList


def add_product( product ):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			#dt = datetime.now()   
			#utc_time = dt.replace(tzinfo = timezone.utc) 
			dt = datetime.now(tz=timezone.utc) 
			#insert into user table
			insert_query = """INSERT INTO products (id, unit_price,currency, billing_frequency, status, created_on) 
								VALUES 
								(%s,%s,%s, %s,%s,%s)"""
			
			data_tuple = (product.id, product.unit_price, product.currency, 
					product.billing_frequency,product.status,dt)
			cursor.execute(insert_query, data_tuple)

			db_con.commit()
			return (0, "Product added successfully.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		return ( -2, str(e))

def update_product(id, updates):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			#dt = datetime.now()   
			#utc_time = dt.replace(tzinfo = timezone.utc) 
			dt = datetime.now(tz=timezone.utc) 

			updates['updated_on'] = dt

			sql_template = "UPDATE products SET ({}) = %s WHERE id = '{}'"
			sql = sql_template.format(', '.join(updates.keys()), str(id))
			params = (tuple(updates.values()),)
			print ( cursor.mogrify(sql, params))
			cursor.execute(sql, params)
			updated_rows = cursor.rowcount
			
			if updated_rows == 1:
				db_con.commit()
				return (0, "Product updated successfully.")
			else:
				db_con.rollback()
				return (1, "Failed : No product found for the given product ID.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		return ( -2, str(e))
		
def list_products(status=PRODUCT_STATUS_ACTIVE):
	error = ''
	try:
		try:
			db_con = dbUtils.getConnFromPool()
			#cursor = db_con.cursor()
			cursor = dbUtils.getNamedTupleCursor(db_con)

			sql = "SELECT * FROM products where status = %s"
			data_tuple = (status,)

			cursor.execute(sql, data_tuple)
			productList = cursor.fetchall()

			for product in productList:
				print("product = ", product.id, "\n")
			
			db_con.commit()

			return (0, "Product list executed successfully.",productList)

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		return ( -2, str(e))

def create_cart(cart_id, status = CART_STATUS_SHOPPING):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			dt = datetime.now(tz=timezone.utc) 
			print(dt)
			#utc_time = dt.replace(tzinfo = timezone.utc) 
			#print(utc_time)
			#insert into user table
			insert_query = """INSERT INTO carts (id, status, created_on) 
								VALUES 
								(%s,%s,%s)"""
			
			data_tuple = (cart_id,status,dt)
			cursor.execute(insert_query, data_tuple)

			db_con.commit()
			return (0, "Cart created successfully.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("Exception occured in cart creation.")
		return ( -2, str(e))

def add_product_to_cart(cart_id, product_id, qty):

	error = ''
	try:

		try:
			#TODO: ensure product_id is in active state                
			
			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			dt = datetime.now(tz=timezone.utc) 
			print(dt)

			insert_query = """INSERT INTO cart_products (cart_id, product_id, created_on,qty) 
								VALUES 
								(%s,%s,%s, %s)"""
			
			data_tuple = (cart_id,product_id,dt,qty)
			cursor.execute(insert_query, data_tuple)

			db_con.commit()
			return (0, "Product successfully added to Cart.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("Exception occured in adding products to cart.")
		return ( -2, str(e))

def remove_product_from_cart(cart_id, product_id):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			#utc_time = dt.replace(tzinfo = timezone.utc) 
			#print(utc_time)
			#insert into user table
			sql_template = """DELETE FROM cart_products WHERE cart_id = %s and product_id = %s"""
			
			data_tuple = (cart_id,product_id)
			cursor.execute(sql_template, data_tuple)

			db_con.commit()
			return (0, "Product successfully removed from Cart.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("Exception occured while removing product from cart.")
		return ( -2, str(e))

def get_cart_details(cart_id):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = dbUtils.getNamedTupleCursor(db_con)

			sql = """select cp.cart_id, p.*,cp.qty from cart_products as cp, products as p 
				where cp.cart_id = %s and p.status = %s and cp.product_id = p.id"""
			data_tuple = (cart_id,PRODUCT_STATUS_ACTIVE)
			
			
			cursor.execute(sql, data_tuple)

			result = cursor.fetchall()

			db_con.commit()
			return (0, "Cart Items details successfully fetched.", result)

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe), None)
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("Exception occured while fetching product details from cart.")
		return ( -2, str(e), None)

def get_cart_TotalAmount(cart_id):
	
	(retCode,msg, results ) = get_cart_details(cart_id)
	if (retCode !=0):
		return ( retCode, "Failed to get cart Details.", None)
	
	total_amt = 0
	for record in results:
		total_amt = total_amt + record.qty * record.unit_price	
	
	return ( retCode, msg, total_amt)


def checkout_cart(cart_id):

	error = ''
	try:

		try:

			db_con = dbUtils.getConnFromPool()
			cursor = db_con.cursor()

			dt = datetime.now(tz=timezone.utc) 
			print(dt)


			sql = """UPDATE carts set status = %s, updated_on = %s where id = %s""" 
			data_tuple = (CART_STATUS_CHECKEDOUT,dt,cart_id)
			cursor.execute(sql, data_tuple)
			
			#get total amount due for the cart 
			(retCode,msg,total_amt) = get_cart_TotalAmount(cart_id)
			if retCode !=0:
				return ( 1, "Failed to calculate total amount")
			
			if total_amt == None :
				return ( 2, "Failed to calculate total amount")

			
			#generate invoice
			invoice_id = "invoice-" + cart_id

			sql = """INSERT INTO invoices( invoice_id, cart_id, created_on, amt_due, amt_paid) 
			VALUES ( %s, %s, %s, %s,%s) """ 
			data_tuple = (invoice_id,cart_id, dt,total_amt,0)
			cursor.execute(sql, data_tuple)
			
			db_con.commit()

			return (0, "Cart checkedout successfully.")

		except Exception as dbe:
			print(dbe)
			db_con.rollback()
			return (-1, str(dbe))
	
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)

	except Exception as e:
		#flash(e)
		print ("Exception occured in cart checkout process.")
		return ( -2, str(e))



## main entry point
if __name__ == "__main__":

		
	"""(retCode, msg ) = add_product('Starter1', 5,'USD')
	print( retCode)
	print ( msg)
	"""

	(retCode, msg, productList ) = list_products()
	print( retCode)
	print (msg)
	print(productList)

	print( "size of product list is ", len(productList) )

	(retCode, msg, cartDetailsList ) = get_cart_details('CART10')

	print("cart details size is ", len(cartDetailsList))

	(retCode,msg) = checkout_cart( 'CART10')


	#print( cartDetailsList)

	#for p in productList:
	#    update_product( p.id, {'description' : 'Description of {}'.format(p.id) })
	
"""     (retCode, msg ) = add_product(Product(id = 'Starter1',unit_price =5,desc=None,currency='USD'))
	print( retCode)
	print ( msg) """
	


