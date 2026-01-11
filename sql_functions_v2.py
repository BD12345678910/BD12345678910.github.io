import sqlite3
from sqlite3 import Error
from datetime import datetime

conn = sqlite3.connect("school.db")

def create_sqlite_tables(db_file):
    """创建SQLite数据库并初始化表结构（包含新增表）"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # 学生信息表
        create_student_table = """
        CREATE TABLE IF NOT EXISTS Student_info (
            stuId INTEGER PRIMARY KEY AUTOINCREMENT,
            stuName TEXT NOT NULL,
            stuGNum TEXT UNIQUE,
            stuAge INTEGER CHECK(stuAge > 0),
            stuNationality TEXT,
            stuEmail TEXT,
            stuPhone TEXT,
            stuGender TEXT,
            stuGrade TEXT,
            stuClass TEXT,
            graduation_year INTEGER,
            stuCourse TEXT
        );
        """
        cursor.execute(create_student_table)

        # 班级信息表
        create_class_table = """
        CREATE TABLE IF NOT EXISTS Class_info (
            classId INTEGER PRIMARY KEY AUTOINCREMENT,
            teacherId INTEGER,
            subject TEXT,
            room TEXT,
            grade TEXT,
            type TEXT,
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId)
        );
        """
        cursor.execute(create_class_table)

        # 教师信息表
        create_teacher_table = """
        CREATE TABLE IF NOT EXISTS teacher_info (
            teacherId INTEGER PRIMARY KEY AUTOINCREMENT,
            teacherName TEXT NOT NULL,
            teacherRoom TEXT,
            teacherSubject TEXT,
            teacherHomeroom TEXT
        );
        """
        cursor.execute(create_teacher_table)

        # 学生-班级关联表
        create_student_class_junction = """
        CREATE TABLE IF NOT EXISTS student_class_junction (
            student_id INTEGER,
            class_id INTEGER,
            PRIMARY KEY (student_id, class_id),
            FOREIGN KEY (student_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_student_class_junction)

        # 咨询信息表
        create_query_table = """
        CREATE TABLE IF NOT EXISTS query_info (
            queryId INTEGER PRIMARY KEY AUTOINCREMENT,
            stuId INTEGER,
            teacherId INTEGER,
            classId INTEGER,
            question TEXT NOT NULL,
            answer TEXT,
            time TIMESTAMP,
            FOREIGN KEY (stuId) REFERENCES Student_info(stuId),
            FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId),
            FOREIGN KEY (classId) REFERENCES Class_info(classId)
        );
        """
        cursor.execute(create_query_table)

        # 日历表
        create_calendar_table = """
        CREATE TABLE IF NOT EXISTS Calendar (
            calendarId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            class_id INTEGER,
            created_by INTEGER NOT NULL,
            created_by_type TEXT NOT NULL CHECK(created_by_type IN ('student', 'teacher')),
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (created_by) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_calendar_table)

        # 作业表
        create_assignment_table = """
        CREATE TABLE IF NOT EXISTS Assignment (
            assignmentId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_time TIMESTAMP NOT NULL,
            class_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            total_points REAL CHECK(total_points >= 0),
            type TEXT,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_assignment_table)

        # 公告表
        create_announcement_table = """
        CREATE TABLE IF NOT EXISTS Announcement (
            announcementId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL
        );
        """
        cursor.execute(create_announcement_table)

        # 讨论表
        create_discussion_table = """
        CREATE TABLE IF NOT EXISTS Discussion (
            discussionId INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            initiator_id INTEGER NOT NULL,
            initiator_type TEXT NOT NULL CHECK(initiator_type IN ('student', 'teacher')),
            class_id INTEGER,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parent_id INTEGER,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (parent_id) REFERENCES Discussion(discussionId) ON DELETE CASCADE,
            FOREIGN KEY (initiator_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (initiator_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_discussion_table)

        # 小组表
        create_group_class_table = """
        CREATE TABLE IF NOT EXISTS GroupClass (
            groupClassId INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            leader_stu_id INTEGER,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE CASCADE,
            FOREIGN KEY (leader_stu_id) REFERENCES Student_info(stuId) ON DELETE SET NULL
        );
        """
        cursor.execute(create_group_class_table)

        # 仪表盘表
        create_dashboard_table = """
        CREATE TABLE IF NOT EXISTS Dashboard (
            dashboardId INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('student', 'teacher')),
            layout_settings TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, user_type),
            FOREIGN KEY (user_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_dashboard_table)

        # 成绩表（修复CHECK约束：移除子查询，仅保留基础非负检查）
        create_my_grades_table = """
        CREATE TABLE IF NOT EXISTS MyGrades (
            gradeId INTEGER PRIMARY KEY AUTOINCREMENT,
            stu_id INTEGER NOT NULL,
            assignment_id INTEGER NOT NULL,
            score REAL,
            comment TEXT,
            graded_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stu_id, assignment_id),
            FOREIGN KEY (stu_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
            FOREIGN KEY (assignment_id) REFERENCES Assignment(assignmentId) ON DELETE CASCADE,
            CHECK(score IS NULL OR score >= 0)  -- 仅保留基础非负检查，子查询移到应用层
        );
        """
        cursor.execute(create_my_grades_table)

        # 教学材料表
        create_material_table = """
        CREATE TABLE IF NOT EXISTS Material (
            materialId INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            class_id INTEGER,
            teacher_id INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
            FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
        );
        """
        cursor.execute(create_material_table)

        conn.commit()
        print("表初始化成功！")
    except Error as e:
        print(f"建表出错: {e}")
    return conn

# 原有函数保持不变...
def add_student(stu_name, stu_gnum=None, stu_age=None, stu_nationality=None,
                stu_email=None, stu_phone=None, stu_gender=None, stu_grade=None,
                stu_class=None, graduation_year=None, stu_course=None):
    # 函数实现不变...
    try:
        if not stu_name:
            print("错误：学生姓名不能为空！")
            return None
        if stu_age is not None and stu_age <= 0:
            print("错误：学生年龄必须大于0！")
            return None

        cursor = conn.cursor()
        sql = """INSERT INTO Student_info 
                 (stuName, stuGNum, stuAge, stuNationality, stuEmail, stuPhone, 
                  stuGender, stuGrade, stuClass, graduation_year, stuCourse)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (stu_name, stu_gnum, stu_age, stu_nationality,
                            stu_email, stu_phone, stu_gender, stu_grade,
                            stu_class, graduation_year, stu_course))
        conn.commit()
        stu_id = cursor.lastrowid
        print(f"学生【{stu_name}】录入成功，stuId: {stu_id}")
        return stu_id
    except Error as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"错误：学生G号【{stu_gnum}】已存在！")
        else:
            print(f"录入学生失败: {e}")
        return None

# 新增函数
def add_calendar(title, start_time, end_time, created_by, created_by_type, description=None, class_id=None):
    """添加日历事件"""
    try:
        if not title or not start_time or not end_time:
            print("错误：标题、开始时间和结束时间不能为空！")
            return None
        if created_by_type not in ('student', 'teacher'):
            print("错误：创建者类型必须是'student'或'teacher'")
            return None

        # 验证创建者存在
        cursor = conn.cursor()
        if created_by_type == 'student':
            cursor.execute("SELECT 1 FROM Student_info WHERE stuId = ?", (created_by,))
        else:
            cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (created_by,))
        if not cursor.fetchone():
            print(f"错误：{created_by_type} ID【{created_by}】不存在！")
            return None

        sql = """INSERT INTO Calendar 
                 (title, description, start_time, end_time, class_id, created_by, created_by_type)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (title, description, start_time, end_time, class_id, created_by, created_by_type))
        conn.commit()
        calendar_id = cursor.lastrowid
        print(f"日历事件【{title}】添加成功，calendarId: {calendar_id}")
        return calendar_id
    except Error as e:
        print(f"添加日历失败: {e}")
        return None

def add_assignment(title, due_time, class_id, teacher_id, description=None, total_points=None, type_=None):
    """添加作业"""
    try:
        if not title or not due_time:
            print("错误：作业标题和截止时间不能为空！")
            return None

        # 验证外键存在
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Class_info WHERE classId = ?", (class_id,))
        if not cursor.fetchone():
            print(f"错误：班级ID【{class_id}】不存在！")
            return None
        
        cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
        if not cursor.fetchone():
            print(f"错误：教师ID【{teacher_id}】不存在！")
            return None

        sql = """INSERT INTO Assignment 
                 (title, description, due_time, class_id, teacher_id, total_points, type)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (title, description, due_time, class_id, teacher_id, total_points, type_))
        conn.commit()
        assignment_id = cursor.lastrowid
        print(f"作业【{title}】添加成功，assignmentId: {assignment_id}")
        return assignment_id
    except Error as e:
        print(f"添加作业失败: {e}")
        return None

def add_announcement(title, content, teacher_id, class_id=None):
    """添加公告"""
    try:
        if not title or not content:
            print("错误：公告标题和内容不能为空！")
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
        if not cursor.fetchone():
            print(f"错误：教师ID【{teacher_id}】不存在！")
            return None

        sql = """INSERT INTO Announcement 
                 (title, content, teacher_id, class_id)
                 VALUES (?, ?, ?, ?)"""
        cursor.execute(sql, (title, content, teacher_id, class_id))
        conn.commit()
        announcement_id = cursor.lastrowid
        print(f"公告【{title}】发布成功，announcementId: {announcement_id}")
        return announcement_id
    except Error as e:
        print(f"发布公告失败: {e}")
        return None

def get_student_query_count(class_id=None):
    """
    按班级统计每个学生的Query提问数量
    :param class_id: 可选，指定班级ID(int)，不传则统计所有班级
    :return: {student_id: query_count} 整型键值对，无提问的学生count为0
    """
    query_count_dict = {}
    try:
        conn = sqlite3.connect("schoolv2.db")
        cursor = conn.cursor()
        # 关联班级-学生-提问表，LEFT JOIN保证无提问的学生也会被统计(数量0)
        sql = """
            SELECT si.stuId, COUNT(qi.queryId) AS query_count
            FROM Student_info si
            JOIN student_class_junction scj ON si.stuId = scj.student_id
            LEFT JOIN query_info qi ON si.stuId = qi.stuId
        """
        # 筛选指定班级
        if class_id and isinstance(class_id, int):
            sql += f" WHERE scj.class_id = {class_id}"
        sql += " GROUP BY si.stuId ORDER BY si.stuId"
        
        cursor.execute(sql)
        # 直接转成 指定格式 {student_id: query_count}
        for row in cursor.fetchall():
            student_id = row[0]
            count = row[1]
            query_count_dict[student_id] = count
    except Error as e:
        print(f"统计学生提问数量失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return query_count_dict

def get_student_prompts(class_id=None):
    """
    获取班级所有学生的Query提问文本，专为词云生成设计
    :param class_id: 可选，指定班级ID(int)，不传则获取所有班级
    :return: {student_id: [prompts_list]} 学生id对应其所有提问文本列表，无提问则为空列表
    """
    student_prompts_dict = {}
    try:
        conn = sqlite3.connect("schoolv2.db")
        cursor = conn.cursor()
        # 先获取该班级所有学生ID，初始化空列表，保证无提问的学生也在字典内
        init_sql = """SELECT DISTINCT si.stuId FROM Student_info si
                      JOIN student_class_junction scj ON si.stuId = scj.student_id"""
        if class_id and isinstance(class_id, int):
            init_sql += f" WHERE scj.class_id = {class_id}"
        cursor.execute(init_sql)
        for stu_id in [row[0] for row in cursor.fetchall()]:
            student_prompts_dict[stu_id] = []

        # 查询学生的提问文本
        sql = """SELECT si.stuId, qi.question FROM Student_info si
                 JOIN query_info qi ON si.stuId = qi.stuId
                 JOIN student_class_junction scj ON si.stuId = scj.student_id"""
        if class_id and isinstance(class_id, int):
            sql += f" WHERE scj.class_id = {class_id}"
        sql += " WHERE qi.question IS NOT NULL AND qi.question != ''"
        
        cursor.execute(sql)
        # 清洗文本+填充列表，去首尾空格，过滤空文本
        for row in cursor.fetchall():
            student_id = row[0]
            prompt = row[1].strip() if row[1] else ""
            if prompt:
                student_prompts_dict[student_id].append(prompt)
    except Error as e:
        print(f"获取学生提问文本失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return student_prompts_dict

def get_student_assignment_score(class_id=None):
    """
    按班级统计每个学生的作业成绩详情
    :param class_id: 可选，指定班级ID(int)，不传则统计所有班级
    :return: {student_id: {"total":总分, "avg":平均分, "complete":[所有作业分数列表]}}
    说明：total=所有有效分数求和；avg=保留2位小数的平均分；complete=所有非空作业分数的有序列表
    无成绩的学生：total=0, avg=0.00, complete=[]
    """
    student_score_dict = {}
    try:
        conn = sqlite3.connect("schoolv2.db")
        cursor = conn.cursor()
        # 先获取该班级所有学生ID，初始化嵌套字典，保证无成绩的学生也在字典内
        init_sql = """SELECT DISTINCT si.stuId FROM Student_info si
                      JOIN student_class_junction scj ON si.stuId = scj.student_id"""
        if class_id and isinstance(class_id, int):
            init_sql += f" WHERE scj.class_id = {class_id}"
        cursor.execute(init_sql)
        for stu_id in [row[0] for row in cursor.fetchall()]:
            student_score_dict[stu_id] = {"total": 0.0, "avg": 0.00, "complete": []}

        # 查询学生的所有有效作业分数
        sql = """SELECT mg.stu_id, mg.score FROM MyGrades mg
                 JOIN student_class_junction scj ON mg.stu_id = scj.student_id
                 WHERE mg.score IS NOT NULL AND mg.score >= 0"""
        if class_id and isinstance(class_id, int):
            sql += f" AND scj.class_id = {class_id}"
        
        cursor.execute(sql)
        # 填充每个学生的分数列表
        for row in cursor.fetchall():
            student_id = row[0]
            score = round(float(row[1]), 2)  # 单分数保留2位小数
            student_score_dict[student_id]["complete"].append(score)

        # 遍历计算总分+平均分
        for stu_id, score_info in student_score_dict.items():
            score_list = score_info["complete"]
            if score_list:
                total_score = round(sum(score_list), 2)  # 总分保留2位小数
                avg_score = round(total_score / len(score_list), 2)  # 平均分保留2位小数
                student_score_dict[stu_id]["total"] = total_score
                student_score_dict[stu_id]["avg"] = avg_score
    except Error as e:
        print(f"统计学生作业成绩失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return student_score_dict
def get_student_class(stu_id):
    """
    根据学生ID查询该学生所就读的所有班级ID
    :param stu_id: 必传，学生ID (整型)
    :return: [class_id1, class_id2, ...] 纯整型班级ID列表，无班级则返回空列表，参数非法也返回空列表
    """
    class_ids = []
    # 严格参数校验：必须是正整数
    if not isinstance(stu_id, int) or stu_id <= 0:
        return class_ids
    
    try:
        conn = sqlite3.connect("schoolv2.db")
        cursor = conn.cursor()
        # 核心SQL：通过学生班级关联表，精准查询学生所属班级，去重+排序保证无重复数据
        sql = """
            SELECT DISTINCT scj.class_id 
            FROM student_class_junction scj
            WHERE scj.student_id = ?
            ORDER BY scj.class_id ASC
        """
        cursor.execute(sql, (stu_id,))
        # 提取纯班级ID列表，返回格式严格为 [数字,数字...]
        class_ids = [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"查询学生班级失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return class_ids
def get_teacher_class(teacher_id):
    """根据教师ID获取授课的所有班级ID列表"""
    class_ids = []
    if isinstance(teacher_id, int) and teacher_id > 0:
        try:
            conn = sqlite3.connect("schoolv2.db")
            cursor = conn.cursor()
            sql = "SELECT DISTINCT classId FROM Class_info WHERE teacherId = ? ORDER BY classId ASC"
            cursor.execute(sql, (teacher_id,))
            class_ids = [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"查询教师班级失败: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    return class_ids

def ID2Name(studentIds):
    names = []
    id_name = {}
    if isinstance(studentIds, list) and studentIds:
        valid_ids = [sid for sid in studentIds if isinstance(sid, int) and sid > 0]
        try:
            conn = sqlite3.connect("schoolv2.db")
            cursor = conn.cursor()
            placeholders = ','.join(['?']*len(valid_ids))
            cursor.execute(f"SELECT stuId, stuName FROM Student_info WHERE stuId IN ({placeholders})", valid_ids)
            for sid, name in cursor.fetchall():
                id_name[sid] = name
        except Error as e:
            print(f"查询学生姓名失败: {e}")
        finally:
            if 'conn' in locals(): conn.close()
    # 严格按传入ID顺序返回，无匹配ID则为空字符串
    for sid in studentIds:
        names.append(id_name.get(sid, ''))
    return names

import jieba
import jieba.analyse
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
STOP_WORDS = {
    '的','了','是','我','你','他','她','它','们','在','有','就','都','而','及','与','也','之','于','和','或','吗','呢','啊','吧','呀','哦','嗯','哈','哎','喂',
    '这','那','此','彼','个','只','本','该','每','各','何','孰','安','焉','乃','则','因','为','所以','如果','那么','但是','不过','而且','于是','因此','然后',
    '怎么','什么','为何','为什么','怎么样','如何','哪里','哪儿','多少','几','是否','能否','可以','应该','需要','要','会','能','让','把','被','给','对','向',
    '上','下','左','右','前','后','里','外','中','间','内','外','旁','又','还','再','才','刚','已','曾','将','过','着','得','地','所','者','矣','乎','哉',
    'a','an','the','and','or','but','not','no','yes','is','are','was','were','be','been','am','do','does','did','have','has','had','will','would','shall','should',
    'can','could','may','might','must','need','want','like','go','get','make','take','give','use','in','on','at','to','for','of','by','with','about','from','into',
    'up','down','left','right','front','back','here','there','this','that','these','those','it','he','she','we','us','you','me','him','her','they','them','my','your',
    'his','her','our','their','i','what','why','how','when','where','which','who','whom','whose','all','any','some','many','much','few','little','more','most','less'
}
def word_cloud(classid):
    if not isinstance(classid, int) or classid <= 0:
        print("Class ID must be a positive integer!")
        return

    prompts = get_student_prompts(classid) # {id:[prompts]}
    all_text = " ".join([text.strip() for text in prompts.values()])
    keywords_with_weight = jieba.analyse.extract_tags(all_text, topK=50, withWeight=True, allowPOS=('n','vn','v','adj'))
    word_freq = {word: int(weight*1000) for word, weight in keywords_with_weight if word not in STOP_WORDS and len(word)>=1}
    wc = WordCloud(
        width=1000, height=600, background_color='white',
        max_words=50, relative_scaling=0.8,
        font_path='simhei.ttf' # Windows default, works for your env
    ).generate_from_frequencies(word_freq)
    wc.to_file(f"{classid}_word_cloud.png")
    print(f"✅ {classid}_word_cloud.png saved!")

def histograph(classid):
    if not isinstance(classid, int) or classid <= 0:
        print("Class ID must be a positive integer!")
        return

    prompts = get_student_prompts(classid) # {id:[prompts]}
    all_text = " ".join([text.strip() for text in prompts.values()])
    words = [w for w in jieba.lcut(all_text) if w not in STOP_WORDS and len(w)>=1]
    word_freq = Counter(words).most_common(20)
    words_list = [w[0] for w in word_freq]
    freq_list = [w[1] for w in word_freq]

    # Fix Chinese display
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(12, 6))
    plt.bar(words_list, freq_list, color='#2196F3', alpha=0.8)
    plt.title(f'Class {classid} - Query Keyword Frequency Statistics', fontsize=14, pad=20)
    plt.xlabel('Keywords', fontsize=12)
    plt.ylabel('Frequency (Count)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{classid}_frequency_hist.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ {classid}_frequency_hist.png saved!")

create_sqlite_tables('schoolv2.db')