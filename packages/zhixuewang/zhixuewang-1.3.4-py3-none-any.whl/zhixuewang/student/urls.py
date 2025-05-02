from zhixuewang.urls import BASE_URL


class Url:
    INFO_URL = f"{BASE_URL}/container/container/student/account/"

    # Login
    SERVICE_URL = f"{BASE_URL}:443/ssoservice.jsp"
    SSO_URL = f"https://open.changyan.com/sso/login?sso_from=zhixuesso&service={SERVICE_URL}"

    CHANGE_PASSWORD_URL = f"{BASE_URL}/portalcenter/home/updatePassword/"
    TEST_PASSWORD_URL = f"{BASE_URL}/weakPwdLogin/?from=web_login"

    TEST_URL = f"{BASE_URL}/container/container/teacher/teacherAccountNew"

    # Exam
    XTOKEN_URL = f"{BASE_URL}/container/app/token/getToken"
    GET_EXAM_URL = f"{BASE_URL}/zhixuebao/report/exam/getUserExamList"
    GET_RECENT_EXAM_URL = f"{BASE_URL}/zhixuebao/report/exam/getRecentExam"
    # GET_MARK_URL = f"{BASE_URL}/zhixuebao/zhixuebao/feesReport/getStuSingleReportDataForPK/"
    GET_SUBJECT_URL = f"{BASE_URL}/zhixuebao/report/exam/getReportMain"
    GET_MARK_URL = GET_SUBJECT_URL
    GET_ORIGINAL_URL = f"{BASE_URL}/zhixuebao/report/checksheet/"
    GET_ACADEMIC_YEAR_URL = f"{BASE_URL}/zhixuebao/base/common/academicYear"

    # Person
    GET_CLAZZS_URL = f"{BASE_URL}/zhixuebao/zhixuebao/friendmanage/"
    # GET_CLASSMATES_URL = f"{BASE_URL}/zhixuebao/zhixuebao/getClassStudent/"
    GET_CLASSMATES_URL = f"{BASE_URL}/container/contact/student/students"
    GET_TEACHERS_URL = f"{BASE_URL}/container/contact/student/teachers"

    APP_BASE_URL = "https://mhw.zhixue.com"
    # Homework
    GET_HOMEWORK_URL = f"{APP_BASE_URL}/homework_middle_service/stuapp/getStudentHomeWorkList"
    GET_HOMEWORK_EXERCISE_URL = f"{APP_BASE_URL}/hw/manage/homework/redeploy"
    GET_HOMEWORK_BANK_URL = f"{APP_BASE_URL}/hwreport/question/listView"

    GET_EXAM_LEVEL_TREND_URL = f"{BASE_URL}/zhixuebao/report/exam/getLevelTrend"

    GET_PAPER_LEVEL_TREND_URL = f"{BASE_URL}/zhixuebao/report/paper/getLevelTrend"
    GET_LOST_TOPIC_URL = f"{BASE_URL}/zhixuebao/report/paper/getExamPointsAndScoringAbility"
    GET_ERRORBOOK_URL = f"{BASE_URL}/zhixuebao/report/paper/getLostTopicAndAnalysis"
    GET_SUBJECT_DIAGNOSIS = f"{BASE_URL}/zhixuebao/report/exam/getSubjectDiagnosis"
