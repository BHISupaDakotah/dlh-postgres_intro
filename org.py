import psycopg2
from flask import Flask, request, jsonify

# - Add Org [x]
# - Update Org [x]
# - Get Org by ID [x]
# - Get all orgs [x]
# - Delete org [x]
# - Activate org [x]
# - Deactivate org [x]

app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt' user='dakotahholmes' host='localhost'")
cursor = conn.cursor()

      # CREATE TABLE IF NOT EXISTS Organizations (
      #    org_id SERIAL PRIMARY KEY,
      #    name VARCHAR NOT NULL,
      #    phone VARCHAR,
      #    city VARCHAR,
      #    state VARCHAR,
      #    active smallint
      # );


# - Add Org
def add_org(name ,phone, city, state, active):
  cursor.execute("""
    INSERT INTO Organizations
    (name, phone, city, state, active)
    VALUES
    (%s, %s, %s,%s, %s);""",
    (name ,phone ,city, state, active))

  conn.commit()

@app.route('/org/add', methods=['POST'])
def add_org_route():
  data = request.form 
  if not data:
    data = request.json

  name = data.get('name')
  phone = data.get('phone')
  city = data.get('city')
  state = data.get('state')
  active = data.get('active')

  add_org(name, phone, city, state, active)

  return jsonify("org created"), 200

# - Update Org
@app.route('/org/update/<org_id>', methods=(['POST', 'PUT']))
def update_org(org_id):
  update_fields = []
  update_values = []
  field_names = ['name', 'phone', 'city', 'state', 'active']

  post_data = request.form if request.form else request.json

  for field in field_names:
    print(field)
    field_value = post_data.get(field)
    if field_value:
      update_fields.append(str(field) + f'=%s')
      print(update_fields)
      update_values.append(field_value)
      print(update_values)

  if update_fields:
    update_values.append(org_id)
    query_string = "UPDATE Organizations SET " + ', '.join(update_fields) + " WHERE org_id=%s"
    cursor.execute(query_string, update_values)

    conn.commit()

    return jsonify("org updated"), 200
  else:
    return jsonify("no values sent in body"), 418

# - Get Org by ID
@app.route('/org/get/<org_id>', methods=(['GET']))
def get_org_by_id(org_id):
  cursor.execute("""SELECT * FROM Organizations WHERE org_id=%s""",[org_id])

  results = cursor.fetchone()

  if results:
    org = {
      'org_id': results[0],
      'name' : results[1],
      'phone' : results[2],
      'city' : results[3],
      'state' : results[4],
      'active' :results[5]
    }

    return jsonify(org), 201
  else:
    return jsonify('sorry org not found'), 418

# - Get all orgs
@app.route('/org/get', methods=['GET'])
def get_all_orgs():
  cursor.execute("""SELECT * FROM Organizations WHERE active=1;""")

  results = cursor.fetchall()
  if results:
    org_list = []
    for org in results:
      org = {
        'org_id': org[0],
        'name' : org[1],
        'phone' : org[2],
        'city' : org[3],
        'state' : org[4],
        'active' : org[5]
      }
      org_list.append(org)

    return jsonify(org_list), 200
  else:
    return jsonify("no organizations"), 404


# - Delete org
@app.route('/org/delete/<org_id>')
def org_delete(org_id):
  cursor.execute(f"""DELETE FROM Organizations WHERE org_id=%s;""",[org_id])

  conn.commit()

  return jsonify("Organization Deleted")

# - Deactivate org
@app.route('/org/deactivate/<org_id>')
def org_deactivate(org_id):
  cursor.execute(f"""UPDATE Organizations SET active=0 WHERE org_id=%s;""",[org_id])

  conn.commit()

  return jsonify("Organization Deactivated")

# - Activate org
@app.route('/org/activate/<org_id>')
def org_activate(org_id):
  cursor.execute("""UPDATE Organizations SET active=1 WHERE org_id=%s;""",[org_id])

  conn.commit()

  return jsonify("Organization Activated")

if __name__ == '__main__':
  # create_all()
  app.run(host='0.0.0.0', port=8089)

