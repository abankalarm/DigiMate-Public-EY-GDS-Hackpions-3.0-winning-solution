from app.base.util import verify_pass
from sqlalchemy.sql.expression import false, null
from sqlalchemy.sql.functions import user
from app.home.plot import *
from app.home.predictions import *
from app.home import blueprint
import os
import pathlib
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_required, current_user
from app import login_manager, db
from jinja2 import TemplateNotFound
#from app.base.util import user
from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.sampledata.iris import flowers
import pandas as pd
import csv
from pandasql import sqldf
from datetime import date
from app.base.models import User
import ast
import datetime
import json
import sqlite3
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import httplib2
import base64


pysqldf = lambda q: sqldf(q, globals())
# con = sqlite3.connect("db.sqlite3")
# dfActivity = pd.read_sql_query("SELECT * from EmployeeActivity", con)
# dfEmployee = pd.read_sql_query("SELECT * from User where id != 1 and id != 451", con)
# dfHealth = pd.read_sql_query("SELECT * from EmployeeHealth", con)
# con.close()

dfActivity = pd.read_csv("./CSVs/EmployeeActivity.csv")
dfHealth = pd.read_csv("./CSVs/EmployeeHealth.csv")
dfEmployee = pd.read_csv("./CSVs/EmployeeDataset.csv")

dfActivity['Month'] = pd.to_datetime(dfActivity['Month'], format = "%d-%m-%Y")
dfHealth['ActivityDate'] = pd.to_datetime(dfHealth['ActivityDate'], format = "%d-%m-%Y")
dfEmployee['dob'] = pd.to_datetime(dfEmployee['dob'], format = "%d-%m-%Y")

with open('app/base/static/assets/data/yoga_data.json') as json_file:
    yoga_data = json.load(json_file)

with open('app/base/static/assets/data/mental_data.json') as json_file:
    mental_data = json.load(json_file)

def apiauth(username,password):
    user = User.query.filter_by(username=username).first()
    for row in User.query.filter_by(username='test').all():
        print(type(row))
        print(row.skills1)
        #print(row.fullname)
    # Check the password
    if user and verify_pass( password, user.password):
        return True
    return False

def getThought():

    url = "https://zenquotes.io/api/random"
    response = requests.request("GET", url)
    return response.json()[0]["q"]

def getCourses(allData,query):
    r = requests.get('https://api.coursera.org/api/courses.v1?q=search&query='+query+'&includes=instructorIds,partnerIds&fields=instructorIds,previewLink,name,photoUrl,previewLink,links,partnerIds')
    j = r.json()

    allData["c1"]={
        "name": j['elements'][0]['name'],
        "img" : j['elements'][0]['photoUrl'],
        "url" : 'https://www.coursera.org/learn/'+j['elements'][0]['slug'],
        "author" : j['linked']['partners.v1'][0]['name']
    }
    allData["c2"]={
        "name": j['elements'][1]['name'],
        "img" : j['elements'][1]['photoUrl'],
        "url" : 'https://www.coursera.org/learn/'+j['elements'][1]['slug'],
        "author" : j['linked']['partners.v1'][1]['name']
    }


    url = 'https://www.udemy.com/api-2.0/search-courses/recommendation/?course_badge=beginners_choice&page_size=5&skip_price=true&q='+query
    headers = {'content-type': 'application/json','Referer': 'https://10.10.10.10/courses/search/'}

    r1 = requests.get(url, headers=headers)
    j1 = r1.json()

    allData["u1"]={
        "name": j1['courses'][0]['title'],
        "img" : j1['courses'][0]['image_100x100'],
        "url" : 'https://www.udemy.com'+j1['courses'][0]['url'],
        "author" : j1['courses'][0]['visible_instructors'][0]['display_name']
    }
    allData["u2"]={
        "name": j1['courses'][1]['title'],
        "img" : j1['courses'][1]['image_100x100'],
        "url" : 'https://www.udemy.com'+j1['courses'][1]['url'],
        "author" : j1['courses'][1]['visible_instructors'][0]['display_name']
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == "pdf"


@blueprint.route('/index',methods=["GET","POST"])
@login_required
def index():
    for row in User.query.filter_by(id=current_user.get_id()).all():
        username = row.username
        department = row.department
        job_level = row.job_level
        res=json.loads(row.skills)
        res=res["skills"]  
    #TODO use thoughtgit
    thought=getThought()
    print(thought)
    events=[]
    temp=[]
    with open('CSVs/Events.csv','r') as data:
        for line in csv.DictReader(data):
            line["Attending"]=ast.literal_eval(line["Attending"])
            events.append(line)
    events=sorted(events, key=lambda x: datetime.datetime.strptime(x["Start"], "%Y-%m-%d"))
    temp=events.copy()
    inEvent=[]
   
    for event in events:
        if(datetime.datetime.strptime(event ["Start"], "%Y-%m-%d") <datetime.datetime.today() ):
            temp.remove(event)
    events=temp.copy()

    for event in temp:
        if username in event['Attending']:
            inEvent.append(event)
            events.remove(event)
        if(datetime.datetime.strptime(event ["Start"], "%Y-%m-%d") <datetime.datetime.today() ):
            events.remove(event)

    if request.method == 'POST':
        registerEvent = request.form["registerEvent"]
        if(registerEvent): 
            registerEvent=str(registerEvent)
            for event in events:
             
                if(event["Id"]==registerEvent and username not in event["Attending"] ) :
                  
                    # temp=[]
                    # with open('CSVs/Events.csv','r') as data:
                    #     for line in csv.DictReader(data):
                    #         temp.append(line)
                    for i in range(len(temp)):
                        if temp[i]==event:
                            temp[i]["Attending"].append(username)
                            break
                    keys = temp[0].keys()
                    with open('CSVs/Events.csv', 'w', newline='')  as output_file:
                        dict_writer = csv.DictWriter(output_file, keys)
                        dict_writer.writeheader()
                        dict_writer.writerows(temp)
                    # with open('CSVs/Events.csv', "wb") as outfile:
                    #     writer = csv.writer(outfile)
                    #     writer.writerow(temp.keys())
                    #     writer.writerows(zip(*temp.values()))
                    
                    events=temp.copy()

                    inEvent=[]
                    for event in temp:
                        if username in event['Attending']:
                            inEvent.append(event)
                            events.remove(event)
                    events=sorted(events, key=lambda x: datetime.datetime.strptime(x["Start"], "%Y-%m-%d"))
                   
                    break


            
            # if(df.loc[df['Id'] == registerEvent]):
            #     row=df.loc[df['Id'] == registerEvent]["Attending"].tolist()
                
            #     print("######",registerEvent)    
            #     print(type(row))
            #     print()

            #     if username not in row:
                    
            #         row.append(username)
            #         df.loc[df.Id == registerEvent, "Attending"] =row
            #         df.to_csv('CSVs\Events.csv',index=False)    
            #         df = pd.read_csv('CSVs\Events.csv', converters={'Attending':pd.eval})
            #         df.sort_values('Start')
            #         events=df.to_dict('records')
            #         temp=events
            #         inEvent={}
            #         for event in temp:
            #             if username in event['Attending']:
            #                 if inEvent=={}:
            #                     inEvent=event
            #                 events.remove(event)
                    
    
 

    
    

    if int(current_user.get_id()) == 1:
        allDataSupplied = {
            'numberOfEmployees': {},
            'totalWorkingThisMonth': 0,
            'totalWorkingLastMonth': 0
        }

        NumberEmployees = pysqldf("""Select department, count(*) as Count from dfEmployee group by department""")

        Work = pysqldf("""Select avg(SystemLoggedInTime) as Work from dfActivity group by Month""").to_dict()

        allDataSupplied['numberOfEmployees'] = NumberEmployees.to_dict()
        allDataSupplied['totalWorkingThisMonth'] = Work['Work'][11]
        allDataSupplied['totalWorkingLastMonth'] = Work['Work'][10]
        return render_template('admin.html', segment='index',allData=allDataSupplied,events=events)
    
    allDataSupplied = {
        'OffsThisMonth': 0,
        'OffsLastMonth': 0,
        'LoggedInThisMonth': 0,
        'LoggedInLastMonth': 0
    }

    EmployeeDetails = pysqldf("""Select Offs, SystemLoggedInTime from dfActivity where username = '{}'""".format(username)).to_dict()

    allDataSupplied['OffsThisMonth'] = EmployeeDetails['Offs'][11]
    allDataSupplied['OffsLastMonth'] = EmployeeDetails['Offs'][10]
    allDataSupplied['LoggedInThisMonth'] = EmployeeDetails['SystemLoggedInTime'][11]
    allDataSupplied['LoggedInLastMonth'] = EmployeeDetails['SystemLoggedInTime'][10]
    
    def listtask1():
        row = User.query.filter_by(id=current_user.get_id()).first()
        
        task = row.tasks
        if (task=="null" or task==""):
            tasks = json.dumps({1:'enter your first task'})
        if task:
            tasks = json.loads(task)
        else:
            tasks = json.dumps({1:'enter your first task'})
        print("gsdhfdjgkfjg",tasks)
        return tasks


    datatasks = listtask1()
    if type(datatasks)==type(str()):
       datatasks=json.loads(datatasks) 
   
    return render_template('index.html', segment='index',events=events,attend=inEvent, department = department, job_level = job_level, skill1 = res[0], skill2 = res[1], skill3 = res[2], allData = allDataSupplied, data = datatasks)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500



# employee entire work all graphs of indivituals to be shown here
@blueprint.route('/work')
def route_work_employee():
    for row in User.query.filter_by(id=current_user.get_id()).all():
        username = row.username
        department = row.department
    
    allDataSupplied = {
        'monthWise': {},
        'deptAvg': {}
    }

    #username = "HR1004"
    #dept = username[0]

    ansOneEmp = pysqldf("""SELECT Month, Email, Meetings, WorkingOnIssues, Offs FROM dfActivity WHERE username='{}' """.format(username))

    ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username in (Select username from dfEmployee where department = '{}') group by Month;""".format(department))
    #ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username like '{}' group by Month""".format(dept + "%"))

    allDataSupplied['monthWise'] = ansOneEmp.to_dict()
    allDataSupplied['deptAvg'] = ansDeptAvg.to_dict()

    return render_template('work_one.html', segment= get_segment(request), allData=allDataSupplied)

# employee health
@blueprint.route('/health')
def route_health_individual():
    for row in User.query.filter_by(id=current_user.get_id()).all():
        username = row.username
        department = row.department

    #username = "HR1004"
    
    allDataSupplied = {
        'employee': {},
        'companyAvg': {},
        'deptAvg': {},
        'biometrics': {}
    }

    q = """Select username, ActivityDate as Date, TotalSteps as Steps, Calories, VeryActiveMinutes as VActive, FairlyActiveMinutes as Active, LightlyActiveMinutes as LActive, SedentaryMinutes as IActive from dfHealth where username = '{}'""".format(username)
    ansEmployee = pysqldf(q).to_dict()
    allDataSupplied['employee'] = ansEmployee

    queryCompanyAvg = """select ActivityDate as Date, avg(TotalSteps) as Steps, avg(Calories) as Calories from dfHealth group by ActivityDate;"""
    ansCompanyAvg = pysqldf(queryCompanyAvg).to_dict()
    allDataSupplied['companyAvg'] =  ansCompanyAvg

    queryDeptAvg = """select ActivityDate as Date, avg(TotalSteps) as Steps, avg(Calories) as Calories from dfHealth, dfEmployee where dfHealth.username = dfEmployee.username and dfEmployee.department = '{}' group by ActivityDate;""".format(department)
    ansDeptAvg = pysqldf(queryDeptAvg).to_dict()
    allDataSupplied['deptAvg'] =  ansDeptAvg

    queryBio = """select height, weight from dfEmployee where username = '{}'""".format(username)
    ansBio = pysqldf(queryBio).to_dict()
    allDataSupplied['biometrics'] =  ansBio

    return render_template('health.html', segment = get_segment(request), allData = allDataSupplied)


#employee basically skill groaph
@blueprint.route('/plots')
def root():
    
    flag=True
    for row in User.query.filter_by(id=current_user.get_id()).all():

            res=json.loads(row.skills)
            print(res)
            try:
                dept=row.department
                jlevel=row.job_level
            except :
                flag=false
    #G = GraphG(r1,r2,r3,r4,r5)

    jlist=[]
    if flag:
        for row in User.query.filter_by(job_level=str(int(jlevel)+1) , department=dept).all():
            temp=json.loads(row.skills)
            jlist.extend(temp["skills"])

    if('dont' not in res):
        res['dont'] = []
    recom,Graph,crecom,Graph1=getRecommendations(res["skills"],res['dont'],jlist)

    return render_template('skills.html', segment = get_segment(request),allData=Graph ,allDataOne = Graph1, recomm = recom, crecomm = crecom, resources=CDN.render())


@blueprint.route('/plots/<template>',methods=["GET","POST"])
def oneskill(template):
    allData = {}
    query = template
    getCourses(allData,query)
    name1=template
    Graph=[]
    buildGraph(name1,Graph)
    dates={"start":"Begin Today","end":"Take your time"}
    for row in User.query.filter_by(id=current_user.get_id()).all():
        res=json.loads(row.skills)
        print(res)
        if template in res:
            dates=res[template]
    
    

    if request.method == 'POST':
        
        if 'pdf-file' in request.files:
            
            pdf = request.files['pdf-file']
            if pdf.filename == '':
                return redirect(request.url)
            if pdf and allowed_file(pdf.filename):
               
                for row in User.query.filter_by(id=current_user.get_id()).all():
                    username = row.username
                    row.SkillPointEarned=str(int(row.SkillPointEarned)+100)
                    res=json.loads(row.skills)
                    if template not in res["skills"]:
                        res["skills"].append(template)
                        if 'dont' not in res:
                            res['dont']=[]
                        res["dont"].append(template)
                    if template not in res:
                        res[template]={}
                    res[template]["end"]=str(datetime.datetime.today())
                    dates=res[template]
                    row.skills=str(json.dumps(res))
                    db.session.commit()
                pathlib.Path("Certificates/"+username).mkdir(parents=True, exist_ok=True)
                pdf.save( "Certificates/"+username+"/"+pdf.filename)          
                print("score+")
                if "start" not in dates:
                    dates={"start":"Begin Today","end":"Take your time"}
                if "end" not in dates:
                    dates["end"]="Take your time"
                print("here",dates)
                return render_template('one-skill.html', segment = get_segment(request), name1=name1,allData = allData, allData1=Graph,res=dates)
        elif "start" in request.form:
            print("@!#@$#$%I^^%$#%@$$#$#$")
            for row in User.query.filter_by(id=current_user.get_id()).all(): 
                    res=json.loads(row.skills)
                    if template not in res:
                        res[template]={}
                    res[template]["start"]=str(datetime.datetime.today())
                    print(res)
                    dates=res[template]
                    row.skills=str(json.dumps(res))
                    db.session.commit()
                    print(row.skills)
            if "start" not in dates:
                dates={"start":"Begin Today","end":"Take your time"}
            if "end" not in dates:
                dates["end"]="Take your time"
            print(res)
            return render_template('one-skill.html', segment = get_segment(request), name1=name1,allData = allData, allData1=Graph,res=dates)
    if "start" not in dates:
        dates={"start":"Begin Today","end":"Take your time"}
    if "end" not in dates:
        dates["end"]="Take your time"
    print(dates)
    
      
    
    
    return render_template('one-skill.html', segment = get_segment(request), name1=name1,allData = allData, allData1=Graph,res=dates)

@blueprint.route('/yoga')
def yoga():
    return render_template('yoga.html', segment = get_segment(request), allData = yoga_data)

@blueprint.route('/yoga/prayanama/<template>')
def yoga_one(template):
    allDataSupplied = list(filter(lambda yo: yo['sanskrit_name'] == template, yoga_data['prayanama']))
    return render_template('yoga-one.html', segment = get_segment(request), allData = allDataSupplied[0])

@blueprint.route('/mental-health')
def mental():
    return render_template('mental-health.html', segment = get_segment(request), allData = mental_data)

@blueprint.route('/mental-health/<template>')
def mental_one(template):
    allDataSupplied = list(filter(lambda yo: yo['name'] == template, mental_data['conditions']))
    return render_template('mental-health-one.html', segment = get_segment(request), allData = allDataSupplied[0])



@blueprint.route('/company')
def route_rank():
    if int(current_user.get_id()) != 1:
        return render_template('page-404.html', segment = get_segment(request))
    allDataSupplied = {
        'topSixLoggedIn' : {},
        'topSixOffs' : {},
        'companyAvg' : {},
        'gender': {}
    }

    queryCompanyAvg = pysqldf("""SELECT Month, avg(Email) as TotalEmail, avg(Meetings) as TotalMeetings, avg(WorkingOnIssues) as TotalIssues, avg(Offs) as TotalOffs
                        FROM dfActivity as df
                        group by Month;""")

    topSixLoggedIn = pysqldf("""SELECT username, sum(SystemLoggedInTime) as TotalTime
                        FROM dfActivity as df
                        group by username order by TotalTime desc limit 6;""")


    topSixOffs = pysqldf("""SELECT username, sum(Offs) as TotalOffs
                            FROM dfActivity as df
                            group by username order by TotalOffs desc limit 6;""")

    gender = pysqldf("""Select Gender, count(*) as Count, avg(job_level) as AvgJobLevel, avg(salary) as AvgSalary from dfEmployee group by Gender""")

    allDataSupplied['topSixLoggedIn'] = topSixLoggedIn.to_dict()
    allDataSupplied['topSixOffs'] = topSixOffs.to_dict()
    allDataSupplied['companyAvg'] = queryCompanyAvg.to_dict()
    allDataSupplied['gender'] = gender.to_dict()

    return render_template('rankings.html', segment = get_segment(request), allData=allDataSupplied)

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  


# for admin
@blueprint.route('/individual',methods=["GET","POST"])
def route_work_one():
    if int(current_user.get_id()) != 1:
        return render_template('page-404.html', segment = get_segment(request))
    dropdownList = dfEmployee["username"].tolist()

    
    if request.method == 'POST':
        username = request.form["username"]
    
       
        row=dfEmployee.loc[dfEmployee["username"]==username].to_dict("records")[0]
     
      
        dob = row["dob"]
        department = row["department"]
        Gender = row["Gender"]
        MaritalStatus = row["MaritalStatus"]
        YearsAtCompany  = row["YearsAtCompany"]
        recruitment_type = row["recruitment_type"]
        job_level = row["job_level"]
        salary = row["salary"]
        PercentSalaryHike=row["PercentSalaryHike"]
        StockOptionLevel=row["StockOptionLevel"]
        YearsInCurrentRole=row["YearsInCurrentRole"]
        rating=row["rating"]
        onsite=row["onsite"]
        education=row["education"]
        height=row["height"]
        weight=row["weight"]
            
        allDataSupplied = {
            'monthWise': {},
            'deptAvg': {}
        }
        employee = {
        'username': username,
        'Gender': Gender,
        'MaritalStatus': MaritalStatus,
        'PercentSalaryHike':PercentSalaryHike,
        'StockOptionLevel':StockOptionLevel,
        'YearsAtCompany':YearsAtCompany,
        'YearsInCurrentRole':YearsInCurrentRole,
        'Dept': department,
        'education':education,
        'recruitment_type':recruitment_type,
        'job_level':job_level,
        'rating':rating,
        'onsite':onsite,
        'salary':salary,
        'height': height,
        'weight': weight,
        'dob':dob
}
        test = {}
        for i in list_of_attributes:
            if i in codes:
                if employee[i] in codes[i]:
                    test[i] = [codes[i][employee[i]]]
                else:
                    k = len(codes[i])
                    codes[i][employee[i]] = k
                    test[i] = [codes[i][employee[i]]]
            else:
                test[i] = [employee[i]]
       
        lstring=["Poor","Average","Good","Great","Excelent"]
        if(getJobSatisfaction(test)[0]==0):
            js="Not Satisfied"
        else:
            js="Satisfied"
        ji=getJobInvolvement(test)[0]
        es=getEnvironmentSatisfaction(test)[0]
        wlb=getWorkLifeBalance(test)[0]
        jis=lstring[ji-1]+"  ( Around "+str(ji*20)+"% )"
        ess=lstring[es-1]+"  ( Around "+str(es*20)+"% )"
        wlbs=lstring[wlb-1]+"  ( Around "+str(wlb*20)+"% )"
        
        #username = "HR1004"
        #dept = username[0]

        ansOneEmp = pysqldf("""SELECT Month, Email, Meetings, WorkingOnIssues, Offs FROM dfActivity WHERE username='{}' """.format(username))

        ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username in (Select username from dfEmployee where department = '{}') group by Month;""".format(department))
        #ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username like '{}' group by Month""".format(dept + "%"))

        allDataSupplied['monthWise'] = ansOneEmp.to_dict()
        allDataSupplied['deptAvg'] = ansDeptAvg.to_dict()
        return render_template('individual.html', segment= get_segment(request),recruitment_type=recruitment_type,department=department,job_level=job_level, username=username, Gender=Gender, MaritalStatus=MaritalStatus, dob=dob,YearsAtCompany=YearsAtCompany, salary=salary, js=js,ji=jis,es=ess,wlb=wlbs,allData=allDataSupplied)
    
    return render_template('search.html',segment= get_segment(request),dropdownList = dropdownList)
# for admin
@blueprint.route('/department')
def route_work_dep():
    if int(current_user.get_id()) != 1:
        return render_template('page-404.html', segment = get_segment(request))
    allDataSupplied = {
        'monthWise': {},
        'monthWiseAvgPerPerson': {},
        'companyAvg': {}
    }

    depts = pysqldf("""Select distinct(department) from dfEmployee;""").to_dict()

    for i in depts['department']:
        allDataSupplied['monthWise'][depts['department'][i]] = pysqldf("""Select dfActivity.Month as Month, sum(dfActivity.Email) as TotalEmail, sum(dfActivity.Meetings) as TotalMeetings, sum(dfActivity.WorkingOnIssues) as TotalIssues, sum(dfActivity.Offs) as TotalOffs from dfEmployee, dfActivity where dfActivity.username = dfEmployee.username and dfEmployee.department = '{}' group by dfActivity.Month""".format(depts['department'][i])).to_dict()
        allDataSupplied['monthWiseAvgPerPerson'][depts['department'][i]] = pysqldf("""Select dfActivity.Month as Month, avg(dfActivity.Email) as TotalEmail, avg(dfActivity.Meetings) as TotalMeetings, avg(dfActivity.WorkingOnIssues) as TotalIssues, avg(dfActivity.Offs) as TotalOffs from dfEmployee, dfActivity where dfActivity.username = dfEmployee.username and dfEmployee.department = '{}' group by dfActivity.Month""".format(depts['department'][i])).to_dict()

    #queryPerMonthSumH = """SELECT Month, sum(Email) as TotalEmail, sum(Meetings) as TotalMeetings, sum(WorkingOnIssues) as TotalIssues, sum(Offs) as TotalOffs
    #                    FROM dfActivity as df
    #                    where username like "H%"
    #                    group by Month;"""

    queryCompanyAvg = pysqldf("""SELECT Month, avg(Email) as TotalEmail, avg(Meetings) as TotalMeetings, avg(WorkingOnIssues) as TotalIssues, avg(Offs) as TotalOffs
                        FROM dfActivity as df
                        group by Month;""")
    allDataSupplied['companyAvg'] = queryCompanyAvg.to_dict()

    return render_template('department.html', segment= get_segment(request), allData=allDataSupplied)

@blueprint.route('/Sync')
def sync_function():
    csvFile = "CSVs/EmployeeDataset.csv"
    dfCsv = pd.read_csv(csvFile)
    for row in User.query.all():
        username = row.username
        print(username)
        diction = dfCsv.loc[dfCsv['username'] == username]
        diction=diction.to_dict('records')
        if(len(diction)>0):
            diction=diction[0]

            row.extra = diction["fullname"]
            row.Gender = diction["Gender"]
            row.MaritalStatus = diction["MaritalStatus"]
            row.PercentSalaryHike = diction["PercentSalaryHike"]
            row.StockOptionLevel    = diction["StockOptionLevel"]
            row.YearsAtCompany  = diction["YearsAtCompany"]
            row.YearsInCurrentRole = diction["YearsInCurrentRole"]
            row.education = diction["education"]
            row.recruitment_type = diction["recruitment_type"]
            row.job_level = diction["job_level"]
            row.rating = diction["rating"]
            row.onsite = diction["onsite"]
            row.department = diction["department"]
            row.salary = diction["salary"]
            row.dob = diction["dob"]
            row.height =str(diction["height"])
            row.weight = str(diction["weight"])
            #row.heightandweight = Column(String)
            db.session.commit()
    return redirect("/page-404.html", code=200)

@blueprint.route('/enterEmployeeCsv', methods=['GET', 'POST'])
def route_enterEmployeeCsv():
    if int(current_user.get_id()) != 1:
        return render_template('page-404.html', segment = get_segment(request))
    if request.method == 'POST':
        # save the single "profile" file
        csvFile = request.files['Csv']
        dfCsv = pd.read_csv(csvFile)
   
        for row in User.query.all():
            username = row.username
            print(username)
            diction = dfCsv.loc[dfCsv['username'] == username]
            diction=diction.to_dict('records')
            if(len(diction)>0):
                diction=diction[0]
       
                row.extra = diction["fullname"]
                row.Gender = diction["Gender"]
                row.MaritalStatus = diction["MaritalStatus"]
                row.PercentSalaryHike = diction["PercentSalaryHike"]
                row.StockOptionLevel    = diction["StockOptionLevel"]
                row.YearsAtCompany  = diction["YearsAtCompany"]
                row.YearsInCurrentRole = diction["YearsInCurrentRole"]
                row.education = diction["education"]
                row.recruitment_type = diction["recruitment_type"]
                row.job_level = diction["job_level"]
                row.rating = diction["rating"]
                row.onsite = diction["onsite"]
                row.salary = diction["salary"]
                row.heightandweight = str(diction["height"]) + " " + str(diction["weight"])
                #row.heightandweight = Column(String)
                db.session.commit()

        
        #dfCsv = pd.read_csv(csvFile).iloc[:, 1:]
        #print(dfCsv.columns)
        # con = sqlite3.connect("db.sqlite3")
        # dfCsv.to_sql('dfCsv', con)
        # cursor = con.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # print(cursor.fetchall())
        # if value == 'General':
        #     df = pd.read_sql_query("select dfCsv.* from dfCsv, User where User.username = dfCsv.username", con)
        #     df.to_sql('User', con)
        #     #cur = con.cursor()
        #     cursor.execute("DROP TABLE dfCsv")
        #     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        #     print(cursor.fetchall())
        
    return render_template('enterEmployeeCsv.html',segment= get_segment(request))



## for everyone

@blueprint.route('/api/getcourse')
def getapicourse():
    if 'x-access-tokens' in request.headers:
        token = request.headers['x-access-tokens']
    else:
        return jsonify({'message': 'no access token'})
    
    
    try:
        token_decoded = base64.b64decode(token).decode("utf-8")
    except:
        return jsonify({'message': 'token is invalid'})
    userpass = token_decoded.split(':')
    if apiauth(userpass[0],userpass[1])==False:
        return jsonify({'message': 'token is invalid'})
    if request.args.get('query'):
        Getdata = {}
        getCourses(Getdata, request.args.get('query'))
        return jsonify(Getdata)        
    
    return jsonify({'message': 'no query string'})

@blueprint.route('/api/profile/own')
def apiprofile():
    if 'x-access-tokens' in request.headers:
        token = request.headers['x-access-tokens']
    else:
        return jsonify({'message': 'no access token'})
    
    
    try:
        token_decoded = base64.b64decode(token).decode("utf-8")
    except:
        return jsonify({'message': 'token is invalid'})
    userpass = token_decoded.split(':')
    if apiauth(userpass[0],userpass[1])==False:
        return jsonify({'message': 'token is invalid'})
    
    for row in User.query.filter_by(username=userpass[0]).all():
        return jsonify({'username':row.username,'department':row.department,'job_level':row.job_level,'fullname':row.extra,'gender':row.Gender,'MaritalStatus ':row.MaritalStatus,'PercentSalaryHike':row.PercentSalaryHike,'StockOptionLevel':row.StockOptionLevel,'YearsAtCompany ':row.YearsAtCompany,'YearsInCurrentRole': row.YearsInCurrentRole,'education ':row.education,'recruitment_type ':row.recruitment_type,'job_level ':row.job_level,'rating ':row.rating,'onsite ':row.onsite})
    return jsonify({'message': 'user not synced'})

@blueprint.route('/task/list')
def listtask():
    row = User.query.filter_by(id=current_user.get_id()).first()
    try:
        tasks = row.tasks
        if tasks:
            return json.loads(tasks)

        tasks = {'message':'empty'}
        return jsonify(tasks)
    except:
        tasks = {'message':'error'}
        return jsonify(tasks) 

@blueprint.route('/task/add', methods=['POST'])
def addtask():
    row = User.query.filter_by(id=current_user.get_id()).first()
    task = row.tasks
    if (task=="null"):
        tasks = {1:'enter your first task'}
    if task:
        tasks = json.loads(task)
    else:
        tasks = {1:'enter your first task'}

    todo = request.form['todoitem']
    id = random.randint(1,10000)
    # newtask = {id,todo}
    # tasks.update(newtask)
    tasks[id]=todo
    row.tasks = json.dumps(tasks)
    db.session.commit()
    return redirect('/')
    return jsonify({"message":"success"})

  
@blueprint.route('/task/delete/<id>')
def completetask(id):
    try:
        row = User.query.filter_by(id=current_user.get_id()).first()
        task = row.tasks
        tasks = json.loads(task)
        try:
            del tasks[id]
            row.tasks = json.dumps(tasks)
            db.session.commit()
            return jsonify({"message":"deleted"})
        except:
            return jsonify({"message":"id doesnt exist"})

    except:
        return jsonify({"message":"id is invalid"})







#     return render_template('course.html', segment = get_segment(request), allData=allDataSupplied)


@blueprint.route('/profile/<template>')
def profile(template):
    username = template

    allDataSupplied = {
        'name': template
    }
    print(allDataSupplied)
    #for row in User.query.filter_by(id=current_user.get_id()).all():
    #        r1 = row.skills1
    #        r2 = row.skills2
    #        r3 = row.skills3
    #        r4 = row.skills4
    #        r5 = row.skills5
    #G = GraphG(r1,r2,r3,r4,r5)
    #recom,Graph=getRecommendations(r1,r2,r3,r4,r5)
    #print(recom)
    return render_template('profile.html', segment = get_segment(request), resources=CDN.render(), allData = allDataSupplied)













# GOOGLE


















































# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/fitness.body.read','https://www.googleapis.com/auth/fitness.activity.read','https://www.googleapis.com/auth/fitness.location.read','https://www.googleapis.com/auth/fitness.oxygen_saturation.read','https://www.googleapis.com/auth/fitness.reproductive_health.read','https://www.googleapis.com/auth/fitness.sleep.read','https://www.googleapis.com/auth/fitness.activity.read','https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar.events.readonly','https://www.googleapis.com/auth/calendar.readonly','https://www.googleapis.com/auth/calendar.settings.readonly']
API_SERVICE_NAME = 'Fitness API'
API_VERSION = 'v2'


@blueprint.route('/indextable')
def print_index_table1():
    return print_index_table()


@blueprint.route('/test')
def test_api_request():
    
    #     return redirect('authorize')

    # # Load credentials from the session.
    # credentials = google.oauth2.credentials.Credentials(
    #     **session['credentials'])

    # drive = googleapiclient.discovery.build(
    #     API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # files = drive.files().list().execute()

    # # Save credentials back to session in case access token was refreshed.
    # # ACTION ITEM: In a production app, you likely want to save these
    # #              credentials in a persistent database instead.
    # session['credentials'] = credentials_to_dict(credentials)

    # return jsonify(**files)

    calendars = []
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    if 'credentials' not in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        calendars.append({"name": calendar_list_entry['summary'], "id": calendar_list_entry['id']})
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    return jsonify("calendarReturn", {"data": calendars})


@blueprint.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('.oauth2callback', _external=True)
    print(flow.redirect_uri)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        state = 'dummy',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    print(authorization_url)
    return redirect(authorization_url)


@blueprint.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('.oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('.test_api_request'))


@blueprint.route('/revoke')
def revoke():
    if 'credentials' not in session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return('Credentials successfully revoked.' + print_index_table())
    else:
        return('An error occurred.' + print_index_table())


@blueprint.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')







