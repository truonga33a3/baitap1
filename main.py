from flask import Flask, render_template, request, flash, session, redirect
from forms import SignUpForm, SignInForm, TaskForm, ProjectForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KietTT Python-Flask Web App'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models

@app.route('/')
def main():
    #return "Hello World! This is a content of Python and Flask web application."

    return render_template('index.html')

@app.route('/signUp', methods=['GET', 'POST'])
def showSignUp():
    form = SignUpForm()

    # if form.is_submitted():
    if form.validate_on_submit():
        print("Validate on submit")
        _fname = form.inputFirstName.data
        _lname = form.inputLastName.data
        _email = form.inputEmail.data
        _password = form.inputPassword.data
        if(db.session.query(models.User).filter_by(email=_email).count() == 0):
        #user = {'fname':_fname, 'lname':_lname, 'email':_email, 'password':_password}
            user = models.User(first_name = _fname, last_name = _lname, email = _email)
            user.set_password(_password)
            db.session.add(user)
            db.session.commit()
            return render_template('signUpSuccess.html', user = user)
        else:
            flash('Email {} is already exsits!'.format(_email))
            return render_template("signup.html", form = form)

    #return render_template('signup.html')
    print("Not validate on submit")
    return render_template('signup.html', form = form)

@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    form = SignInForm()

    if form.validate_on_submit():
        _email = form.inputEmail.data
        _password = form.inputPassword.data

        user = db.session.query(models.User).filter_by(email=_email).first()
        if(user is None):
            flash('Wrong email address or password!')
        else:
            if (user.check_password(_password)):
                session['user'] = user.user_id
                #return render_template('userhome.html')
                return redirect('/userHome')
            else:
                flash('Wrong email address or password!')

    return render_template('signin.html', form = form)

@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        projects = user.projects
        tasks = []
        for project in projects:
            tasks.extend(project.tasks)  # Gộp tất cả các nhiệm vụ từ các dự án thành một danh sách

        return render_template('userhome.html', user=user, projects=projects, tasks=tasks)
    else:
        return redirect('/')

@app.route('/userTask', methods=['GET', 'POST'])
def userTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        projects = user.projects
        tasks = []
        for project in projects:
            tasks.extend(project.tasks.copy())  # Sử dụng bản sao của danh sách tasks

        return render_template('usertask.html', user=user, projects=projects, tasks=tasks)
    else:
        return redirect('/')

@app.route('/newTask', methods=['GET', 'POST'])
def newTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    form.inputProject.choices = [(pj.project_id, pj.name) for pj in db.session.query(models.Project).all()]
    form.inputStatus.choices = [(s.status_id, s.description) for s in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()

        if form.validate_on_submit():
            _description = form.inputDescription.data
            _deadline = form.inputDeadline.data
            _priority_id = form.inputPriority.data
            _project_id = form.inputProject.data

            _status_id = form.inputStatus.data
            status = db.session.query(models.Status).filter_by(status_id = _status_id).first()

            priority = db.session.query(models.Priority).filter_by(priority_id = _priority_id).first()
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()

            projects = user.projects

            if project and _deadline > project.deadline:
                flash("Deadline of the task cannot be later than the project's deadline.")
                return render_template('/newtask.html', form=form, user=user)

            if status.description == "Đang thực hiện":
                project.status_id = 2  # Giả sử 2 là mã trạng thái 'Đang thực hiện' trong bảng trạng thái của project



            _task_id = request.form['hiddenTaskId']
            if (_task_id == "0"):
                task = models.Task(description = _description, deadline = _deadline , status = status, project = project, priority = priority)
                db.session.add(task)
            else:
                task = db.session.query(models.Task).filter_by(task_id = _task_id).first()
                task.description = _description
                task.deadline = _deadline
                task.project = project
                task.priority = priority
                task.status = status

            db.session.commit()

            update_project_status(projects)
            return redirect('/userTask')

        return render_template('/newtask.html', form = form, user = user)

    return redirect('/userTask')

def update_project_status(projects):
    tasks = []
    for project in projects:
        tasks.extend(project.tasks)

    all_completed = all(task.status_id == 4 for task in tasks)
    if all_completed:
        project.status_id = 4  # Chuyển sang trạng thái "Hoàn thành"
    else:
        project.status_id = 2
    db.session.commit()

@app.route('/deleteTask', methods=['GET', 'POST'])
def deleteTask():
    _user_id = session.get('user')
    if _user_id:
        _task_id = request.form['hiddenTaskId']
        if _task_id:
            user = db.session.query(models.User).filter_by(user_id=_user_id).first()
            projects = user.projects
            task = db.session.query(models.Task).filter_by(task_id = _task_id).first()
            db.session.delete(task)
            db.session.commit()
            update_project_status(projects)

            return redirect('/userTask')

    return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    form.inputProject.choices = [(pj.project_id, pj.name) for pj in db.session.query(models.Project).all()]
    form.inputStatus.choices = [(s.status_id, s.description) for s in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id = request.form['hiddenTaskId']
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id = _task_id).first()
            form.inputDescription.default = task.description
            form.inputDeadline.default = task.deadline
            form.inputStatus.default = task.status_id
            form.inputProject.default = task.project_id
            form.inputPriority.default = task.priority_id
            form.process()
            return render_template('/newtask.html', form = form, user = user, task = task)

    return redirect('/')

@app.route('/doneTask', methods=['GET', 'POST'])
def doneTask():
    _user_id = session.get('user')
    if _user_id:
        _task_id = request.form['hiddenTaskId']
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id = _task_id).first()
            task.isCompleted = True
            db.session.commit()

        return redirect('/userTask')

    return redirect('/')

@app.route('/newProject', methods=['GET', 'POST'])
def newProject():
    _user_id = session.get('user')
    form = ProjectForm()
    form.inputStatus.choices = [(s.status_id, s.description) for s in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()

        if form.validate_on_submit():
            _name = form.inputName.data
            _description = form.inputDescription.data
            _deadline = form.inputDeadline.data
            _status_id = form.inputStatus.data
            status = db.session.query(models.Status).filter_by(status_id = _status_id).first()

            _project_id = request.form['hiddenProjectId']
            if (_project_id == "0"):
                project = models.Project(name = _name, description = _description, deadline = _deadline, user = user, status = status)
                db.session.add(project)
            else:
                project = db.session.query(models.Project).filter_by(project_id = _project_id).first()
                project.name = _name
                project.description = _description
                project.deadline = _deadline
                project.status = status

            db.session.commit()
            return redirect('/userProject')

        return render_template('/newproject.html', form = form, user = user)

    return redirect('/')

@app.route('/deleteProject', methods=['GET', 'POST'])
def deleteProject():
    _user_id = session.get('user')
    if _user_id:
        _project_id = request.form['hiddenProjectId']
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id = _project_id).first()
            db.session.delete(project)
            db.session.commit()

            return redirect('/userProject')

    return redirect('/')

@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id = session.get('user')
    form = ProjectForm()
    form.inputStatus.choices = [(s.status_id, s.description) for s in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _project_id = request.form['hiddenProjectId']
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id = _project_id).first()
            form.inputName.default = project.name
            form.inputDescription.default = project.description
            form.inputDeadline.default = project.deadline
            form.inputStatus.default = project.status_id
            form.process()
            return render_template('/newproject.html', form = form, user = user, project = project)

    return redirect('/')

@app.route('/userProject', methods=['GET', 'POST'])
def userProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        return render_template('userproject.html', user = user)
    else:
        return redirect('/')

@app.route('/searchTask', methods=['GET', 'POST'])
def searchTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        search_query = request.form['search_query']  # Truy vấn tìm kiếm từ form

        # Tìm kiếm các task có trạng thái phù hợp với truy vấn tìm kiếm
        tasks = db.session.query(models.Task).filter(models.Task.status.has(models.Status.description.ilike(f'%{search_query}%'))).all()

        return render_template('usertask.html', user=user, tasks=tasks, search_query=search_query)
    else:
        return redirect('/')

@app.route('/searchProject', methods=['GET', 'POST'])
def searchProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        search_query = request.form['search_query']  # Truy vấn tìm kiếm từ form

        # Tìm kiếm các project có trạng thái phù hợp với truy vấn tìm kiếm
        projects = db.session.query(models.Project).filter(models.Project.status.has(models.Status.description.ilike(f'%{search_query}%'))).all()
        print(projects)

        return render_template('userprojectsearch.html', user=user, projects=projects, search_query=search_query)
    else:
        return redirect('/')

@app.route('/searchByNameTask', methods=['POST'])
def search_by_name_task():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        search_name_query = request.form['search_name_query']  # Truy vấn tìm kiếm từ form

        # Tìm kiếm các task có mô tả chứa truy vấn tìm kiếm
        tasks = db.session.query(models.Task).filter(models.Task.description.ilike(f'%{search_name_query}%')).all()

        return render_template('usertask.html', user=user, tasks=tasks, search_name_query=search_name_query)
    else:
        return redirect('/')

@app.route('/searchByNameProject', methods=['POST'])
def search_by_name_project():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        search_name_query = request.form['search_name_query']  # Truy vấn tìm kiếm từ form

        # Tìm kiếm các task có mô tả chứa truy vấn tìm kiếm
        projects = db.session.query(models.Project).filter(models.Project.name.ilike(f'%{search_name_query}%')).all()

        return render_template('userprojectsearch.html', user=user, projects=projects, search_name_query=search_name_query)
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)