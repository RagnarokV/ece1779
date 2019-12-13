from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, TextAreaField, HiddenField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError



class LoginForm(FlaskForm):
    account = StringField('Account', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    account = StringField('Account', validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4,max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validateAccountname(self, accountname):
        #return databaseModule.verify_account(accountname)
        #change to dynamo
        return 1

class ApplicationUploadForm(FlaskForm):
    application = StringField('Application', validators=[DataRequired(), Length(min=4, max=100)])

    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['prop'])
    ])

    submit = SubmitField('Upload')

class ApplicationSelection(FlaskForm):
    application = SelectField('Current Application')
    submit = SubmitField('Go')


class ResourceSelection(FlaskForm):
    application = SelectField('Current Application')
    node = SelectField('Current Node')
    metric = SelectField('Current Meric')
    submit = SubmitField('Launch')

class addUser(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Account', validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4,max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    access_level = SelectField('Current Access Level',choices=[('1','Reader'),('2','Creator'),('3','Administrator')])
    submit = SubmitField('Save')
    remove = SubmitField('Delete')

class addHealthRule(FlaskForm):
    rule_id = HiddenField('Health-Rule ID', validators=[DataRequired()]);
    rule_name = StringField('Name', validators=[DataRequired()])
    application = SelectField('Current Application')
    node = SelectField('Current Node')
    metric = SelectField('Current Metric')
    operator = SelectField('Operator',choices=[('>','>'),('==','=='),('<','<'),('=>','=>'),('=<','=<')])
    value= DecimalField('Value',validators=[DataRequired()])
    submit_health_rule = SubmitField('Save')
    remove_health_rule = SubmitField('Delete')

class addActionGroup(FlaskForm):
    groupID = HiddenField('Group ID', validators=[DataRequired()])
    group_name = StringField('Group Name', validators=[DataRequired()])
    email_list = TextAreaField('Email List', validators=[DataRequired()])
    submit_action = SubmitField('Save')
    remove_action= SubmitField('Delete')

class addPolicy(FlaskForm):
    policy_id = IntegerField('Policy Id', validators=[DataRequired()])
    action_group = StringField('Action Group', validators=[DataRequired()])
    health_rule = StringField('Health Rule', validators=[DataRequired()])
    submit = SubmitField('Save')

class widgetForm(FlaskForm):
    widgetID= HiddenField('Widget ID',validators=[DataRequired()])
    DashboardID = HiddenField('Widget ID',validators=[DataRequired()])
    widgetQuery = HiddenField('Widget Query',validators=[DataRequired()])
    submit_widget = SubmitField('Pin')

class lookupDashboard(FlaskForm):
    DashboardID = HiddenField('Widget ID', validators=[DataRequired()])
    submit_dashboard = SubmitField('Pin')

class newDashboard(FlaskForm):
    dashboardID= HiddenField('Widget ID', validators=[DataRequired()])
    dashboardName= StringField('Action Group', validators=[DataRequired()])
    create_dashboard = SubmitField('Save')











