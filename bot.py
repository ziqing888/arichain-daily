import json
import time
import random
import requests
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import pyfiglet
from termcolor import colored
init(autoreset=True)


输出样式 = {
    '分隔线': Fore.BLACK + '━' * 50,
    '小分隔线': Fore.BLACK + '─' * 50,
    '状态图标': {
        '成功': Fore.GREEN + '✅',
        '警告': Fore.YELLOW + '⚠️',
        '错误': Fore.RED + '❌',
        '进度': Fore.CYAN + '⏳'
    },
    '颜色主题': {
        '地址': Fore.CYAN,
        '数值': Fore.YELLOW,
        '时间': Fore.LIGHTBLACK_EX,  
        '强调': Fore.GREEN,
        '次要': Fore.LIGHTBLACK_EX 
    }
}

def 显示标题():
    # 使用 pyfiglet 创建 banner 字符串
    banner = pyfiglet.figlet_format('Arichain', font='slant')
    print(colored(banner, 'cyan'))

    print(
        colored('加入我们：电报频道：https://t.me/ksqxszq', 'yellow') +
        colored('  v2.1.0', 'green') +
        '\n' +
        '-' * 50 + '\n' +  # 简单的分隔线
        colored('当前时间: ' + str(datetime.now()), 'white')
    )


# 配置参数
CONFIG_FILE = 'user_config.json'
API_SETTINGS = {
    'base_url': 'https://arichain.io/api',
    'endpoints': {
        'auth': '/wallet/get_list_mobile',
        'checkin': '/event/checkin',
        'quiz': '/event/quiz_q',
        'answer': '/event/quiz_a'
    }
}

# 加载用户配置文件
def 加载配置文件(文件路径):
    try:
        with open(文件路径, 'r', encoding='utf-8') as 文件:
            return json.load(文件)
    except Exception as 异常:
        print(f"配置文件加载失败: {异常}")
        exit()

# 代理验证模块
class 代理管理器:
    @staticmethod
    def 验证代理(代理地址):
        try:
            响应 = requests.get(
                'https://ipapi.co/json/',
                proxies={'http': 代理地址, 'https': 代理地址},
                timeout=10
            )
            数据 = 响应.json()
            return (
                数据.get('ip'),
                数据.get('city'),
                数据.get('country_name')
            )
        except Exception as 异常:
            return None, None, None

# 日志记录模块
class 日志记录器:
    @staticmethod
    def 记录(消息, 颜色, 换行=False):
        if 换行:
            print("\n")
        print(颜色 + str(消息))

# API 请求模块
class 链操作:
    def __init__(self, 用户配置, 代理=None):
        self.用户 = 用户配置
        self.代理 = 代理
        self.请求头 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept-language": "zh-CN,zh;q=0.9"
        }

    def 执行请求(self, 接口类型, 附加参数=None):
        接口路径 = API_SETTINGS['endpoints'][接口类型]
        请求地址 = f"{API_SETTINGS['base_url']}{接口路径}"
        基础参数 = {
            "blockchain": "testnet",
            "lang": "zh",
            "device": "app",
            "is_mobile": "Y"
        }

       
        if 接口类型 == 'auth':
            基础参数.update({"email": self.用户['email']})
        elif 接口类型 in ('checkin', 'quiz', 'answer'):
            基础参数.update({"address": self.用户['wallet_address']})

        if 附加参数:
            基础参数.update(附加参数)

        try:
           
            if self.代理:
                响应 = requests.post(
                    url=请求地址,
                    headers=self.请求头,
                    data=基础参数,
                    proxies=self.代理,
                    timeout=15
                )
            else:
                响应 = requests.post(
                    url=请求地址,
                    headers=self.请求头,
                    data=基础参数,
                    timeout=15  
                )
            return 响应.json() if 响应.status_code == 200 else None
        except Exception as 异常:
            日志记录器.记录(f"请求异常: {异常}", Fore.RED)
            return None

# 核心业务流程
def 执行用户任务(用户配置):
    日志记录器.记录(f"开始处理用户: {用户配置['name']}", Fore.YELLOW, True)

    # 代理检测
    if 'proxy' in 用户配置 and 用户配置['proxy']:  
        ip, 城市, 国家 = 代理管理器.验证代理(用户配置['proxy'])
        if ip:
            日志记录器.记录(f"代理状态正常 | 位置: {国家}-{城市}", Fore.CYAN)
        else:
            日志记录器.记录("代理连接异常", Fore.RED)
            return
    else:
        日志记录器.记录("没有配置代理，跳过代理验证", Fore.YELLOW)

    # 初始化API客户端
    客户端 = 链操作(用户配置, 用户配置.get('proxy')) 

    # 身份验证
    if 认证结果 := 客户端.执行请求('auth'):
        if 认证结果.get('status') == 'success':
            余额 = 认证结果['result'][0]['balance']
            日志记录器.记录(f"认证成功 | 当前余额: {余额} ARI", Fore.GREEN)
            time.sleep(random.uniform(1.5, 3.5))
        else:
            日志记录器.记录("认证失败，跳过后续操作", Fore.RED)
            return

    # 每日签到
    if 签到结果 := 客户端.执行请求('checkin'):
        if "Already Checked in" in str(签到结果):
            日志记录器.记录("今日已完成签到", Fore.LIGHTYELLOW_EX)
        else:
            日志记录器.记录("签到成功", Fore.LIGHTGREEN_EX)
    time.sleep(random.randint(2, 4))

    # 答题流程
    if 题目数据 := 客户端.执行请求('quiz'):
        if 题目数据.get('status') == 'success':
            题目编号 = 题目数据['result']['quiz_idx']
            问题编号 = 题目数据['result']['quiz_q'][0]['q_idx']
            日志记录器.记录(f"获取题目成功 | 题号: {题目编号}", Fore.LIGHTBLUE_EX)
            
            回答参数 = {"quiz_idx": 题目编号, "answer_idx": 问题编号}
            if 答题结果 := 客户端.执行请求('answer', 回答参数):
                if "Already taken quiz" in str(答题结果):
                    日志记录器.记录("今日已完成答题", Fore.LIGHTYELLOW_EX)
                else:
                    日志记录器.记录("答题已提交", Fore.LIGHTGREEN_EX)
            time.sleep(random.uniform(3, 6))

if __name__ == "__main__":
    显示标题() 
    
    # 加载配置
    用户列表 = 加载配置文件(CONFIG_FILE)
    日志记录器.记录(f"成功加载 {len(用户列表)} 个用户配置", Fore.LIGHTCYAN_EX)

    # 执行任务
    while True:
        random.shuffle(用户列表)  
        for 用户 in 用户列表:
            执行用户任务(用户)
            time.sleep(random.randint(5, 15))
        
        间隔时间 = random.randint(24*3600 + 1800, 25*3600)
        下次执行 = datetime.now() + timedelta(seconds=间隔时间) 
        日志记录器.记录(f"本轮任务完成，下次执行时间: {下次执行.strftime('%Y-%m-%d %H:%M')}", Fore.LIGHTWHITE_EX, True)
        time.sleep(间隔时间)
