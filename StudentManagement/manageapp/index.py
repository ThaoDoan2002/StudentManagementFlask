from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from manageapp import app, login, dao, db
from manageapp.decorators import loggedin, teacherlogined, employeelogined
from manageapp.models import UserRole, Sex, Student, Studying, Semester, SchoolYear, MyClass, Score, \
    Outline


@app.context_processor
def roles_context_processor():
    if current_user.is_authenticated and current_user.user_role == UserRole.TEACHER:
        m_class = dao.get_my_class_of_user(current_user.id)
        subjects = dao.load_subjects_of_grade(m_class.name)
    else:
        subjects = []
    return {
        'roles': UserRole,
        'subjects': subjects
    }


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):  # tu dong duoc goi khi da login, du lieu tra ve luu vao bien current_user
    return dao.get_user_by_id(user_id)


@app.route('/login', methods=['get', 'post'])
@loggedin
def loginUser():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        u = dao.auth_user(username=username, password=password, role=role)
        if u:
            login_user(user=u)
            return redirect('/')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu hoặc quyền truy cập sai!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/login-admin', methods=['get', 'post'])
def admin_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_admin(username=username, password=password)
        if u:
            login_user(user=u)
            return redirect('/admin')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu hoặc quyền truy cập sai!'
    return render_template('admin/index.html', err_msg=err_msg)


@app.route('/logout', methods=['get'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


# yc1
@app.route('/students/add_student', methods=['get', 'post'])
@login_required
@teacherlogined
def add_student():
    err_msg1 = ''
    err_msg2 = ''
    err_msg3 = ''
    min_age = dao.get_rule_value('minAge')
    max_age = dao.get_rule_value('maxAge')
    f1 = True
    f2 = True
    f3 = True
    if request.method.__eq__('POST'):
        fn = request.form.get('fn')
        ln = request.form.get('ln')
        dob = request.form.get('dob')
        sex = request.form.get('sex')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')

        if min_age.value > (datetime.now().year - datetime.strptime(dob, "%Y-%m-%d").year) or (
                datetime.now().year - datetime.strptime(dob, "%Y-%m-%d").year) > max_age.value:
            err_msg1 = 'Chỉ nhận học sinh có độ tuổi 15 - 20 tuổi!'
            f1 = False
        if dao.is_email_duplicate(email):
            err_msg2 = 'Email đã tồn tại!'
            f2 = False
        if dao.is_phone_duplicate(phone):
            err_msg3 = 'Số điện thoại đã tồn tại!'
            f3 = False
        if f1 and f2 and f3:
            student = dao.add_student(fn=fn, ln=ln, dob=dob, sex=sex, address=address, phone=phone, email=email)
            return redirect(url_for('student_detail', id=student.id))

    return render_template('employee/add-student.html', sexes=Sex, err_msg1=err_msg1, err_msg2=err_msg2,
                           err_msg3=err_msg3)


@app.route('/students/new_students')
@login_required
def new_students():
    students = dao.load_new_student()
    err_msg = ''
    if len(students) == 0:
        err_msg = 'Danh sách học sinh mới trống!'
    return render_template('employee/new-students.html', students=students, err_msg=err_msg)


@app.route('/students/<int:id>')
@login_required
def student_detail(id):
    student = dao.get_student_by_id(id)
    return render_template('employee/student-detail.html', student=student)


# yc2.1
@app.route('/arrange_class', methods=['GET'])
@login_required
@teacherlogined
def arrange_class():
    number_max = dao.get_rule_value('maxNumber')  # rule

    new_students = dao.load_new_student()
    classes = dao.load_classes_g10()

    # Tạo danh sách số lượng học sinh trong mỗi lớp
    class_student_counts = {c.id: dao.number_students_in_class(c.id) for c in classes}

    for s in new_students:
        assigned = False  # học sinh chưa được xếp lớp
        for c in classes:
            if class_student_counts[c.id] < number_max.value:
                studying = Studying(student_id=s.id, my_class_id=c.id)
                db.session.add(studying)
                # Cập nhật số lượng học sinh trong lớp
                class_student_counts[c.id] += 1
                assigned = True
                break  # Thoát vòng lặp sau khi xếp được vào một lớp
        if not assigned:
            err_msg = (
                    'Không đủ lớp để xếp cho tất cả học sinh, mỗi lớp chỉ chứa tối đa '
                    + str(number_max)
                    + ' học sinh. '
                    + 'Vui lòng thêm lớp mới để xếp lớp, số học sinh cần xếp lớp là '
                    + str(len(new_students))
            )
            return render_template('employee/new-students.html', students=new_students, err_msg=err_msg)

    db.session.commit()

    # Redirect sau khi hoàn thành xếp lớp
    return redirect('/classes')


@app.route('/classes')
def info_classes():
    classes = dao.load_classes_detail()
    m_class_detail_id = request.args.get('m_class')
    name = request.args.get('name')

    class_detail = dao.get_class_detail_by_id(m_class_detail_id)

    students = dao.load_students(m_class_detail_id, name)

    return render_template('employee/class.html', classes=classes, students=students,
                           class_detail=class_detail)


# yc2.2
@app.route('/students/change_class/<int:st_id>/<int:cl_dt_id>', methods=['get', 'post'])
@login_required
@teacherlogined
def change_class(st_id, cl_dt_id):
    student = Student.query.get(st_id)

    name_class_now = dao.get_class_detail_by_id(cl_dt_id).name
    my_class = dao.get_my_class_by_dt_cl(cl_dt_id)

    max_number = dao.get_rule_value('maxNumber')

    err_msg = ''
    classrooms = dao.load_class_for_update(cl_dt_id, max_number.value,
                                           name_class_now)  # lấy ra các class khác cl_id và phải có số lượng học sinh còn dư theo yêu cầu, và khối nào chuyển theo khối đó
    if request.method.__eq__('POST'):
        n_class_id = request.form.get('n-class')
        if n_class_id and n_class_id != '0':
            # Tìm đối tượng studying cần cập nhật
            studying = Studying.query.filter(Studying.student_id == st_id, Studying.my_class_id == my_class.id).first()
            if studying:
                studying.my_class_id = n_class_id
                db.session.commit()
                n_class = MyClass.query.get(n_class_id)
                return redirect(url_for('info_classes', m_class=n_class.my_class_detail.id, year=app.config["YEAR"]))
        else:
            err_msg = "Vui lòng chọn lớp hợp lệ!"

    return render_template('employee/change-class.html', err_msg=err_msg, student=student,
                           name_class_now=name_class_now,
                           classrooms=classrooms)


# yc3.1

@app.route('/scores/<int:sj_id>', methods=['get', 'post'])
@login_required
@employeelogined
def input_scores(sj_id):
    m_class = dao.get_my_class_of_user(current_user.id)
    subject = dao.get_subject_by_id(sj_id)
    students = dao.load_students_of_user(m_class.id)
    score_types = dao.load_score_types()
    semesters = dao.load_semester(sj_id, m_class.id)
    type_15m = dao.get_outline(sj_id, m_class.id, 1)
    type_1h = dao.get_outline(sj_id, m_class.id, 2)

    if request.method.__eq__('POST'):
        data = request.form  # Lấy dữ liệu từ biểu mẫu HTML
        if data.get('type_1') and data.get('type_2'):
            q_15m = int(data['type_1']) #lay sl diem 15p do nguoi dung nhap
            q_1h = int(data['type_2'])
            o1 = Outline(subject_id=sj_id, my_class_id=m_class.id, score_type_id=1, number_score=q_15m)
            o2 = Outline(subject_id=sj_id, my_class_id=m_class.id, score_type_id=2, number_score=q_1h)
            db.session.add_all([o1, o2])

        # Lặp qua dữ liệu từ biểu mẫu HTML và lưu vào cơ sở dữ liệu
        for key, value in data.items():
            if key.startswith('score_'):
                info = key.split('_')
                studying_id = int(info[2])  # Lấy ID của học sinh từ tên trường dữ liệu
                type_id = int(info[1])  # Lấy ID của loại điểm từ tên trường dữ liệu
                semester = Semester(int(data['semester']))  # Lấy học kỳ từ tên trường dữ liệu

                # Tạo một bản ghi Score mới và lưu vào cơ sở dữ liệu
                new_score = Score(studying_id=studying_id, subject_id=sj_id, type_id=type_id, semester=semester,
                                  value=float(value))
                db.session.add(new_score)

        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        return redirect(url_for('scores_of_class_by_subject', sj_id=subject.id, se_value=semester.value))
    return render_template('teacher/input-scores.html', m_class=m_class, subject=subject, students=students,
                           semesters=semesters, score_types=score_types, type_15m=type_15m, type_1h=type_1h)


@app.route('/get_scores/<int:sj_id>', methods=['get'])
@login_required
def scores_of_class_by_subject(sj_id):
    err_msg = ''
    err_msg2 = ''
    se = request.args.get('se_value')
    if se is None:
        err_msg = 'Hãy chọn học kì!'

    subject = dao.get_subject_by_id(sj_id)
    m_class = dao.get_my_class_of_user(current_user.id)

    student_scores = []
    if se is not None:
        student_scores = dao.load_scores_of_class(subject.id, m_class.id, int(se))
        if len(student_scores) < 1:
            err_msg2 = "Chưa nhập điểm!"

    type_15m = dao.load_number_score_by_type(subject.id, 1, m_class.id)
    type_1h = dao.load_number_score_by_type(subject.id, 2, m_class.id)
    return render_template('teacher/scores.html', student_scores=student_scores, subject=subject,
                           m_class=m_class, type_15m=type_15m, type_1h=type_1h, semesters=Semester, err_msg=err_msg,
                           err_msg2=err_msg2)


@app.route("/api/classes", methods=['get'])
def api_classes():
    year = request.args.get('year')
    classes = dao.load_classes_for_api(year)
    classes_dict = [{'id': c.id, 'name': c.name} for c in classes]
    return jsonify(classes_dict)




@app.route('/average_scores')
@login_required
def average_scores():
    years = SchoolYear.query.all()
    err_msg = ''
    err_msg2 = ''
    classes = []
    year = request.args.get('year')
    m_class = request.args.get('m_class')


    if year is None or year == '':
        err_msg = 'Hãy chọn năm học!'

    if m_class is None or m_class == '':
        err_msg2 = 'Hãy chọn lớp học!'

    if year:
        classes = dao.load_classes_for_api(year)


    averages = dao.get_semester_avg(year, m_class)
    return render_template('teacher/average-scores.html', averages=averages, years=years, err_msg=err_msg, err_msg2=err_msg2,classes =classes)


@app.route('/api/load-subjects', methods=['GET'])
def load_subjects_api():
    grade_id = request.args.get('grade_id')
    subjects = dao.load_subject_by_grade(grade_id)
    subjects_dict = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    return jsonify(subjects_dict)


if __name__ == "__main__":
    app.run()
