import pandas as pd
import pickle
from datetime import date
codes = {'Gender': {'Female': 0, 'Male': 1},
             'MaritalStatus': {'Divorced': 0, 'Married': 1, 'Single': 2},
             'Dept': {'HR': 0,
              'Marketing': 1,
              'Purchasing': 2,
              'Sales': 3,
              'Technology': 4},
             'education': {'PG': 0, 'UG': 1},
             'recruitment_type': {'On-Campus': 0,
              'Recruitment Agency': 1,
              'Referral': 2,
              'Walk-in': 3}}

list_of_attributes = ['Gender', 'MaritalStatus', 'PercentSalaryHike', 'StockOptionLevel',
               'YearsAtCompany', 'YearsInCurrentRole', 'Dept', 'education',
               'recruitment_type', 'job_level', 'rating', 'onsite', 'salary', 'dob']

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def getJobSatisfaction(test):
    model = pickle.load(open('JobSatisfactionModel.pkl', 'rb'))

    df_test = pd.DataFrame.from_dict(test)
    df_test.dob = pd.to_datetime(df_test.dob)
    df_test.dob = [calculate_age(i) for i in df_test.dob]
    return model.predict(df_test)
    
def getEnvironmentSatisfaction(test):
    model = pickle.load(open('EnvironmentSatisfactionModel.pkl', 'rb'))

    df_test = pd.DataFrame.from_dict(test)
    df_test.dob = pd.to_datetime(df_test.dob)
    df_test.dob = [calculate_age(i) for i in df_test.dob]
    return model.predict(df_test)


def getJobInvolvement(test):
    model = pickle.load(open('JobInvolvementModel.pkl', 'rb'))

    df_test = pd.DataFrame.from_dict(test)
    df_test.dob = pd.to_datetime(df_test.dob)
    df_test.dob = [calculate_age(i) for i in df_test.dob]
    return model.predict(df_test)

def getWorkLifeBalance(test):
    model = pickle.load(open('WorkLifeBalanceModel.pkl', 'rb'))

    df_test = pd.DataFrame.from_dict(test)
    df_test.dob = pd.to_datetime(df_test.dob)
    df_test.dob = [calculate_age(i) for i in df_test.dob]
    return model.predict(df_test)

