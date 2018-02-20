from flask import Flask,jsonify,request,Response,json,Request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app = Flask(__name__)





app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:password@mysql:3306/certificateManagement'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
DATABASE='certificateManagement'

# A Customer:

# Has a name

# Has an email address

# Has a password

# May have zero to many Certificates

class Customer(db.Model):
    __tablename__ = 'customer_info'
    customer_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Unicode(20),nullable=False)
    email = db.Column(db.Unicode(40),nullable=False)
    password = db.Column(db.Unicode(20),nullable=False)
    certificate_count = db.Column(db.Integer,nullable=False)

    def __init__(self,name,email,password,certificate_count):
       # self.customer_id=customer_id
        self.name=name
        self.email=email
        self.password=password
        self.certificate_count=certificate_count

# A Certificate:

# Belongs to one and only one Customer

# Can be either active or inactive

# Has a private key

# Has a certificate body

class Certificate(db.Model):
    __tablename__ = 'certificate_management'
    certificate_id = db.Column(db.Integer, primary_key=True, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Unicode(20),nullable=False)
    key = db.Column(db.Unicode(40),nullable=False)
    certificate_body=db.Column(db.LargeBinary,nullable=False)

    def __init__(self,customer_id,state,key,certificate_body):
        #self.certificate_id=certificate_id
        self.customer_id=customer_id
        self.state=state
        self.key=key
        self.certificate_body=certificate_body






@app.route("/")
def home():
	return render_template('index.html')

@app.route("/v1/addcustomer")
def add_customer():
	return render_template('addCustomer.html')



# add a new customer
@app.route('/v1/customers',methods=['POST']) 
def post_customer():
	customer_info=request.get_json(force='True')
	name=customer_info['name']
	email=customer_info['email']
	password=customer_info['password']
	certificate_count= 0
	engine = create_engine("mysql://root:password@mysql:3306")
	engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE))
	engine.execute("USE %s "%(DATABASE))
	db.create_all()
	new_customer=Customer(name,email,password,certificate_count)
	db.session.add(new_customer)
	db.session.commit()
	print new_customer
	data={'id':str(new_customer.customer_id),'name':new_customer.name, 'email':new_customer.email,'certificate_count':new_customer.certificate_count}
	resp = Response(response=json.dumps(data),
		status=201,
		mimetype="application/json")
	return resp 

#get customer
@app.route('/v1/customers/<string:customer_id>', methods=['GET'])
def getCustomer(customer_id):
	customer=Customer.query.filter_by(customer_id=customer_id).first()
	if customer==None:
		resp = Response(response=None,status=204,mimetype="application/json")
		return resp
	data={'id':str(customer.customer_id),'name':customer.name, 'email':customer.email,'password':customer.password,'certificate_count':customer.certificate_count}
	resp = Response(response=json.dumps(data),status=200,mimetype="application/json")
	return resp

#delete customer
@app.route("/v1/deletecustomer")
def del_customer():
  return render_template('deleteCustomer.html')

@app.route('/v1/customers/<string:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
	customer=Customer.query.filter_by(customer_id=customer_id).first()
	if customer==None:
		data={"message":"Customer doesnot exists !"}
		resp = Response(response=json.dumps(data),status=400,mimetype="application/json")
		return resp
    # Also Delete certificates for that customer from database
	certificates=Certificate.query.filter_by(customer_id=customer_id).all()
	if certificates is not None:
		for certificate in certificates:
			db.session.delete(certificate)

	db.session.delete(customer)
	db.session.commit()

    
	data={'message':'Customer succesfully Deleted!','id':str(customer.customer_id),'name':customer.name, 'email':customer.email,'password':customer.password,'certificate_count':customer.certificate_count}
	resp = Response(response=json.dumps(data),status=200,mimetype="application/json")
	return resp

#delete customer
@app.route("/v1/addcertificate")
def add_certificate():
  return render_template('addCertificates.html')

# add a new certificate
@app.route('/v1/customers/certificates',methods=['POST']) 
def create_certificates():
	certificate_info=request.get_json(force='True')
	#certificate_id = certificate_info['certificate_id']
	customer_id = certificate_info['customer_id']
	customer=Customer.query.filter_by(customer_id=customer_id).first()
	if customer==None:
		data={"message":"Customer doesnot exists !"}
		resp = Response(response=json.dumps(data),status=400,mimetype="application/json")
		return resp 
	customer.certificate_count=customer.certificate_count+1
	state = certificate_info['state']
	key = certificate_info['key']
	certificate_body=certificate_info['certificate_body']
	engine = create_engine("mysql://root:password@mysql:3306")
	engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE))
	engine.execute("USE %s "%(DATABASE))
	db.create_all()
	new_certificate=Certificate(customer_id,state,key,certificate_body)
	db.session.add(new_certificate,customer)
	db.session.commit()
	print new_certificate
	data={'message':'succesfully created : certificate ID : '+ str(new_certificate.certificate_id),'customer_id':str(new_certificate.customer_id),'state':new_certificate.state, 'key':new_certificate.key,'certificate_body':new_certificate.certificate_body}
	resp = Response(response=json.dumps(data),
		status=201,
		mimetype="application/json")
	return resp 


# get certificate by customer_id
@app.route('/v1/customers/<string:customer_id>/certificates', methods=['GET'])
def get_certificates(customer_id):
	certificates=Certificate.query.filter_by(customer_id=customer_id).all()
	if certificates==None:
		resp = Response(response=None,status=404,mimetype="application/json")
		return resp
	certificate_list=[]
	for certificate in certificates:
		certificate_data={'id':str(certificate.certificate_id),'state':certificate.state, 'key':certificate.key,'certificate_body':certificate.certificate_body}
		certificate_list.append(certificate_data)
	data={'certificates':certificate_list}
	resp = Response(response=json.dumps(data),status=200,mimetype="application/json")
	return resp


@app.route("/v1/listCertificates")
def list_certificate():
  return render_template('listCertificates.html')

# get active/deactive certificate by customer_id
@app.route('/v1/customers/<string:customer_id>/certificates/<string:state>', methods=['GET'])
def get_certificates_by_state(customer_id,state):
	certificates=Certificate.query.filter_by(customer_id=customer_id).all()
	print certificates
	if certificates==None:
		resp = Response(response=None,status=404,mimetype="application/json")
		return resp
	certificate_list=[]
	for certificate in certificates:
		certificate_data={'id':str(certificate.certificate_id),'state':certificate.state, 'key':certificate.key,'certificate_body':certificate.certificate_body}
		certificate_list.append(certificate_data)
	data={'certificates':certificate_list}
	print certificate_list
	resp = Response(response=json.dumps(data),status=200,mimetype="application/json")
	return resp


@app.route("/v1/updateCertificate")
def update_certificate():
  return render_template('updateCertificate.html')

#update certificate state
@app.route('/v1/certificates/<string:certificate_id>',methods=['PUT'])
def update_certificate_state(certificate_id):
	certificate_state=request.get_json(force='True')
	certificate_info=Certificate.query.filter_by(certificate_id=certificate_id).first()
	certificate_info.state=certificate_state['state']
	db.session.commit()
	data={"message":"Updated succesfully !"}
	resp = Response(response=json.dumps(data),
		status=202,
		mimetype="application/json")
	return resp


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", debug=True)