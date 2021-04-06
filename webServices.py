from flask import Flask, jsonify, request 

import random
from flask_mail import Mail, Message 
from flask_cors import CORS

import constants
import userUtils
import emailUtils
from jinja2 import Environment, FileSystemLoader
from werkzeug.utils import secure_filename

import productUtils

import os
#import json
import decimal
import stripe
stripe.api_key = os.environ.get("STRIPE_API_KEY")



ALLOWED_EXTENSIONS = {'pdf', 'docx'}
YOUR_DOMAIN = 'http://localhost:4000'


app = Flask(__name__) 
CORS(app)

mail = Mail(app) # instantiate the mail class 
   
# configuration of mail 

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '43476df397bb98'
app.config['MAIL_PASSWORD'] = '549b9cb128c807'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOAD_FOLDER'] = './temp'

mail = Mail(app) 


@app.route('/v1/getOTP', methods = ['POST']) 	
def getOTP():
	try:
		print('**** Processing POST request **********')
		print(request.json)	

		if request.method != "POST":
			return jsonify({'retcode': -101}, {'msg': 'POST method not found.'}),400
		
		if ('email' in request.json == False):
			return jsonify({'retcode': -102}, {'msg': 'Email parameter not found in request. '}),400

		(retCode,msg) = userUtils.getOTP(str(request.json['email']))
		
		return jsonify({'retcode': retCode}, {'msg': msg})

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -110},{'msg':str(e)}) ,400


@app.route('/v1/signUp', methods = ['POST'])
def userSignUp():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		assert 'username'  in request.json , "User ID not found in request json."
		assert 'email'  in request.json , "User ID not found in request json."

		print('**** Processing POST request **********')
		print(request.json)			
		
		new_username = str(request.json['username'])
		print ( new_username)

		new_email = str(request.json['email'])
		print ( new_email)


		(retCode,msg) = userUtils.signUp(new_username,new_email)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400


@app.route('/v1/authenticate', methods = ['POST'])
def authenticate():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		print('**** Processing POST request **********')
		
		assert 'Email'  in request.json , "Email not found in request json."
		assert 'OTP' in request.json, "OTP not found in request json."

		#if userID exists in request.json == false :
		#	raise 
		email = request.json['Email']
		print ( email)

		otp = request.json['OTP']
		print ( otp)
		
		(retCode,msg) = userUtils.userSignIn(email,otp)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/v1/productAdd', methods = ['POST'])
def productAdd():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'productID'  in request.json , "Product ID not found in request json."
		assert 'unitPrice'  in request.json , "Unit Price not found in request json."
		assert 'currency' in request.json , "Currency Price not found in request json."
		#assert 'billingFrequency' in request.form , "Billing Frequency not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		productID = str(request.json['productID'])
		print ( productID)

		unitPrice = str(request.json['unitPrice'])
		print ( unitPrice)

		currency = str(request.json['currency'])
		print ( currency)			

		#(retCode,msg) = productUtils.add_product(productID, unitPrice,currency)
		(retCode,msg) = productUtils.add_product(productUtils.Product(id = productID,
			unit_price = unitPrice,desc=None,
			currency=currency))
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) 

@app.route('/v1/deactivateProduct', methods = ['POST'])
def deactivateProduct():
	error = ''
	try:		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		#assert 'productID'  in request.query_string , "Product ID not found in request json."

		print('**** Processing POST request **********')
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		assert 'productID'  in request.json , "Product ID not found in request json."

		productID = request.json['productID']


		(retCode,msg) = productUtils.update_product(productID, 
				{'status' : productUtils.PRODUCT_STATUS_INACTIVE} )
			
		return jsonify({'retcode': retCode},{'msg': 'Product deactivated successfully.'})

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/listProducts', methods = ['POST'])
def listProducts():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."


		print('**** Processing POST request **********')
		#print(request.json)			
		
		(retCode,msg, productList) = productUtils.list_products()

		return jsonify({'retcode': retCode},{'msg': msg}, {'result': productList})
		#return jsonify(json.dumps(result, cls=CustomEncoder))

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/createCart', methods = ['POST'])
def createCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cart ID not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		(retCode,msg) = productUtils.create_cart(cartID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/addProductToCart', methods = ['POST'])
def addProductToCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "parameter 'cartID' not found in request json."
		assert 'productID'  in request.json , "parameter productID not found in request json."
		assert 'qty'  in request.json , "parameter 'qty' not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		productID = str(request.json['productID'])

		(retCode,msg) = productUtils.add_product_to_cart(cartID,productID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400


@app.route('/v1/removeProductFromCart', methods = ['POST'])
def removeProductFromCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cartID not found in request json."
		assert 'productID'  in request.json , "productID not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		productID = str(request.json['productID'])

		(retCode,msg) = productUtils.remove_product_from_cart(cartID,productID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/getCartDetails', methods = ['POST'])
def getCartDetails():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cartID not found in request json."

		print('**** Processing POST request **********')
		
		cartID = str(request.json['cartID'])

		(retCode,msg,result) = productUtils.get_cart_details(cartID)
		return jsonify({'retcode': retCode},{'msg': msg}, {'result': result})
		
	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/checkoutCartUsingSwipe', methods = ['POST'])
def checkoutCartUsingSwipe():
	error = ''
	try:		
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		
		assert 'cartID'  in request.json , "cartID not found in request json."
		assert 'successURL' in request.json , " Success URL parameter not found in request json."
		assert 'cancelURL' in request.json , " Cancel URL parameter not found in request json."

		print('**** Processing POST request **********')

		cartID = str(request.json['cartID'])
		successURL = str(request.json['successURL'])
		cancelURL = str( request.json['cancelURL'])
		(retCode,msg) = productUtils.checkout_cart(cartID)

		if retCode != 0: 
			return jsonify({'retcode': 1},{'msg': 'Check out failed.'})	
		
		checkout_session_id = swipe_create_checkout_session(cartID,"http://wwww.https://www.wemoodle.cloud/", "http://www.fulgorithm.com/")	
			#jsonify({'id': checkout_session.id})
		#checkout_session_id = productUtils.create_checkout_session(cartID, success_url,cancel_url,)
		
		print("got session id")
		#print(checkout_session_id)
		#return( checkout_session_id)
		#return jsonify({'retcode': retCode},{'msg': msg},{'sessionId': checkout_session_id})
		return jsonify({'id': checkout_session_id})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': 400},{'msg': str(e)}) , 400

def swipe_create_checkout_session( cart_Id, success_url,cancel_url,
	payment_method_type = 'card',mode ='payment'):

	try:
		#getCartDetails(cart_Id)
		(retCode,msg,records) = productUtils.get_cart_details(cart_Id)
		for record in records:
			currency = record.currency
			qty = record.qty
			product_desc = record.description
			unit_amt = record.unit_price
			break

		#currency = 'INR'
		#unit_amt = 35000
		#qty = 2
		#product_desc = 'www.weMoodle.cloud Monthly Basic subscription'
		payment_method_types = [payment_method_type]
		line_items =[
			{
				'price_data' : {
					'currency' : currency,
					'unit_amount' : unit_amt,
					'product_data' : {
						'name' : product_desc,
						'images' : ['https://i.imgur.com/EHyR2nP.png'],
					}
				},
				'quantity' : qty,
			},
		]
		print(line_items)

		checkout_session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
        )

		print(checkout_session.id)
		return checkout_session.id

	except Exception as e:
		raise e


def create_checkout_session2(cartID, success_url,cancel_url, payment_method_type = 'card', payment_mode = 'payment' ):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 5,
                        'product_data': {
                            'name': 'www.weMoodle.cloud Monthly Basic subscription',
                            'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
        return checkout_session.id #jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403
 

# driver function 
if __name__ == '__main__': 
	app.run(debug = True, port=4000) 
