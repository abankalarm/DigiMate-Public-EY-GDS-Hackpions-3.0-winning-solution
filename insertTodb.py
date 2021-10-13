import sqlite3
import pandas as pd
import hashlib, binascii, os
import json

def hash_pass( password ):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash) # return bytes
con = sqlite3.connect("db.sqlite3")

li=pd.read_csv("./CSVs/EmployeesIncludedDataset.csv", converters={'skills':pd.eval}).to_dict("records")
#print(li)
sqlite_insert_with_param = """INSERT INTO User 
    (
    id,username,email,password,dob,department,skills,skills1,skills2,skills3,skills4,skills5,Gender,MaritalStatus,PercentSalaryHike,StockOptionLevel,extra,YearsAtCompany,YearsInCurrentRole,education,recruitment_type,job_level,rating,onsite,salary,height,weight,SkillPointEarned
    ) 
                          VALUES (?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?,?,?,?);"""
for l in range(len(li)):
    i=l+2
    #print(i)
    da=li[l]
    # for x in da:
    #     print(x,type(da[x]))
    data_tuple =(i,da['username'],da['email'],hash_pass( da['username'] ),da['dob'],da['Dept'],json.dumps({"skills":da['skills']}),da['skills'][0],da['skills'][1],da['skills'][2],da['skills'][3],da['skills'][4],da['Gender'],da['MaritalStatus'],str(da['PercentSalaryHike']),str(da['StockOptionLevel']),da['fullname'],str(da['YearsAtCompany']),str(da['YearsInCurrentRole']),da['education'],da['recruitment_type'],str(da['job_level']),str(da['rating']),str(da['onsite']),str(da['salary']),str(da['height']),str(da['weight']),str(da['SkillPointEarned']))
    #print(len(data_tuple))
    cursor=con.cursor()
    cursor.execute(sqlite_insert_with_param, data_tuple)
    con.commit()