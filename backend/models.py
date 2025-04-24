from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Admin Table
class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    admin_password = db.Column(db.String(255), nullable=False) 

# Professional Table
class Professional(db.Model):
    __tablename__ = 'professionals'
    professional_id = db.Column(db.Integer, primary_key=True)
    professional_name = db.Column(db.String(100), nullable=False)
    professional_password = db.Column(db.String(255), nullable=False) 
    service_type = db.Column(db.String(100), nullable=False) 
    professional_number = db.Column(db.String(15), nullable=False)
    professional_email = db.Column(db.String(255))
    experience = db.Column(db.Integer, nullable=False)
    professional_pincode = db.Column(db.String(15), nullable=False)
    date_joined = db.Column(db.DateTime)
    professional_rating = db.Column(db.String(15), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False) 
    reason_for_blocking = db.Column(db.String(255), nullable=False)

# Customer Table
class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_password = db.Column(db.String(255), nullable=False)  
    contact_number = db.Column(db.String(15), nullable=False)
    customer_rating = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), nullable=False) 
    reason_for_blocking = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(120))

# Service Table
class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50))
    description = db.Column(db.String(255))

# ServiceRequest Table
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.professional_id'), nullable=True)
    date_of_request = db.Column(db.DateTime)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20))  
    rating_for_professional = db.Column(db.String(15), nullable=False)
    rating_for_customer = db.Column(db.String(15), nullable=False)
    remarks_for_professional = db.Column(db.String(255))
    remarks_for_customer = db.Column(db.String(255))
