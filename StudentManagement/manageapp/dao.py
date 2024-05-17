from sqlalchemy import func, and_, desc, text, case
from sqlalchemy.orm import aliased


from manageapp.models import User, UserRole, Student, Sex, Studying, Subject, SchoolYear, \
    ScoreType, MyClass, Outline, Score, Semester, MyClassDetail,  Rule
import hashlib
from manageapp import db, app


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password, role):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password),
                             User.user_role.__eq__(UserRole(int(role)))).first()


def auth_admin(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


# yc1

def add_student(fn, ln, dob, sex, address, phone, email):
    s = Student(first_name=fn,
                last_name=ln,
                dob=dob,
                sex=Sex(int(sex)),
                address=address,
                phone=phone,
                email=email)
    db.session.add(s)
    db.session.commit()
    return s


def is_email_duplicate(email):
    # Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu hay không
    existing_student = Student.query.filter(Student.email == email).first()
    return existing_student is not None


def is_phone_duplicate(phone):
    # Kiểm tra xem phone đã tồn tại trong cơ sở dữ liệu hay không
    existing_student = Student.query.filter(Student.phone == phone).first()
    return existing_student is not None


def load_new_student():
    students = Student.query \
        .outerjoin(Studying) \
        .filter(Studying.my_class_id.is_(None)) \
        .order_by(desc(Student.id)) \
        .all()
    return students


# yc2
# yc2.1

def load_classes_g10():
    classes = MyClass.query \
        .join(MyClassDetail, MyClassDetail.id == MyClass.my_class_detail_id) \
        .filter(MyClassDetail.name.contains('10'), MyClass.school_year_id == app.config["YEAR"]).all()
    return classes


def number_students_in_class(class_id):
    n = db.session.query(func.count(Studying.id)) \
        .filter(Studying.my_class_id == class_id) \
        .scalar()
    return n


def load_classes_detail():
    classes = MyClassDetail.query.all()
    return classes


def load_years():
    year = SchoolYear.query.all()
    return year


def load_students(m_class_detail_id=None, name=None):
    query = db.session.query(Student.id, Student.first_name, Student.last_name, Student.sex, Student.dob,
                             Student.address) \
        .join(Studying, Studying.student_id == Student.id) \
        .join(MyClass, Studying.my_class_id == MyClass.id) \
        .filter(MyClass.school_year_id == app.config["YEAR"])

    if m_class_detail_id is not None:
        query = query.filter(MyClass.my_class_detail_id == m_class_detail_id)
    if name is not None:
        query = query.filter((Student.first_name.contains(name)) | (Student.last_name.contains(name)))

    students = query.all()

    return students


def get_class_detail_by_id(id):
    return MyClassDetail.query.get(id)


def get_studying_by_stid_clid(st_id, cl_id, year):
    return Studying.query.filter_by(student_id=st_id, my_class_id=cl_id, school_year_id=year).first()


# yc2.2

def get_my_class_by_dt_cl(dt_cl_id):
    m_class = MyClass.query.filter(MyClass.my_class_detail_id == dt_cl_id,
                                   MyClass.school_year_id == app.config['YEAR']).first()
    return m_class


def load_class_for_update(cl_dt_id, max_number, name):
    classrooms = db.session.query(MyClass.id, MyClassDetail.name) \
        .join(MyClass, MyClass.my_class_detail_id == MyClassDetail.id) \
        .join(Studying, Studying.my_class_id == MyClass.id) \
        .filter(MyClass.school_year_id == app.config["YEAR"], MyClassDetail.id != cl_dt_id,
                MyClassDetail.name.icontains(name[:2])) \
        .group_by(MyClass.id) \
        .having(func.count(Studying.student_id) < max_number) \
        .all()

    return classrooms


def get_student_by_id(id):
    return Student.query.get(id)


# yc3.1


def get_my_class_of_user(user_id):
    m_class = db.session.query(MyClass.id, MyClassDetail.name, SchoolYear.year) \
        .join(MyClassDetail, MyClassDetail.id == MyClass.my_class_detail_id) \
        .join(SchoolYear, SchoolYear.id == MyClass.school_year_id) \
        .filter(MyClass.user_id == user_id, MyClass.school_year_id == app.config["YEAR"]) \
        .first()
    return m_class


def add_outline(sj_id, cl_id, score_type_id, quantity):
    o = Outline(subject_id=sj_id, my_class_id=cl_id, score_type_id=score_type_id, number_score=quantity)
    db.session.add(o)
    db.session.commit()
    return o


def load_subject():
    return Subject.query.all()


def load_subjects_of_grade(c_name):
    grade = c_name[:2]
    subjects = Subject.query.filter(Subject.grade.contains(grade)).all()
    return subjects


def load_subject_by_grade(grade):
    return Subject.query.filter(Subject.grade.contains(grade)).all()


def load_students_of_user(cl_id):
    students = db.session.query(Studying.id, Student.first_name, Student.last_name) \
        .join(Studying, Studying.student_id == Student.id) \
        .filter(Studying.my_class_id == cl_id) \
        .order_by(Student.first_name).all()
    print(students)
    return students


def load_score_types():
    return ScoreType.query.all()


def load_number_score_by_type(sj_id, type_id, cl_id):
    outline = Outline.query. \
        filter(Outline.subject_id == sj_id, Outline.score_type_id == type_id, Outline.my_class_id == cl_id) \
        .first()
    if outline:
        return outline.number_score
    return 0;


def get_subject_by_id(sj_id):
    return Subject.query.get(sj_id)


def add_scores(scores):
    if scores:
        for score in scores.values():
            studying = Studying.query.filter(Studying.student_id == score['st_id'],
                                             Studying.my_class_id == score['cl_id'],
                                             Studying.school_year_id == 2).first()
            if studying:
                s = Score(studying_id=studying.id, subject_id=score['sj_id'], type_id=score['type_id'],
                          semester=Semester(score['semester']), value=score['value'])
                db.session.add(s)
            else:
                print(f"Studying not found for student_id: {score['st_id']} and class_id: {score['cl_id']}")
        db.session.commit()


def load_semester(sj_id, cl_id):
    entered_semesters = Score.query \
        .join(Studying) \
        .filter(
        Studying.my_class_id == cl_id,
        Score.subject_id == sj_id
    ).distinct(Score.semester).all()

    # Chuyển danh sách các học kỳ đã nhập điểm thành set
    entered_semesters_set = set(semester.semester for semester in entered_semesters)

    # Lấy danh sách tất cả các học kỳ
    all_semesters = {Semester.S1, Semester.S2}  # Điều chỉnh tùy theo số lượng học kỳ của bạn

    # Tìm các học kỳ chưa nhập điểm
    missing_semesters = list(all_semesters - entered_semesters_set)

    print(missing_semesters)
    return missing_semesters


def get_outline(sj_id, cl_id, sc_type_id):
    o = db.session.query(Outline.score_type_id, Outline.number_score) \
        .filter(Outline.subject_id == sj_id, Outline.my_class_id == cl_id, Outline.score_type_id == sc_type_id).first()
    print(o)
    return o


def load_scores_of_class(s_id, cl_id, se_value):
    # Tạo câu truy vấn SQL sử dụng tham số :school_year_id
    query = text("""
          WITH subAllScores AS (
        SELECT 
            s.id,
            s.first_name, 
            s.last_name, 
            score_type.name as type, 
            sc.value
        FROM 
            student s
        JOIN 
            studying st ON s.id = st.student_id
        JOIN 
            score sc ON sc.studying_id = st.id
        JOIN 
            score_type ON sc.type_id = score_type.id
        WHERE 
            sc.subject_id = :subject_id
            AND st.my_class_id = :my_class_id
            AND sc.semester= :semester
    ),
    dao_score AS (
        SELECT 
            first_name,
            last_name,
            GROUP_CONCAT(CASE WHEN type = '15 phút' THEN value ELSE NULL END ORDER BY value) AS fifteen_minutes,
            GROUP_CONCAT(CASE WHEN type = '1 tiết' THEN value ELSE NULL END ORDER BY value) AS one_hour,
            GROUP_CONCAT(CASE WHEN type = 'Thi cuối kì' THEN value ELSE NULL END ORDER BY value) AS final_test
        FROM 
            subAllScores
        GROUP BY 
            first_name, last_name
        ORDER BY first_name
    )
    
    SELECT * FROM dao_score;
    """)

    se = Semester(int(se_value)).name
    # Truyền giá trị tham số vào khi thực thi truy vấn
    result = db.session.execute(query, {"subject_id": s_id, "my_class_id": cl_id,
                                        "semester": se})

    # Lấy kết quả
    scores_results = []
    for row in result:
        scores_results.append(row)
    print(scores_results)
    return scores_results


def load_classes_for_api(year):
    classes = db.session.query(MyClass.id, MyClassDetail.name) \
        .join(MyClassDetail, MyClassDetail.id == MyClass.my_class_detail_id) \
        .filter(MyClass.school_year_id == year) \
        .all()
    return classes


def get_semester_avg(year=None, cl_id=None):
    # Tạo câu truy vấn SQL sử dụng tham số :school_year_id va my_class_id
    query = text("""
        WITH subTBM AS (
                   SELECT 
                sc.studying_id,
                s.first_name,
                s.last_name,
                cd.name,
                sc.subject_id, 
                sc.semester, 
                AVG(sc.value) AS avg_value
            FROM 
                score sc
            JOIN 
                studying sty ON sty.id = sc.studying_id
            JOIN 
                student s ON s.id = sty.student_id
            JOIN 
                my_class c ON c.id = sty.my_class_id
            JOIN 
				my_class_detail cd ON cd.id = c.my_class_detail_id 
            WHERE 
                c.school_year_id = :school_year_id and c.id = :my_class_id  -- Sử dụng tham số :school_year_id
            GROUP BY 
                sc.studying_id, sc.subject_id, sc.semester
        ),
        semester_avg AS (
            SELECT 
                studying_id,
                first_name,
                last_name,
                name,
                AVG(CASE WHEN semester = 'S1' THEN avg_value ELSE NULL END) AS semester1,
                AVG(CASE WHEN semester = 'S2' THEN avg_value ELSE NULL END) AS semester2
            FROM 
                subTBM
            GROUP BY 
                studying_id
        )

        SELECT * FROM semester_avg;
    """)
    if year and cl_id:
        # Truyền giá trị tham số vào khi thực thi truy vấn
        result = db.session.execute(query, {"school_year_id": year, "my_class_id": cl_id})

        # Lấy kết quả
        semester_avg_results = []
        for row in result:
            semester_avg_results.append(row)
        return semester_avg_results
    else:
        return []


# def stats(subject_id, semester_id, year_id):
#     subject_stats = db.session.query(
#         MyClassDetail.name,
#         func.count(Student.id),
#         func.sum(case([(Score.value >= 5, 1)], else_=0)),
#         func.avg(case([(Score.value >= 5, 1)], else_=0))
#     ).join(MyClass, MyClass.my_class_detail_id == MyClassDetail.id) \
#         .join(Studying, MyClass.id == Studying.my_class_id) \
#         .join(Student, Student.id == Studying.student_id) \
#         .join(Score, Score.studying_id == Studying.id) \
#         .filter(Score.subject_id == subject_id, Score.semester == semester_id, MyClass.school_year_id == year_id) \
#         .group_by(MyClassDetail.name).all()
#     return subject_stats


def calculate_class_statistics(subject_id, semester_name, year_id):
    # Lấy thông tin các lớp học
    class_infos = (db.session.query(MyClass)
                   .join(MyClassDetail)
                   .join(SchoolYear)
                   .join(Studying).filter(
        MyClass.school_year_id == year_id,
        Studying.id == Score.studying_id,
        Score.subject_id == Subject.id
    ).all())

    if class_infos:
        result = []
        for class_info in class_infos:
            # Lấy điểm trung bình của từng học sinh trong lớp
            avg_scores_query = db.session.query(Studying.student_id, func.avg(Score.value).label("average_score")).join(
                Score).filter(
                Studying.my_class_id == class_info.id,
                Score.semester == semester_name
            ).group_by(Studying.student_id).subquery()

            # Đếm số lượng học sinh có điểm trung bình >= 5
            num_passing_students = db.session.query(func.count()).filter(
                avg_scores_query.c.average_score >= 5
            ).scalar()

            # Tính tỷ lệ
            total_students = (db.session.query(func.count(Studying.id))
                              .filter_by(my_class_id=class_info.id).scalar())
            if total_students:
                pass_rate = num_passing_students / total_students * 100
            else:
                pass_rate = 0

            result.append((
                class_info.my_class_detail.name,
                total_students,
                num_passing_students,
                pass_rate
            ))

        return result
    else:
        return None


def get_value_by_name(name):
    result = db.session.query(Rule.value).filter(Rule.name==name).first()
    return int(result[0])

def get_rule_value(name):
    result = db.session.query(Rule.value).filter(Rule.name == name).first()
    return result


if __name__ == '__main__':
    with app.app_context():
        # results = calculate_class_statistics(1, 'S1', 3)
        # print(results)
        # print(load_subject_by_grade('G11'))

