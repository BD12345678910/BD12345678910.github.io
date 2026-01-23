'''
Docstring for classes
Calender
Assignment
Announcement
Discussion
GroupClass
Dashboard
MyGrades
Student
Teacher
Material
Query
Class
'''
from datetime import datetime
from sql_functions_v3 import SQLManager as sql_functions
import matplotlib.pyplot as plt

class Student:
    """学生类，对应Student_info表"""
    def __init__(self, stu_name, stu_id=None, stu_gnum=None, stu_age=None, 
                 stu_nationality=None, stu_email=None, stu_phone=None, 
                 stu_gender=None, stu_grade=None, stu_class=None, 
                 graduation_year=None, stu_course=None):
        self.stu_id = stu_id  # 主键，数据库自动生成
        self.stu_name = stu_name  # 必填
        self.stu_gnum = stu_gnum  # 唯一标识
        self.stu_age = stu_age
        self.stu_nationality = stu_nationality
        self.stu_email = stu_email
        self.stu_phone = stu_phone
        self.stu_gender = stu_gender
        self.stu_grade = stu_grade
        self.stu_class = stu_class
        self.graduation_year = graduation_year
        self.stu_course = stu_course
        self.stu_classes = sql_functions.get_student_classes(stu_id) if stu_id else []
    def save(self):
        """保存学生信息到数据库，返回生成的stu_id"""
        if self.stu_id is None:  # 新增学生
            self.stu_id = sql_functions.add_student(
                stu_name=self.stu_name,
                stu_gnum=self.stu_gnum,
                stu_age=self.stu_age,
                stu_nationality=self.stu_nationality,
                stu_email=self.stu_email,
                stu_phone=self.stu_phone,
                stu_gender=self.stu_gender,
                stu_grade=self.stu_grade,
                stu_class=self.stu_class,
                graduation_year=self.graduation_year,
                stu_course=self.stu_course
            )
        return self.stu_id

    def enroll_in_class(self, class_id):
        """学生注册到班级"""
        if self.stu_id:
            return sql_functions.add_student_to_class(self.stu_id, class_id)
        print("错误：学生未保存，无法注册班级")
        return False


class Teacher:
    """教师类，对应teacher_info表"""
    def __init__(self, teacher_name, teacher_id=None, teacher_room=None, 
                 teacher_nationality=None, teacher_email=None, 
                 teacher_subject=None, teacher_homeroom=None):
        self.teacher_id = teacher_id  # 主键，数据库自动生成
        self.teacher_name = teacher_name  # 必填
        self.teacher_room = teacher_room  # 办公室
        self.teacher_nationality = teacher_nationality
        self.teacher_email = teacher_email
        self.teacher_subject = teacher_subject  # 主讲科目
        self.teacher_homeroom = teacher_homeroom  # 班主任班级
        self.teacher_classes = sql_functions.get_teacher_class(teacher_id) if teacher_id else []

    def save(self):
        """保存教师信息到数据库，返回生成的teacher_id"""
        if self.teacher_id is None:  # 新增教师
            self.teacher_id = sql_functions.add_teacher(
                teacher_name=self.teacher_name,
                teacher_room=self.teacher_room,
                teacher_nationality=self.teacher_nationality,
                teacher_email=self.teacher_email,
                teacher_subject=self.teacher_subject,
                teacher_homeroom=self.teacher_homeroom
            )
        return self.teacher_id
    def get_grades(self, classid):
        """获取教师所教班级的学生成绩"""
        return sql_functions.get_student_assignment_score(classid)
    def grades_distribution(self, classid):
        """获取教师所教班级的成绩分布情况"""
        grades = self.get_grades(classid) # {student_id: {"total":总分, "avg":平均分, "complete":[所有作业分数列表]}}
        plt.bar(sql_functions.ID2Name(grades.keys()), [grades[sid]['avg'] for sid in grades])
        plt.xlabel('student Name')
        plt.ylabel('homework average score')
        plt.show()
    def student_distribution(self, stuId, classid):
        """获取某学生在某个班级的成绩分布情况"""
        grades = self.get_grades(classid) # {student_id: {"total":总分, "avg":平均分, "complete":[所有作业分数列表]}}
        student_grade = grades.get(stuId)
        plt.hist(student_grade['complete'], bins=10, edgecolor='black')
        plt.xlabel('Score Range')
        plt.ylabel('Frequency')
        plt.title(f'Student ID: {stuId} Score Distribution')
        plt.show()
    def class_word_cloud(self,classid):
        sql_functions.word_cloud(classid) #classid}_word_cloud.png"
    def class_histograph_word(self,classid):
        sql_functions.histograph(classid) #{classid}_frequency_hist.png"
    
    

class Class:
    """班级/课程类，对应Class_info表"""
    def __init__(self, teacher_id, class_id=None, subject=None, room=None, 
                 grade=None, type_=None):
        self.class_id = class_id  # 主键，数据库自动生成
        self.teacher_id = teacher_id  # 授课教师ID（外键）
        self.subject = subject  # 科目
        self.room = room  # 教室
        self.grade = grade  # 年级
        self.type_ = type_  # 类型（必修/选修等）

    def save(self):
        """保存班级信息到数据库，返回生成的class_id"""
        if self.class_id is None:  # 新增班级
            self.class_id = sql_functions.add_class(
                teacher_id=self.teacher_id,
                subject=self.subject,
                room=self.room,
                grade=self.grade,
                type_=self.type_
            )
        return self.class_id


class Query:
    """咨询/问题类，对应query_info表"""
    def __init__(self, stu_id, teacher_id, class_id, question, query_id=None, 
                 answer=None, time_=None):
        self.query_id = query_id  # 主键，数据库自动生成
        self.stu_id = stu_id  # 提问学生ID（外键）
        self.teacher_id = teacher_id  # 接收教师ID（外键）
        self.class_id = class_id  # 关联班级ID（外键）
        self.question = question  # 问题内容（必填）
        self.answer = answer  # 回答内容
        self.time_ = time_ or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 提问时间

    def save(self):
        """保存咨询记录到数据库，返回生成的query_id"""
        if self.query_id is None:  # 新增咨询
            self.query_id = sql_functions.add_query(
                stu_id=self.stu_id,
                teacher_id=self.teacher_id,
                class_id=self.class_id,
                question=self.question,
                answer=self.answer,
                time_=self.time_
            )
        return self.query_id


class Calendar:
    """日历事件类，对应Calendar表"""
    def __init__(self, title, start_time, end_time, created_by, created_by_type,
                 calendar_id=None, description=None, class_id=None):
        self.calendar_id = calendar_id  # 主键，数据库自动生成
        self.title = title  # 事件标题（必填）
        self.description = description  # 事件描述
        self.start_time = start_time  # 开始时间（必填）
        self.end_time = end_time  # 结束时间（必填）
        self.class_id = class_id  # 关联班级（可选）
        self.created_by = created_by  # 创建者ID（学生/教师）
        self.created_by_type = created_by_type  # 创建者类型（'student'/'teacher'）

    def save(self):
        """保存日历事件到数据库，返回生成的calendar_id"""
        if self.calendar_id is None:  # 新增事件
            self.calendar_id = sql_functions.add_calendar(
                title=self.title,
                description=self.description,
                start_time=self.start_time,
                end_time=self.end_time,
                class_id=self.class_id,
                created_by=self.created_by,
                created_by_type=self.created_by_type
            )
        return self.calendar_id


class Assignment:
    """作业类，对应Assignment表"""
    def __init__(self, title, due_time, class_id, teacher_id, assignment_id=None,
                 description=None, publish_time=None, total_points=None, type_=None):
        self.assignment_id = assignment_id  # 主键，数据库自动生成
        self.title = title  # 作业标题（必填）
        self.description = description  # 作业描述
        self.publish_time = publish_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 发布时间
        self.due_time = due_time  # 截止时间（必填）
        self.class_id = class_id  # 所属班级（外键）
        self.teacher_id = teacher_id  # 发布教师（外键）
        self.total_points = total_points  # 总分
        self.type_ = type_  # 作业类型

    def save(self):
        """保存作业到数据库，返回生成的assignment_id"""
        if self.assignment_id is None:  # 新增作业
            self.assignment_id = sql_functions.add_assignment(
                title=self.title,
                description=self.description,
                due_time=self.due_time,
                class_id=self.class_id,
                teacher_id=self.teacher_id,
                total_points=self.total_points,
                type_=self.type_
            )
        return self.assignment_id


class Announcement:
    """公告类，对应Announcement表"""
    def __init__(self, title, content, teacher_id, announcement_id=None,
                 class_id=None, publish_time=None):
        self.announcement_id = announcement_id  # 主键，数据库自动生成
        self.title = title  # 公告标题（必填）
        self.content = content  # 公告内容（必填）
        self.publish_time = publish_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 发布时间
        self.teacher_id = teacher_id  # 发布教师（外键）
        self.class_id = class_id  # 关联班级（可选，可为全校公告）

    def save(self):
        """保存公告到数据库，返回生成的announcement_id"""
        if self.announcement_id is None:  # 新增公告
            self.announcement_id = sql_functions.add_announcement(
                title=self.title,
                content=self.content,
                teacher_id=self.teacher_id,
                class_id=self.class_id
            )
        return self.announcement_id


class Discussion:
    """讨论类，对应Discussion表（支持嵌套回复）"""
    def __init__(self, topic, content, initiator_id, initiator_type,
                 discussion_id=None, class_id=None, time_=None, parent_id=None):
        self.discussion_id = discussion_id  # 主键，数据库自动生成
        self.topic = topic  # 讨论主题（必填）
        self.content = content  # 讨论内容（必填）
        self.initiator_id = initiator_id  # 发起者ID（学生/教师）
        self.initiator_type = initiator_type  # 发起者类型（'student'/'teacher'）
        self.class_id = class_id  # 关联班级（可选）
        self.time_ = time_ or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 发布时间
        self.parent_id = parent_id  # 父评论ID（用于回复，None表示主贴）

    def save(self):
        """保存讨论到数据库（需先在sql_functions中实现add_discussion函数）"""
        if self.discussion_id is None:
            # 假设已实现add_discussion函数
            self.discussion_id = sql_functions.add_discussion(
                topic=self.topic,
                content=self.content,
                initiator_id=self.initiator_id,
                initiator_type=self.initiator_type,
                class_id=self.class_id,
                time_=self.time_,
                parent_id=self.parent_id
            )
        return self.discussion_id


# 其他类（GroupClass、Dashboard、MyGrades、Material）的实现模式类似，以下为简化版
class GroupClass:
    """小组类，对应GroupClass表"""
    def __init__(self, group_name, class_id, group_class_id=None, leader_stu_id=None):
        self.group_class_id = group_class_id
        self.group_name = group_name  # 小组名称（必填）
        self.class_id = class_id  # 所属班级（外键）
        self.leader_stu_id = leader_stu_id  # 组长（学生ID）

    def save(self):
        # 需在sql_functions中实现add_group_class函数
        if self.group_class_id is None:
            self.group_class_id = sql_functions.add_group_class(
                self.group_name, self.class_id, self.leader_stu_id
            )
        return self.group_class_id


class MyGrades:
    """成绩类，对应MyGrades表"""
    def __init__(self, stu_id, assignment_id, grade_id=None, score=None, comment=None, graded_time=None):
        self.grade_id = grade_id
        self.stu_id = stu_id  # 学生ID（外键）
        self.assignment_id = assignment_id  # 作业ID（外键）
        self.score = score  # 分数
        self.comment = comment  # 评语
        self.graded_time = graded_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save(self):
        # 需在sql_functions中实现add_my_grades函数
        if self.grade_id is None:
            self.grade_id = sql_functions.add_my_grades(
                self.stu_id, self.assignment_id, self.score, self.comment, self.graded_time
            )
        return self.grade_id


class Material:
    """教学材料类，对应Material表"""
    def __init__(self, title, teacher_id, material_id=None, description=None,
                 file_path=None, upload_time=None, class_id=None):
        self.material_id = material_id
        self.title = title  # 材料标题（必填）
        self.description = description  # 材料描述
        self.file_path = file_path  # 文件路径
        self.upload_time = upload_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.class_id = class_id  # 关联班级（可选）
        self.teacher_id = teacher_id  # 上传教师（外键）

    def save(self):
        # 需在sql_functions中实现add_material函数
        if self.material_id is None:
            self.material_id = sql_functions.add_material(
                self.title, self.description, self.file_path, self.class_id, self.teacher_id
            )
        return self.material_id


class Dashboard:
    """仪表盘类，对应Dashboard表"""
    def __init__(self, user_id, user_type, dashboard_id=None, layout_settings=None, last_updated=None):
        self.dashboard_id = dashboard_id
        self.user_id = user_id  # 用户ID（学生/教师）
        self.user_type = user_type  # 用户类型（'student'/'teacher'）
        self.layout_settings = layout_settings  # 布局设置（JSON字符串等）
        self.last_updated = last_updated or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save(self):
        # 需在sql_functions中实现add_dashboard函数
        if self.dashboard_id is None:
            self.dashboard_id = sql_functions.add_dashboard(
                self.user_id, self.user_type, self.layout_settings, self.last_updated
            )
        return self.dashboard_id