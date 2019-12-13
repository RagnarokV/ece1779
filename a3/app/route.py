from flask import Flask, render_template, url_for, request, jsonify , flash, redirect, request, session
from app import resources, database
from app.forms import LoginForm,RegistrationForm, ApplicationUploadForm, ApplicationSelection, addUser, addHealthRule, addActionGroup, addPolicy
from app.forms import ResourceSelection, widgetForm, lookupDashboard, newDashboard
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib
import datetime
import pprint
import os
import time
import requests

webapp= Flask(__name__)
webapp.config['SECRET_KEY'] = "c7e22c3ba94bd20390e19e9954796d8b"
AWS_ACCESS_KEY = #access key
AWS_SECRET_KEY = # secret key


@webapp.route('/', methods=['GET', 'POST'])
@webapp.route('/login', methods=['GET', 'POST'])
def login():
    session["loggedIn"] = False
    session["currentUser"] = ""
    session["access_level"]=""
    session["accountName"] =""
    form = LoginForm()
    if form.validate_on_submit():
        account = str(form.account.data)
        username = str(form.username.data)
        password = str(form.password.data)

        verify_variable=database.verify_username(account,username, password)
        if verify_variable[0]==1:
            print("Successful Authentication")
            session["access_level"]= str(verify_variable[1])
            session["loggedIn"] = True
            session["currentUser"] = username
            session["accountName"] =account
            return redirect(url_for('home_page'))

        else:
            error="Failed Authentication!"
            return render_template("login.html", form=form, error=error)
    return render_template("login.html",form=form,error="")

@webapp.route('/home_page', methods=['GET', 'POST'])
def home_page():
    if 'loggedIn' in session:
        if session["loggedIn"] == True:
            form2 = ApplicationSelection()
            application_list = database.scan(str(session["accountName"]), 'applications')
            event_list = database.scan(str(session['accountName']), 'events')
            form2.application.choices = []
            for app in application_list:
                form2.application.choices.append((app['application_name'],app['application_name']))
            form = ApplicationUploadForm()
            account = str(session['accountName'])
            if form.validate_on_submit():
                if 'submit' in request.form:
                    f=form.upload.data
                    application=str(form.application.data)

                    filename = secure_filename(f.filename)
                    temp=(webapp.instance_path).split('/')
                    temp=temp[:-1]
                    s='/'
                    final_path=s.join(temp)
                    file_path=final_path+"/app/static/Applications/"
                    file_name=session["accountName"] +'_'+application+ '_' + (str(time.time())).replace('.', '_') + '_' + filename
                    final_paths = file_path + file_name
                    print(final_paths)
                    f.save(final_paths)
                    node_data=resources.parse_applictaion_properties(final_paths)
                    node_list=node_data["node_list"]
                    adj_list= node_data["adjacency_list"]
                    resources.draw_application_graph(str(session["accountName"]),application, node_list, adj_list);

                    for node in node_list:
                        database.insert_into_nodes(str(session["accountName"]), int(node["node_ID"]), node["node_type"], application)
                        database.insert_into_applications(str(session["accountName"]),application,final_paths)

            return render_template("home.html",form=form,form2=form2, account=account, event_list = event_list)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))



@webapp.route('/monitor_page', methods=['GET', 'POST'])
def monitor_page():
    if 'loggedIn' in session:
        response = database.get_item(str(session['accountName']), 'users', 'username', str(session['currentUser']))
        access_level = int(response['access'])
        if access_level < 2:
            flash('You do not have permissions to access that page!', 'danger')
            return redirect(url_for('dashboard_page'))
        if session["loggedIn"] == True:
            form = ResourceSelection()
            application_list = database.scan(str(session["accountName"]), 'applications')
            node_list= database.scan(str(session['accountName']), 'nodes')
            for node in node_list:
                node['node_ID'] = str(node['node_ID'])
            dashboard_list = database.scan(str(session['accountName']), 'dashboards')
            for dashboard in dashboard_list:
                dashboard['dashboard_ID'] = str(dashboard['dashboard_ID'])
            application_choices=[]
            node_choices= []
            for application in application_list:
                application_choices.append((application['application_name'],application['application_name']))
            for node in node_list:
                node_choices.append((node['node_ID'], node['node_ID']))
            widget_form=widgetForm()
            form.application.choices = application_choices
            form.node.choices = node_choices
            form.metric.choices = [('disk_util', 'disk_util'), ('cpu_util', 'cpu_util'), ('mem_util', 'mem_util')]

            data_x=[]
            data_y=[]
            query=""
            widget_count = len(database.scan(str(session['accountName']), 'widgets'))

            if ('application' in request.form) and ('node' in request.form) and ('metric' in request.form):
                application = str(request.form['application'])
                node = str(request.form['node'])
                metric = str(request.form['metric'])
                (query, list_tupple) = resources.graph_data(application, node, metric)
                query = str(query)
                print('List Tupple: ', list_tupple)
                for tupple in list_tupple:
                    data_x.append(tupple[0])
                    data_y.append(tupple[1])

            if ('widgetID' in request.form) and ('DashboardID' in request.form) and ('widgetQuery' in request.form):
                widgetID = int(request.form['widgetID'])
                DashboardID = str(request.form['DashboardID'])
                widgetQuery = str(request.form['widgetQuery'])
                widgetQuery = widgetQuery.replace('"','')
                print(widgetID, DashboardID, widgetQuery)
                database.insert_into_widgets(str(session['accountName']), widgetID, DashboardID, widgetQuery)
            print(dashboard_list)
            return render_template("monitor.html",form=form, node_list = node_list, data_x= data_x, data_y= data_y,
                                   dashboard_list= dashboard_list, query= str(query), widget_count= widget_count, widget_form= widget_form)
    else:
        return redirect(url_for('login'))



@webapp.route('/alert_page', methods=['GET', 'POST'])
def alert_page():
    if 'loggedIn' in session:
        response = database.get_item(str(session['accountName']), 'users', 'username', str(session['currentUser']))
        access_level = int(response['access'])
        if access_level < 2:
            flash('You do not have permissions to access that page!', 'danger')
            return redirect(url_for('dashboard_page'))
        if session["loggedIn"] == True:
            node_list = database.scan(str(session['accountName']), 'nodes')
            for node in node_list:
                node['node_ID'] = str(node['node_ID'])
            alert_list = database.scan(str(session['accountName']), 'alerts')
            for alert in alert_list:
                alert['alert_ID'] = str(alert['alert_ID'])
                alert['node_ID'] = str(alert['node_ID'])
            application_list=[]
            for node in node_list:
                if node['application_name'] not in application_list:
                    application_list.append(node['application_name'])

            for alert in alert_list:
                for node in node_list:
                    if node['node_ID']==str(alert['node_ID']):
                        alert['Application'] = node['application_name']

            application_choices = []
            node_choices = []
            i = 0
            for application in application_list:
                application_choices.append((application, application))
                i = i + 1
            i = 0
            for node in node_list:
                node_choices.append((node['node_ID'], node['node_ID']))
                i = i + 1

            action_group= database.scan(str(session['accountName']), 'action_group')
            policies = database.scan(str(session['accountName']), 'policies')
            policy_form = addPolicy()
            form = ResourceSelection()
            form.application.choices = application_choices
            form.node.choices = node_choices

            create_health_form = addHealthRule()
            create_health_form.application.choices = application_choices
            create_health_form.node.choices = node_choices
            create_health_form.metric.choices = [('disk_util', 'disk_util'), ('cpu_util', 'cpu_util'), ('mem_util', 'mem_util')]
            create_action_form = addActionGroup()

            if ('submit_health_rule' in request.form) :
                if ('rule_id' in request.form)  and ('rule_name' in request.form) and ('application' in request.form) and ('node' in request.form) and ('metric' in request.form) and ('operator' in request.form) and ('value' in request.form):
                    rule_id= int(request.form['rule_id'])
                    rule_name= str(request.form['rule_name'])
                    application= str(request.form['application'])
                    node= str(request.form['node'])
                    metric= str(request.form['metric'])
                    operator= str(request.form['operator'])
                    value= str(request.form['value'])
                    query= "SELECT timestamp, metric_value FROM metrics WHERE machineid = '%s' and metric_name = '%s' AND metric_value %s %s AND timestamp = (SELECT MAX(timestamp) FROM metrics);" % (node, metric, operator, value)
                    print(rule_id, node, rule_name, query)
                    database.insert_into_alerts(str(session['accountName']), rule_id, node, rule_name, query)

            if ('submit_action' in request.form) :
                if ('groupID' in request.form) and ('group_name' in request.form) and ('email_list' in request.form):
                    groupID= int(request.form['groupID'])
                    group_name=str(request.form['group_name'])
                    temp_email_list= str(request.form['email_list'])
                    temp_email_list=temp_email_list.replace('\n','')
                    temp_email_list= temp_email_list.replace(' ','')
                    temp_email_list = temp_email_list.replace('\r','')

                    email_list= temp_email_list.split(',')
                    for email in email_list:
                        if len(email) == 0:
                            email_list.remove(email)
                    print(groupID, group_name, email_list)
                    database.insert_into_action_group(str(session['accountName']), groupID, group_name, email_list)

            if ('submit' in request.form):
                print('inside policies')
                if ('policy_id' in request.form) and ('action_group' in request.form) and ('health_rule' in request.form):
                    policy_id= int(request.form['policy_id'])
                    action_group_id= str(request.form['action_group'])
                    health_rule_id= str(request.form['health_rule'])
                    print(policy_id, action_group_id, health_rule_id)
                    database.insert_into_policies(str(session['accountName']), policy_id, action_group_id, health_rule_id)

            return render_template("alert.html",form=form,create_health_form=create_health_form,
                                   create_action_form = create_action_form, alert_list= alert_list,
                                   node_list = node_list, group_list=action_group,
                                   policy_list=policies, policy_form = policy_form)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@webapp.route('/dashboard_page', methods=['GET', 'POST'])
def dashboard_page():
    if 'loggedIn' in session:
        if session["loggedIn"] == True:
            dashboard_list = database.scan(str(session['accountName']), 'dashboards')
            for dashboard in dashboard_list:
                dashboard['dashboard_ID'] = str(dashboard['dashboard_ID'])
            widget_list = database.scan(str(session['accountName']), 'widgets')
            for widget in widget_list:
                widget['widget_ID'] = str(widget['widget_ID'])
            dashboard_form=newDashboard()
            form = lookupDashboard()
            try:
                current_dashboard= dashboard_list[0]
            except:
                database.insert_into_dashboards(str(session['accountName']), 0, 'No dashboards')

            if ('dashboardID' in request.form) and ('dashboardName' in request.form):
                dashboardID = int(request.form['dashboardID'])
                print('Type of dashboardID: ', type(dashboardID))
                dashboardName = str(request.form['dashboardName'])
                database.insert_into_dashboards(str(session['accountName']), dashboardID, dashboardName)

            if 'DashboardID' in request.form:
                DashboardID = str(request.form['DashboardID'])
                print("Now looking at "+ str(DashboardID))
                for dashboard in dashboard_list:
                    if str(dashboard['dashboard_ID'])==DashboardID:
                        current_dashboard = dashboard
                        break
            current_id= str(current_dashboard['dashboard_ID'])
            current_widget_list= []
            for widget in widget_list:
                if str(widget['dashboard_ID'])==current_id:
                    current_widget_list.append(widget)
            trace_list=[]
            for widget in current_widget_list:
                list_tupple = resources.query_rds(widget['query'])

                data_x=[]
                data_y=[]
                for tupple in list_tupple:
                    data_x.append(tupple[0])
                    data_y.append(tupple[1])
                trace={}
                trace['x'] = data_x
                trace['y'] =data_y
                trace['type']= 'scatter'
                trace_list.append(trace)
            #pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(trace_list)
            dashboard_title= current_dashboard['dashboard_name']
            return render_template("dashboard.html", dashboard_list= dashboard_list, form = form,
                                   dashboard_title=dashboard_title, trace_list= trace_list, dashboard_form= dashboard_form )
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@webapp.route('/administrator_page', methods=['GET', 'POST'])
def admin_page():
    if 'loggedIn' in session:
        response = database.get_item(str(session['accountName']), 'users', 'username', str(session['currentUser']))
        access_level = int(response['access'])
        if access_level < 3:
            flash('You do not have permissions to access that page!', 'danger')
            return redirect(url_for('dashboard_page'))
        if session["loggedIn"] == True:
            form=addUser()
            list_user = database.scan(str(session['accountName']), 'users')
            if ('username' in request.form) and ('password' in request.form) and ('access_level' in request.form) and ('name' in request.form):
                username = str(request.form['username'])
                password = str(request.form['password'])
                name = str(request.form['name'])
                access = int(request.form['access_level'])
                print(username, password, name, access)
                database.insert_into_users(str(session['accountName']), username, password, access, name)
            return render_template("administrator.html",form=form,user_list=list_user)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))




@webapp.route('/register_page', methods=['GET', 'POST'])
def register_page():
    session["loggedIn"] = False
    session["currentUser"] = ""
    session["access_level"] = ""
    session["accountName"] = ""
    form2 = RegistrationForm()
    if form2.validate_on_submit():
        #print("hello")
        account = str(form2.account.data)
        password = str(form2.password.data)
        if form2.validateAccountname(account)==0:
            error="Sorry the Account already exist!"
            flash(error)
            return render_template("register.html", form=form2, error=error)
        else:
            database.create_account(account)
            database.insert_into_users(account,'root',password,'3')
            success="Congrats! New User Created!"
            return render_template("register.html", form=form2, success=success)
    return render_template("register.html", form=form2,error="")



