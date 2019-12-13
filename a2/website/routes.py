from flask import render_template, url_for, flash, redirect, request
from website import app, instance_start_time
from datetime import datetime, timedelta
from operator import itemgetter
import boto3

#Default route and login route the same
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/workers')
def workers():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    client = boto3.client('cloudwatch')
    metric_name = 'CPUUtilization'
    statistic = 'Average'  

    count = 0
    CPU_Util = {}
    HTTP_Req = {}

    for instance in instances:

        # HTTP req metric
        time_stamps = []        
        requests = []
        response = client.get_metric_statistics(
            Period=1 * 60,
            StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName='HTTP_Requests',
            Namespace='HTTP_Requests',
            Statistics=['Maximum'],
            Dimensions=[
                    {
                    'Name': 'Instance_ID',
                    'Value': instance.id
                    },
                ]
        )
        print('This is the custom metric:')

        requests = []
        time_stamps = []
        for point in response["Datapoints"]:
            hour = point['Timestamp'].hour
            minute = point['Timestamp'].minute
            time = hour + minute/60
            time_stamps.append(round(time, 2))
            requests.append(point['Maximum'])
        
        indexes = list(range(len(time_stamps)))
        indexes.sort(key=time_stamps.__getitem__)
        time_stamps = list(map(time_stamps.__getitem__, indexes))
        requests = list(map(requests.__getitem__, indexes))
        HTTP_Req['localhost'] = [time_stamps, requests]
        for i in range(len(time_stamps)):
            print(time_stamps[i], requests[i])

        # CPU Util metrics
        time_stamps = []
        cpu_stats = []
        response = client.get_metric_statistics(
            Period=1 * 60,
            StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
            EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
            MetricName=metric_name,
            Namespace='AWS/EC2',
            Statistics=[statistic],
            Dimensions=[{'Name': 'InstanceId', 'Value': instance.id}]
        )

        for point in response['Datapoints']:
            hour = point['Timestamp'].hour
            minute = point['Timestamp'].minute
            time = hour + minute/60
            time_stamps.append(round(time, 2))
            cpu_stats.append(round(point['Average'], 2))
        indexes = list(range(len(time_stamps)))
        indexes.sort(key=time_stamps.__getitem__)
        time_stamps = list(map(time_stamps.__getitem__, indexes))
        cpu_stats = list(map(cpu_stats.__getitem__, indexes))
        CPU_Util[instance.id] = [time_stamps, cpu_stats]
    
    # CPU_Util is a dictionary, with keys = instance_id, and values = [sorted time_stamps, cpu_utilization values]

    #for key, value in CPU_Util.items():
    #    print('Labels: ', value[0])
    #   print('CPU Utilization: ', value[1])

    if not CPU_Util:
        flash('Worker pool currently empty, please manually start some instances.', category='danger')
    else:
        flash('There are currently {} worker(s).'.format(len(CPU_Util)), category='success')
    return render_template('workers.html', instances = instances, 
                            CPU_Util = CPU_Util, HTTP_Req = HTTP_Req)
                

@app.route('/control_workers')
def control_workers():
    title='Change Workers'
    return render_template('control_workers.html', title=title)

@app.route('/increase_workers')
def increase_workers():
    title='Change Workers'
    ec2 = boto3.resource('ec2')
    ec2.create_instances(ImageId='ami-080bb209625b6f74f', MinCount=1, MaxCount=1)
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    count = 0
    for instance in instances:
        count += 1
    flash('There are currently {} workers'.format(count))
    return redirect(url_for('control_workers'))

@app.route('/decrease_workers')
def decrease_workers():
    title='Change Workers'
    
    return redirect(url_for('control_workers'))


@app.route('/stop',methods=['GET','POST'])
# Stop a EC2 instance
def stop():
    ec2 = boto3.resource('ec2')

    ###### DO NOT CHANGE THE FILTER, REMOVING IT WILL DELETE ALL INSTANCES, INCLUDING THE ASSIGNMENT 1 INSTANCE! #######
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]).stop()
    ###### DO NOT CHANGE THE FILTER, REMOVING IT WILL DELETE ALL INSTANCES, INCLUDING THE ASSIGNMENT 1 INSTANCE! #######
    
    flash('Instances stopped/terminated successfully! Please manually restart instances from AWS to view charts.', category='success')
    return redirect(url_for('home'))