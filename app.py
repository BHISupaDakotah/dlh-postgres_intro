
from pprint import pprint
import psycopg2
from flask import Flask, request, jsonify
# pipenv install psycopg2

# - Add [x]
# - Update [x]
# - Get user by ID [x]
# - Get all user [x]
# - Delete user [x]
# - Activate user [x]
# - Deactivate user [x]

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt' user='dakotahholmes' host='localhost'")
cursor = conn.cursor()

def create_all():
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint
      );
   """)
   cursor.execute("""
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint
      );
   """)
   print("Creating tables...")
   conn.commit()

# ************************** Add [x] *****************************

def add_user(first_name, last_name, email, phone, city, state, org_id, active):
    cursor.execute(f"""
      INSERT INTO Users 
      (first_name, last_name, email, phone, city, state, org_id, active)
      VALUES 
      (%s,%s,%s,%s,%s,%s,%s,%s);""",
      (first_name, last_name, email, phone, city, state, org_id, active))

    conn.commit()

@app.route('/user/add', methods=['POST']) # ^function has to be above decorator call
def user_add():
    post_data = request.form
    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')
    email = post_data.get('email')
    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    add_user(first_name, last_name, email, phone, city, state, org_id, active)
    
    return jsonify("User created"), 201

#********************* Get user by ID [x] ***************************

@app.route('/user/<user_id>', methods=['GET']) # add decorator to normal funtion(<user_id>)
def get_user_by_id(user_id): #matches paramater
  cursor.execute(f"""
    SELECT u.user_id,
     u.first_name, 
     u.last_name, 
     u.email, 
     u.phone, 
     u.city, 
     u.state, 
     u.org_id, 
     u.active,
      o.org_id, 
      o.name,
      o.phone,
      o.city, 
      o.state, 
      o.active as active_org
    FROM Users u
    JOIN Organizations o
    ON u.org_id=o.org_id
       WHERE user_id=%s;""",
      [user_id])

  results = cursor.fetchone()

  if results:
    user = {
      'user_id':results[0],
      'first_name':results[1],
      'last_name':results[2],
       'email':results[3],
      'phone':results[4], 
      'city':results[5], 
      'state':results[6], 
      'org_id':results[7],
      'organization' : {
        'org_id': results[9],
        'name' : results[10],
        'phone' : results[11],
        'city' : results[12],
        'state' : results[12],
        'active_org': results[13]
      },
      'active':results[8]
    }
    return jsonify(user), 200 # jsonify response and status code
  else:
    return jsonify('user not found'), 418 # jsonify response and status code

# *********************** Activate User [x] ***********************

@app.route('/user/activate/<user_id>')
def activate_user(user_id):
    cursor.execute(f"""
        UPDATE Users
            SET active=1
            WHERE user_id=%s;""",
        [user_id])
    
    conn.commit()

    return jsonify("User activated"), 200

# ********************* Delete User [x] *************************

@app.route('/user/delete/<user_id>')
def delete_user(user_id):
  cursor.execute(f"""
      DELETE FROM Users
      WHERE user_id=%s;""", [user_id])

  # conn.commit()

  return jsonify("User permently deleted!")


# ********************* Deactivate User [x] *************************

@app.route('/user/deactivate/<user_id>')
def deactivate_user(user_id):
  cursor.execute(f"""
  UPDATE Users
    SET active=0
    WHERE user_id=%s;""", [user_id])
  
  conn.commit()

  return jsonify("User Deactivated")

# get all users
@app.route('/users/get')
def get_all_active_users():
  cursor.execute("""
  SELECT * FROM Users
    WHERE active=1;"""
  )
  list_of_users = cursor.fetchall()
  if list_of_users:
    user_list = []
    for single_user in list_of_users:
      user = {
        'user_id':single_user[0],
        'first_name':single_user[1],
        'last_name':single_user[2],
        'email':single_user[3],
        'phone':single_user[4], 
        'city':single_user[5], 
        'state':single_user[6], 
        'org_id':single_user[7], 
        'active':single_user[8]
    }
      user_list.append(user)
      user = {}
    return  jsonify(user_list),200 #user_list
  else: 
    return jsonify('sorry'),404 #None

#  no commit needed because its only querying

# **************************** Update [x] ****************************

@app.route('/user/update/<user_id>', methods=(['POST','PUT']))
def user_update(user_id):
  update_fields = []
  update_values = []
  field_names = ['first_name','last_name','email','phone','city','state','org_id','active']
  
  post_data = request.form
  if not post_data:
    post_data = request.json

  for field in field_names:
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + f'=%s')
      update_values.append(field_value)

  if update_fields:
    update_values.append(user_id)
    query_string = "UPDATE Users SET " + ', '.join(update_fields) + " WHERE user_id=%s"
    cursor.execute(query_string, update_values)

    conn.commit()

    return jsonify(("updated user settings")), 200
  else:
    return jsonify('no values sent in body'), 418

if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0',port=8088)