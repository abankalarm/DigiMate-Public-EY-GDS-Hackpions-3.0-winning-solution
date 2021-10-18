import sqlite3
import pandas as pd
import hashlib, binascii, os
import json
# dfActivity = pd.read_csv("./CSVs/EmployeeActivity.csv").to_dict("records")
# dfHealth = pd.read_csv("./CSVs/EmployeeHealth.csv").to_dict("records")
# dfEvent=pd.read_csv("./CSVs/Events.csv", converters={'Attending':pd.eval}).to_dict("records")
con = sqlite3.connect("db.sqlite3")


cur=con.cursor()
# cur.execute("DELETE FROM EmployeeActivity WHERE username=?",("test1",))
# con.commit()

# cur.execute("CREATE TABLE EmployeeActivity (username,Month,SystemLoggedInTime,Email,Meetings,WorkingOnIssues,SystemInactiveTime,Offs,SkillPointEarned);")
# con.commit()
# cur.execute("CREATE TABLE EmployeeHealth (username,ActivityDate,TotalSteps,TotalDistance,TrackerDistance,LoggedActivitiesDistance,VeryActiveDistance,ModeratelyActiveDistance,LightActiveDistance,SedentaryActiveDistance,VeryActiveMinutes,FairlyActiveMinutes,LightlyActiveMinutes,SedentaryMinutes,Calories);")
# con.commit()
# cur.execute("CREATE TABLE Events (Id,Event,Start,Description,Attending);")
# con.commit()

# sqlite_insert_with_param = """INSERT INTO EmployeeActivity 
#     (
#     username,Month,SystemLoggedInTime,Email,Meetings,WorkingOnIssues,SystemInactiveTime,Offs,SkillPointEarned
#     ) 
#                           VALUES (?,?,?,?,?,?,?,?,?);"""
# for row in dfActivity:
#     cur=con.cursor()
#     print(row)
#     data_tuple=(row["username"],row["Month"],row["SystemLoggedInTime"],row["Email"],row["Meetings"],row["WorkingOnIssues"],row["SystemInactiveTime"],row["Offs"],row["SkillPointEarned"])
#     cur.execute(sqlite_insert_with_param, data_tuple)
#     con.commit()
# print("done1")



# sqlite_insert_with_param = """INSERT INTO EmployeeHealth 
#     (username,ActivityDate,TotalSteps,TotalDistance,TrackerDistance,LoggedActivitiesDistance,VeryActiveDistance,ModeratelyActiveDistance,LightActiveDistance,SedentaryActiveDistance,VeryActiveMinutes,FairlyActiveMinutes,LightlyActiveMinutes,SedentaryMinutes,Calories
#     ) 
#                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
# for row in dfHealth:
#     cur=con.cursor()
#     data_tuple=(row["username"],row["ActivityDate"],row["TotalSteps"],row["TotalDistance"],row["TrackerDistance"],row["LoggedActivitiesDistance"],row["VeryActiveDistance"],row["ModeratelyActiveDistance"],row["LightActiveDistance"],row["SedentaryActiveDistance"],row["VeryActiveMinutes"],row["FairlyActiveMinutes"],row["LightlyActiveMinutes"],row["SedentaryMinutes"],row["Calories"])
#     cur.execute(sqlite_insert_with_param, data_tuple)
#     con.commit()
# print("done2")


# sqlite_insert_with_param = """INSERT INTO Events 
#     (Id,Event,Start,Description,Attending
#     ) 
#                           VALUES (?,?,?,?,?);"""
# for row in dfEvent:
#     cur=con.cursor()
#     print(str(   json.dumps( row["Attending"] )  ))
#     data_tuple=( row["Id"],row["Event"],row["Start"],row["Description"],    str(   json.dumps( row["Attending"] )  )   )
#     cur.execute(sqlite_insert_with_param, data_tuple)
#     con.commit()
# print("done3")

# def hash_pass( password ):
#     """Hash a password for storing."""
#     salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
#     pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
#                                 salt, 100000)
#     pwdhash = binascii.hexlify(pwdhash)
#     return (salt + pwdhash) # return bytes
# con = sqlite3.connect("db.sqlite3")

# li=pd.read_csv("./CSVs/EmployeesIncludedDataset.csv", converters={'skills':pd.eval}).to_dict("records")
# #print(li)
# sqlite_insert_with_param = """INSERT INTO User 
#     (
#     id,username,email,password,dob,department,skills,Gender,MaritalStatus,PercentSalaryHike,StockOptionLevel,extra,YearsAtCompany,YearsInCurrentRole,education,recruitment_type,job_level,rating,onsite,salary,height,weight,SkillPointEarned,tasks
#     ) 
#                           VALUES (?, ?, ?, ?, ?,?,?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?,?,?,?);"""
# for l in range(len(li)):
#     i=l+2
#     #print(i)
#     da=li[l]
#     # for x in da:
#     #     print(x,type(da[x]))
#     data_tuple =(i,da['username'],da['email'],hash_pass( da['username'] ),da['dob'],da['Dept'],str(json.dumps({"skills":da['skills']})),da['Gender'],da['MaritalStatus'],str(da['PercentSalaryHike']),str(da['StockOptionLevel']),da['fullname'],str(da['YearsAtCompany']),str(da['YearsInCurrentRole']),da['education'],da['recruitment_type'],str(da['job_level']),str(da['rating']),str(da['onsite']),str(da['salary']),str(da['height']),str(da['weight']),str(da['SkillPointEarned']),"")
#     #print(len(data_tuple))
#     cursor=con.cursor()
#     cursor.execute(sqlite_insert_with_param, data_tuple)
#     con.commit()