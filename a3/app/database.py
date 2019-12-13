import boto3
from botocore.exceptions import ClientError
import hashlib, uuid
from boto3.dynamodb.conditions import Key, Attr


########################################################################

#######       METHODS AVAILABLE   #######
#   create_account(company_name)
#   insert_into_<table_name>(company_name, other_fields_in_table)
#   delete_item(company_name, table_name, primary_key, primary_key_value)
#   get_item(company_name, table_name, primary_key, primary_key_value)
#   retrieve_items(company_name, table_name, **kwargs)
########################################################################


boto_session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name='us-east-1')

dynamodb = boto_session.resource('dynamodb')
dynamodb_client = boto_session.client('dynamodb')
s3_client = boto_session.client('s3')
#Helper
def get_table_name(company_name, table_name):
    return company_name + '_' + table_name

# Creates a table with given primary key and primary key type
def create_table(name, primary_key, primary_key_type):
    table = dynamodb.create_table(
        TableName=name,
        KeySchema=[
            {
                'AttributeName': primary_key,
                'KeyType': 'HASH'  #Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': primary_key,
                'AttributeType': primary_key_type
            },     
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        Tags=[
            {
            'Key': 'TableName',
            'Value': name
            }
        ]
    )

    #Wait until table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=name)
    print(table.item_count)
    print("Table status:", table.table_status)
    return


# Registers a new account and creates corresponding tables, creates an empty S3 bucket for the company
def create_account(name):
    current_tables = dynamodb_client.list_tables()['TableNames']
    #runs the first time to create an Accounts table
    if 'Accounts' not in current_tables:
        create_table('Accounts', 'AccountName', 'S')

    #Insert new account details into Accounts table and create other tables
    account_data = {'AccountName': name}
    insert_into_table('Accounts', account_data)
    print('Added new account')
    print('Creating other tables')

    # USERS
    user_table_name = get_table_name(name, 'users')
    create_table(user_table_name, 'username', 'S')

    # APPLICATIONS
    app_table_name = get_table_name(name, 'applications')
    create_table(app_table_name, 'application_name', 'S')

    # NODES
    node_table_name = get_table_name(name, 'nodes')
    create_table(node_table_name, 'node_ID', 'N')

    # ALERTS
    alerts_table_name = get_table_name(name, 'alerts')
    create_table(alerts_table_name, 'alert_ID', 'N')

    # ACTION GROUP
    actionGroup_name = get_table_name(name, 'action_group')
    create_table(actionGroup_name, 'group_ID', 'N')

    # POLICY
    policy_table_name = get_table_name(name, 'policies')
    create_table(policy_table_name, 'policy_ID', 'N')

    # WIDGETS
    widget_table_name = get_table_name(name, 'widgets')
    create_table(widget_table_name, 'widget_ID', 'N')

    # DASHBOARD
    policy_table_name = get_table_name(name, 'dashboards')
    create_table(policy_table_name, 'dashboard_ID', 'N')

    events_table_name = get_table_name(name, 'events')
    create_table(events_table_name, 'timestamp_alert', 'S')

    print('Initialized tables for new account')
    print('Creating S3 bucket')
    bucket_name = name
    s3_client.create_bucket(Bucket=bucket_name)
    print('Finished creating new bucket')

def insert_into_table(table_name, data): # (string, dict) -> None
    table = dynamodb.Table(table_name)
    '''
    test_key = 'test_key1'
    username = 'test_username1'
    password = 'test_password1'
    table.put_item(
        Item={ 
            'test_key': test_key,
            'username': username,
            'password': password
        }
    )
    '''
    table.put_item(
        Item=data
    )
    print("Successfully inserted data into {} table".format(table_name))
    return

# Returns dictionary of entire row as key value pairs
def get_item(company_name, table_name, primary_key, primary_key_value):
    table_name = get_table_name(company_name, table_name)
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(
            Key={
                primary_key: primary_key_value
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        print('Successfully retrieved item')
        return item
    return


### Inserting in all the tables - uses insert_into_table
def insert_into_users(company_name, username, password, access, name):
    table_name = get_table_name(company_name, 'users')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print('Created',password)
    print('Hashed',hashed_password)
    data = {
        'username': username,
        'password': hashed_password,
        'access': access,
        'name': name
    }
    insert_into_table(table_name, data)

def insert_into_applications(company_name, application_name, file_):
    table_name = get_table_name(company_name, 'applications')
    data = {
        'application_name': application_name,
        'file': file_
    }
    insert_into_table(table_name, data)

def insert_into_nodes(company_name, node_ID, node_type, application_name):
    table_name = get_table_name(company_name, 'nodes')
    data = {
        'node_ID': node_ID,
        'node_type': node_type,
        'application_name': application_name
    }
    insert_into_table(table_name, data)

def insert_into_alerts(company_name, alert_ID, node_ID, description, query):
    table_name = get_table_name(company_name, 'alerts')
    data = {
        'alert_ID': alert_ID,
        'node_ID': node_ID,
        'description': description,
        'query': query
    }
    insert_into_table(table_name, data)
    
def insert_into_action_group(company_name, group_ID, group_name, action):
    table_name = get_table_name(company_name, 'action_group')
    data = {
        'group_ID': group_ID,
        'group_name': group_name,
        'action': action
    }
    insert_into_table(table_name, data)

def insert_into_policies(company_name, policy_ID, group_ID, alerts):
    table_name = get_table_name(company_name, 'policies')
    data = {
        'policy_ID': policy_ID,
        'group_ID': group_ID,
        'alerts': alerts
    }
    insert_into_table(table_name, data)

def insert_into_widgets(company_name, widget_ID, dashboard_ID, query):
    table_name = get_table_name(company_name, 'widgets')
    data = {
        'widget_ID': widget_ID,
        'dashboard_ID': dashboard_ID,
        'query': query
    }
    insert_into_table(table_name, data)

def insert_into_dashboards(company_name, dashboard_ID, dashboard_name):
    table_name = get_table_name(company_name, 'dashboards')
    data = {
        'dashboard_ID': dashboard_ID,
        'dashboard_name': dashboard_name
    }
    insert_into_table(table_name, data)


# Delete item from table
def delete_item(company_name, table_name, primary_key, primary_key_value):
    table_name = get_table_name(company_name, table_name)
    table = dynamodb.Table(table_name)
    try:
        response = table.delete_item(
            Key={
                primary_key: primary_key_value
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            print(e.response['Error']['Message'])
    else:
        print("DeleteItem succeeded:")

def verify_username(company_name, username, password):
    table = dynamodb.Table('Accounts')
    response = table.get_item(
            Key={
                'AccountName': company_name
            }
        )
    if 'Item' not in response:
        print('Invalid company name')
        return(0,0)
    print(response['Item'])
    print('Entered password: ', password)
    response = get_item(company_name, 'users', 'username', username)
    password2 = response['password']
    validate_password = hashlib.sha256(password.encode()).hexdigest()
    print('Hashed entered password: ', validate_password)
    print('Password in DB: ', password2)
    return (1,response['access']) if password2 == validate_password else (0,0)

def retrieve_items(company_name, table_name, **kwargs):
    table_name = get_table_name(company_name, table_name)
    print('Table name: ', table_name)
    numArgs = len(kwargs)
    if numArgs == 1:
        return retrieve_one(table_name, kwargs)
    elif numArgs == 2:
        return retrieve_two(table_name, kwargs)
    else:
        return retrieve_three(table_name, kwargs)


def retrieve_one(table_name, kwargs):
    table = dynamodb.Table(table_name)
    keys, values = [], []
    for key, val in kwargs.items():
        keys.append(key)
        values.append(val)
    print(keys, values)
    response = table.scan(
        FilterExpression=Attr(str(keys[0])).eq(str(values[0]))
    )
    return response['Items']

def retrieve_two(table_name, kwargs):
    table = dynamodb.Table(table_name)
    keys, values = [], []
    for key, val in kwargs.items():
        keys.append(key)
        values.append(val)
    print(keys, values)
    response = table.scan(
        FilterExpression=Attr(str(keys[0])).eq(str(values[0])) & Attr(str(keys[1])).eq(str(values[1]))
    )
    return response['Items']

def retrieve_three(table_name, kwargs):
    table = dynamodb.Table(table_name)
    keys, values = [], []
    for key, val in kwargs.items():
        keys.append(key)
        values.append(val)
    print(keys, values)
    response = table.scan(
        FilterExpression=Attr(str(keys[0])).eq(str(values[0])) & Attr(str(keys[1])).eq(str(values[1])) & Attr(str(keys[2])).eq(str(values[2]))
    )
    return response['Items']

def scan(company_name, table_name):
    table_name = get_table_name(company_name, table_name)
    table = dynamodb.Table(table_name)
    response = table.scan()
    return response['Items']
# Accounts - AccountName
# Users - username, password, access, name
# Application - application ID, file
# Nodes - nodeID, application ID
# Alerts - ID, node, description, sql query
# Action Group - ID, action
# Policy - ID, group ID, Alerts
# Widgets - widget ID, dashboard, SQL query
# Dashboard - ID
