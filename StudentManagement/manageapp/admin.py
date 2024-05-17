from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask import Flask, request, redirect, url_for
from manageapp import db, dao, app
from manageapp.models import UserRole,Subject, Rule
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user

class MyIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


class StatsView(BaseView):
    @expose('/')
    def index(self):
        grade = request.args.get('grade_id')
        years = dao.load_years()
        year = request.args.get('year_id')
        semester = request.args.get('semester_id')

        if grade:
            subjects = dao.load_subject_by_grade(grade)
            stat = dao.calculate_class_statistics(subjects, semester, year)
            return self.render('admin/stats.html', subjects=subjects, years=years, semester=semester, stat=stat)
        else:
            return self.render('admin/stats.html', years=years)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class ManageSubject(ModelView):
    column_list = ['name','grade']
    column_editable_list = ['name']
    column_searchable_list = ['name']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class ChangeRule(ModelView):
    column_list = ['name','value']
    column_editable_list = ['value']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('admin.index'))
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN



admin = Admin(app=app, name='Quản trị', template_mode='bootstrap4', index_view=MyIndexView())
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(ManageSubject(Subject, db.session, name='Quản lý môn học'))
admin.add_view(ChangeRule(Rule,db.session, name='Thay đổi quy định'))
admin.add_view(LogoutView(name='Đăng xuất'))
