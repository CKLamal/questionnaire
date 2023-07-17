from flask import Flask, render_template, request, jsonify, redirect
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'db-questionnaire.cluster-cebkgp7vsusb.ap-northeast-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Gcis1234'
app.config['MYSQL_DB'] = 'questionnaire'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('questionnaire.html')

@app.route('/preferences', methods=['POST'])
def save_preferences():
    data = request.get_json()
    selected_countries = data.get('countries', [])
    participant_name = data.get('participantName')
    # Check if the maximum number of selections is exceeded
    if len(selected_countries) > 5:
        return jsonify({'success': False, 'message': 'You can select up to 5 countries.'}), 400
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        print(request.form)
        
        print(participant_name)
        if participant_name:
            print("now add participant")
            cursor.execute("INSERT INTO participants (participant_name) VALUES (%s)", (participant_name,))
            participant_id = cursor.lastrowid
        else:
            participant_id = "Unknown"

        # Insert preferences into preferences table
        for country_id in selected_countries:
            print("now add preferences")
            cursor.execute("INSERT INTO preferences (participant_id, country_id) VALUES (%s, %s)", (participant_id, country_id))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Preferences submitted successfully!'})

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500
    

    return jsonify({'success': True, 'message': 'Preferences submitted successfully!'})

@app.route('/result')
def result():
    try:
        conn = mysql.connection
        cursor = conn.cursor()

        # Retrieve the total number of participants
        cursor.execute("SELECT COUNT(DISTINCT participant_id) FROM preferences")
        total_participants = cursor.fetchone()[0]
        print('Total Participants:', total_participants)

        # Retrieve the total number of countries selected
        cursor.execute("SELECT COUNT(DISTINCT country_id) FROM preferences")
        total_countries_selected = cursor.fetchone()[0]
        print('Total Countries Selected:', total_countries_selected)

        # Retrieve the total number of votes for each country with country names
        cursor.execute("SELECT c.country_name, COUNT(*) AS vote_count FROM preferences AS p JOIN countries AS c ON p.country_id = c.country_id GROUP BY c.country_name")
        vote_counts = cursor.fetchall()
        print('Vote Counts:', vote_counts)

        # Retrieve the top 3 favorite countries with country names
        cursor.execute("SELECT c.country_name, COUNT(*) AS vote_count FROM preferences AS p JOIN countries AS c ON p.country_id = c.country_id GROUP BY c.country_name ORDER BY vote_count DESC LIMIT 3")
        top_countries = cursor.fetchall()
        print('Top Countries:', top_countries)

        # Retrieve the last 24-hour vote distribution
        cursor.execute("SELECT HOUR(timestamp) AS hour, COUNT(*) AS vote_count FROM preferences WHERE timestamp >= NOW() - INTERVAL 1 DAY GROUP BY HOUR(timestamp)")
        vote_distribution = cursor.fetchall()
        print('Vote Distribution:', vote_distribution)

        cursor.close()
        #conn.close()

        return render_template('result.html', total_participants=total_participants, total_countries_selected=total_countries_selected,
                               vote_counts=vote_counts, top_countries=top_countries, vote_distribution=vote_distribution)
    except Exception as e:
        print (e)
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500


if __name__ == '__main__':
    app.run(port=2021,host='0.0.0.0')

# ec2 instance i-084091c761b350b01