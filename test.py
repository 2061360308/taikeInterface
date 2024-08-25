from login import login, get_phoenix_jwt, login_jwglxt
from utils import CookieManager

user = ""  # 用户名(学号)
password = ""  # 密码

cookie_manager = CookieManager()  # 初始化CookieManager

# 登录
login(user, password, cookie_manager)  # 登录统一门户
get_phoenix_jwt(cookie_manager)  # 获取统一门户到教务系统的中间令牌phoenix-jwt
login_jwglxt(cookie_manager)  # 登录教务系统

# 以下是调用各个API的示例
from api import free_room, school_calendar, current_week_and_weekday, recent_courses


# 获取当前周数和星期数
week_number, weekday_number = current_week_and_weekday(cookie_manager)
print(f"当前是第{week_number}周，星期{weekday_number}")

# 查询空闲教室
print("查询空闲教室")
print(free_room(cookie_manager, week=week_number, day=weekday_number, selected_jc=[1, 2]))

# 查询学校日历
print("查询学校日历")
print(school_calendar(cookie_manager))

# 查询最近课程
print("查询最近课程")
print(recent_courses(cookie_manager))