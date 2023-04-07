import os
import pandas as pd
import numpy as np
import openpyxl
import psycopg2
import datetime
from datetime import date
from flask import Flask, request, redirect, url_for,flash
from flask import render_template
from config import get_db_connection
from flask import make_response
from flask import abort
from flask import Flask
from flask import Flask
from flask_caching import Cache
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from config import pg_engine
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

attendanceUPLOAD_FOLDER = r"E:\uploads\Attendence_sheet\\"

marksUPLOAD_FOLDER = r"E:\\uploads\\mark_sheets\\"


UPLOAD_FOLDER=r"E:\uploads\\"


ALLOWED_EXTENSIONS = { 'csv','xlsx'}

app = Flask(__name__)
# Set the database URI using the PostgreSQL JDBC driver
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{user}:{psw}@localhost/{db}".format(user='postgres',psw='Otsi1234',db='school')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = 'fneapgfvnoowenvfbijnwgvopbi9wo'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['attendanceUPLOAD_FOLDER'] = attendanceUPLOAD_FOLDER
app.config['marksUPLOAD_FOLDER'] = marksUPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000

@app.route('/')
def home():
    return render_template('imagebutton.html')
    
    
#Student Info page
@app.route('/studentinfoCLASS',methods=("POST", "GET"))
def studentinfo():
    cl=request.form['class_info']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM student_details WHERE Current_Class={cl};''')
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'AND table_name   = 'student_details';''')
    col_name=[col[3] for col in cur.fetchall()]
    cur.close()
    conn.close()
    df=pd.DataFrame(data=tables,columns=col_name)
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

#Student Marks page
@app.route('/marksnavigator',methods=("POST", "GET"))
def marksnavigator():
    
    return render_template('marks_naviagtion.html')

#Update marks
@app.route('/marks_data_entry', methods=['GET', 'POST'])
def marks_data_entry():
   
    cl=request.form['marks_update']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')
    students = cur.fetchall() 
    # subjects=['English','Hindi','Telugu','Maths','Science','Social']
    students=[tuple(list(t) + ['English','Hindi','Telugu','Maths','Science','Social',]) for t in students]
    # return cl
    return render_template('marks_form.html', students=students,cls=cl)

# #Marks report
@app.route('/marks_data_change', methods=['GET', 'POST'])
def marks_data_change():
  exam_type=request.form['exam_type']
  marks_change_class=request.form['marks_change_class']
  conn = get_db_connection()
  #get table names from DB
  cur = conn.cursor()
  cur.execute(f'''SELECT DISTINCT roll_number from acadamic_reports WHERE current_class = {marks_change_class} AND exam_type='{exam_type}';''')
  students = [roll[0]for roll in cur.fetchall()] 
  cur.execute(f'''SELECT DISTINCT subject from acadamic_reports WHERE current_class = {marks_change_class} AND exam_type='{exam_type}';''')
  subject = [sub[0]for sub in cur.fetchall()] 
  # df=pd.DataFrame(data=students,columns=['roll_number','subject'])
  # df.groupby()
  return render_template('edit_marks.html',students=students,subject=subject,exam_type=exam_type,clss=marks_change_class)
  # return request.form
# #Marks report
@app.route('/marks_data_change_entry', methods=['GET', 'POST'])
def marks_data_change_entry():
  lc_pg_eng=pg_engine()
  conn = get_db_connection()
  records=request.form.to_dict()
  df=pd.DataFrame()
  df['roll_number']=[records.get('roll_number')]
  df['subject']=[records.get('subject')]
  df['score']=[records.get('score')]
  df['current_class']=[records.get('cls')]
  df['exam_type']=[records.get('exam_type')]
  cur = conn.cursor()
  cur.execute(f'''UPDATE acadamic_reports    
              SET score = {records.get('score')}
              WHERE
              roll_number={records.get('roll_number')} AND current_class= {records.get('cls')} AND 
              subject= '{records.get('subject')}' AND exam_type= '{records.get('exam_type')}'; ''')
  conn.commit()
  conn.close()
  return render_template("sucessfully_updated.html")
  # return request.form

#Marks report
@app.route('/marks_data', methods=['GET', 'POST'])
def marks_data():
    lc_pg_eng=pg_engine()
    conn = get_db_connection()
    marks_records=request.form.to_dict()
    cls=request.form['cls']
    exam_type=request.form['exam_type']
    marks_records.pop('cls')
    marks_records.pop('exam_type')
    roll_number=[i.split("-")[0] for i in marks_records.keys()]
    subject=[i.split("-")[1] for i in marks_records.keys()]
    score=marks_records.values()

    df=pd.DataFrame()
    df['roll_number']=roll_number
    df['subject']=subject
    df['score']=score
    df['current_class']=cls
    df['exam_type']=exam_type
    
    df.to_sql('acadamic_reports',con=lc_pg_eng,if_exists='append',index=False)
    
    return render_template("sucessfully_updated.html")
#View Marks 
@app.route('/marksinfoCLASS',methods=("POST", "GET"))
def marksinfo():
    exam_type=request.form['exam_type']
    cl=request.form['marks_info']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM acadamic_reports where current_class = {cl} AND exam_type= '{exam_type}';''')
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'AND table_name   = 'acadamic_reports';''')
    col_name=[col[3] for col in cur.fetchall()]
    cur.execute(f'''SELECT roll_number,student_name FROM student_details where current_class = {cl} ;''')
    student_names=cur.fetchall()
    student_info =[std_info for std_info in student_names]
    std_info=pd.DataFrame(data=student_info,columns=['roll_number','student_name'])
    df=pd.DataFrame(data=tables,columns=col_name)
    df=df.merge(std_info,how='inner',on='roll_number')
    marks_list=pd.pivot_table(df,index=['roll_number','student_name'],columns=['subject'],values='score')
    marks_list['Total_score']=marks_list.sum(axis=1)
    marks_list['percentage']=pd.pivot_table(df,index=['roll_number','student_name'],columns=['subject'],values='score').sum(axis=1)/df['subject'].nunique()
    marks_list=marks_list.sort_values(by='percentage',ascending=False).reset_index()
    # return exam_type
    return render_template('simple.html',  tables=[marks_list.to_html(classes='data')], titles=marks_list.columns.values,exam_type=exam_type)

@app.route('/view_attentence_fillter',methods=("POST", "GET"))
def attentence_fillter_date():
  
  return render_template('attendance_navigation.html')
 
@app.route('/attentence_info',methods=("POST", "GET"))
def attentence_info():
  
  return render_template("view_attentence_fillters.html")

@app.route('/attendence_report',methods=("POST", "GET"))
def attendence_report():
  cl=request.form['attendence_class']
  start_date = str(request.form['from_date'])
  end_date = str(request.form['to_date'])
  conn = get_db_connection()
  #get table names from DB
  cur = conn.cursor()
  cur.execute(f'''SELECT * FROM attendence WHERE Current_Class={cl};''')
  db_tables=cur.fetchall()
  tables =[table for table in db_tables]
  cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'AND table_name   = 'attendence';''')
  col_name=[col[3] for col in cur.fetchall()]
  cur.close()
  conn.close()
  df=pd.DataFrame(data=tables,columns=col_name)
  df['date']= pd.to_datetime(df['date'])
  df=df.loc[(df['date']>=start_date) & (df['date']<=end_date)]
  attendes_df=pd.pivot_table(data=df,values='attendance',index=['roll_number', 'student_name', 'current_class'],columns=df['date'].dt.date)
  attendes_df['attendence_pecent']=(attendes_df.sum(axis=1)/len(attendes_df.columns))*100
  attendes_df['Prestent_days']=attendes_df[attendes_df.columns[:-1]].sum(axis=1)
  Total_attendence=attendes_df.pop('Prestent_days')
  attendence_percentage=attendes_df.pop('attendence_pecent')
  attendes_df.insert(0,"Attendence_percentage",attendence_percentage)
  attendes_df.insert(1,"Prestent_days",Total_attendence)
  attendes_df=attendes_df.reset_index()
  return render_template('simple.html',  tables=[attendes_df.to_html(classes='data')], titles=attendes_df.columns.values)

@app.route('/attentence_rcrd',methods=("POST", "GET"))
def attentence_rcrd():
  
  return render_template("attendance_rcrd.html")

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    dt=request.form['Date']
    cl=request.form['attendence_class']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')
    students = cur.fetchall()
    students=[tuple(list(t) + [dt,cl]) for t in students]
    # Display form
    return render_template('attendence_form.html', students=students,cls=cl,Date=dt)
@app.route('/attendance_data', methods=['GET', 'POST'])
def attendance_data():
    date =request.form['Date']
    cl=request.form['cls']
    df=pd.DataFrame()
    lc_pg_eng=pg_engine()
    attendance_record=request.form.to_dict()
    roll_numbers=attendance_record.keys()
    attendance=attendance_record.values()
    cls=attendance_record.pop('cls')
    date=attendance_record.pop('Date')
    df=pd.DataFrame()
    df['roll_number']=roll_numbers
    df['attendance']=attendance
    df['date']=date
    df['current_class']=cls
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')   
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    col_name=['roll_number','student_name']
    dbdf=pd.DataFrame(data=tables,columns=col_name)
    dbdf['roll_number']=dbdf['roll_number'].astype(str)
    df=pd.merge(left=dbdf,right=df,how='inner',on=['roll_number'])  
    df=df[['roll_number','student_name','current_class','date','attendance']]
    df.to_sql('attendence',con=lc_pg_eng,if_exists='append',index=False)
    return redirect("/attentence_info")
  
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "Sucessfully uploaded"
            # return redirect(url_for('download_file', name=filename))
    return '''
    <!DOCTYPE html>
<html>
  <head>
    <title>Upload</title>
    <style>
      /* Define the style for the header section */
      header {
        background-color: #333;
        color: #fff;
        padding: 20px;
        text-align: center;
      }

      /* Define the style for the buttons */
      .btn {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 12px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <header>
    <a href="/"><button>Home</button></a>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
  </body>
</html>'''
#render_template('upload_file.html')
@app.route('/download/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)
# @app.route('/db_tables_list')
# def db_tables_list():
#     conn = get_db_connection()
#     #get table names from DB
#     cur = conn.cursor()
#     cur.execute('''SELECT table_name 
#     FROM information_schema.tables 
#     WHERE table_schema = 'public';''')
#     db_tables=cur.fetchall()
#     table_name =[table[0] for table in db_tables]
#     cur.close()
#     conn.close()
#     return redirect(url_for('db_tables', table_name=table_name))

# @app.route('/select_table')
# def select_table():
    
#     conn = get_db_connection()
#     cur = conn.cursor()
#     # get selected table from form data
#     table_name = request.form['table_name']
#     # get rows from selected table
#     cur.execute(f"SELECT * FROM {table_name}")
#     rows = cur.fetchall()
#     # get column names from selected table
#     cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
#     columns = [col[3] for col in cur.fetchall()]
#     cur.close()
#     conn.close()
#     return pd.DataFrame(data=rows,columns=columns).to_html()

# class new_table(db.Model):
#     empid = db.Column(db.Integer, primary_key=True)
#     user_name = db.Column(db.String(50), unique=True, nullable=False)
#     passwd = db.Column(db.String(50), nullable = False)
#     first_name=db.Column(db.String(20),nullable = False)
#     last_name=db.Column(db.String(20),nullable = True)
#     role_id=db.Column(db.Integer,nullable = False)
#     reporting_manager=db.Column(db.String(50),nullable = False)
#     active_status=db.Column(db.String(10),nullable = False)
#     experience=db.Column(db.Integer(),nullable=True)
#     def __init__(self, empid, user_name,passwd,first_name,last_name,role_id,reporting_manager,active_status,experience):
#         self.empid = empid
#         self.user_name = user_name
#         self.passwd = passwd
#         self.first_name = first_name
#         self.last_name = last_name
#         self.role_id = role_id
#         self.reporting_manager = reporting_manager
#         self.active_status=active_status
#         self.experience=experience
        
# @app.route("/addperson")
# def addperson():
#     return render_template("addperson.html")

# @app.route("/personadd", methods=['POST'])
# def personadd():
#     empid = request.form["empid"]
#     user_name = request.form["user_name"]
#     passwd = request.form["passwd"]
#     first_name = request.form["first_name"]   
#     last_name=request.form["last_name"]
#     role_id=request.form["role_id"]
#     reporting_manager=request.form["reporting_manager"]
#     active_status=request.form["active_status"]
#     experience=request.form["experience"]
#     entry = new_table(empid, user_name,passwd,first_name,last_name,role_id,reporting_manager,active_status,experience)
#     db.session.add(entry)
#     db.session.commit()
#     return redirect('/table/')

# @app.route('/table_info')
# def tab_info():
#     # get selected table from form data
#     table_name = request.form['table_name']
#     conn = get_db_connection()
#     #get table names from DB
#     cur = conn.cursor()
#     cur.execute('''select column_name, data_type, character_maximum_length, column_default, is_nullable
#                     from INFORMATION_SCHEMA.COLUMNS where table_name = '{}';'''.format(table_name))
#     db_tables_info=cur.fetchall()
#     cur.close()
#     conn.close()
#     return {"info":db_tables_info}




# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return "Sucessfully uploaded"
#             # return redirect(url_for('download_file', name=filename))
#     return '''
#     <!DOCTYPE html>
# <html>
#   <head>
#     <title>Assingments upload page</title>
#     <style>
#       /* Define the style for the header section */
#       header {
#         background-color: #333;
#         color: #fff;
#         padding: 20px;
#         text-align: center;
#       }

#       /* Define the style for the buttons */
#       .btn {
#         background-color: #4CAF50;
#         border: none;
#         color: white;
#         padding: 12px 16px;
#         text-align: center;
#         text-decoration: none;
#         display: inline-block;
#         font-size: 16px;
#         margin: 4px 2px;
#         cursor: pointer;
#       }
#     </style>
#   </head>
#   <body>
#     <header>
#     <a href="/"><button>Home</button></a>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#   </body>
# </html>'''
# #render_template('upload_file.html')

# @app.route('/download/<name>')
# def download_file(name):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], name)



if __name__ == '__main__':
    db.create_all()
    # app.run(debug=True)
    app.run(debug=True,host='10.80.1.72',port=2545)