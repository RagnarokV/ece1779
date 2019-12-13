import os
import json
import networkx as nx
import matplotlib.pyplot as plt
import time

from operator import itemgetter
import mysql.connector

USERNAME = #user
PASSWORD = #pass
HOSTNAME = #host
DATABASE = #db


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


# run a query against RDS
def query_rds(query):
    db = mysql.connector.connect(
        user=USERNAME,
        password=PASSWORD,
        host=HOSTNAME,
        database=DATABASE)
    cur = db.cursor()
    cur.execute(query)

    result = cur.fetchall()
    print(result)
    cur.close()
    db.close()

    return result

def graph_data(application,node,metric_name,time_before=10):
    machine_id= str(node)
    time_now = time.time()/60
    time_beyond = time_now - time_before

    query_template= "SELECT timestamp, metric_value FROM metrics WHERE machineid = '%s' and metric_name = '%s' AND timestamp >= '%s';" % (machine_id, metric_name, time_beyond)
    print(query_template)
    return (query_template,query_rds(query_template))




def parse_applictaion_properties(file_path):
    with open(file_path,'r') as fp:
        data=json.load(fp)
        print(data)
        return data

def draw_application_graph(company_name,application_name,node_list, adj_matrix):
    G = nx.Graph()
    labels = {}
    mapping = {}
    print((node_list[0])["node_ID"])
    for i in range(len(node_list)):
        node = node_list[i]
        G.add_node(int(node["node_ID"]))
        labels[int(node["node_ID"])] = " " + node["node_type"] + "\n" + "---------" + "\n" + "ID: " + str(node["node_ID"])

    for i in range(0, len(adj_matrix)):
        for j in range(0, len(adj_matrix[i])):
            if adj_matrix[i][j] == 1:
                # print(int((node[i])["Node ID"]),int((node[j])["Node_ID"]))
                nodeX = node_list[i]
                nodeY = node_list[j]
                G.add_edge(int(nodeX["node_ID"]), int(nodeY["node_ID"]))

    # nx.set_node_attributes(G, attr)
    H = nx.relabel_nodes(G, labels)
    pos = nx.spring_layout(H, scale=2, seed=84)

    # r'$\circ$'

    nx.draw_networkx(H, pos=pos, node_shape='o', node_color="#48c22d", font_family='Krungthep', edge_color='#2065e8',
                     width=4, font_color="black", node_size=3300, font_size=9, style="dashed")
    nx.draw_networkx(H, pos=pos, node_shape='o', node_color="white", font_family='Krungthep',
                     edge_color='white', width=0.8, font_color="black", node_size=2200, font_size=9)
    # nx.draw_networkx_labels(G, nx.spring_layout(G), labels)
    # save in s3 later
    plt.savefig('app/static/graphs/' + company_name + '_' + application_name)


'''draw_application_graph('dhtest','test_app',[{"Node ID": "1313", "Node Type": "PC"},
                                            {"Node ID": "7575", "Node Type": "Server"},
                                            {"Node ID": "775", "Node Type": "Server"}],
                                            [[0,1,0], [1,0,1],[1,0,1]])'''

    
    
#print(query_rds("SELECT DISTINCT timestamp FROM metrics ORDER BY timestamp "))

#print('lets see')

#print(query_rds("SELECT timestamp, metric_value FROM metrics WHERE metric_name = 'disk_util' AND metric_value > 4 AND timestamp = (SELECT MAX(timestamp) FROM metrics);"))



