from os import environ
import dj_database_url

# ================== 实验配置 ==================
SESSION_CONFIGS = [
    dict(
        name='public_goods_corrupt',
        display_name="公共品博弈实验（腐败奖励+惩罚组）",
        app_sequence=['public_goods_corrupt'],
        num_demo_participants=4,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=3.00,
    doc="公共品博弈实验（腐败奖励+惩罚组）"
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ================== 国际化设置 ==================
LANGUAGE_CODE = 'zh-hans'
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True

# ================== 房间配置 ==================
ROOMS = [
    dict(
        name='experiment_room',
        display_name='实验房间',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(
        name='live_demo',
        display_name='实时演示（无参与者标签）'
    ),
]

# ================== 管理后台 ==================
ADMIN_USERNAME = 'admin'
# 推荐在 Render 的环境变量设置 OTREE_ADMIN_PASSWORD
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', '1234')

# ================== 实验首页 ==================
DEMO_PAGE_INTRO_HTML = """
欢迎参加公共品博弈实验！
"""

# ================== 安全密钥 ==================
SECRET_KEY = environ.get('SECRET_KEY', 'unsafe-default-key')

# ================== 应用加载 ==================
INSTALLED_APPS = ['otree']

# ================== 数据库配置 ==================
# 本地默认 SQLite，Render 自动切 PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

# ================== 生产模式 ==================
# 在 Render 环境变量设置 OTREE_PRODUCTION=1 可隐藏 debug 信息
if environ.get('OTREE_PRODUCTION'):
    DEBUG = False
else:
    DEBUG = True
