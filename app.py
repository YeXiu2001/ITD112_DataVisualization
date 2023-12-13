from flask import Flask, render_template, jsonify, g
import mysql.connector

app = Flask(__name__)
app.secret_key = 'abcdefqwerty'

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'finalproj112'

# Function to get a MySQL connection
def get_mysql_connection():
    if 'mysql_connection' not in g:
        g.mysql_connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=3306
        )
    return g.mysql_connection

# Close the MySQL connection at the end of each request
@app.teardown_appcontext
def close_mysql_connection(e=None):
    mysql_connection = g.pop('mysql_connection', None)
    if mysql_connection is not None:
        mysql_connection.close()

# Route for main page
@app.route('/')
def Index():
    # Get overall cases and deaths
    cursor = get_mysql_connection().cursor(dictionary=True)
    cursor.execute("SELECT SUM(cases) AS total_cases FROM dengue_data")
    total_cases_result = cursor.fetchone()
    total_cases = total_cases_result['total_cases'] if total_cases_result else None
    cursor.execute("SELECT SUM(deaths) AS total_deaths FROM dengue_data")
    deaths = cursor.fetchone()
    total_deaths = deaths['total_deaths'] if deaths else None

    # Get top region with highest cases
    cursor.execute("""
        SELECT Region, SUM(cases) AS total_cases
        FROM dengue_data
        GROUP BY Region
        ORDER BY total_cases DESC
        LIMIT 1
    """)
    highest_cases_data = cursor.fetchone()

    # Close cursor and prepare data
    cursor.close()

    # Render the index template with data
    return render_template(
        'index.html',
        totalc=total_cases,
        totalD=total_deaths,
        region=highest_cases_data['Region'],
        cases=highest_cases_data['total_cases'],
    )

@app.route('/ind2')
def ind2():
    cursor = get_mysql_connection().cursor(dictionary=True)

    total_hr_query = """SELECT 
    SUM(Dentist) AS TotalDentist,
    SUM(Doctor) AS TotalDoctor,
    SUM(`Medical Technologist`) AS TotalMedicalTechnologist,
    SUM(Midwife) AS TotalMidwife,
    SUM(Nurse) AS TotalNurse,
    SUM(Dietitian) AS TotalDietitian,
    SUM(Pharmacist) AS TotalPharmacist,
    SUM(`Physical Therapist`) AS TotalPhysicalTherapist,
    SUM(RadiologicTechnologist) AS TotalRadiologicTechnologist,
    SUM(`X-rayTechnologist`) AS TotalXrayTechnologist
    FROM doh_humanresource"""
    cursor.execute(total_hr_query)
    total_hr = cursor.fetchall()

    c_query = """SELECT 
    Classification,
    SUM(Dentist + Doctor + `Medical Technologist` + Midwife + Nurse + Dietitian + Pharmacist + `Physical Therapist` + RadiologicTechnologist + `X-rayTechnologist`) AS TotalNumber
FROM doh_humanresource
GROUP BY Classification;"""
    cursor.execute(c_query)
    total_c = cursor.fetchall()

    # Close cursor and prepare data
    cursor.close()
    return render_template('ind2.html', total_hr = total_hr[0], total_c = total_c)

# Function regional cases data
@app.route('/get_regional_cases')
def get_regional_cases():
    try:
        cursor = get_mysql_connection().cursor(dictionary=True)
        cursor.execute("SELECT Region, SUM(cases) AS total_cases FROM dengue_data GROUP BY Region")
        r_data = cursor.fetchall()
        cursor.close()
        print(f"Regional Cases Data: {r_data}")  # Add this line for debug
        return jsonify(r_data)
    except Exception as e:
        print(f"Error in get_regional_cases: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
    
# Function regional cases data
@app.route('/get_regional_death')
def get_regional_death():
    try:
        cursor = get_mysql_connection().cursor(dictionary=True)
        cursor.execute("SELECT Region, SUM(deaths) AS total_deaths FROM dengue_data GROUP BY Region")
        d_data = cursor.fetchall()
        cursor.close()
        print(f"Regional Deaths Data: {d_data}")  # Add this line for debug
        return jsonify(d_data)
    except Exception as e:
        print(f"Error in get_regional_d: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

# Route for heatmap data
@app.route('/get_heatmap_data')
def get_heatmap_data():
    try:
        cursor = get_mysql_connection().cursor(dictionary=True)
        cursor.execute("SELECT lat, lon, cases FROM dengue_data")
        heatmapdata = cursor.fetchall()
        cursor.close()
        heatmap_data = [[row['lat'], row['lon'], row['cases']] for row in heatmapdata]
        return jsonify(heatmap_data)
    except Exception as e:
        print(f"Error in get_heatmap_data: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True)
