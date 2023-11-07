from flask import Flask,render_template,request,redirect,session,flash,url_for
from functools import wraps
from flask_mysqldb import MySQL
import mysql.connector
app=Flask(__name__)

# DATABASE CONNECTION
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="pod_score",
  connect_timeout=1000
)
dbconn = mydb.cursor(dictionary=True) # dict format

#Login
@app.route('/') 
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        eid=request.form["email"]
        pwd=request.form["password"]
        print(request.form)
        cur=mydb.cursor()
        cur.execute("select * from login where email=%s and password=%s",(eid,pwd))
        data1=cur.fetchone()
        if data1:
            print(data1)
            session['logged_in']='8973818'
            session['email']= eid
            session['announcement']= "Happy Diwali"
            flash('Login Successfully','success')
            return redirect("/time_sheet_dashboard")
        else:
            flash('Invalid Login. Try Again','danger')
    return render_template("index.html")
  
#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('login'))
	return wrap
  
#logout
@app.route("/logout")
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))

#Time sheet Definition
@app.route("/definition")
@is_logged_in
def fetch_title():
    cur=mydb.cursor(dictionary=True)
    cur.execute("SELECT id,title FROM  title WHERE status=1 and module=2 order by title;")
    title=cur.fetchall()
    cur.close()
    
    cur=mydb.cursor(dictionary=True)
    cur.execute("select t.title,d.type,d.id,d.status,d.editable from definition d join title t on t.id=d.title WHERE module=2  order by t.title,d.type;")
    definition_list=cur.fetchall()
    cur.close()
    print(title)
    if title:
        return render_template('definition.html',title=title,definition_list=definition_list)  
    else:
        return render_template('definition.html')
    

#Time sheet Dashboard
@app.route("/time_sheet_dashboard")
@is_logged_in
def time_sheet_dashboard():
    cur=mydb.cursor(dictionary=True)
    cur.execute("SELECT id,title FROM  title WHERE status=1 and module=2 order by title;")
    title=cur.fetchall()
    cur.close()
    
    cur=mydb.cursor(dictionary=True)
    cur.execute("select t.title,d.type,d.id,d.status,d.editable from definition d join title t on t.id=d.title WHERE module=2  order by t.title,d.type;")
    definition_list=cur.fetchall()
    cur.close()
    print(title)
    if title:
        return render_template('time_sheet_dashboard.html',title=title,definition_list=definition_list)  
    else:
        return render_template('time_sheet_dashboard.html')


#AJAX INSERT AND UPDATE
@app.route('/Ajax_call',methods=['POST','GET'])
@is_logged_in
def Ajax_call():
    d=request.form.to_dict()
    ke=val=""
    sources=1
    session['logged_in']=8973818
    cur=mydb.cursor(dictionary=True)
    if d['act']=="addUpdate" :
        if d['id']=="":
            for key, value in d.items():
                if key!="act" and key!="id" and key!="page" and key!="module" :
                    ke+=key+","
                    if key=="tapal_date" and value=="":
                        val+="NULL,"
                    else:
                        val+="'"+str(value)+"',"

            qy="INSERT INTO  " + d['page'] +" ("+ke+" sources,created_by) value("+val+str(sources)+","+str('8973818')+");"	
        else:
            for key, value in d.items():
                if key!="act" and key!="id" and key!="page" and key!="module" :
                    if key=="tapal_date" and value=="":
                        ke+=key+"=NULL,"
                    else:
                        ke+=key+"="+"'"+value+"',"

            print(ke)
            qy="UPDATE " + d['page'] +" SET "+ke[:-1]+" WHERE id="+d['id']
        print(qy)
        cur.execute(qy)	
        mydb.commit()
        cur.close()
        return ("1")
    
    if d['act']=="editView" :
        cur=mydb.cursor(dictionary=True)
        cur.execute("select * from definition where id ="+d['id'])
        editresult=cur.fetchone()
        cur.close()
        return (editresult)
    if d['act']=="DeleteData" : 
        qy="UPDATE " + d['page'] +" SET status="+d['status']+ "WHERE id="+d['id']
        print(qy)
        cur.execute(qy)	
        mydb.commit()
        cur.close()
        return ("1")

    

    


if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)