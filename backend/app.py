from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Admin, Customer, Professional, ServiceRequest, Service
import bcrypt
import json
import logging
from datetime import datetime, timedelta  as dt_timedelta
from celery import Celery
from flask_mail import Mail, Message
import os
import redis
from celery.signals import task_sent
import time
from celery.schedules import timedelta,crontab
import csv
from flask import send_file
from celery.result import AsyncResult


app = Flask(__name__, static_folder='static')

# CORS Configuration
CORS(app, origins=["http://54.242.17.17:8080"], methods=["POST", "GET","PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  
jwt = JWTManager(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'   #'sqlite:///household_services.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  

logging.basicConfig(level=logging.INFO)
app.config['SQLALCHEMY_ECHO'] = True

# Redis Configuration
app.config['CELERY_BROKER_URL'] = 'redis://54.242.17.17:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://54.242.17.17:6379/0'

def make_celery(app):
    celery = Celery(
        "app",
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# @celery.on_after_configure.connect
# def setup_tasks(sender, **kwargs):
#     print("HI")
#     sender.add_periodic_task(10.0, send_daily_reminders.s(), name='add every 10')  

@celery.on_after_configure.connect
def setup_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=12, minute=30),  # UTC 12:30 pm = Indian Zone 6:00pm
        send_daily_reminders.s(),
        name='Daily reminder at 6 PM'
    )

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=6, minute=30),  # utc 6:30 am= ist 12:00 pm
        generate_monthly_report.s(),
        name="Monthly Report - 1st day of month"
    )

# @celery.on_after_configure.connect
# def setup_tasks(sender, **kwargs):
#     now = datetime.now()
    
#     # Target time: 2:05 PM (14:05)
#     target_time = now.replace(hour=8, minute=45, second=0, microsecond=0)

#     # If it's already past 2:05 PM today, schedule for tomorrow
#     if now >= target_time:
#         target_time += dt_timedelta(days=1)

#     # Calculate the delay in seconds
#     delay = (target_time - now).total_seconds()

#     # First execution (apply_async for exact delay)
#     send_daily_reminders.apply_async(countdown=delay)

#     # Schedule future runs every 24 hours
#     sender.add_periodic_task(
#         timedelta(days=1),  
#         send_daily_reminders.s(),
#         name="Daily reminder every 24 hours"
#     )
@celery.task()
def add_together():
    time.sleep(5)
    return (1+2)

redis_client = redis.Redis(host="54.242.17.17", port=6379, db=0)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "kasturisangale2811@gmail.com"
app.config['MAIL_PASSWORD'] = " "
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER']="kasturisangale2811@gmail.com"
#app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def schedule_task_using_sender():
    """Schedule the send_daily_reminders task using the Celery sender."""
    add_together.apply_async(countdown=60)  
    print("Task scheduled using sender.")
# ======================== Helper Functions ======================== #
def hash_password(raw_password):
    """Hash a plaintext password."""
    return bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(raw_password, hashed_password):
    """Verify a plaintext password against a hashed password."""
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ======================== Routes ================================= #

# Customer Register Route
@app.route('/api/customers/register', methods=['POST'])
def customer_signup():
    raw_password = request.json.get('customer_password')
    customer_name = request.json.get('customer_name')
    customer_number = request.json.get('customer_number')
    customer_email = request.json.get('customer_email')
    hashed_password = hash_password(raw_password)
    new_customer = Customer(
        customer_password=hashed_password,
        customer_name=customer_name,
        contact_number=customer_number,
        customer_rating='0',
        customer_email = customer_email,
        status='active',
        reason_for_blocking='Not Applicable'
    )
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({
        'message': 'Customer registered successfully!',
        'customer_id': new_customer.customer_id  # Assuming customer_id is the primary key
    }), 201

# Update verification status of a professional
@app.route('/api/admins/professionalinfo/updateverification/<int:professional_id>', methods=['POST'])
def verify_professional(professional_id):
    try:
        professional = Professional.query.get_or_404(professional_id)
        new_verified_status = request.json.get('verified')
        professional.verified = new_verified_status
        db.session.commit()
        return jsonify({"success": True, "message": "Professional verification status updated."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

#Block customer from admin side
@app.route('/api/admins/customerinfo/blockcustomer/<int:customer_id>', methods=['POST'])
@jwt_required()
def block_customer(customer_id):
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    blocked_reason = request.json.get('blocked_reason')
    if not blocked_reason:
        return jsonify({'success': False, 'message': 'Reason for blocking is required'}), 400
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    customer.reason_for_blocking = blocked_reason
    customer.status = 'blocked'  
    db.session.commit() 
    return jsonify({'success': True, 'message': 'Customer has been successfully blocked'}), 200

# Get all customer data for Admin
@app.route('/api/admins/customerinfo', methods=['GET'])
@jwt_required()  
def get_customers():
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    customers = Customer.query.filter(Customer.status.in_(['active', 'blocked'])).all()
    customer_data = []
    for customer in customers:
        service_requests = db.session.query(ServiceRequest).filter(ServiceRequest.customer_id == customer.customer_id).all()
        services_requested = []
        for req in service_requests:
            service = Service.query.filter_by(service_id=req.service_id).first()
            if service:
                service_status = req.service_status.lower()  
                if service_status == 'requested':
                    color = 'yellow'
                elif service_status == 'assigned':
                    color = 'green'
                elif service_status == 'closed':
                    color = 'red'
                else:
                    color = 'black'  
                services_requested.append({
                    'service_name': service.service_name,
                    'status': service_status,
                    'color': color 
                })
        customer_data.append({
            'id': customer.customer_id,
            'name': customer.customer_name,
            'phone': customer.contact_number,
            'email': customer.customer_email,
            'rating': customer.customer_rating,
            'status': customer.status,  
            'reason_for_blocking': customer.reason_for_blocking if customer.status == 'blocked' else None,
            'services_requested': services_requested  
        })
    return jsonify({'message': 'Customers retrieved successfully', 'customers': customer_data}), 200

#Unblock Customer from admin side
@app.route('/api/admins/customerinfo/unblockcustomer/<int:customer_id>', methods=['POST'])
@jwt_required()
def unblock_customer(customer_id):
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    if customer.status == 'active':
        return jsonify({'success': False, 'message': 'Customer is already active'}), 400
    customer.status = 'active'
    customer.reason_for_blocking = 'Not Applicable'  
    db.session.commit() 
    return jsonify({'success': True, 'message': 'Customer has been successfully unblocked'}), 200

# Professional Register 
@app.route('/api/professionals/register', methods=['POST'])
def professional_signup():
    raw_password = request.json.get('professional_password')
    professional_name = request.json.get('professional_name')
    service_type = request.json.get('service_type')
    professional_number = request.json.get('professional_number')
    professional_email = request.json.get('professional_email')
    years_of_experience = request.json.get('years_of_experience')
    pin_code = request.json.get('pin_code')
    hashed_password = hash_password(raw_password)
    new_professional = Professional(
        professional_name=professional_name,
        professional_password=hashed_password,
        service_type=service_type,
        professional_number=professional_number,
        professional_email=professional_email,
        experience=years_of_experience,
        professional_pincode=pin_code,
        date_joined=datetime.utcnow(),
        professional_rating="0",
        status='active',
        verified=0,
        reason_for_blocking='Not Applicable'
    )
    db.session.add(new_professional)
    db.session.commit()
    return jsonify({'message': 'Professional registered successfully!'}), 201


#Block Professional from admin side
@app.route('/api/admins/professionalinfo/blockprofessional/<int:professional_id>', methods=['POST'])
@jwt_required()
def block_professional(professional_id):
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    blocked_reason = request.json.get('blocked_reason')
    if not blocked_reason:
        return jsonify({'success': False, 'message': 'Reason for blocking is required'}), 400
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return jsonify({'success': False, 'message': 'Professional not found'}), 404
    professional.reason_for_blocking = blocked_reason
    professional.status = 'blocked'  
    db.session.commit() 
    return jsonify({'success': True, 'message': 'Professional has been successfully blocked'}), 200

#fetch all services from admin side
@app.route('/api/admins/serviceinfo', methods=['GET'])
def get_services():
    try:
        services = Service.query.all()
        services_data = [
            {
                "id": service.service_id,
                "service_name": service.service_name,
                "price": service.price,
                "time_required": service.time_required,
                "description": service.description,
            }
            for service in services
        ]
        return jsonify({"services": services_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Add a new service for admin side
@app.route('/api/admins/addservice', methods=['POST'])
def add_service():
    try:
        data = request.json
        new_service = Service(
            service_name=data["service_name"],
            price=data["price"],
            time_required=data.get("time_required", ""),
            description=data.get("description", ""),
        )
        db.session.add(new_service)
        db.session.commit()
        return jsonify({"success": True, "service": {
            "id": new_service.service_id,
            "service_name": new_service.service_name,
            "price": new_service.price,
            "time_required": new_service.time_required,
            "description": new_service.description,
        }}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#delete a service for admin side
@app.route('/api/admins/service/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404
        db.session.delete(service)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#edit service for admin side
@app.route('/api/admins/service/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    data = request.get_json()
    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    service.service_name = data['service_name']
    service.price = data['price']
    service.time_required = data['time_required']
    service.description = data['description']
    db.session.commit()
    return jsonify({'success': True, 'service': {
        'id': service.service_id,
        'service_name': service.service_name,
        'price': service.price,
        'time_required': service.time_required,
        'description': service.description
    }})

# Unblock Professional for admin side
@app.route('/api/admins/professionalinfo/unblockprofessional/<int:professional_id>', methods=['POST'])
@jwt_required()
def unblock_professional(professional_id):
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if not professional:
        return jsonify({'success': False, 'message': 'Professional not found'}), 404
    if professional.status == 'active':
        return jsonify({'success': False, 'message': 'Professional is already active'}), 400
    professional.status = 'active'
    professional.reason_for_blocking = 'Not Applicable'  
    db.session.commit()  
    return jsonify({'success': True, 'message': 'Professional has been successfully unblocked'}), 200

# Get all professionals data for Admin
@app.route('/api/admins/professionalinfo', methods=['GET'])
@jwt_required()  
def get_professionals():
    user_identity = json.loads(get_jwt_identity()  )
    if user_identity['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    professionals = Professional.query.filter(Professional.status.in_(['active', 'blocked'])).all()
    professional_data = []
    for professional in professionals:
        service_requests = db.session.query(ServiceRequest).filter(ServiceRequest.professional_id == professional.professional_id).all()
        services_requested = []
        for req in service_requests:
            service = Service.query.filter_by(service_id=req.service_id).first()
            if service:
                service_status = req.service_status.lower()
                if service_status == 'requested':
                    color = 'yellow'
                elif service_status == 'assigned':
                    color = 'green'
                elif service_status == 'closed':
                    color = 'red'
                else:
                    color = 'black'
                services_requested.append({
                    'service_name': service.service_name,
                    'status': service_status,
                    'color': color 
                })
        professional_data.append({
            'id': professional.professional_id,
            'name': professional.professional_name,
            'phone': professional.professional_number,
            'servicetype': professional.service_type,
            'experience': professional.experience,
            'pincode': professional.professional_pincode,
            'datejoined': professional.date_joined,
            'rating': professional.professional_rating,
            'verified': professional.verified,
            'status': professional.status, 
            'reason_for_blocking': professional.reason_for_blocking if professional.status == 'blocked' else None,
            'services_requested': services_requested
        })
    return jsonify({'message': 'Professionals retrieved successfully', 'professionals': professional_data}), 200

# Admin Login 
@app.route('/api/admins/login', methods=['POST'])
def admin_login():
    admin_id = request.json.get('admin_id')
    password = request.json.get('admin_password')
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    print("CREDDDDD: ",admin_id,password,admin.admin_password)
    print("Resultttttt",admin and check_password(password, admin.admin_password))
    if admin and check_password(password, admin.admin_password):
        access_token = create_access_token(identity=json.dumps({'id': admin.admin_id, 'role': 'admin'}), expires_delta=timedelta(hours=1))
        return jsonify({'message': 'Login successful!', 'token': access_token, 'admin_name': admin.admin_name}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Customer Login 
@app.route('/api/customers/login', methods=['POST'])
def customer_login():
    customer_id = request.json.get('customer_id')
    password = request.json.get('customer_password')
    customer = Customer.query.filter_by(customer_id=customer_id).first()
    if customer:
        if customer.status == 'blocked':
            return jsonify({'message': f'Your account is blocked. Reason: {customer.reason_for_blocking}'}), 403  
        if check_password(password, customer.customer_password):
            access_token = create_access_token(identity=json.dumps({'id': customer.customer_id, 'role': 'customer'}), expires_delta=timedelta(hours=1))
            return jsonify({'message': 'Login successful!', 'token': access_token, 'customer_name': customer.customer_name}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Professional Login
@app.route('/api/professionals/login', methods=['POST'])
def professional_login():
    professional_id = request.json.get('professional_id')
    password = request.json.get('professional_password')
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    if professional and check_password(password, professional.professional_password):
        access_token = create_access_token(
    identity=json.dumps({'id': professional.professional_id, 'role': 'professional'}),
    expires_delta=timedelta(hours=1)
)

        return jsonify({'message': 'Login successful!', 'token': access_token, 'professional_name': professional.professional_name}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

#Update password for admin side
@app.route('/api/admins/updatepassword', methods=['PUT'])
@jwt_required()
def update_password():
    user_identity = json.loads(get_jwt_identity()  )
    new_password = request.json.get('new_password')
    app.logger.info(f"Update password request received for user: {user_identity['id']}")
    if not new_password:
        app.logger.error("New password is missing")
        return jsonify({'message': 'New password is required'}), 400
    admin = Admin.query.filter_by(admin_id=user_identity['id']).first()
    if admin:
        hashed_password = hash_password(new_password)
        admin.admin_password = hashed_password
        db.session.commit()
        app.logger.info(f"Password updated for admin: {user_identity['id']}")
        return jsonify({'message': 'Password updated successfully'}), 200
    else:
        app.logger.error(f"Admin with id {user_identity['id']} not found")
        return jsonify({'message': 'Admin not found'}), 404

# Get all service requests data for Admin
@app.route('/api/admins/servicerequests', methods=['GET'])
@jwt_required()  
def get_service_requests():
    try:
        service_requests = db.session.query(ServiceRequest, Customer, Professional, Service).\
            join(Customer, ServiceRequest.customer_id == Customer.customer_id, isouter=True).\
            join(Professional, ServiceRequest.professional_id == Professional.professional_id, isouter=True).\
            join(Service, ServiceRequest.service_id == Service.service_id, isouter=True).\
            all()
        result = []
        for service_request, customer, professional, service in service_requests:
            result.append({
                'service_request_id': service_request.id,
                'service_name': service.service_name,
                'customer_name': customer.customer_name if customer else None,
                'professional_name': professional.professional_name if professional else None,
                'service_status': service_request.service_status,
                'rating_for_professional': service_request.rating_for_professional,
                'rating_for_customer': service_request.rating_for_customer,
                'remarks_for_professional': service_request.remarks_for_professional if service_request else None,
                'remarks_for_customer': service_request.remarks_for_customer if service_request else None,
                'date_of_request': service_request.date_of_request,
                'date_of_completion': service_request.date_of_completion if service_request else None,
                'price': service.price
            })
        return jsonify({'service_requests': result}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

#Fetch Logged-in User Data
@app.route('/api/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    print("JWT says hiuser")
    user_identity = json.loads(get_jwt_identity())
    if user_identity['role'] == 'admin':
        admin = Admin.query.filter_by(admin_id=user_identity['id']).first()  
        if admin:
            return jsonify({
                'message': 'User info retrieved successfully',
                'user': {
                    'admin_name': admin.admin_name,
                    'admin_id': admin.admin_id
                }
            }), 200
        else:
            return jsonify({'message': 'Admin not found'}), 404
    return jsonify({'message': 'Unauthorized access'}), 403

#Close service request for admin side
@app.route('/api/admins/servicerequestclose/<int:id>', methods=['PUT'])
def close_service_request(id):
    print(f"Closing service request with ID: {id}")
    request_data = ServiceRequest.query.get(id)
    if not request_data:
        logging.error(f"Service request with ID {id} not found")
        return jsonify({"success": False, "message": "Service request not found"}), 404
    if request_data.service_status not in ['requested', 'assigned']:
        logging.error(f"Cannot close service request with ID {id}. Invalid status: {request_data.service_status}")
        return jsonify({"success": False, "message": "Only 'Requested' or 'Assigned' requests can be closed"}), 400
    request_data.service_status = 'calledoff'
    request_data.date_of_completion = datetime.now()  
    db.session.commit()
    logging.info(f"Service request with ID {id} has been closed successfully.")
    return jsonify({"success": True, "message": "Service request has been closed."}), 200

#Get customer-info
@app.route('/api/customer-info', methods=['GET'])
@jwt_required()
def get_customer_info():
    print("JWT says hi")
    customer_identity = json.loads(get_jwt_identity()  )  
    print(type(customer_identity))
    customer_id = customer_identity.get('id')  
    if not isinstance(customer_id, int):
        return jsonify({"message": "Invalid customer ID."}), 400
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    return jsonify({
        "user": {
            "customer_id": customer.customer_id,
            "customer_name": customer.customer_name,
            "contact_number": customer.contact_number,
            "customer_rating": customer.customer_rating,
            "status": customer.status,
        }
    }), 200

#get professional Info
@app.route('/api/professional-info', methods=['GET'])
@jwt_required()
def get_professional_info():
    print("HIIIIIIII KASSSSSS")
    professional_identity = json.loads(get_jwt_identity()  )  
    professional_id = professional_identity.get('id')  
    if not isinstance(professional_id, int):
        return jsonify({"message": "Invalid customer ID."}), 400
    professional = Professional.query.get(professional_id)
    if not professional:
        return jsonify({"message": "professional not found"}), 404
    return jsonify({
        "user": {
            "professional_id": professional.professional_id,
            "professional_name": professional.professional_name,
            "contact_number": professional.professional_number,
            "professional_rating": professional.professional_rating,
            "status": professional.status,
        }
    }), 200

#Explore servies for customer side
@app.route('/api/customer/explore', methods=['GET'])
@jwt_required()  
def explore_services():
    try:
        services = Service.query.all()
        if not services:
            return jsonify({"message": "No services available."}), 404
        services_data = [{
            'service_id': service.service_id,
            'service_name': service.service_name,
            'price': service.price,
            'time_required': service.time_required,
            'description': service.description,
        } for service in services]
        
        return jsonify({'services': services_data}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#explore opportunities for porfessional
@app.route('/api/professional/explore', methods=['GET'])
@jwt_required()
def explorep_services():
    try:
        professional_idd = json.loads(get_jwt_identity()  )
        professional_id = professional_idd.get('id')
        if not professional_id:
            return jsonify({"message": "Invalid token structure."}), 401
        professional = Professional.query.filter_by(professional_id=professional_id).first()
        if not professional:
            return jsonify({"message": "Professional not found."}), 404
        service = Service.query.filter_by(service_name=professional.service_type).first()
        if not service:
            return jsonify({"message": "No service found for this professional's expertise."}), 404
        matching_requests = (
            db.session.query(ServiceRequest, Customer, Service)  
            .join(Customer, ServiceRequest.customer_id == Customer.customer_id)
            .join(Service, ServiceRequest.service_id == Service.service_id) 
            .filter(
                ServiceRequest.service_id == service.service_id,
                ServiceRequest.service_status.in_(["requested"])
            )
            .all()
        )
        if not matching_requests:
            return jsonify({"message": "No matching service requests available."}), 404
        services_data = [
            {
                'service_request_id': service_request.id,
                'service_name': service.service_name, 
                'customer_name': customer.customer_name,
                'date_of_request': service_request.date_of_request.isoformat() if service_request.date_of_request else None,
                'service_status': service_request.service_status,
            }
            for service_request, customer, service in matching_requests  
        ]
        return jsonify({'service_requests': services_data}), 200
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#Book service for customer side
@app.route('/api/customer/book-service', methods=['POST'])
@jwt_required()
def book_service():
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )  
        customer_id = customer_id_from_token.get('customer_id')
        data = request.get_json()
        service_id = data.get('service_id')
        customer_id = data.get('customer_id')
        if not service_id:
            return jsonify({"message": "Service ID is required."}), 400
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"message": "Service not found."}), 404
        new_request = ServiceRequest(
            service_id=service_id,
            customer_id=customer_id,
            date_of_request=datetime.utcnow(),
            service_status="requested",
            rating_for_professional=0,
            rating_for_customer=0
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({"message": "Service booked successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#View previous services for customer side
@app.route('/api/customer/previous-services', methods=['GET'])
@jwt_required()
def get_previous_services():
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )
        customer_id = customer_id_from_token.get('id')  
        closed_services = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='closed').all()
        if not closed_services:
            return jsonify({"message": "No previous services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                professional = db.session.get(Professional, request.professional_id)
                professional_name = professional.professional_name if professional else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "date_of_completion": request.date_of_completion,
                    "professional_name": professional_name,  
                    "remarks_for_profesional": request.remarks_for_professional,
                    "remarks_for_customer": request.remarks_for_customer,
                    "rating_for_professional": request.rating_for_professional
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#View assigned Services for customer side
@app.route('/api/customer/assigned-services', methods=['GET'])
@jwt_required()
def get_assigned_services():
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )
        customer_id = customer_id_from_token.get('id')
        closed_services = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='assigned').all()
        if not closed_services:
            return jsonify({"message": "No assigned services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                professional = db.session.get(Professional, request.professional_id)
                professional_name = professional.professional_name if professional else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "professional_name": professional_name  
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#View assigned Services for customer side
@app.route('/api/customer/cancelled-services', methods=['GET'])
@jwt_required()
def get_cancelled_services():
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )
        customer_id = customer_id_from_token.get('id')
        closed_services = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='calledoff').all()
        if not closed_services:
            return jsonify({"message": "No cancelled services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                professional = db.session.get(Professional, request.professional_id)
                professional_name = professional.professional_name if professional else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "professional_name": professional_name  
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#Cancel service request for customer side
@app.route('/api/customer/cancelservice/<int:request_id>', methods=['PUT'])
@jwt_required()
def cancel_assigned_service(request_id):
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )
        customer_id = customer_id_from_token.get('id') 
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return jsonify({"message": "Service request not found."}), 404
        if service_request.customer_id != customer_id:
            return jsonify({"message": "You can only cancel your own service requests."}), 403
        if service_request.service_status not in ['assigned', 'requested']:
            print("we are there!!!!!!!!!")
            return jsonify({"message": "Only assigned services can be cancelled."}), 400
        service_request.service_status = 'calledoff'
        db.session.commit()
        return jsonify({"message": "Service request has been cancelled successfully."}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#view requested services for customer side
@app.route('/api/customer/requested-services', methods=['GET'])
@jwt_required()
def get_requested_services():
    try:
        customer_id_from_token = json.loads(get_jwt_identity()  )
        customer_id = customer_id_from_token.get('id')
        closed_services = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='requested').all()
        if not closed_services:
            return jsonify({"message": "No assigned services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#update the remarks and rating for customer side
@app.route('/api/customer/update-service-feedback', methods=['PUT'])
def update_service_feedback():
    print("Processing customer feedback...")
    data = request.get_json()
    print("Incoming Data:", data)

    service_request_id = data.get('service_request_id') or data.get('service_id')
    remarks_for_professional = data.get('remarks_for_professional')
    rating_for_professional = data.get('rating_for_professional')

    if not service_request_id:
        return jsonify({'message': 'Service request ID is required'}), 400

    service_request = ServiceRequest.query.get(service_request_id)
    if not service_request:
        return jsonify({'message': 'Service request not found'}), 404

    if remarks_for_professional is not None:
        service_request.remarks_for_professional = remarks_for_professional

    if rating_for_professional is not None:
        try:
            rating_for_professional = int(rating_for_professional) 
            if not (1 <= rating_for_professional <= 5):
                return jsonify({'message': 'Rating for professional must be between 1 and 5'}), 400
            service_request.rating_for_professional = rating_for_professional
        except ValueError:
            return jsonify({'message': 'Invalid rating for professional. It must be an integer.'}), 400

    try:
        db.session.commit()
        print("Feedback updated successfully.")
        return jsonify({'message': 'Feedback updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error updating feedback:", str(e))
        return jsonify({'message': f'Error updating feedback: {str(e)}'}), 500


#update feedback by professional for already closed req 
@app.route('/api/professional/update-service-feedback', methods=['PUT'])
def update_service_feedbackp():
    data = request.get_json()
    service_request_id = data.get('service_request_id') or data.get('service_id')
    remarks_for_customer = data.get('remarks_for_customer')
    rating_for_customer = data.get('rating_for_customer')

    if not service_request_id:
        return jsonify({'message': 'Service request ID is required'}), 400

    service_request = ServiceRequest.query.get(service_request_id)
    if not service_request:
        return jsonify({'message': 'Service request not found'}), 404

    # Update remarks if provided
    if remarks_for_customer is not None:
        service_request.remarks_for_customer = remarks_for_customer

    # Update rating if provided
    if rating_for_customer is not None:
        try:
            rating_for_customer = int(rating_for_customer)  
        except ValueError:
            return jsonify({'message': 'Rating must be a valid integer'}), 400

        if not (1 <= rating_for_customer <= 5):
            return jsonify({'message': 'Rating must be between 1 and 5'}), 400
        service_request.rating_for_customer = rating_for_customer

    # If service is not already closed, close it
    if service_request.service_status != 'closed':
        service_request.service_status = 'closed'
        service_request.date_of_completion = datetime.now()  # Set completion date

    try:
        db.session.commit()
        return jsonify({'message': 'Feedback updated successfully, service marked as closed if not already.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating service request: {str(e)}'}), 500



#accept the service (professional side)
@app.route('/api/professional/assign-service/<int:service_request_id>', methods=['PUT'])
def assign_service(service_request_id):
    try:
        professional_id = request.json.get('professional_id')
        service_status = request.json.get('service_status', 'assigned')
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return jsonify({"message": "Service request not found"}), 404
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"message": "Professional not found"}), 404
        service_request.professional_id = professional_id
        service_request.service_status = service_status
        db.session.commit()
        return jsonify({"message": "Service successfully assigned", "service_request": service_request_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while assigning the service"}), 500
    
#see previous services (profeesional side)
@app.route('/api/professional/previous-services', methods=['GET'])
@jwt_required()
def get_previous_services_for_professional():
    try:
        professional_id_from_token = json.loads(get_jwt_identity()  )
        professional_id = professional_id_from_token.get('id')  
        closed_services = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='closed').all()
        if not closed_services:
            return jsonify({"message": "No previous services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                customer = db.session.get(Customer, request.customer_id)
                customer_name = customer.customer_name if customer else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "date_of_completion": request.date_of_completion,
                    "customer_name": customer_name,  
                    "remarks_for_professional": request.remarks_for_professional,
                    "rating_for_professional": request.rating_for_professional,
                    "remarks_for_customer": request.remarks_for_customer,
                    "rating_for_customer": request.rating_for_customer
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#see previous services (profeesional side)
@app.route('/api/professional/cancelled-services', methods=['GET'])
@jwt_required()
def get_cancelled_services_for_professional():
    try:
        professional_id_from_token = json.loads(get_jwt_identity()  )
        professional_id = professional_id_from_token.get('id')  
        closed_services = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='calledoff').all()
        if not closed_services:
            return jsonify({"message": "No previous services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                customer = db.session.get(Customer, request.customer_id)
                customer_name = customer.customer_name if customer else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "date_of_completion": request.date_of_completion,
                    "customer_name": customer_name,  
                    "remarks_for_professional": request.remarks_for_professional,
                    "rating_for_professional": request.rating_for_professional,
                    "remarks_for_customer": request.remarks_for_customer,
                    "rating_for_customer": request.rating_for_customer
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


#view assigned service (pro side)
@app.route('/api/professional/assigned-services', methods=['GET'])
@jwt_required()
def get_assigned_servicesp():
    try:
        professional_id_from_token = json.loads(get_jwt_identity()  )
        professional_id = professional_id_from_token.get('id')  
        closed_services = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='assigned').all()
        if not closed_services:
            return jsonify({"message": "No assigned services found."}), 404
        services = []
        for request in closed_services:
            service = db.session.get(Service, request.service_id)
            if service:
                customer = db.session.get(Customer, request.customer_id)
                customer_name = customer.customer_name if customer else 'N/A'
                services.append({
                    "request_id": request.id,
                    "service_name": service.service_name,
                    "price": service.price,
                    "time_required": service.time_required,
                    "date_of_request": request.date_of_request,
                    "customer_name": customer_name  
                })
        return jsonify({"services": services}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#cancel service (pro side)
@app.route('/api/professional/cancelservice/<int:request_id>', methods=['PUT'])
@jwt_required()
def cancel_assigned_servicep(request_id):
    try:
        professional_id_from_token = json.loads(get_jwt_identity()  )
        professional_id = professional_id_from_token.get('id')  
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            print("service req not found")
            return jsonify({"message": "Service request not found."}), 404
        if service_request.professional_id != professional_id:
            return jsonify({"message": "You can only cancel your own service requests."}), 403
        if service_request.service_status not in ['assigned']:
            print("we are there!!!!!!!!!")
            return jsonify({"message": "Only assigned services can be cancelled."}), 400
        service_request.service_status = 'requested'
        service_request.professional_id = None
        db.session.commit()
        return jsonify({"message": "Service request has been cancelled successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

#search customer info by admin
@app.route('/api/admins/customerinfo/search', methods=['GET'])
@jwt_required()  
def search_customers():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            customers = Customer.query.all()
        else:
            customers = Customer.query.filter(
                (Customer.customer_name.ilike(f"%{query}%")) |  
                (Customer.customer_id.cast(db.String).ilike(f"%{query}%"))  
            ).all()
        customer_data = []
        service_requests = db.session.query(ServiceRequest).filter(
            ServiceRequest.customer_id.in_([customer.customer_id for customer in customers])
        ).all()
        services = {service.service_id: service for service in Service.query.filter(
            Service.service_id.in_([req.service_id for req in service_requests])
        ).all()}
        for customer in customers:
            customer_service_requests = [
                req for req in service_requests if req.customer_id == customer.customer_id
            ]
            services_requested = []
            for req in customer_service_requests:
                service = services.get(req.service_id)
                if service:
                    service_status = req.service_status.lower()  
                    if service_status == 'requested':
                        color = 'yellow'
                    elif service_status == 'assigned':
                        color = 'green'
                    elif service_status == 'closed':
                        color = 'red'
                    else:
                        color = 'black'  
                    services_requested.append({
                        'service_name': service.service_name,
                        'status': service_status,
                        'color': color 
                    })
            customer_data.append({
                'id': customer.customer_id,
                'name': customer.customer_name,
                'phone': customer.contact_number,
                'email': customer.customer_email,
                'rating': customer.customer_rating,
                'status': customer.status, 
                'reason_for_blocking': customer.reason_for_blocking if customer.status == 'blocked' else None,
                'services_requested': services_requested 
            })
        return jsonify({'message': 'Customers retrieved successfully', 'customers': customer_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while retrieving customer information', 'error': str(e)}), 500

#search pro info by admin
@app.route('/api/admins/professionalinfo/search', methods=['GET'])
@jwt_required()  
def search_professionalsp():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            professionals = Professional.query.all()
        else:
            professionals = Professional.query.filter(
                (Professional.professional_name.ilike(f"%{query}%")) |  
                (Professional.professional_id.cast(db.String).ilike(f"%{query}%")) 
            ).all()
        professional_data = []
        for professional in professionals:
            service_requests = db.session.query(ServiceRequest).join(Service).filter(
                ServiceRequest.professional_id == professional.professional_id
            ).all()
            services_requested = []
            for req in service_requests:
                service = Service.query.get(req.service_id)  
                service_status = req.service_status.lower() 
                color = 'black'  
                if service_status == 'requested':
                    color = 'yellow'
                elif service_status == 'assigned':
                    color = 'green'
                elif service_status == 'closed':
                    color = 'red'
                services_requested.append({
                    'service_name': service.service_name,
                    'status': service_status,
                    'color': color  
                })
            professional_data.append({
                'id': professional.professional_id,
                'name': professional.professional_name,
                'phone': professional.professional_number,
                'servicetype': professional.service_type,
                'experience': professional.experience,
                'pincode': professional.professional_pincode,
                'datejoined': professional.date_joined,
                'rating': professional.professional_rating,
                'verified': professional.verified,
                'status': professional.status, 
                'reason_for_blocking': professional.reason_for_blocking if professional.status == 'blocked' else None,
                'services_requested': services_requested 
            })
        return jsonify({'message': 'Professionals retrieved successfully', 'professionals': professional_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while searching professionals.', 'error': str(e)}), 500

#search servicessss info by admin
@app.route('/api/admins/serviceinfo/search', methods=['GET'])
@jwt_required()  
def search_servicess():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            services = Service.query.all()
        else:
            services = Service.query.filter(
                (Service.service_name.ilike(f"%{query}%")) | 
                (Service.service_id.cast(db.String).ilike(f"%{query}%"))  
            ).all()
        services_data = [
            {
                "id": service.service_id,
                "service_name": service.service_name,
                "price": service.price,
                "time_required": service.time_required,
                "description": service.description,
            }
            for service in services
        ]
        return jsonify({"services": services_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Search request information by admin (only by ServiceRequest ID)
@app.route('/api/admins/requestinfo/search', methods=['GET'])
@jwt_required()  
def search_service_requests():
    try:
        query = request.args.get('query', '').strip()
        service_requests_query = db.session.query(ServiceRequest, Customer, Professional, Service).\
            join(Customer, ServiceRequest.customer_id == Customer.customer_id, isouter=True).\
            join(Professional, ServiceRequest.professional_id == Professional.professional_id, isouter=True).\
            join(Service, ServiceRequest.service_id == Service.service_id, isouter=True)
        if query:
            service_requests_query = service_requests_query.filter(
                ServiceRequest.id == int(query)  
            )
        service_requests = service_requests_query.all()
        result = []
        for service_request, customer, professional, service in service_requests:
            result.append({
                'service_request_id': service_request.id,
                'service_name': service.service_name,
                'customer_name': customer.customer_name if customer else None,
                'professional_name': professional.professional_name if professional else None,
                'service_status': service_request.service_status,
                'rating_for_professional': service_request.rating_for_professional,
                'rating_for_customer': service_request.rating_for_customer,
                'remarks_for_professional': service_request.remarks_for_professional,
                'remarks_for_customer': service_request.remarks_for_customer,
                'date_of_request': service_request.date_of_request,
                'date_of_completion': service_request.date_of_completion,
                'price': service.price
            })
        return jsonify({'service_requests': result}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
#search services by customer
@app.route('/api/customers/serviceinfo/search', methods=['GET'])
@jwt_required()
def search_servicessc():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            services = Service.query.all()
        else:
            services = Service.query.filter(
                (Service.service_name.ilike(f"%{query}%")) |  
                (Service.service_id.cast(db.String).ilike(f"%{query}%"))  
            ).all()
        services_data = [
            {
                "id": service.service_id,
                "service_name": service.service_name,
                "price": service.price,
                "time_required": service.time_required,
                "description": service.description,
            }
            for service in services
        ]
        return jsonify({"services": services_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#display professional wise services customer side
@app.route('/api/customer/professionalwise-services', methods=['GET'])
@jwt_required()
def get_professionalwise_services():
    print("HIHIHI")
    try:
        professionals = Professional.query.filter(Professional.status.in_(['active'])).all()
        professional_data = []
        for professional in professionals:
            service_requests = db.session.query(ServiceRequest).filter(ServiceRequest.professional_id == professional.professional_id).all()
            services_requested = []
            service_ids = [req.service_id for req in service_requests]
            services = Service.query.filter(Service.service_id.in_(service_ids)).all()
            service_dict = {service.service_id: service for service in services}
            for req in service_requests:
                service = service_dict.get(req.service_id)
                if service:
                    service_status = req.service_status.lower()
                    if service_status == 'requested':
                        color = 'yellow'
                    elif service_status == 'assigned':
                        color = 'green'
                    elif service_status == 'closed':
                        color = 'red'
                    else:
                        color = 'black'
                    services_requested.append({
                        'service_name': service.service_name,
                        'status': service_status,
                        'color': color  
                    })
            professional_data.append({
                'id': professional.professional_id,
                'name': professional.professional_name,
                'phone': professional.professional_number,
                'email': professional.professional_email,
                'servicetype': professional.service_type,
                'experience': professional.experience,
                'pincode': professional.professional_pincode,
                'datejoined': professional.date_joined,
                'rating': professional.professional_rating,
                'verified': professional.verified,
                'status': professional.status,  
                'services_requested': services_requested
            })
        return jsonify({'message': 'Professionals retrieved successfully', 'professionals': professional_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching the professional services.'}), 500

#search pro info by customer
@app.route('/api/customers/professionalinfo/search', methods=['GET'])
@jwt_required()  
def search_professionalsc():
    try:
        query = request.args.get('query', '').strip().lower()
        if not query:
            professionals = Professional.query.all()
        else:
            professionals = Professional.query.filter(
                (Professional.professional_name.ilike(f"%{query}%")) | 
                (Professional.professional_id.cast(db.String).ilike(f"%{query}%")) | 
                (Professional.professional_pincode.cast(db.String).ilike(f"%{query}%")) 
            ).all()
        professional_data = []
        for professional in professionals:
            service_requests = db.session.query(ServiceRequest).join(Service).filter(
                ServiceRequest.professional_id == professional.professional_id
            ).all()
            services_requested = []
            for req in service_requests:
                service = Service.query.get(req.service_id)
                service_status = req.service_status.lower()
                color = 'black'  
                if service_status == 'requested':
                    color = 'yellow'
                elif service_status == 'assigned':
                    color = 'green'
                elif service_status == 'closed':
                    color = 'red'
                services_requested.append({
                    'service_name': service.service_name,
                    'status': service_status,
                    'color': color  
                })
            professional_data.append({
                'id': professional.professional_id,
                'name': professional.professional_name,
                'phone': professional.professional_number,
                'servicetype': professional.service_type,
                'experience': professional.experience,
                'pincode': professional.professional_pincode,
                'datejoined': professional.date_joined,
                'rating': professional.professional_rating,
                'verified': professional.verified,
                'status': professional.status,  
                'reason_for_blocking': professional.reason_for_blocking if professional.status == 'blocked' else None,
                'services_requested': services_requested  
            })
        return jsonify({'message': 'Professionals retrieved successfully', 'professionals': professional_data}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while searching professionals.', 'error': str(e)}), 500

#for the flask route to see if its working
@app.route('/')
def home():
    return "Welcome to Household Services!"

#global for incoming reqs and debugging
@app.before_request
def log_request_info():
    print("Method:", request.method)
    print("URL:", request.url)
    print("Headers:", request.headers)

# ======================== Backend Jobs ========================

#Send reminders to professionals for pending tasks (A1)
@celery.task()
def send_daily_reminders():
    """Send daily reminders to professionals who have pending service requests."""
    try:
        professionals = Professional.query.filter_by(status="active").all()

        for professional in professionals:
            pending_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional.professional_id,
                ServiceRequest.service_status == 'assigned'
            ).all()

            if pending_requests:
                reminder_msg = "Reminder: You have pending service requests. Please check and update them."
                send_email("Pending Service Reminder", professional.professional_email, reminder_msg)
                
                print(f"Daily reminder sent to {professional.professional_email}")  
    except Exception as e:
        print(f"Error sending daily reminders: {e}")

#Send monthly report to customer for their activity (B1)
@celery.task
def generate_monthly_report():
    """Generate and send a monthly report for the customers."""
    try:
        now = datetime.utcnow()

        start_date = '2025-03-01'  # For testing
        end_date = '2025-03-30'   
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_day_of_previous_month = (first_day_of_month - timedelta(days=1)).replace(day=1)
        last_day_of_previous_month = first_day_of_month - timedelta(days=1)
        service_requests = ServiceRequest.query.filter(
            ServiceRequest.date_of_request.between(first_day_of_previous_month, last_day_of_previous_month)
        ).all()

        logging.info(f"DEBUG: Found {len(service_requests)} service requests for the selected period.")

        if not service_requests:
            logging.warning(" No service requests to report.")
            return
        
        active_customers = {c.customer_id: c.customer_email for c in Customer.query.filter_by(status="active").all()}
        logging.info(f"DEBUG: Found {len(active_customers)} active customers.")

        if not active_customers:
            logging.warning("No active customers to send reports to.")
            return
        customer_reports = generate_report_content(service_requests, active_customers)

        for customer_id, report in customer_reports.items():
            send_email("Monthly Activity Report", [active_customers[customer_id]], report, True)

        customers_with_no_activity = set(active_customers.keys()) - set(customer_reports.keys())

        for customer_id in customers_with_no_activity:
            send_email("No Activity Report", [active_customers[customer_id]], "No activity for this month.", False)

        logging.info(" Monthly report generated and sent successfully.")
    
    except Exception as e:
        logging.error(f"Error generating monthly report: {e}")

#to generate report content to send to customer (B2)
def generate_report_content(service_requests, active_customers):
    """Generate HTML reports for each active customer."""
    
    customer_service_map = {}
    
    for req in service_requests:
        if req.customer_id in active_customers: 
            if req.customer_id not in customer_service_map:
                customer_service_map[req.customer_id] = []
            customer_service_map[req.customer_id].append([ 
                req.id,
                req.service_status,
                req.professional_id  
            ])
    professional_ids = {req.professional_id for req in service_requests if req.professional_id}
    professionals = {p.professional_id: p.professional_name for p in Professional.query.filter(Professional.professional_id.in_(professional_ids))}

    customer_reports = {}

    for customer_id, services in customer_service_map.items():
        customer_email = active_customers.get(customer_id, "Unknown")  

        report_content = f"""
        <html>
            <body>
                <h2>Monthly Service Activity Report for {customer_email}</h2>
                <table border="1">
                    <tr>
                        <th>Service ID</th>
                        <th>Service Status</th>
                        <th>Professional</th>
                    </tr>
        """

        for service in services:
            service_id, service_status, professional_id = service
            professional_name = professionals.get(professional_id, "Not Assigned") 

            report_content += f"""
                <tr>
                    <td>{service_id}</td>
                    <td>{service_status}</td>
                    <td>{professional_name}</td>
                </tr>
            """

        report_content += "</table></body></html>"
        
        customer_reports[customer_id] = report_content

    return customer_reports
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

#Service req information available to download for admin (C1)
@celery.task
def generate_service_requests_csv():
    """Generate CSV of closed service requests and store it."""
    try:
        now = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"closed_service_requests_{now}.csv"
        filepath = os.path.join(EXPORT_FOLDER, filename)

        service_requests = ServiceRequest.query.filter_by(service_status="closed").all()

        if not service_requests:
            logging.info("No closed service requests found.")
            return None  

        with open(filepath, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Service ID", "Customer ID", "Professional ID", "Date of Request", "Remarks"])
            
            for req in service_requests:
                writer.writerow([
                    req.id,
                    req.customer_id,
                    req.professional_id,
                    req.date_of_request.strftime('%Y-%m-%d'),
                    req.remarks_for_professional or "No remarks"
                ])
        
        logging.info(f"CSV generated: {filepath}")
        return filename 
    
    except Exception as e:
        logging.error(f"Error generating CSV: {str(e)}")
        return None


#Send emails (required for task A and B) (A2, B3)
def send_email(subject, to_emails, body, is_html=False):
    """Helper function to send email."""
    try:
        if not isinstance(to_emails, list):
            to_emails = [to_emails]  

        msg = Message(subject, sender="kasturisangale2811@gmail.com", recipients=to_emails)
        
        if is_html:
            msg.html = body 
        else:
            msg.body = body  

        mail.send(msg)  
        print(f"Email sent to {', '.join(to_emails)}") 
    except Exception as e:
        print(f"Error sending email: {e}")



# ======================== Route Definitions ========================

# Trigger for daily reminders to professionals (A3)
@app.route('/trigger/daily-reminder', methods=['POST'])
def trigger_daily_reminder():
    send_daily_reminders()  
    return jsonify({"msg": "Daily reminder job triggered."}), 200

#Monthly report for customers (B4)
@app.route('/trigger/monthly-report', methods=['POST'])
def trigger_monthly_report():
    generate_monthly_report() 
    return jsonify({"msg": "Monthly report job triggered."}), 200

#service reqs made available for admin to downlaod (C2)
@app.route('/export-service-requests', methods=['POST'])
def export_service_requests():
    """API to trigger the CSV export asynchronously."""
    task = generate_service_requests_csv.delay() 
    return jsonify({"message": "CSV export started", "task_id": task.id}), 202

#service reqs made available for admin to downlaod (C3)
@app.route('/check-task-status/<task_id>', methods=['GET'])
def check_task_status(task_id):
    """Check Celery task status and return filename if ready."""
    task_result = AsyncResult(task_id, app=celery)

    if task_result.status == 'SUCCESS':
        return jsonify({"status": "SUCCESS", "filename": task_result.result})
    else:
        return jsonify({"status": task_result.status})

#service reqs made available for admin to downlaod (C4)
@app.route('/download-csv/<filename>', methods=['GET'])
def download_csv(filename):
    """API to download the generated CSV file."""
    filepath = os.path.join(EXPORT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

# ======================== Main ======================== #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


