from imutils.object_detection import non_max_suppression
from operator import itemgetter
import mysql.connector

USERNAME = #username
PASSWORD = #pass
HOSTNAME = #host'
DATABASE = #db'

# query last 30 minutes data
def grab_metrics(metric_name, machine_id):
	db = mysql.connector.connect(
		user=USERNAME,
		password=PASSWORD,
		host=HOSTNAME,
		database=DATABASE)
	cur = db.cursor()
	cur.execute(
		"SELECT `timestamp`, `metric_value` FROM metrics WHERE machineid = '%s' and metric_name = '%s' \
		and timestamp >= 2625002;" % (machine_id, metric_name))

	result = cur.fetchall()
	cur.close()
	db.close()

	timestamp = []
	value = []

	result = sorted(result, key=itemgetter(0))

	for item in result:
		timestamp.append(int(item[0]))
		value.append(item[1])
	
	data = [timestamp, value]
	return data
