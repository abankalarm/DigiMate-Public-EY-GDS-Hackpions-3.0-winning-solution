from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import user
from app.home.plot import *
from app.home.predictions import *
from app.home import blueprint
from flask import render_template, redirect, url_for, request
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
import sqlite3
pysqldf = lambda q: sqldf(q, globals())

dfActivity = pd.read_csv("./CSVs/EmployeeActivity.csv")
dfHealth = pd.read_csv("./CSVs/EmployeeHealth.csv")
dfEmployee = pd.read_csv("./CSVs/EmployeeDataset.csv")

dfActivity['Month'] = pd.to_datetime(dfActivity['Month'], format = "%d-%m-%Y")
dfHealth['ActivityDate'] = pd.to_datetime(dfHealth['ActivityDate'], format = "%d-%m-%Y")
dfEmployee['dob'] = pd.to_datetime(dfEmployee['dob'], format = "%d-%m-%Y")

@blueprint.route('/index',methods=["GET","POST"])
@login_required
def index():
    for row in User.query.filter_by(id=current_user.get_id()).all():
        username = row.username
        department = row.department
        job_level = row.job_level
        skill1 = row.skills1
        skill2 = row.skills2
        skill3 = row.skills3

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
    print(temp)
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
                    print("here")
                    print(events)
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
                    
    
 

    
    
    print(current_user.get_id())
    if int(current_user.get_id()) == 1:
        allDataSupplied = {
            'numberOfEmployees': {},
            'totalWorkingThisMonth': 0,
            'totalWorkingLastMonth': 0
        }

        NumberEmployees = pysqldf("""Select Dept, count(*) as Count from dfEmployee group by Dept""")

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

    return render_template('index.html', segment='index',events=events,attend=inEvent, department = department, job_level = job_level, skill1 = skill1, skill2 = skill2, skill3 = skill3, allData = allDataSupplied)

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

    ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username in (Select username from dfEmployee where Dept = '{}') group by Month;""".format(department))
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

    queryDeptAvg = """select ActivityDate as Date, avg(TotalSteps) as Steps, avg(Calories) as Calories from dfHealth, dfEmployee where dfHealth.username = dfEmployee.username and dfEmployee.Dept = '{}' group by ActivityDate;""".format(department)
    ansDeptAvg = pysqldf(queryDeptAvg).to_dict()
    allDataSupplied['deptAvg'] =  ansDeptAvg

    queryBio = """select height, weight from dfEmployee where username = '{}'""".format(username)
    ansBio = pysqldf(queryBio).to_dict()
    allDataSupplied['biometrics'] =  ansBio

    return render_template('health.html', segment = get_segment(request), allData = allDataSupplied)


#employee basically skill groaph
@blueprint.route('/plots')
def root():
    for row in User.query.filter_by(id=current_user.get_id()).all():
            r1 = row.skills1
            r2 = row.skills2
            r3 = row.skills3
            r4 = row.skills4
            r5 = row.skills5
    #G = GraphG(r1,r2,r3,r4,r5)
    recom,Graph=getRecommendations(r1,r2,r3,r4,r5)
    print(recom)
    return render_template('skills.html', segment = get_segment(request),allData=Graph ,recomm = recom, resources=CDN.render())

# @blueprint.route('/plot')
# def plot():
#     for row in User.query.filter_by(id=current_user.get_id()).all():
#         r1 = row.skills1
#         r2 = row.skills2
#         r3 = row.skills3
#         r4 = row.skills4
#         r5 = row.skills5
#     G = GraphG(r1,r2,r3,r4,r5)
#     p = make_plot(G)
#     return json.dumps(json_item(p, "myplot"))

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
    # for row in User.query.all():
    #     if row.username != 'test':
    #         dropdownList.append(row.username)
    #     #department = row.department
    # dropdownList=sorted(dropdownList)
    
    if request.method == 'POST':
        username = request.form["username"]
        print(username)
        print(dfEmployee)
        row=dfEmployee.loc[dfEmployee["username"]==username].to_dict("records")[0]
        print(row)
        print(row["dob"])
        dob = row["dob"]
        department = row["Dept"]
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
        # employee = {
        #         'username': 'T123',
        #         'Gender': 'Female',
        #         'MaritalStatus': 'Married',
        #         'PercentSalaryHike':10,
        #         'StockOptionLevel':1,
        #         'YearsAtCompany':20,
        #         'YearsInCurrentRole':14,
        #         'Dept': 'Technology',
        #         'education':'PG',
        #         'recruitment_type':0,
        #         'job_level':5,
        #         'rating':4,
        #         'onsite':1,
        #         'salary':10000,
        #         'height': 154,
        #         'weight': 67,
        #         'dob':'1958-12-21'
        # }
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
        print("here")
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

        ansDeptAvg = pysqldf("""SELECT Month, avg(Email) as Email, avg(Meetings) as Meetings, avg(WorkingOnIssues) as WorkingOnIssues, avg(Offs) as Offs FROM dfActivity WHERE username in (Select username from dfEmployee where Dept = '{}') group by Month;""".format(department))
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

    depts = pysqldf("""Select distinct(Dept) from dfEmployee;""").to_dict()

    for i in depts['Dept']:
        allDataSupplied['monthWise'][depts['Dept'][i]] = pysqldf("""Select dfActivity.Month as Month, sum(dfActivity.Email) as TotalEmail, sum(dfActivity.Meetings) as TotalMeetings, sum(dfActivity.WorkingOnIssues) as TotalIssues, sum(dfActivity.Offs) as TotalOffs from dfEmployee, dfActivity where dfActivity.username = dfEmployee.username and dfEmployee.Dept = '{}' group by dfActivity.Month""".format(depts['Dept'][i])).to_dict()
        allDataSupplied['monthWiseAvgPerPerson'][depts['Dept'][i]] = pysqldf("""Select dfActivity.Month as Month, avg(dfActivity.Email) as TotalEmail, avg(dfActivity.Meetings) as TotalMeetings, avg(dfActivity.WorkingOnIssues) as TotalIssues, avg(dfActivity.Offs) as TotalOffs from dfEmployee, dfActivity where dfActivity.username = dfEmployee.username and dfEmployee.Dept = '{}' group by dfActivity.Month""".format(depts['Dept'][i])).to_dict()

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
            print(type(diction["username"]),diction["username"])
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
            row.department = diction["Dept"]
            row.salary = diction["salary"]
            row.dob = diction["dob"]
            row.heightandweight = str(diction["height"]) + " " + str(diction["weight"])
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
        print(dfCsv)
        for row in User.query.all():
            username = row.username
            print(username)
            diction = dfCsv.loc[dfCsv['username'] == username]
            diction=diction.to_dict('records')
            if(len(diction)>0):
                diction=diction[0]
                print(type(diction["username"]),diction["username"])
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
