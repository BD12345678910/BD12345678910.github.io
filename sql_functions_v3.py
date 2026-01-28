import sqlite3
from sqlite3 import Error
from datetime import datetime
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from logger import logger

class SQLManager:
    def __init__(self, db_file):
        if db_file is None:
            db_file = self.create_sqlite_tables()
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.STOP_WORDS = {
        '的','了','是','我','你','他','她','它','们','在','有','就','都','而','及','与','也','之','于','和','或','吗','呢','啊','吧','呀','哦','嗯','哈','哎','喂',
        '这','那','此','彼','个','只','本','该','每','各','何','孰','安','焉','乃','则','因','为','所以','如果','那么','但是','不过','而且','于是','因此','然后',
        '怎么','什么','为何','为什么','怎么样','如何','哪里','哪儿','多少','几','是否','能否','可以','应该','需要','要','会','能','让','把','被','给','对','向',
        '上','下','左','右','前','后','里','外','中','间','内','外','旁','又','还','再','才','刚','已','曾','将','过','着','得','地','所','者','矣','乎','哉',
        'a','an','the','and','or','but','not','no','yes','is','are','was','were','be','been','am','do','does','did','have','has','had','will','would','shall','should',
        'can','could','may','might','must','need','want','like','go','get','make','take','give','use','in','on','at','to','for','of','by','with','about','from','into',
        'up','down','left','right','front','back','here','there','this','that','these','those','it','he','she','we','us','you','me','him','her','they','them','my','your',
        'his','her','our','their','i','what','why','how','when','where','which','who','whom','whose','all','any','some','many','much','few','little','more','most','less'
    }
        
       

    def create_sqlite_tables(self):
        """创建SQLite数据库并初始化表结构（包含新增表）"""
        db_file = "schoolv3.db"
        conn = sqlite3.connect(db_file)
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
                className TEXT NOT NULL,
                teacherId INTEGER,
                subject TEXT,
                room TEXT,
                term TEXT,
                grade TEXT,
                type TEXT,
                FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId)
            );
            """
            # type: (optional, compulsory, M1, M2, M3 ... IB, AP, Alevel,etc)
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
                visible_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                pinned BOOLEAN DEFAULT 0,
                visible BOOLEAN DEFAULT 1,
                publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visible_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            create_my_submission_table = """
            CREATE TABLE IF NOT EXISTS Submission (
                -- 1. 提交唯一标识，主键自增（和MyGrades表命名风格一致）
                submissionId INTEGER PRIMARY KEY AUTOINCREMENT,
                -- 2. 提交时间，默认取当前时间戳（和MyGrades的graded_time保持一致）
                submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- 3. 上传文件绝对路径，文本类型（允许NULL，若有学生未上传文件仅提交文字）
                submission_file TEXT,
                -- 4. 学生ID，非空，外键关联student_info表的stuId（级联删除）
                student_id INTEGER NOT NULL,
                -- 5. 班级ID，非空，外键关联class_info表的classId（级联删除，假设class_info主键为classId）
                class_id INTEGER NOT NULL,
                -- 6. 是否迟交，布尔类型（SQLite中BOOLEAN是INTEGER别名，0=否，1=是），默认值FALSE（0）
                is_late BOOLEAN DEFAULT 0,
                -- 7. 作业ID，非空，外键关联Assignment表的assignmentId（级联删除）
                assignment_id INTEGER NOT NULL,
                -- 8. 该作业的提交尝试次数，非空，默认值1（第一次提交）
                attempt INTEGER NOT NULL DEFAULT 1,
                
                -- 外键约束配置（和MyGrades表外键行为一致，ON DELETE CASCADE表示主表记录删除时，子表关联记录也删除）
                FOREIGN KEY (student_id) REFERENCES Student_info(stuId) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES class_info(classId) ON DELETE CASCADE,
                FOREIGN KEY (assignment_id) REFERENCES Assignment(assignmentId) ON DELETE CASCADE,
                
                -- 额外合理约束，保证数据完整性
                CHECK(attempt >= 1),  -- 提交次数至少为1，不允许0或负数
                CHECK(is_late IN (0, 1)),  -- 确保is_late只能是0（不迟交）或1（迟交）
                UNIQUE(student_id, assignment_id, attempt)  -- 确保同一学生、同一作业、同一提交次数不重复
            );
            """
            # 执行创建表语句
            cursor.execute(create_my_submission_table)
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
                visible_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                class_id INTEGER,
                teacher_id INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES Class_info(classId) ON DELETE SET NULL,
                FOREIGN KEY (teacher_id) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
            );
            """
            cursor.execute(create_material_table)

            create_unified_auth_table = """
            CREATE TABLE IF NOT EXISTS UserAuthSettings (
                -- 核心主键：统一的用户ID
                user_id INTEGER PRIMARY KEY,          
                -- 通用基础信息
                user_name TEXT NOT NULL,              
                gender TEXT,                          
                grade_dept TEXT,                      
                -- 用户类型：明确区分学生/教师（核心区分字段）
                user_type TEXT NOT NULL CHECK(user_type IN ('student', 'teacher')), 
                -- 账号状态：沿用原表约束
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')), 
                -- 认证核心信息
                password_hash TEXT NOT NULL,          
                email TEXT,                           
                email_verification_token TEXT UNIQUE, 
                email_verified INTEGER DEFAULT 0 CHECK(email_verified IN (0, 1)), 
                -- 偏好设置
                preference_language TEXT,
                preference_size INT,
                preference_timezone TEXT,            
                -- 时间戳
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                -- 学生专属字段：仅学生用户非空，且保持唯一性
                stuId INTEGER UNIQUE,        
                -- 教师专属字段：仅教师用户非空，且保持唯一性
                teacherId INTEGER UNIQUE,
                -- 关键约束：保证数据一致性
                -- 1. 学生必须有stuId，且无teacherId；教师必须有teacherId，且无stuId
                CHECK (
                    (user_type = 'student' AND stuId IS NOT NULL AND teacherId IS NULL) 
                    OR 
                    (user_type = 'teacher' AND teacherId IS NOT NULL AND stuId IS NULL)
                ),
                -- 外键约束：沿用原表的关联关系
                FOREIGN KEY (stuId) REFERENCES Student_info(stuId) ON DELETE CASCADE,
                FOREIGN KEY (teacherId) REFERENCES teacher_info(teacherId) ON DELETE CASCADE
            );
            """

            # 执行建表语句
            cursor.execute(create_unified_auth_table)   
            conn.commit()
            logger.info("表初始化成功！")
        except Error as e:
            logger.error(f"建表出错: {e}")
        return str(db_file)

    def add_student(self,stu_name, stu_gnum=None, stu_age=None, stu_nationality=None,
                    stu_email=None, stu_phone=None, stu_gender=None, stu_grade=None,
                    stu_class=None, graduation_year=None, stu_course=None):
        # 函数实现不变...
        conn = self.conn
        try:
            if not stu_name:
                logger.error("错误：学生姓名不能为空！")
                return None
            if stu_age is not None and stu_age <= 0:
                logger.error("错误：学生年龄必须大于0！")
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
            logger.info(f"学生【{stu_name}】录入成功，stuId: {stu_id}")
            return stu_id
        except Error as e:
            if "UNIQUE constraint failed" in str(e):
                logger.error(f"错误：学生G号【{stu_gnum}】已存在！")
            else:
                logger.error(f"录入学生失败: {e}")
            return None

    # 新增函数
    def add_calendar(self, title, start_time, end_time, created_by, created_by_type, description=None, class_id=None):
        """添加日历事件"""
        try:
            if not title or not start_time or not end_time:
                logger.error("错误：标题、开始时间和结束时间不能为空！")
                return None
            if created_by_type not in ('student', 'teacher'):
                logger.error("错误：创建者类型必须是'student'或'teacher'")
                return None

            # 验证创建者存在
            cursor = self.conn.cursor()
            if created_by_type == 'student':
                cursor.execute("SELECT 1 FROM Student_info WHERE stuId = ?", (created_by,))
            else:
                cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (created_by,))
            if not cursor.fetchone():
                logger.error(f"错误：{created_by_type} ID【{created_by}】不存在！")
                return None

            sql = """INSERT INTO Calendar 
                    (title, description, start_time, end_time, class_id, created_by, created_by_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (title, description, start_time, end_time, class_id, created_by, created_by_type))
            self.conn.commit()
            calendar_id = cursor.lastrowid
            logger.info(f"日历事件【{title}】添加成功，calendarId: {calendar_id}")
            return calendar_id
        except Error as e:
            logger.error(f"添加日历失败: {e}")
            return None

    def add_assignment(self, title, due_time, class_id, teacher_id, description=None, total_points=None, type_=None):
        """添加作业"""
        try:
            if not title or not due_time:
                logger.error("错误：作业标题和截止时间不能为空！")
                return None

            # 验证外键存在
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM Class_info WHERE classId = ?", (class_id,))
            if not cursor.fetchone():
                logger.error(f"错误：班级ID【{class_id}】不存在！")
                return None
            
            cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
            if not cursor.fetchone():
                logger.error(f"错误：教师ID【{teacher_id}】不存在！")
                return None

            sql = """INSERT INTO Assignment 
                    (title, description, due_time, class_id, teacher_id, total_points, type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (title, description, due_time, class_id, teacher_id, total_points, type_))
            self.conn.commit()
            assignment_id = cursor.lastrowid
            logger.info(f"作业【{title}】添加成功，assignmentId: {assignment_id}")
            return assignment_id
        except Error as e:
            logger.error(f"添加作业失败: {e}")
            return None

    def add_announcement(self,title, content, teacher_id, class_id=None):
        """添加公告"""
        try:
            if not title or not content:
                logger.error("错误：公告标题和内容不能为空！")
                return None

            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM teacher_info WHERE teacherId = ?", (teacher_id,))
            if not cursor.fetchone():
                logger.error(f"错误：教师ID【{teacher_id}】不存在！")
                return None

            sql = """INSERT INTO Announcement 
                    (title, content, teacher_id, class_id)
                    VALUES (?, ?, ?, ?)"""
            cursor.execute(sql, (title, content, teacher_id, class_id))
            self.conn.commit()
            announcement_id = cursor.lastrowid
            logger.info(f"公告【{title}】发布成功，announcementId: {announcement_id}")
            return announcement_id
        except Error as e:
            logger.error(f"发布公告失败: {e}")
            return None

    def get_student_query_count(self,class_id=None):
        """
        按班级统计每个学生的Query提问数量
        :param class_id: 可选，指定班级ID(int)，不传则统计所有班级
        :return: {student_id: query_count} 整型键值对，无提问的学生count为0
        """
        query_count_dict = {}
        try:
            cursor = self.conn.cursor()
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
            logger.error(f"统计学生提问数量失败: {e}")
        return query_count_dict

    def get_student_prompts(self,class_id=None):
        """
        获取班级所有学生的Query提问文本，专为词云生成设计
        :param class_id: 可选，指定班级ID(int)，不传则获取所有班级
        :return: {student_id: [prompts_list]} 学生id对应其所有提问文本列表，无提问则为空列表
        """
        student_prompts_dict = {}
        try:
            cursor = self.conn.cursor()
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
            logger.error(f"获取学生提问文本失败: {e}")
        return student_prompts_dict

    def get_student_assignment_score(self,class_id=None):
        """
        按班级统计每个学生的作业成绩详情
        :param class_id: 可选，指定班级ID(int)，不传则统计所有班级
        :return: {student_id: {"total":总分, "avg":平均分, "complete":[所有作业分数列表]}}
        说明：total=所有有效分数求和；avg=保留2位小数的平均分；complete=所有非空作业分数的有序列表
        无成绩的学生：total=0, avg=0.00, complete=[]
        """
        student_score_dict = {}
        try:
            cursor = self.conn.cursor()
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
            logger.error(f"统计学生作业成绩失败: {e}")
        return student_score_dict
    def get_student_class(self,stu_id):
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
            cursor = self.conn.cursor()
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
            logger.error(f"查询学生班级失败: {e}")
        return class_ids
    def get_teacher_class(self,teacher_id):
        """根据教师ID获取授课的所有班级ID列表"""
        class_ids = []
        if isinstance(teacher_id, int) and teacher_id > 0:
            try:
                cursor = self.conn.cursor()
                sql = "SELECT DISTINCT classId FROM Class_info WHERE teacherId = ? ORDER BY classId ASC"
                cursor.execute(sql, (teacher_id,))
                class_ids = [row[0] for row in cursor.fetchall()]
            except Error as e:
                logger.error(f"查询教师班级失败: {e}")
        return class_ids

    def ID2Name(self, studentIds):
        names = []
        id_name = {}
        if isinstance(studentIds, list) and studentIds:
            valid_ids = [sid for sid in studentIds if isinstance(sid, int) and sid > 0]
            try:
                cursor = self.conn.cursor()
                placeholders = ','.join(['?']*len(valid_ids))
                cursor.execute(f"SELECT stuId, stuName FROM Student_info WHERE stuId IN ({placeholders})", valid_ids)
                for sid, name in cursor.fetchall():
                    id_name[sid] = name
            except Error as e:
                logger.error(f"查询学生姓名失败: {e}")
        # 严格按传入ID顺序返回，无匹配ID则为空字符串
        for sid in studentIds:
            names.append(id_name.get(sid, ''))
        return names

    def word_cloud(self,classid):
        if not isinstance(classid, int) or classid <= 0:
            logger.error("Class ID must be a positive integer!")
            return

        prompts = self.get_student_prompts(classid) # {id:[prompts]}
        all_text = " ".join([text.strip() for text in prompts.values()])
        keywords_with_weight = jieba.analyse.extract_tags(all_text, topK=50, withWeight=True, allowPOS=('n','vn','v','adj'))
        word_freq = {word: int(weight*1000) for word, weight in keywords_with_weight if word not in self.STOP_WORDS and len(word)>=1}
        wc = WordCloud(
            width=1000, height=600, background_color='white',
            max_words=50, relative_scaling=0.8,
            font_path='simhei.ttf' # Windows default, works for your env
        ).generate_from_frequencies(word_freq)
        wc.to_file(f"{classid}_word_cloud.png")
        logger.info(f"✅ {classid}_word_cloud.png saved!")

    def histograph(self,classid):
        if not isinstance(classid, int) or classid <= 0:
            logger.error("Class ID must be a positive integer!")
            return

        prompts = self.get_student_prompts(classid) # {id:[prompts]}
        all_text = " ".join([text.strip() for text in prompts.values()])
        words = [w for w in jieba.lcut(all_text) if w not in self.STOP_WORDS and len(w)>=1]
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
        logger.info(f"✅ {classid}_frequency_hist.png saved!")

    def login(self, user_type, user_id, password_hash):
        """
        用户登录验证
        :param user_type: 'student'或'teacher'
        :param user_name: 用户名
        :param password_hash: 密码哈希值
        :return: 成功返回用户ID(int)，失败返回None
        """
        if user_type not in ('student', 'teacher'):
            logger.error("错误：用户类型必须是'student'或'teacher'")
            return None
        
        table_name = "StudentAuthSettings" if user_type == 'student' else "TeacherAuthSettings"
        try:
            cursor = self.conn.cursor()
            sql = f"""SELECT user_name FROM {table_name} 
                      WHERE user_id = ? AND password_hash = ? AND status = 'active'"""
            cursor.execute(sql, (user_id, password_hash))
            result = cursor.fetchone()
            if result:
                return result[0]  # 返回用户ID
            else:
                logger.warning("登录失败：用户名或密码错误，或账户未激活")
                return None
        except Error as e:
            logger.error(f"登录验证失败: {e}")
            return None

    def add_query(self, stu_id, teacher_id, class_id, question, answer=None, time_=None):
        """
        录入学生的咨询/问题记录
        :param conn: 数据库连接对象
        :param stu_id: 学生ID
        :param teacher_id: 教师ID
        :param class_id: 班级ID
        :param question: 问题内容（必填）
        :param answer: 回答内容（可选）
        :param time_: 提问时间（默认当前时间，格式：YYYY-MM-DD HH:MM:SS）
        :return: 新增查询的queryId（成功）/None（失败）
        """
        try:
            if not question:
                print("错误：问题内容不能为空！")
                return None
            
            if time_ is None:
                time_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = self.conn.cursor()
            sql = """INSERT INTO query_info 
                    (stuId, teacherId, classId, question, answer, time)
                    VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (stu_id, teacher_id, class_id, question, answer, time_))
            self.conn.commit()
            query_id = cursor.lastrowid
            return query_id
        except Error as e:
            logger.error(f"录入咨询记录失败: {e}")
            return None
    def users_get_name(self,user_id):
        """根据用户ID获取用户名，支持学生和教师"""
        name = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_name FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                name = result[0]
        except Error as e:
            logger.error(f"查询用户姓名失败: {e}")
        return name
    def users_get_gender(self,user_id):
        """根据用户ID获取用户性别，支持学生和教师"""
        gender = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT gender FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                gender = result[0]
        except Error as e:
            logger.error(f"查询用户性别失败: {e}")
        return gender
    def users_get_status(self,user_id):
        """根据用户ID获取用户状态，支持学生和教师"""
        status = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT status FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                status = result[0]
        except Error as e:
            logger.error(f"查询用户状态失败: {e}")
        return status
    def users_set_status(self,user_id,new_status):
        """根据用户ID设置用户状态，支持学生和教师"""
        if new_status not in ('active', 'inactive'):
            logger.error("错误：状态必须是'active'或'inactive'")
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE UserAuthSettings SET status = ? WHERE user_id = ?", (new_status, user_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"用户ID【{user_id}】不存在，状态更新失败")
                return False
        except Error as e:
            logger.error(f"更新用户状态失败: {e}")
            return False
    def users_get_user_type(self, user_id):
        """根据用户ID获取用户类型，支持学生和教师"""
        type = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT user_type FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                type = result[0]
        except Error as e:
            logger.error(f"查询用户类型失败: {e}")
        return type
    def auth_passwords_get_pass_hash(self,user_id):
        """根据用户ID获取密码哈希值，支持学生和教师"""
        pass_hash = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                pass_hash = result[0]
        except Error as e:
            logger.error(f"查询密码哈希值失败: {e}")
        return pass_hash
    def auth_passwords_set_pass_hash(self,user_id,new_hash):
        """根据用户ID设置密码哈希值，支持学生和教师"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE UserAuthSettings SET password_hash = ? WHERE user_id = ?", (new_hash, user_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"用户ID【{user_id}】不存在，密码哈希值更新失败")
                return False
        except Error as e:
            logger.error(f"更新密码哈希值失败: {e}")
            return False
    def auth_passwords_check_pass_hash(self,user_id,pass_hash):
        """根据用户ID和密码哈希值检查密码是否正确，支持学生和教师"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result and result[0] == pass_hash:
                return True
        except Error as e:
            logger.error(f"检查密码哈希值失败: {e}")
        return False
    def user_preferences_get_language(self,user_id):
        """根据用户ID获取用户语言偏好，支持学生和教师"""
        language = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT preference_language FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                language = result[0]
        except Error as e:
            logger.error(f"查询用户语言偏好失败: {e}")
        return language
    def user_preferences_set_language(self,user_id,new_language):
        """根据用户ID设置用户语言偏好，支持学生和教师"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE UserAuthSettings SET preference_language = ? WHERE user_id = ?", (new_language, user_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"用户ID【{user_id}】不存在，语言偏好更新失败")
                return False
        except Error as e:
            logger.error(f"更新用户语言偏好失败: {e}")
            return False
    def user_preferences_get_timezone(self,user_id):
        """根据用户ID获取用户时区偏好，支持学生和教师"""
        timezone = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT preference_timezone FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                timezone = result[0]
        except Error as e:
            logger.error(f"查询用户时区偏好失败: {e}")
        return timezone
    def user_preferences_set_timezone(self,user_id,new_timezone):
        """根据用户ID设置用户时区偏好，支持学生和教师"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE UserAuthSettings SET preference_timezone = ? WHERE user_id = ?", (new_timezone, user_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"用户ID【{user_id}】不存在，时区偏好更新失败")
                return False
        except Error as e:
            logger.error(f"更新用户时区偏好失败: {e}")
            return False
    def user_preferences_get_font_size(self,user_id):
        """根据用户ID获取用户界面大小偏好，支持学生和教师"""
        size = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT preference_size FROM UserAuthSettings WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                size = result[0]
        except Error as e:
            logger.error(f"查询用户界面大小偏好失败: {e}")
        return size
    def user_preferences_set_font_size(self,user_id,new_size):
        """根据用户ID设置用户界面大小偏好，支持学生和教师"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE UserAuthSettings SET preference_size = ? WHERE user_id = ?", (new_size, user_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"用户ID【{user_id}】不存在，界面大小偏好更新失败")
                return False
        except Error as e:
            logger.error(f"更新用户界面大小偏好失败: {e}")
            return False
    def courses_get_name(self, course_id):
        """根据课程ID获取课程名称"""
        name = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT className FROM Class_info WHERE classId = ?", (course_id,))
            result = cursor.fetchone()
            if result:
                name = result[0]
        except Error as e:
            logger.error(f"查询课程名称失败: {e}")
        return name
    def courses_set_name(self, course_id, new_name):
        """根据课程ID设置课程名称"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Class_info SET className = ? WHERE classId = ?", (new_name, course_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"课程ID【{course_id}】不存在，课程名称更新失败")
                return False
        except Error as e:
            logger.error(f"更新课程名称失败: {e}")
            return False
    def courses_get_term(self,course_id):
        """根据课程ID获取课程学期"""
        term = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT term FROM Class_info WHERE classId = ?", (course_id,))
            result = cursor.fetchone()
            if result:
                term = result[0]
        except Error as e:
            logger.error(f"查询学期名称失败: {e}")
        return term
    def courses_set_term(self,course_id,new_term):
        """根据课程ID设置课程学期"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Class_info SET term = ? WHERE classId = ?", (new_term, course_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"课程ID【{course_id}】不存在，学期更新失败")
                return False
        except Error as e:
            logger.error(f"更新学期失败: {e}")
            return False
    def courses_get_teacher(self,course_id):
        """根据课程ID获取授课教师ID"""
        teacher_id = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT teacherId FROM Class_info WHERE classId = ?", (course_id,))
            result = cursor.fetchone()
            if result:
                teacher_id = result[0]
        except Error as e:
            logger.error(f"查询授课教师ID失败: {e}")
        return teacher_id
    def courses_set_teacher(self,course_id,new_teacher_id):
        """根据课程ID设置授课教师ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Class_info SET teacherId = ? WHERE classId = ?", (new_teacher_id, course_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"课程ID【{course_id}】不存在，授课教师ID更新失败")
                return False
        except Error as e:
            logger.error(f"更新授课教师ID失败: {e}")
            return False
    def courses_get_students(self,course_id):
        """根据课程ID获取所有选课学生ID列表"""
        student_ids = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT student_id FROM student_class_junction WHERE class_id = ?", (course_id,))
            student_ids = [row[0] for row in cursor.fetchall()]
        except Error as e:
            logger.error(f"查询选课学生ID失败: {e}")
        return student_ids
    def courses_add_student(self,course_id,student_id):
        """根据课程ID添加选课学生ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO student_class_junction (student_id, class_id) VALUES (?, ?)", (student_id, course_id))
            self.conn.commit()
            logger.info(f"学生ID【{student_id}】成功添加到课程ID【{course_id}】")
            return True
        except Error as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"学生ID【{student_id}】已选修课程ID【{course_id}】，无需重复添加")
            else:
                logger.error(f"添加选课学生ID失败: {e}")
            return False
    def courses_remove_student(self,course_id,student_id):
        """根据课程ID移除选课学生ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM student_class_junction WHERE student_id = ? AND class_id = ?", (student_id, course_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"学生ID【{student_id}】成功从课程ID【{course_id}】移除")
                return True
            else:
                logger.warning(f"学生ID【{student_id}】未选修课程ID【{course_id}】，移除失败")
                return False
        except Error as e:
            logger.error(f"移除选课学生ID失败: {e}")
            return False
    def assignments_get_title(self,assignment_id):
        """根据作业ID获取作业标题"""
        title = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT title FROM Assignment WHERE assignmentId = ?", (assignment_id,))
            result = cursor.fetchone()
            if result:
                title = result[0]
        except Error as e:
            logger.error(f"查询作业标题失败: {e}")
        return title
    def assignments_set_title(self,assignment_id,new_title):
        """根据作业ID设置作业标题"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Assignment SET title = ? WHERE assignmentId = ?", (new_title, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"作业ID【{assignment_id}】不存在，作业标题更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业标题失败: {e}")
            return False
    def assignments_get_due_at(self,assignment_id):
        """根据作业ID获取作业截止时间"""
        due_time = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT due_time FROM Assignment WHERE assignmentId = ?", (assignment_id,))
            result = cursor.fetchone()
            if result:
                due_time = result[0]
        except Error as e:
            logger.error(f"查询作业截止时间失败: {e}")
        return due_time
    def assignments_set_due_at(self,assignment_id,new_due_time):
        """根据作业ID设置作业截止时间"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Assignment SET due_time = ? WHERE assignmentId = ?", (new_due_time, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"作业ID【{assignment_id}】不存在，作业截止时间更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业截止时间失败: {e}")
            return False
    def assignments_get_publish_at(self,assignment_id):
        """根据作业ID获取作业发布时间"""
        publish_time = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT publish_time FROM Assignment WHERE assignmentId = ?", (assignment_id,))
            result = cursor.fetchone()
            if result:
                publish_time = result[0]
        except Error as e:
            logger.error(f"查询作业发布时间失败: {e}")
        return publish_time
    def assignments_set_publish_at(self,assignment_id,new_publish_time):
        """根据作业ID设置作业发布时间"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Assignment SET publish_time = ? WHERE assignmentId = ?", (new_publish_time, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"作业ID【{assignment_id}】不存在，作业发布时间更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业发布时间失败: {e}")
            return False
    def assignments_get_max_points(self,assignment_id):
        """根据作业ID获取作业总分"""
        total_points = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT total_points FROM Assignment WHERE assignmentId = ?", (assignment_id,))
            result = cursor.fetchone()
            if result:
                total_points = result[0]
        except Error as e:
            logger.error(f"查询作业总分失败: {e}")
        return total_points
    def assignments_set_max_points(self,assignment_id,new_total_points):
        """根据作业ID设置作业总分"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Assignment SET total_points = ? WHERE assignmentId = ?", (new_total_points, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"作业ID【{assignment_id}】不存在，作业总分更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业总分失败: {e}")
            return False
    def assignments_get_description(self,assignment_id):
        """根据作业ID获取作业描述"""
        description = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT description FROM Assignment WHERE assignmentId = ?", (assignment_id,))
            result = cursor.fetchone()
            if result:
                description = result[0]
        except Error as e:
            logger.error(f"查询作业描述失败: {e}")
        return description
    def assignments_set_description(self,assignment_id,new_description):
        """根据作业ID设置作业描述"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Assignment SET description = ? WHERE assignmentId = ?", (new_description, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"作业ID【{assignment_id}】不存在，作业描述更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业描述失败: {e}")
            return False
    def assignment_grades_get_score(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取作业分数"""
        score = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT score FROM MyGrades WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                score = result[0]
        except Error as e:
            logger.error(f"查询作业分数失败: {e}")
        return score
    def assignment_grades_set_score(self,stu_id,assignment_id,new_score):
        """根据学生ID和作业ID设置作业分数"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE MyGrades SET score = ? WHERE stu_id = ? AND assignment_id = ?", (new_score, stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的成绩记录不存在，分数更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业分数失败: {e}")
            return False
    def assignment_grades_get_feedback(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取作业反馈"""
        feedback = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT comment FROM MyGrades WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                feedback = result[0]
        except Error as e:
            logger.error(f"查询作业反馈失败: {e}")
        return feedback
    def assignment_grades_set_feedback(self,stu_id,assignment_id,new_feedback):
        """根据学生ID和作业ID设置作业反馈"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE MyGrades SET comment = ? WHERE stu_id = ? AND assignment_id = ?", (new_feedback, stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的成绩记录不存在，反馈更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业反馈失败: {e}")
            return False
    def assignment_grades_get_graded_at(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取作业评分时间"""
        graded_time = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT graded_time FROM MyGrades WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                graded_time = result[0]
        except Error as e:
            logger.error(f"查询作业评分时间失败: {e}")
        return graded_time
    def assignment_grades_set_graded_at(self,stu_id,assignment_id,new_graded_time):
        """根据学生ID和作业ID设置作业评分时间"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE MyGrades SET graded_time = ? WHERE stu_id = ? AND assignment_id = ?", (new_graded_time, stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的成绩记录不存在，评分时间更新失败")
                return False
        except Error as e:
            logger.error(f"更新作业评分时间失败: {e}")
            return False
    def announcements_get_title(self,announcement_id):
        """根据公告ID获取公告标题"""
        title = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT title FROM Announcements WHERE announcementId = ?", (announcement_id,))
            result = cursor.fetchone()
            if result:
                title = result[0]
        except Error as e:
            logger.error(f"查询公告标题失败: {e}")
        return title
    def announcements_set_title(self,announcement_id,new_title):
        """根据公告ID设置公告标题"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Announcements SET title = ? WHERE announcementId = ?", (new_title, announcement_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"公告ID【{announcement_id}】不存在，公告标题更新失败")
                return False
        except Error as e:
            logger.error(f"更新公告标题失败: {e}")
            return False
    def announcements_get_body(self,announcement_id):
        """根据公告ID获取公告内容"""
        content = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT content FROM Announcements WHERE announcementId = ?", (announcement_id,))
            result = cursor.fetchone()
            if result:
                content = result[0]
        except Error as e:
            logger.error(f"查询公告内容失败: {e}")
        return content
    def announcements_set_body(self,announcement_id,new_content):
        """根据公告ID设置公告内容"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Announcements SET content = ? WHERE announcementId = ?", (new_content, announcement_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"公告ID【{announcement_id}】不存在，公告内容更新失败")
                return False
        except Error as e:
            logger.error(f"更新公告内容失败: {e}")
            return False
    def announcement_get_published_at(self,announcement_id):
        """根据公告ID获取公告发布时间"""
        post_time = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT publish_time FROM Announcements WHERE announcementId = ?", (announcement_id,))
            result = cursor.fetchone()
            if result:
                post_time = result[0]
        except Error as e:
            logger.error(f"查询公告发布时间失败: {e}")
        return post_time
    def announcement_set_published_at(self,announcement_id,new_publish_time):
        """根据公告ID设置公告发布时间"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Announcements SET publish_time = ? WHERE announcementId = ?", (new_publish_time, announcement_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"公告ID【{announcement_id}】不存在，公告发布时间更新失败")
                return False
        except Error as e:
            logger.error(f"更新公告发布时间失败: {e}")
            return False
    def announcement_get_pinned(self, announcement_id):
        """根据公告ID获取公告置顶状态"""
        pinned = False
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT pinned FROM Announcements WHERE announcementId = ?", (announcement_id,))
            result = cursor.fetchone()
            if result:
                pinned = bool(result[0])
        except Error as e:
            logger.error(f"查询公告置顶状态失败: {e}")
        return pinned
    def announcement_set_pinned(self, announcement_id, is_pinned):
        """根据公告ID设置公告置顶状态"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Announcements SET pinned = ? WHERE announcementId = ?", (int(is_pinned), announcement_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"公告ID【{announcement_id}】不存在，公告置顶状态更新失败")
                return False
        except Error as e:
            logger.error(f"更新公告置顶状态失败: {e}")
            return False
    def announcement_get_visibility(self, announcement_id):
        """根据公告ID获取公告可见性"""
        visibility = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT visible FROM Announcements WHERE announcementId = ?", (announcement_id,))
            result = cursor.fetchone()
            if result:
                visibility = result[0]
        except Error as e:
            logger.error(f"查询公告可见性失败: {e}")
        return visibility
    def announcement_set_visibility(self, announcement_id, new_visibility):
        """根据公告ID设置公告可见性"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Announcements SET visible = ? WHERE announcementId = ?", (new_visibility, announcement_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"公告ID【{announcement_id}】不存在，公告可见性更新失败")
                return False
        except Error as e:
            logger.error(f"更新公告可见性失败: {e}")
            return False
    def submissions_get_submitted_at(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取提交时间"""
        submit_time = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT submit_time FROM Submissions WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                submit_time = result[0]
        except Error as e:
            logger.error(f"查询提交时间失败: {e}")
        return submit_time
    def submissions_set_submitted_at(self,stu_id,assignment_id,new_submit_time):
        """根据学生ID和作业ID设置提交时间"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Submissions SET submit_time = ? WHERE stu_id = ? AND assignment_id = ?", (new_submit_time, stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的提交记录不存在，提交时间更新失败")
                return False
        except Error as e:
            logger.error(f"更新提交时间失败: {e}")
            return False
    def submissions_get_path(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取提交文件路径"""
        path = ""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT submission_file FROM Submissions WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                path = result[0]
        except Error as e:
            logger.error(f"查询提交文件路径失败: {e}")
        return path
    def submissions_set_path(self,stu_id,assignment_id,new_path):
        """根据学生ID和作业ID设置提交文件路径"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Submissions SET submission_file = ? WHERE stu_id = ? AND assignment_id = ?", (new_path, stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的提交记录不存在，提交文件路径更新失败")
                return False
        except Error as e:
            logger.error(f"更新提交文件路径失败: {e}")
            return False
    def submissions_get_late(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取是否迟交状态"""
        late = False
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT is_late FROM Submissions WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                late = bool(result[0])
        except Error as e:
            logger.error(f"查询是否迟交状态失败: {e}")
        return late
    def submissions_set_late(self,stu_id,assignment_id,is_late):
        """根据学生ID和作业ID设置是否迟交状态"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Submissions SET is_late = ? WHERE stu_id = ? AND assignment_id = ?", (int(is_late), stu_id, assignment_id))
            self.conn.commit()
            if cursor.rowcount > 0:
                return True
            else:
                logger.warning(f"学生ID【{stu_id}】和作业ID【{assignment_id}】的提交记录不存在，是否迟交状态更新失败")
                return False
        except Error as e:
            logger.error(f"更新是否迟交状态失败: {e}")
            return False
    def submission_get_attempt(self,stu_id,assignment_id):
        """根据学生ID和作业ID获取提交尝试次数"""
        attempts = 0
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT attempt FROM Submissions WHERE stu_id = ? AND assignment_id = ?", (stu_id, assignment_id))
            result = cursor.fetchone()
            if result:
                attempts = result[0]
        except Error as e:
            logger.error(f"查询提交尝试次数失败: {e}")
        return attempts
    
SQL = SQLManager(None)  # 初始化数据库连接
SQL.create_sqlite_tables()  # 创建表结构