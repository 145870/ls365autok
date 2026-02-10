# -*- coding: utf-8 -*-
"""
湖南外国语职业学院自动化学习脚本
一个完整的单文件解决方案，无需复杂配置

使用方法：
1. 先在浏览器中手动登录到学习系统
2. 运行此脚本：python auto_study.py
3. 按照提示操作即可

作者：AI Assistant
版本：1.0.0
"""

import time
import random
import re
import os
import sys
import json
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# 自动安装缺少的依赖包
def install_package(package):
    """自动安装缺少的包"""
    import subprocess
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"{package} 安装失败")
        return False

# 检查并安装必要的依赖包
required_packages = {
    'selenium': 'selenium',
    'webdriver_manager': 'webdriver-manager'
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("检测到缺少的依赖包，正在自动安装...")
    for package in missing_packages:
        if not install_package(package):
            print(f"无法自动安装 {package}，请手动安装：pip install {package}")
            sys.exit(1)
    print("所有依赖包安装完成，重新启动脚本...")
    # 重新导入模块
    import importlib
    for module in required_packages.keys():
        try:
            importlib.import_module(module)
        except ImportError:
            pass

# 现在导入所需的库
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    print(f"导入失败: {e}")
    print("请手动安装依赖包：pip install selenium webdriver-manager")
    sys.exit(1)

class AutoStudyBot:
    """自动学习机器人"""
    
    def __init__(self):
        """初始化机器人"""
        self.driver = None
        self.wait = None
        self.config = self.load_config()
        
        # 从配置文件读取参数
        self.ELEMENT_TIMEOUT = self.config["automation"]["element_timeout"]
        self.PAGE_LOAD_TIMEOUT = self.config["automation"]["page_load_timeout"]
        self.ENABLE_DELAYS = self.config["automation"]["enable_delays"]
        self.ENABLE_DURATION_CHECK = self.config["automation"]["enable_duration_check"]
        self.HIGHLIGHT_ELEMENTS = self.config["debug"]["highlight_elements"]
        self.HIGHLIGHT_DURATION = 1 if self.HIGHLIGHT_ELEMENTS else 0
        self.VIDEO_SPEED = self.config["automation"]["video_speed"]
        self.VIDEO_WAIT_AFTER_COMPLETE = self.config["automation"]["video_wait_after_complete"]
        self.CONCURRENT_VIDEOS = self.config["automation"].get("concurrent_videos", 1)
        
        # 网站配置
        self.WEBSITE_URL = self.config["website"]["url"]
        self.USERNAME = self.config["website"]["username"]
        self.PASSWORD = self.config["website"]["password"]
        
        # AI配置
        self.AI_PROVIDER = self.config["ai"].get("provider", "openai")
        self.OPENAI_API_KEY = self.config["ai"].get("openai_api_key", "")
        self.OPENAI_BASE_URL = self.config["ai"].get("openai_base_url", "https://api.openai.com/v1")
        self.OPENAI_MODEL = self.config["ai"].get("openai_model", "gpt-3.5-turbo")
        self.ZHIPU_API_KEY = self.config["ai"].get("zhipu_api_key", "")
        self.ZHIPU_MODEL = self.config["ai"].get("zhipu_model", "glm-4-flash")
        self.ai_client = None
        
        # 作业配置
        self.USE_AI = self.config["homework"]["use_ai"]
        self.AUTO_SUBMIT = self.config["homework"]["auto_submit"]
        self.MIN_PASSING_SCORE = self.config["homework"]["min_passing_score"]
        self.RETRY_IF_FAILED = self.config["homework"]["retry_if_failed"]
        
        print("=" * 60)
        print("湖南外国语职业学院自动化学习脚本".center(60))
        print("开源免费 | 仅供学习交流使用 | 禁止商业用途".center(60))
        print("=" * 60)
        sys.stdout.flush()  # 强制刷新输出
        
        # 隐藏敏感信息
        # print(f"目标网站: {self.WEBSITE_URL}")
        # print(f"用户账号: {self.USERNAME}")
        
        # 显示作业配置
        if self.USE_AI:
            answer_mode = f"AI智能答题 ({self.AI_PROVIDER.upper()})"
        else:
            answer_mode = "随机选择"
        submit_mode = "自动提交" if self.AUTO_SUBMIT else "手动提交"
        retry_mode = "启用" if self.RETRY_IF_FAILED else "禁用"
        print(f"答题模式: {answer_mode}")
        print(f"提交方式: {submit_mode}")
        print(f"及格分数: {self.MIN_PASSING_SCORE}分")
        print(f"不及格重做: {retry_mode}")
        sys.stdout.flush()  # 强制刷新输出
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("配置文件加载成功")
            return config
        except FileNotFoundError:
            print("未找到config.json配置文件")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            sys.exit(1)
    
    
    def setup_browser(self):
        """启动Chrome浏览器并访问目标网站"""
        try:
            print("正在启动Chrome浏览器...")
            sys.stdout.flush()
            
            chrome_options = Options()
            
            # 基础窗口设置
            chrome_options.add_argument(f"--window-size={self.config['browser']['window_width']},{self.config['browser']['window_height']}")
            
            # 稳定性选项
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 无头模式
            if self.config["browser"]["headless"]:
                chrome_options.add_argument("--headless=new")
                print("无头模式（后台运行）")
            else:
                print("浏览器窗口模式（可见）")
            
            sys.stdout.flush()
            
            # 尝试多种方式启动
            max_retries = 3
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    print(f"\n[{attempt + 1}/{max_retries}] 正在启动浏览器...")
                    sys.stdout.flush()
                    
                    # 方法1: 直接启动（Selenium 4.6+会自动管理ChromeDriver）
                    try:
                        print("尝试方法1: 自动管理ChromeDriver...")
                        sys.stdout.flush()
                        self.driver = webdriver.Chrome(options=chrome_options)
                        print("✓ 方法1成功!")
                    except Exception as e1:
                        print(f"方法1失败: {str(e1)[:100]}")
                        
                        # 方法2: 使用selenium-manager
                        try:
                            print("尝试方法2: 使用selenium-manager...")
                            sys.stdout.flush()
                            from selenium.webdriver.chrome.service import Service as ChromeService
                            service = ChromeService()
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            print("✓ 方法2成功!")
                        except Exception as e2:
                            print(f"方法2失败: {str(e2)[:100]}")
                            raise Exception(f"所有方法都失败了。错误1: {str(e1)[:50]}, 错误2: {str(e2)[:50]}")
                    
                    self.driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
                    self.wait = WebDriverWait(self.driver, self.ELEMENT_TIMEOUT)
                    
                    print("Chrome浏览器启动成功!")
                    sys.stdout.flush()
                    break
                    
                except Exception as e:
                    last_error = e
                    print(f"第 {attempt + 1} 次启动失败:")
                    print(f"   错误: {str(e)}")
                    sys.stdout.flush()
                    
                    if attempt < max_retries - 1:
                        print(f"等待 3 秒后重试...")
                        sys.stdout.flush()
                        time.sleep(3)
                        
                        try:
                            if hasattr(self, 'driver') and self.driver:
                                self.driver.quit()
                        except:
                            pass
                    else:
                        error_msg = f"浏览器启动失败（已重试{max_retries}次）\n"
                        error_msg += f"最后错误: {str(last_error)}\n\n"
                        error_msg += "请确保:\n"
                        error_msg += "1. 已安装Chrome浏览器\n"
                        error_msg += "2. Chrome版本不要太旧\n"
                        error_msg += "3. 以管理员身份运行程序"
                        raise Exception(error_msg)
            
            # 访问目标网站
            print(f"\n正在访问网站...")
            sys.stdout.flush()
            self.driver.get(self.WEBSITE_URL)
            
            print("等待页面加载...")
            sys.stdout.flush()
            self.wait_for_page_load()
            
            print("网站访问成功!")
            sys.stdout.flush()
            return True
            
        except Exception as e:
            print(f"\n浏览器启动失败:")
            print(str(e))
            sys.stdout.flush()
            
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            return False
    
    def auto_login(self):
        """自动登录"""
        try:
            print("开始自动登录...")
            
            # 查找用户名输入框 - 使用已知有效的选择器
            username_element = self.find_element_safe(By.CSS_SELECTOR, "input[type='text']", timeout=5)
            
            if not username_element:
                print("未找到用户名输入框")
                return False
            
            # 输入用户名
            print(f"输入用户名: {self.USERNAME}")
            username_element.clear()
            username_element.send_keys(self.USERNAME)
            
            # 查找密码输入框 - 使用已知有效的选择器
            password_element = self.find_element_safe(By.CSS_SELECTOR, "input[type='password']", timeout=5)
            
            if not password_element:
                print("未找到密码输入框")
                return False
            
            # 输入密码
            print("输入密码...")
            password_element.clear()
            password_element.send_keys(self.PASSWORD)
            
            # 查找登录按钮 - 根据实际HTML元素
            login_element = self.find_element_safe(By.CSS_SELECTOR, "a.lg-card-btn#lg-card-btn", timeout=5)
            
            if not login_element:
                print("未找到登录按钮")
                return False
            
            # 点击登录按钮
            print("点击登录按钮...")
            if self.config["debug"]["highlight_elements"]:
                self.highlight_element(login_element)
            
            login_element.click()
            
            # 等待登录完成
            time.sleep(3)
            
            # 检查登录结果
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"登录后页面: {page_title}")
            print(f"当前地址: {current_url}")
            
            if "login" not in current_url.lower():
                print("登录成功!")
                return True
            else:
                print("登录状态未知，继续执行...")
                return True
                
        except Exception as e:
            print(f"自动登录失败: {e}")
            return False
    
    
    def random_delay(self, min_delay=0.1, max_delay=0.5):
        """随机延迟，模拟人类操作"""
        if not self.ENABLE_DELAYS:
            return
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def wait_for_page_load(self, timeout=30):
        """等待页面完全加载"""
        try:
            # 等待页面加载状态为complete
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 额外等待一点时间确保JavaScript执行完成
            time.sleep(2)
            
            print("页面加载完成")
            return True
            
        except Exception as e:
            print(f"页面加载超时: {e}")
            return False
    

    def highlight_element(self, element):
        """高亮显示元素"""
        # 根据配置决定是否高亮
        if not self.config.get("debug", {}).get("highlight_elements", False):
            return
            
        try:
            # 添加红色边框高亮
            original_style = element.get_attribute("style") or ""
            self.driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1] + 'border: 3px solid red !important; box-shadow: 0 0 10px red !important;');", 
                element, original_style
            )
            
            # 滚动到元素位置
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            
            time.sleep(self.HIGHLIGHT_DURATION)
            
            # 恢复原始样式
            self.driver.execute_script(
                "arguments[0].setAttribute('style', arguments[1]);", 
                element, original_style
            )
            
        except Exception as e:
            print(f"高亮元素失败: {e}")
    
    def find_element_safe(self, by, value, timeout=None, parent=None):
        """安全查找元素"""
        try:
            if timeout is None:
                timeout = self.ELEMENT_TIMEOUT
            
            # 如果指定了父元素，在父元素中查找
            if parent:
                element = parent.find_element(by, value)
            else:
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located((by, value)))
            
            print(f"找到元素: {by}={value}")
            print(f"   元素文本: {element.text[:50]}...")
            print(f"   元素标签: {element.tag_name}")
            
            return element
        except Exception as e:
            print(f"未找到元素: {by}={value} ({e})")
            return None

    def find_all_elements_debug(self, by, value):
        """查找所有匹配的元素并显示调试信息"""
        try:
            elements = self.driver.find_elements(by, value)
            print(f"查找 {by}={value} 找到 {len(elements)} 个元素:")
            
            for i, element in enumerate(elements):
                try:
                    text = element.text[:30] if element.text else "无文本"
                    visible = element.is_displayed()
                    enabled = element.is_enabled()
                    print(f"   [{i}] 文本: {text} | 可见: {visible} | 可用: {enabled}")
                except:
                    print(f"   [{i}] 无法获取元素信息")
            
            return elements
        except Exception as e:
            print(f"查找元素失败: {e}")
            return []
    
    def click_element_safe(self, element):
        """安全点击元素"""
        try:
            if element is None:
                return False
            
            # 滚动到元素
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # 高亮显示
            self.highlight_element(element)
            
            # 点击
            element.click()
            self.random_delay()
            return True
        except:
            return False
    
    def navigate_to_courses(self):
        """导航到我的课程"""
        print("正在查找'我的课程'选项...")
        
        # 查找"我的课程"链接（根据你提供的HTML结构）
        course_link = self.find_element_safe(By.XPATH, "//a[@href='/University/User/Student/mycourselist.aspx?m=wdkc']")
        
        if course_link:
            print("找到'我的课程'链接")
            if self.HIGHLIGHT_ELEMENTS:
                self.highlight_element(course_link)
            
            if self.click_element_safe(course_link):
                print("成功点击'我的课程'")
                self.wait_for_page_load()
                
                # 点击"学习中"标签
                return self.select_studying_tab()
            else:
                print("点击'我的课程'失败")
                return False
        else:
            print("未找到'我的课程'链接，尝试查找'学习中'标签")
            # 可能已经在课程页面，直接选择"学习中"标签
            return self.select_studying_tab()
    
    def select_studying_tab(self):
        """选择'学习中'标签"""
        print("正在查找'学习中'标签...")
        
        # 查找"学习中"标签
        studying_tab = self.find_element_safe(By.XPATH, "//a[@href='javascript:getStuding();' and contains(text(), '学习中')]")
        
        if studying_tab:
            print("找到'学习中'标签")
            if self.HIGHLIGHT_ELEMENTS:
                self.highlight_element(studying_tab)
            
            if self.click_element_safe(studying_tab):
                print("成功点击'学习中'标签")
                self.wait_for_page_load()
                return True
            else:
                print("点击'学习中'标签失败")
                return False
        else:
            print("未找到'学习中'标签，可能已经选中")
            return True
    
    def navigate_to_homework(self):
        """导航到我的作业列表页面"""
        print("正在查找'我的作业'选项...")
        
        # 根据HTML结构,精确查找"我的作业"链接
        homework_link = self.find_element_safe(
            By.XPATH,
            "//a[@href='/University/User/Student/dohomework.aspx?m=wdzy']",
            timeout=10
        )
        
        if homework_link:
            print("找到'我的作业'链接")
            self.highlight_element(homework_link)
            homework_link.click()
            self.wait_for_page_load()
            print("已进入作业列表页面")
            return True
        
        print("可能已在作业页面,继续...")
        return True
    
    def find_uncompleted_homework(self):
        """查找未完成或得分低于60的作业 - 优先完成未开始的"""
        print("\n正在查找需要完成的作业...")
        
        # 查找所有作业项
        homework_items = self.driver.find_elements(By.CSS_SELECTOR, "div.home-list")
        
        if not homework_items:
            print("未找到作业列表")
            return None
        
        print(f"找到 {len(homework_items)} 个作业")
        
        # 两次遍历: 第一次找"开始作业", 第二次找"需要重做"
        
        # 第一遍: 优先找未开始的作业
        for item in homework_items:
            try:
                # 获取作业名称
                name_elem = item.find_element(By.CSS_SELECTOR, "div.work_course_name span")
                homework_name = name_elem.text.strip()
                
                # 检查作业状态
                status_elem = item.find_element(By.CSS_SELECTOR, "div.home-btn a.seeWork")
                button_text = status_elem.text.strip()
                
                # 如果是"开始作业",说明未完成 - 优先处理
                if button_text == "开始作业":
                    print(f"[优先] 发现未开始作业: {homework_name}")
                    return {
                        'name': homework_name,
                        'button': status_elem,
                        'score': 0,
                        'status': '未开始'
                    }
                    
            except Exception as e:
                continue
        
        # 第二遍: 找不及格需要重做的(如果启用了重做功能)
        if self.RETRY_IF_FAILED:
            for item in homework_items:
                try:
                    # 获取作业名称
                    name_elem = item.find_element(By.CSS_SELECTOR, "div.work_course_name span")
                    homework_name = name_elem.text.strip()
                    
                    # 检查作业状态
                    status_elem = item.find_element(By.CSS_SELECTOR, "div.home-btn a.seeWork")
                    button_text = status_elem.text.strip()
                    
                    # 获取分数(如果有)
                    try:
                        score_elem = item.find_element(By.CSS_SELECTOR, "div.work-status")
                        score_text = score_elem.text
                        
                        # 提取分数
                        import re
                        score_match = re.search(r'(\d+)分', score_text)
                        score = int(score_match.group(1)) if score_match else 0
                        
                        # 如果已完成但分数低于及格线,需要重新做
                        if score > 0 and score < self.MIN_PASSING_SCORE:
                            print(f"[重做] 发现低分作业: {homework_name} (当前分数: {score}分)")
                            return {
                                'name': homework_name,
                                'button': status_elem,
                                'score': score,
                                'status': '需要重做'
                            }
                    except:
                        pass
                        
                except Exception as e:
                    continue
        else:
            print("[提示] 不及格重做功能已禁用,跳过低分作业")
        
        print("所有作业都已完成且达标!")
        return None
    
    def play_all_videos(self):
        """播放所有课程视频"""
        print("开始批量播放视频...")
        
        # 查找所有"进入学习"按钮
        enter_study_elements = self.find_all_elements_debug(By.XPATH, "//a[contains(text(), '进入学习')]")
        
        if not enter_study_elements:
            print("未找到任何'进入学习'按钮")
            return False
        
        print(f"找到 {len(enter_study_elements)} 个课程")
        
        # 记录原始窗口
        original_window = self.driver.current_window_handle
        opened_windows = []
        
        # 批量打开视频窗口
        concurrent_count = min(len(enter_study_elements), self.MAX_CONCURRENT_VIDEOS)
        print(f"同时打开 {concurrent_count} 个视频窗口")
        
        for i in range(concurrent_count):
            element = enter_study_elements[i]
            if element and element.is_displayed() and element.is_enabled():
                print(f"打开第 {i+1} 个课程...")
                
                # 右键点击在新标签页打开
                actions = ActionChains(self.driver)
                actions.context_click(element).perform()
                time.sleep(1)
                
                # 或者直接点击（会在新窗口打开）
                if self.click_element_safe(element):
                    time.sleep(2)
                    
                    # 获取新打开的窗口
                    all_windows = self.driver.window_handles
                    new_window = None
                    for window in all_windows:
                        if window != original_window and window not in opened_windows:
                            new_window = window
                            break
                    
                    if new_window:
                        opened_windows.append(new_window)
                        print(f"第 {i+1} 个课程窗口已打开")
        
        # 切换到每个窗口并设置视频
        for i, window in enumerate(opened_windows):
            print(f"处理第 {i+1} 个视频窗口...")
            self.driver.switch_to.window(window)
            time.sleep(2)
            
            # 设置视频倍速和开始播放
            self.setup_video_playback()
        
        # 监控所有视频完成情况
        self.monitor_all_videos(opened_windows, original_window)
        
        return True
    
    def play_first_video(self):
        """播放视频并自动循环播放所有视频"""
        print("开始自动刷视频...")
        print(f"配置: 同时打开 {self.CONCURRENT_VIDEOS} 个视频窗口")
        
        # 记录原始窗口
        original_window = self.driver.current_window_handle
        video_windows = []
        
        # 先查找所有"进入学习"按钮
        enter_study_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), '进入学习')]")
        
        if not enter_study_buttons:
            print("未找到任何'进入学习'按钮")
            return False
        
        print(f"找到 {len(enter_study_buttons)} 个课程")
        
        # 筛选出未完成的课程
        uncompleted_courses = []
        for i, button in enumerate(enter_study_buttons):
            try:
                if not button.is_displayed() or not button.is_enabled():
                    continue
                
                # 尝试找到按钮所在的课程项容器，检查进度
                try:
                    # 向上查找父元素，找到包含进度信息的容器
                    parent = button
                    for _ in range(5):  # 最多向上查找5层
                        parent = parent.find_element(By.XPATH, "..")
                        # 尝试在这个容器中查找进度
                        try:
                            progress_elem = parent.find_element(By.CSS_SELECTOR, "p.learningStatus span.lsPercents")
                            progress_text = progress_elem.text.strip()
                            progress_value = float(progress_text.replace('%', ''))
                            
                            # 获取课程标题
                            try:
                                title_elem = parent.find_element(By.CSS_SELECTOR, "a")
                                course_title = title_elem.get_attribute("title") or title_elem.text
                            except:
                                course_title = f"课程 {i+1}"
                            
                            print(f"课程: {course_title.strip()}, 进度: {progress_value}%")
                            
                            # 如果进度已经是100%，跳过
                            if progress_value >= 100:
                                print(f"  -> 课程已完成，跳过")
                                break  # 跳出父元素查找循环
                            
                            print(f"  -> 课程未完成，加入待学习列表")
                            uncompleted_courses.append((button, course_title.strip(), progress_value))
                            break  # 找到进度后跳出父元素查找循环
                            
                        except:
                            continue  # 继续向上查找
                    else:
                        # 如果找不到进度信息，认为是未开始的课程
                        try:
                            course_title = button.get_attribute("title") or f"课程 {i+1}"
                        except:
                            course_title = f"课程 {i+1}"
                        
                        print(f"课程: {course_title}, 进度: 未知")
                        print(f"  -> 加入待学习列表")
                        uncompleted_courses.append((button, course_title, 0))
                        
                except:
                    # 如果所有尝试都失败，直接加入列表
                    uncompleted_courses.append((button, f"课程 {i+1}", 0))
                    
            except:
                continue
        
        if not uncompleted_courses:
            print("所有课程都已完成！")
            return False
        
        print(f"\n共有 {len(uncompleted_courses)} 个未完成课程")
        
        # 打开多个视频窗口
        open_count = min(self.CONCURRENT_VIDEOS, len(uncompleted_courses))
        print(f"准备打开 {open_count} 个视频窗口...\n")
        
        for i in range(open_count):
            button, course_title, progress = uncompleted_courses[i]
            print(f"打开第 {i+1} 个视频: {course_title} (进度: {progress}%)")
            
            # 记录点击前的窗口
            windows_before = self.driver.window_handles
            
            # 点击按钮
            try:
                if self.HIGHLIGHT_ELEMENTS:
                    self.highlight_element(button)
                button.click()
                time.sleep(3)
                
                # 查找新窗口
                windows_after = self.driver.window_handles
                new_window = None
                for window in windows_after:
                    if window not in windows_before:
                        new_window = window
                        break
                
                if new_window:
                    video_windows.append(new_window)
                    print(f"  -> 窗口已打开\n")
                else:
                    print(f"  -> 可能在当前窗口打开\n")
                    if self.driver.current_window_handle not in video_windows:
                        video_windows.append(self.driver.current_window_handle)
                
                # 切回原始窗口继续点击下一个
                if i < open_count - 1:
                    self.driver.switch_to.window(original_window)
                    time.sleep(1)
                    
            except Exception as e:
                print(f"  -> 打开失败: {e}\n")
        
        if not video_windows:
            print("没有成功打开任何视频窗口")
            return False
        
        print(f"\n成功打开 {len(video_windows)} 个视频窗口，开始监控...")
        
        # 进入自动播放循环，监控所有窗口
        self.auto_play_videos_loop_multi(video_windows, original_window)
        return True
    
    def set_video_speed(self, window_idx):
        """设置视频播放倍速"""
        try:
            print(f"  -> 窗口 {window_idx}: 设置视频倍速为 {self.VIDEO_SPEED}...")
            time.sleep(2)  # 等待视频播放器加载
            
            # 点击倍速设置按钮
            speed_setting = self.driver.find_element(By.CSS_SELECTOR, ".prism-setting-item.prism-setting-speed")
            speed_setting.click()
            time.sleep(1)
            
            # 根据配置选择倍速
            speed_text_map = {
                "0.5X": "0.5X",
                "1X": "正常",
                "1.25X": "1.25X",
                "1.5X": "1.5X",
                "2X": "2X"
            }
            
            target_speed = speed_text_map.get(self.VIDEO_SPEED, "2X")
            
            # 查找并点击对应的倍速选项
            speed_options = self.driver.find_elements(By.CSS_SELECTOR, ".prism-speed-selector .selector-list li span")
            for option in speed_options:
                if option.text == target_speed:
                    option.click()
                    print(f"  -> 窗口 {window_idx}: 倍速已设置为 {self.VIDEO_SPEED}")
                    time.sleep(0.5)
                    return True
            
            print(f"  -> 窗口 {window_idx}: 未找到倍速选项 {self.VIDEO_SPEED}")
            return False
            
        except Exception as e:
            print(f"  -> 窗口 {window_idx}: 设置倍速失败: {e}")
            return False
    
    def auto_play_videos_loop_multi(self, video_windows, original_window):
        """监控多个视频窗口"""
        print("\n" + "=" * 60)
        print(f"多窗口监控模式已启动 (共 {len(video_windows)} 个窗口)")
        print("脚本会自动检测每个窗口的视频完成状态")
        print("如需停止，请按 Ctrl+C")
        print("=" * 60 + "\n")
        
        # 首先为所有窗口设置倍速
        print("正在为所有窗口设置视频倍速...")
        for idx, window in enumerate(video_windows):
            try:
                self.driver.switch_to.window(window)
                self.set_video_speed(idx + 1)
            except Exception as e:
                print(f"  -> 窗口 {idx+1}: 设置倍速时出错: {e}")
        
        print("\n开始监控视频完成状态...\n")
        
        completed_count = 0
        window_status = {window: {"completed": False, "check_count": 0, "last_check": 0} for window in video_windows}
        
        try:
            import time as time_module
            start_time = time_module.time()
            
            while True:
                current_time = time_module.time()
                
                # 检查每个窗口（每5秒检测一次）
                for idx, window in enumerate(video_windows):
                    if window_status[window]["completed"]:
                        continue
                    
                    # 检查是否到了该窗口的检测时间（每5秒）
                    if current_time - window_status[window]["last_check"] < 5:
                        continue
                    
                    window_status[window]["last_check"] = current_time
                    
                    try:
                        # 切换到该窗口
                        self.driver.switch_to.window(window)
                        window_status[window]["check_count"] += 1
                        check_count = window_status[window]["check_count"]
                        
                        # 检测完成弹窗
                        popup = self.driver.find_element(By.ID, "reader_msgbg")
                        popup_style = popup.get_attribute("style") or ""
                        
                        print(f"[窗口 {idx+1} 检测 #{check_count}] ", end="")
                        
                        # 检查是否完成
                        if "display: block" in popup_style or "display:block" in popup_style:
                            print("[视频完成]")
                            
                            # 查找"学习下一节"按钮
                            try:
                                next_btn = self.driver.find_element(By.ID, "learnNextSection")
                                if next_btn.is_displayed():
                                    print(f"  -> 窗口 {idx+1}: 点击'学习下一节'...")
                                    next_btn.click()
                                    time.sleep(3)
                                    
                                    completed_count += 1
                                    window_status[window]["check_count"] = 0
                                    
                                    # 为新视频设置倍速
                                    self.set_video_speed(idx + 1)
                                    
                                    print(f"  -> 窗口 {idx+1}: 已切换到下一个视频 (总完成: {completed_count})")
                                else:
                                    print(f"  -> 窗口 {idx+1}: 所有视频已完成")
                                    window_status[window]["completed"] = True
                            except:
                                print(f"  -> 窗口 {idx+1}: 所有视频已完成")
                                window_status[window]["completed"] = True
                        else:
                            print(f"播放中...")
                            
                    except Exception as e:
                        print(f"[窗口 {idx+1}] 检测出错: {e}")
                
                # 检查是否所有窗口都完成
                if all(status["completed"] for status in window_status.values()):
                    print("\n所有窗口的视频都已完成！")
                    break
                
                # 短暂休眠，避免CPU占用过高
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n用户中断自动播放")
            print(f"本次共完成 {completed_count} 个视频")
        except Exception as e:
            print(f"\n自动播放出错: {e}")
            print(f"本次共完成 {completed_count} 个视频")
        finally:
            # 切回原始窗口
            try:
                self.driver.switch_to.window(original_window)
            except:
                pass
    
    def auto_play_videos_loop(self):
        """自动播放视频循环 - 检测完成弹窗并点击下一节"""
        print("\n" + "=" * 60)
        print("自动刷视频模式已启动")
        print("脚本会自动检测视频完成并点击'学习下一节'")
        print("如需停止，请按 Ctrl+C")
        print("=" * 60 + "\n")
        
        completed_count = 0
        check_count = 0  # 检测次数计数
        
        try:
            # 等待视频页面加载完成
            print("等待视频页面加载...")
            time.sleep(8)
            
            # 确认已进入视频播放页面
            print(f"当前页面URL: {self.driver.current_url}")
            print(f"当前页面标题: {self.driver.title}")
            
            # 检查是否在视频播放页面
            if "play.aspx" not in self.driver.current_url and "play.html" not in self.driver.current_url:
                print("\n[警告] 当前不在视频播放页面，可能页面跳转失败")
                print("请确认已成功点击'进入学习'按钮")
                return
            
            print("\n开始监控视频完成状态...\n")
            
            while True:
                # 每5秒检测一次完成弹窗
                time.sleep(5)
                check_count += 1
                
                try:
                    # 检测完成弹窗是否显示
                    popup = self.driver.find_element(By.ID, "reader_msgbg")
                    
                    if popup:
                        # 检查弹窗的display样式
                        popup_style = popup.get_attribute("style") or ""
                        
                        # 输出检测日志
                        print(f"[检测 #{check_count}] 检查弹窗状态... ", end="")
                        
                        # 检查是否是 display: block (视频完成)
                        if "display: block" in popup_style or "display:block" in popup_style:
                            print("[弹窗已显示]")
                            
                            print(f"\n{'='*60}")
                            print(f"检测到视频完成弹窗！")
                            completed_count += 1
                            print(f"已完成视频数: {completed_count}")
                            print(f"{'='*60}\n")
                            
                            # 查找"学习下一节"按钮
                            try:
                                next_btn = self.driver.find_element(By.ID, "learnNextSection")
                                
                                if next_btn.is_displayed():
                                    print("找到'学习下一节'按钮，正在点击...")
                                    
                                    # 高亮按钮
                                    if self.HIGHLIGHT_ELEMENTS:
                                        self.highlight_element(next_btn)
                                    
                                    # 点击按钮
                                    next_btn.click()
                                    
                                    print("[成功] 已点击'学习下一节'，等待新视频加载...")
                                    time.sleep(5)  # 等待页面切换
                                    
                                    # 重置检测计数
                                    check_count = 0
                                    print("\n继续检测下一个视频...\n")
                                    
                                else:
                                    print("'学习下一节'按钮不可见")
                                    
                            except Exception as e:
                                print(f"未找到'学习下一节'按钮: {e}")
                                print("可能所有视频已完成，停止循环")
                                break
                        else:
                            print(f"弹窗隐藏中 (style: {popup_style[:50]}...)，视频播放中...")
                        
                except Exception as e:
                    # 找不到弹窗元素
                    print(f"[检测 #{check_count}] 未找到弹窗元素，可能不在视频页面")
                
        except KeyboardInterrupt:
            print("\n\n用户中断自动播放")
            print(f"本次共完成 {completed_count} 个视频")
        except Exception as e:
            print(f"\n自动播放出错: {e}")
            print(f"本次共完成 {completed_count} 个视频")
    
    def find_next_uncompleted_course_in_sidebar(self):
        """在右侧边栏中查找下一个未完成的课程"""
        try:
            print("查找右侧课程列表...")
            
            # 尝试多种选择器查找课程列表
            course_list_selectors = [
                ".course-list",
                ".chapter-list", 
                "[class*='course']",
                "[class*='chapter']",
                "[class*='lesson']",
                "ul li",  # 通用列表项
                ".sidebar",
                ".right-panel"
            ]
            
            course_items = []
            for selector in course_list_selectors:
                items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if items:
                    print(f"使用选择器 {selector} 找到 {len(items)} 个课程项")
                    course_items = items
                    break
            
            if not course_items:
                # 尝试XPath查找
                xpath_selectors = [
                    "//div[contains(text(), '课时')]",
                    "//li[contains(@class, 'course') or contains(@class, 'chapter')]",
                    "//a[contains(@href, 'course') or contains(@href, 'video')]"
                ]
                
                for xpath in xpath_selectors:
                    items = self.driver.find_elements(By.XPATH, xpath)
                    if items:
                        print(f"使用XPath {xpath} 找到 {len(items)} 个课程项")
                        course_items = items
                        break
            
            if not course_items:
                print("未找到任何课程列表项")
                return None
            
            # 遍历课程项查找未完成的
            for i, item in enumerate(course_items):
                try:
                    # 查找链接
                    links = item.find_elements(By.TAG_NAME, "a")
                    if not links:
                        continue
                    
                    course_link = links[0]
                    course_title = course_link.get_attribute("title") or course_link.text
                    
                    if course_title and course_title.strip():
                        # 检查是否有进度指示器
                        progress_imgs = item.find_elements(By.TAG_NAME, "img")
                        
                        # 如果没有进度图片，或者有未完成的进度图片
                        is_uncompleted = True
                        for img in progress_imgs:
                            img_src = img.get_attribute("src") or ""
                            # 如果包含完成标识，跳过
                            if "03-4.png" in img_src or "complete" in img_src.lower():
                                is_uncompleted = False
                                break
                        
                        if is_uncompleted:
                            print(f"找到未完成课程: {course_title.strip()}")
                            return {
                                'element': course_link,
                                'title': course_title.strip()
                            }
                                
                except Exception as e:
                    print(f"检查课程项 {i} 时出错: {e}")
                    continue
            
            print("所有课程都已完成")
            return None
            
        except Exception as e:
            print(f"查找右侧课程列表失败: {e}")
            return None
    
    def setup_video_playback(self):
        """设置视频播放（倍速等）"""
        try:
            print("设置视频播放参数...")
            
            # 等待视频播放器加载
            print("等待视频播放器加载...")
            time.sleep(5)
            
            # 首先尝试悬浮在视频播放器上以显示控制栏
            print("尝试激活视频控制栏...")
            video_player = self.find_element_safe(By.CSS_SELECTOR, "#CuPlayer", timeout=5)
            if video_player:
                print("找到视频播放器，悬浮激活控制栏...")
                ActionChains(self.driver).move_to_element(video_player).perform()
                time.sleep(2)
            
            # 尝试通过JavaScript直接设置倍速
            print("尝试通过JavaScript设置倍速...")
            try:
                # 查找video元素并设置playbackRate
                js_script = """
                var video = document.querySelector('video');
                if (video) {
                    video.playbackRate = 2.0;
                    console.log('视频倍速已设置为2X');
                    return true;
                }
                return false;
                """
                result = self.driver.execute_script(js_script)
                if result:
                    print("成功通过JavaScript设置倍速为2X")
                    print("视频播放设置完成")
                    return True
                else:
                    print("未找到video元素")
            except Exception as js_error:
                print(f"JavaScript设置失败: {js_error}")
            
            # 如果JavaScript失败，尝试UI操作
            print("尝试通过UI设置倍速...")
            setting_btn = self.find_element_safe(By.ID, "CuPlayer_component_7E7309DF-EF0F-4071-9B3B-23E2AC57267B", timeout=5)
            
            if not setting_btn:
                setting_btn = self.find_element_safe(By.CSS_SELECTOR, ".prism-setting-btn", timeout=3)
            
            if setting_btn:
                print("找到设置按钮，正在点击...")
                ActionChains(self.driver).move_to_element(setting_btn).click().perform()
                time.sleep(2)
                
                speed_setting = self.find_element_safe(By.CSS_SELECTOR, ".prism-setting-item.prism-setting-speed", timeout=5)
                
                if speed_setting:
                    print("找到倍速设置项，正在点击...")
                    ActionChains(self.driver).move_to_element(speed_setting).click().perform()
                    time.sleep(2)
                    
                    speed_2x = self.find_element_safe(By.XPATH, "//div[contains(@class, 'prism-speed-selector')]//li//span[text()='2X']", timeout=5)
                    
                    if speed_2x:
                        print("找到2X倍速选项，正在设置...")
                        ActionChains(self.driver).move_to_element(speed_2x).click().perform()
                        time.sleep(1)
                        print("成功设置倍速为2X")
                    else:
                        print("未找到2X倍速选项")
            else:
                print("UI方式未找到设置按钮")
            
            print("视频播放设置完成")
            return True
            
        except Exception as e:
            print(f"设置视频播放失败: {e}")
            print("视频会自动播放...")
            return True
    
    def monitor_all_videos(self, video_windows, original_window):
        """监控所有视频播放完成"""
        print("开始监控视频播放进度...")
        
        completed_videos = set()
        
        while len(completed_videos) < len(video_windows):
            for i, window in enumerate(video_windows):
                if window in completed_videos:
                    continue
                
                try:
                    self.driver.switch_to.window(window)
                    
                    # 检查视频是否播放完成
                    if self.is_video_completed():
                        print(f"第 {i+1} 个视频播放完成")
                        completed_videos.add(window)
                        
                        # 尝试点击"学习下一节"按钮
                        next_button = self.find_element_safe(By.ID, "learnNextSection", timeout=3)
                        if next_button and next_button.is_displayed():
                            print("点击'学习下一节'按钮")
                            next_button.click()
                            time.sleep(2)
                            
                            # 等待新课程加载并设置播放
                            self.wait_for_page_load()
                            self.setup_video_playback()
                        else:
                            # 如果没有"学习下一节"按钮，回到课程列表查找下一个
                            print("未找到'学习下一节'按钮，返回课程列表")
                            self.driver.switch_to.window(original_window)
                            
                            # 查找并点击下一个未完成的课程
                            if self.click_next_uncompleted_course():
                                print("已自动打开下一个课程")
                            else:
                                print("所有课程已完成或无更多课程")
                
                except Exception as e:
                    print(f"监控第 {i+1} 个视频时出错: {e}")
                    completed_videos.add(window)
            
            # 每30秒检查一次
            time.sleep(30)
        
        # 回到原始窗口
        self.driver.switch_to.window(original_window)
        print("所有视频播放完成！")
    
    def is_video_completed(self):
        """检查视频是否播放完成"""
        try:
            # 根据你提供的HTML，检查具体的完成标识
            # 1. 检查成功弹窗是否显示
            success_div = self.find_element_safe(By.CSS_SELECTOR, "#reader_success_video.success", timeout=1)
            if success_div:
                style = success_div.get_attribute("style") or ""
                if "display: block" in style:
                    print("检测到视频完成弹窗显示")
                    return True
            
            # 2. 检查"学习下一节"按钮是否出现
            next_btn = self.find_element_safe(By.CSS_SELECTOR, "#learnNextSection", timeout=1)
            if next_btn and next_btn.is_displayed():
                print("检测到'学习下一节'按钮")
                return True
            
            # 3. 检查完成提示文本
            tip_element = self.find_element_safe(By.CSS_SELECTOR, "#tipResult", timeout=1)
            if tip_element:
                tip_text = tip_element.text.strip()
                if "本课时已学完" in tip_text:
                    print("检测到完成提示文本")
                    return True
            
            # 4. 使用JavaScript检查视频播放状态
            try:
                video_status = self.driver.execute_script("""
                    var video = document.querySelector('video');
                    if (video) {
                        return {
                            ended: video.ended,
                            currentTime: video.currentTime,
                            duration: video.duration,
                            paused: video.paused
                        };
                    }
                    return null;
                """)
                
                if video_status:
                    if video_status.get('ended'):
                        print("JavaScript检测到视频播放结束")
                        return True
                    
                    # 检查是否接近结束（最后10秒内）
                    current_time = video_status.get('currentTime', 0)
                    duration = video_status.get('duration', 0)
                    if duration > 0 and (duration - current_time) <= 10:
                        print(f"视频接近结束 ({current_time:.1f}/{duration:.1f})")
                        return True
                        
            except Exception as js_error:
                print(f"JavaScript检查失败: {js_error}")
            
            return False
            
        except Exception as e:
            print(f"检查视频完成状态时出错: {e}")
            return False
    
    def time_to_seconds(self, time_str):
        """将时间字符串转换为秒数"""
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except:
            return 0
    
    def open_next_video(self, original_window, completed_count):
        """打开下一个视频"""
        try:
            self.driver.switch_to.window(original_window)
            
            # 查找所有课程项
            course_items = self.driver.find_elements(By.CSS_SELECTOR, "div.ListLi, li.ListLi")
            
            if not course_items:
                print("未找到课程列表")
                return None
            
            # 统计已跳过的课程数量
            skipped = 0
            checked = 0
            
            # 遍历课程项，找到下一个未完成的课程
            for i, item in enumerate(course_items):
                try:
                    # 查找"进入学习"按钮
                    button = item.find_element(By.XPATH, ".//a[contains(text(), '进入学习')]")
                    
                    if not button.is_displayed() or not button.is_enabled():
                        continue
                    
                    # 检查学习进度
                    try:
                        progress_elem = item.find_element(By.CSS_SELECTOR, "p.learningStatus span.lsPercents")
                        progress_text = progress_elem.text.strip()
                        progress_value = float(progress_text.replace('%', ''))
                        
                        # 获取课程标题
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, "a")
                            course_title = title_elem.get_attribute("title") or title_elem.text
                        except:
                            course_title = f"课程 {i+1}"
                        
                        # 如果进度已经是100%，跳过
                        if progress_value >= 100:
                            print(f"课程: {course_title.strip()}, 进度: {progress_value}% - 已完成，跳过")
                            skipped += 1
                            continue
                        
                    except:
                        pass
                    
                    # 检查是否是我们需要打开的那个（扣除已完成和已打开的）
                    if checked == completed_count + self.MAX_CONCURRENT_VIDEOS - skipped:
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, "a")
                            course_title = title_elem.get_attribute("title") or title_elem.text
                            print(f"打开课程: {course_title.strip()}")
                        except:
                            print(f"打开第 {i + 1} 个课程...")
                        
                        if self.click_element_safe(button):
                            time.sleep(2)
                            
                            # 切换到新窗口并设置
                            all_windows = self.driver.window_handles
                            new_window = all_windows[-1]
                            self.driver.switch_to.window(new_window)
                            self.setup_video_playback()
                            
                            return new_window
                    
                    checked += 1
                    
                except:
                    continue
            
        except Exception as e:
            print(f"打开下一个视频失败: {e}")
        
        return None
    
    def click_next_uncompleted_course(self):
        """查找并点击下一个未完成的课程"""
        try:
            print("查找'进入学习'按钮...")
            
            # 记录当前窗口句柄
            original_window = self.driver.current_window_handle
            original_windows = self.driver.window_handles
            
            # 查找所有课程项
            course_items = self.driver.find_elements(By.CSS_SELECTOR, "div.ListLi, li.ListLi")
            
            if not course_items:
                print("未找到课程列表")
                return False
            
            print(f"找到 {len(course_items)} 个课程项")
            
            # 遍历所有课程项，找到未完成的课程
            for i, item in enumerate(course_items):
                try:
                    # 查找"进入学习"按钮
                    button = item.find_element(By.XPATH, ".//a[contains(text(), '进入学习')]")
                    
                    if not button.is_displayed() or not button.is_enabled():
                        continue
                    
                    # 检查学习进度
                    try:
                        progress_elem = item.find_element(By.CSS_SELECTOR, "p.learningStatus span.lsPercents")
                        progress_text = progress_elem.text.strip()
                        
                        # 提取百分比数字
                        progress_value = float(progress_text.replace('%', ''))
                        
                        # 获取课程标题
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, "a")
                            course_title = title_elem.get_attribute("title") or title_elem.text
                        except:
                            course_title = f"课程 {i+1}"
                        
                        print(f"课程: {course_title.strip()}, 进度: {progress_value}%")
                        
                        # 如果进度已经是100%，跳过
                        if progress_value >= 100:
                            print(f"  → 课程已完成，跳过")
                            continue
                        
                        print(f"  → 课程未完成，准备进入学习")
                        
                    except Exception as e:
                        # 如果找不到进度信息，认为是未开始的课程
                        print(f"课程 {i+1}: 未找到进度信息，可能未开始")
                    
                    # 高亮显示
                    if self.HIGHLIGHT_ELEMENTS:
                        self.highlight_element(button)
                    
                    # 点击按钮
                    if self.click_element_safe(button):
                        print("成功点击'进入学习'按钮，等待页面响应...")
                        time.sleep(3)
                        
                        # 检查是否打开了新窗口
                        new_windows = self.driver.window_handles
                        if len(new_windows) > len(original_windows):
                            # 有新窗口打开，切换到新窗口
                            for window in new_windows:
                                if window not in original_windows:
                                    print("检测到新窗口，切换到视频页面...")
                                    self.driver.switch_to.window(window)
                                    break
                        
                        # 等待页面加载
                        self.wait_for_page_load()
                        
                        print(f"当前页面: {self.driver.current_url}")
                        
                        return True
                    else:
                        print(f"点击按钮失败，尝试下一个")
                        continue
                        
                except Exception as e:
                    # 如果这个课程项没有"进入学习"按钮，继续下一个
                    continue
            
            print("所有课程都已完成或无可用的'进入学习'按钮")
            return False
            
        except Exception as e:
            print(f"查找'进入学习'按钮失败: {e}")
            return False
    
    def do_all_homework(self):
        """循环完成所有作业直到全部达标"""
        print("\n" + "=" * 80)
        print("开始批量完成作业")
        print("优先级: 1.未开始的作业 > 2.不及格的作业")
        print("=" * 80)
        
        completed_count = 0
        max_attempts = 20  # 最多处理20个作业
        
        while completed_count < max_attempts:
            # 查找未完成或低分作业(优先查找未开始的)
            homework = self.find_uncompleted_homework()
            
            if not homework:
                print("\n" + "=" * 80)
                print("所有作业已完成!")
                print("=" * 80)
                break
            
            print(f"\n{'=' * 80}")
            print(f"准备完成作业: {homework['name']}")
            print(f"状态: {homework['status']}", end="")
            if homework['score'] > 0:
                print(f" | 当前分数: {homework['score']}分")
            else:
                print()
            print(f"{'=' * 80}\n")
            
            # 点击"开始作业"或"再次练习"按钮
            try:
                # 记录当前窗口句柄
                main_window = self.driver.current_window_handle
                all_windows_before = self.driver.window_handles
                
                self.highlight_element(homework['button'])
                homework['button'].click()
                time.sleep(3)
                
                # 检查是否打开了新窗口
                all_windows_after = self.driver.window_handles
                if len(all_windows_after) > len(all_windows_before):
                    # 切换到新窗口
                    new_window = [w for w in all_windows_after if w not in all_windows_before][0]
                    self.driver.switch_to.window(new_window)
                    print("已切换到作业窗口")
                    self.wait_for_page_load()
                else:
                    print("作业在当前窗口打开")
                
                # 完成作业
                result = self.complete_homework()
                
                # 处理返回结果
                if result and result.get('submitted'):
                    completed_count += 1
                    score = result.get('score', '未知')
                    passed = result.get('passed')
                    
                    print(f"\n已完成第 {completed_count} 个作业")
                    
                    if score != '未知' and score is not None:
                        print(f"本次得分: {score}分")
                        
                        if passed:
                            print(f"分数达标!")
                        elif passed is False and not self.RETRY_IF_FAILED:
                            print(f"分数未达标,但配置为不重试,跳过")
                    
                    # 如果在新窗口,关闭并返回主窗口
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                        print("已关闭作业窗口并返回主窗口")
                    
                    # 返回作业列表页面
                    print("\n返回作业列表...")
                    self.navigate_to_homework()
                    time.sleep(2)
                else:
                    print("作业未成功提交,跳过...")
                    # 如果在新窗口,也要关闭
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(main_window)
                    break
                    
            except Exception as e:
                print(f"处理作业时出错: {e}")
                break
        
        print(f"\n{'=' * 50}")
        print(f"本次共完成 {completed_count} 个作业")
        print("=" * 50)
    
    def init_ai_client(self):
        """初始化AI客户端 (支持OpenAI兼容格式和智谱AI)"""
        if self.ai_client:
            return True
        
        print("\n" + "=" * 80)
        print("正在初始化AI客户端...")
        print("=" * 80)
        
        try:
            if self.AI_PROVIDER == "openai":
                # 初始化OpenAI兼容客户端 (支持OpenAI/Kimi/DeepSeek等)
                if not self.OPENAI_API_KEY:
                    print("\n" + "=" * 80)
                    print("错误: 未配置 API Key")
                    print("请在 config.json 中配置 ai.openai_api_key")
                    print("=" * 80)
                    return False
                
                try:
                    from openai import OpenAI
                except ImportError:
                    print("正在安装openai SDK...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "--quiet"])
                    from openai import OpenAI
                
                # 初始化客户端
                self.ai_client = OpenAI(
                    api_key=self.OPENAI_API_KEY,
                    base_url=self.OPENAI_BASE_URL
                )
                print(f"✓ AI客户端对象创建成功")
                print(f"  Base URL: {self.OPENAI_BASE_URL}")
                print(f"  模型: {self.OPENAI_MODEL}")
                
                # 测试AI调用
                print("\n正在测试AI连接...")
                try:
                    test_response = self.ai_client.chat.completions.create(
                        model=self.OPENAI_MODEL,
                        messages=[
                            {"role": "user", "content": "测试"}
                        ],
                        max_tokens=5,
                        timeout=10
                    )
                    print("✓ AI连接测试成功")
                    print(f"  测试响应: {test_response.choices[0].message.content}")
                    print("=" * 80)
                    return True
                    
                except Exception as test_error:
                    print("\n" + "=" * 80)
                    print("错误: AI连接测试失败")
                    print("=" * 80)
                    print(f"错误类型: {type(test_error).__name__}")
                    print(f"错误信息: {str(test_error)}")
                    
                    # 尝试提取更详细的错误信息
                    if hasattr(test_error, 'response'):
                        print(f"HTTP状态码: {test_error.response.status_code if hasattr(test_error.response, 'status_code') else '未知'}")
                        if hasattr(test_error.response, 'text'):
                            print(f"响应内容: {test_error.response.text[:500]}")
                    
                    print("\n可能的原因:")
                    print("1. API Key 无效或已过期")
                    print("2. Base URL 配置错误")
                    print("3. 模型名称不正确")
                    print("4. 网络连接问题")
                    print("5. API 服务暂时不可用")
                    print("\n请检查 config.json 中的配置:")
                    print(f"  - ai.openai_api_key: {self.OPENAI_API_KEY[:10]}...")
                    print(f"  - ai.openai_base_url: {self.OPENAI_BASE_URL}")
                    print(f"  - ai.openai_model: {self.OPENAI_MODEL}")
                    print("=" * 80)
                    
                    import traceback
                    print("\n完整错误堆栈:")
                    traceback.print_exc()
                    print("=" * 80)
                    
                    self.ai_client = None
                    return False
                
            elif self.AI_PROVIDER == "zhipu":
                # 初始化智谱AI客户端
                if not self.ZHIPU_API_KEY:
                    print("\n" + "=" * 80)
                    print("错误: 未配置智谱AI API密钥")
                    print("请在 config.json 中配置 ai.zhipu_api_key")
                    print("=" * 80)
                    return False
                
                try:
                    from zai import ZhipuAiClient
                except ImportError:
                    print("正在安装智谱AI SDK...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "zai-sdk", "--quiet"])
                    from zai import ZhipuAiClient
                
                # 初始化客户端
                self.ai_client = ZhipuAiClient(api_key=self.ZHIPU_API_KEY)
                print(f"✓ 智谱AI客户端初始化成功 (模型: {self.ZHIPU_MODEL})")
                
                # 测试AI调用
                print("\n正在测试AI连接...")
                try:
                    test_response = self.ai_client.chat.completions.create(
                        model=self.ZHIPU_MODEL,
                        messages=[
                            {"role": "user", "content": "测试"}
                        ],
                        max_tokens=5
                    )
                    print("✓ AI连接测试成功")
                    print("=" * 80)
                    return True
                    
                except Exception as test_error:
                    print("\n" + "=" * 80)
                    print("错误: 智谱AI连接测试失败")
                    print("=" * 80)
                    print(f"错误信息: {str(test_error)}")
                    print("\n请检查:")
                    print("1. API Key 是否正确")
                    print("2. 模型名称是否正确")
                    print("3. 网络连接是否正常")
                    print("=" * 80)
                    
                    import traceback
                    traceback.print_exc()
                    
                    self.ai_client = None
                    return False
            
            else:
                print("\n" + "=" * 80)
                print(f"错误: 不支持的AI提供商: {self.AI_PROVIDER}")
                print("支持的提供商: openai, zhipu")
                print("=" * 80)
                return False
            
        except Exception as e:
            print("\n" + "=" * 80)
            print("错误: AI客户端初始化失败")
            print("=" * 80)
            print(f"错误信息: {str(e)}")
            print("=" * 80)
            import traceback
            traceback.print_exc()
            return False
    
    def answer_with_ai(self, question_text):
        """使用AI回答题目 (支持Kimi和智谱AI)"""
        if not self.ai_client:
            print("\n" + "=" * 80)
            print("错误: AI客户端未初始化")
            print("=" * 80)
            return None
        
        try:
            # 构建提示词
            prompt = f"""
你是一位知识渊博的大学教授。请仔细分析以下题目,并给出正确答案。

{question_text}

要求:
1. 认真思考题目,给出准确答案
2. 只返回一个选项字母(如A、B、C、D等)
3. 不要有任何解释,只返回字母

答案:"""
            
            # 根据不同AI提供商调用不同接口
            if self.AI_PROVIDER == "openai":
                # 调用OpenAI兼容API (支持OpenAI/Kimi/DeepSeek等)
                response = self.ai_client.chat.completions.create(
                    model=self.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一位知识渊博的AI助手，擅长回答各类问题。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                # 提取答案
                answer_raw = response.choices[0].message.content.strip()
                
            elif self.AI_PROVIDER == "zhipu":
                # 调用智谱AI
                response = self.ai_client.chat.completions.create(
                    model=self.ZHIPU_MODEL,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=5
                )
                
                # 提取答案
                answer_raw = response.choices[0].message.content.strip()
            else:
                print(f"\n" + "=" * 80)
                print(f"错误: 不支持的AI提供商: {self.AI_PROVIDER}")
                print("=" * 80)
                return None
            
            # 如果AI返回空,返回None表示失败
            if not answer_raw:
                print(f"\n" + "=" * 80)
                print(f"错误: AI返回空答案")
                print("=" * 80)
                return None
            
            answer = answer_raw.upper()
            
            # 清理答案,提取字母(支持单选和多选)
            import re
            # 先尝试匹配多选格式: A,B,C 或 A、B、C 或 ABC
            multi_match = re.findall(r'[A-Z]', answer)
            if multi_match:
                # 如果找到多个字母,返回逗号分隔的格式
                if len(multi_match) > 1:
                    extracted = ','.join(multi_match)
                    return extracted
                # 如果只有一个字母,返回单个字母
                else:
                    extracted = multi_match[0]
                    return extracted
            
            print(f"\n" + "=" * 80)
            print(f"错误: 未能从AI回答中提取有效答案")
            print(f"AI原始回答: {answer_raw}")
            print("=" * 80)
            return None
            
        except Exception as e:
            print(f"\n" + "=" * 80)
            print(f"错误: AI调用失败")
            print(f"错误信息: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()
            return None
    
    def complete_homework(self):
        """完成作业 - 使用AI或随机选择"""
        print("正在完成作业...")
        
        # 如果使用AI,初始化AI客户端
        if self.USE_AI:
            if not self.init_ai_client():
                print("AI客户端初始化失败,切换为随机选择模式")
                self.USE_AI = False  # 临时切换为随机模式
        
        # 等待页面加载
        print("等待作业页面加载...")
        time.sleep(5)
        
        # 检查是否在作业页面
        exam_container = self.find_element_safe(By.CSS_SELECTOR, "div.exam", timeout=10)
        if not exam_container:
            print("未找到作业容器 div.exam")
            # 尝试调试 - 保存当前页面截图
            try:
                screenshot_path = f"debug_screenshots/homework_page_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"已保存页面截图: {screenshot_path}")
            except:
                pass
            return False
        
        print("找到作业容器")
        
        # 查找所有题目 (根据你提供的HTML结构)
        questions = self.driver.find_elements(By.CSS_SELECTOR, "div.exam_question")
        
        if not questions:
            print("未找到题目 div.exam_question")
            # 尝试其他可能的选择器
            questions = self.driver.find_elements(By.XPATH, "//div[@class='exam_question']")
            
        if not questions:
            print("仍然未找到题目,尝试打印页面源码...")
            try:
                # 检查页面中是否有 exam_question 文本
                page_source = self.driver.page_source
                if "exam_question" in page_source:
                    print("页面源码中包含 exam_question")
                else:
                    print("页面源码中不包含 exam_question")
                    
                # 保存页面源码用于调试
                with open("debug_screenshots/homework_source.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                print("已保存页面源码: debug_screenshots/homework_source.html")
            except Exception as e:
                print(f"保存页面源码失败: {e}")
            return False
        
        print(f"找到 {len(questions)} 道题目")
        
        for i, question in enumerate(questions, 1):
            try:
                print(f"\n{'='*80}")
                print(f"第 {i}/{len(questions)} 题")
                print(f"{'='*80}")
                
                # 获取题目文本
                question_title = question.find_element(By.CSS_SELECTOR, "div.exam_question_title")
                question_text = question_title.text
                print(f"\n【题目】")
                print(question_text)
                
                # 获取所有选项(在调用AI之前)
                print(f"\n【选项】")
                options_list = question.find_elements(By.CSS_SELECTOR, "ul.question_select li")
                all_options_detail = []
                for idx, li in enumerate(options_list):
                    try:
                        mark_elem = li.find_element(By.CSS_SELECTOR, "em.select_mark")
                        option_letter = mark_elem.text.strip().split()[0]
                        option_detail = li.find_element(By.CSS_SELECTOR, "div.select_detail")
                        option_text = option_detail.text.strip()
                        all_options_detail.append(f"{option_letter}. {option_text}")
                        print(f"  {option_letter}. {option_text}")
                    except:
                        pass
                
                # 获取答案 - AI或随机
                if self.USE_AI:
                    print(f"\n【AI分析中...】")
                    answer = self.answer_with_ai(question_text)
                    
                    if not answer:
                        print(f"[错误] AI未能生成答案,跳过此题")
                        continue
                    
                    print(f"\n【AI选择】 {answer}")
                else:
                    # 随机选择答案
                    import random
                    if all_options_detail:
                        random_option = random.choice(all_options_detail)
                        answer = random_option[0]  # 获取选项字母
                        print(f"\n【随机选择】 {answer}")
                    else:
                        print(f"[错误] 无法获取选项,跳过此题")
                        continue
                
                # 查找选项并点击
                if self.select_answer_in_homework(question, answer):
                    print(f"第 {i} 题已完成\n")
                else:
                    print(f"第 {i} 题提交失败\n")
                
                # 答题间隔
                time.sleep(1)
                
            except Exception as e:
                print(f"第 {i} 题处理失败: {e}")
                continue
        
        # 提交作业
        return self.submit_homework()
    
    def select_answer_in_homework(self, question_element, answer):
        """在作业页面选择答案"""
        try:
            # 根据HTML结构,找到选项列表
            options_list = question_element.find_elements(By.CSS_SELECTOR, "ul.question_select li")
            
            if not options_list:
                print("  [错误] 未找到选项列表")
                return False
            
            # 遍历选项进行匹配
            for li in options_list:
                try:
                    # 获取选项标记(支持A/B/C/D/E/F等)
                    mark_elem = li.find_element(By.CSS_SELECTOR, "em.select_mark")
                    option_text = mark_elem.text.strip()
                    option_letter = option_text.split()[0] if option_text else ""  # 提取第一个单词
                    
                    # 如果匹配答案
                    if option_letter.upper() == answer.upper():
                        print(f"\n【提交答案】 {option_letter}")
                        
                        # 点击选项
                        try:
                            li.click()
                            time.sleep(0.3)
                        except:
                            pass
                        
                        # 确保radio被选中
                        try:
                            radio_input = li.find_element(By.CSS_SELECTOR, "input[type='radio']")
                            if not radio_input.is_selected():
                                radio_input.click()
                                time.sleep(0.2)
                        except:
                            pass
                        
                        return True
                        
                except Exception as e:
                    continue
            
            print(f"\n  [警告] 未找到匹配的选项 {answer}, 默认选择第一个")
            # 默认选择第一个选项
            if options_list:
                options_list[0].click()
                time.sleep(0.3)
                return True
                
        except Exception as e:
            print(f"  [错误] 选择答案失败: {e}")
        
        return False
    
    def submit_homework(self):
        """提交作业 - 根据配置自动或手动提交"""
        print("\n" + "=" * 50)
        print("所有题目已完成!")
        print("=" * 50)
        
        should_submit = False
        
        if self.AUTO_SUBMIT:
            # 自动提交模式
            print("\n自动提交模式已启用")
            should_submit = True
        else:
            # 手动提交模式 - 询问用户
            while True:
                user_input = input("\n是否提交作业? (输入 y 确认提交, n 取消): ").strip().lower()
                
                if user_input == 'y':
                    should_submit = True
                    break
                elif user_input == 'n':
                    print("\n已取消提交,浏览器保持打开状态")
                    print("你可以手动检查答案后再提交")
                    return {'submitted': False, 'score': None}
                else:
                    print("无效输入,请输入 y 或 n")
        
        if should_submit:
            print("\n正在提交作业...")
            
            # 记录当前URL,用于刷新
            current_url = self.driver.current_url
            
            # 根据HTML,提交按钮的ID是btn_save2
            submit_btn = self.find_element_safe(By.ID, "btn_save2", timeout=5)
            
            if submit_btn:
                print("找到提交按钮")
                self.highlight_element(submit_btn)
                submit_btn.click()
                time.sleep(5)  # 等待提交处理
                
                print("刷新页面查看分数...")
                self.driver.refresh()
                self.wait_for_page_load()
                time.sleep(3)
                
                # 尝试获取分数
                score = self.get_homework_score()
                
                if score is not None:
                    print(f"\n作业提交完成! 得分: {score}分")
                    
                    if score >= self.MIN_PASSING_SCORE:
                        print(f"恭喜!分数达标 (>= {self.MIN_PASSING_SCORE}分)")
                        return {'submitted': True, 'score': score, 'passed': True}
                    else:
                        print(f"分数未达标 (< {self.MIN_PASSING_SCORE}分)")
                        if self.RETRY_IF_FAILED:
                            print("将在下次循环中重新尝试")
                        return {'submitted': True, 'score': score, 'passed': False}
                else:
                    print("作业提交完成! (无法获取分数)")
                    return {'submitted': True, 'score': None, 'passed': None}
            else:
                print("未找到提交按钮")
                return {'submitted': False, 'score': None}
    
    def get_homework_score(self):
        """获取作业分数"""
        try:
            # 尝试多种方式查找分数
            # 方式1: 从历史记录中查找最新分数
            score_links = self.driver.find_elements(By.XPATH, "//div[@class='work_record']//a[contains(text(), '分')]")
            
            if score_links:
                # 获取最后一个(最新的)分数记录
                last_score_text = score_links[-1].text
                # 提取分数: "第X次 ( XX分 )"
                score_match = re.search(r'(\d+)分', last_score_text)
                if score_match:
                    score = int(score_match.group(1))
                    print(f"从历史记录中获取到分数: {score}分")
                    return score
            
            # 方式2: 从成绩显示区域查找
            score_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '分数') or contains(text(), '得分')]")
            for elem in score_elements:
                text = elem.text
                score_match = re.search(r'(\d+)分', text)
                if score_match:
                    score = int(score_match.group(1))
                    print(f"从成绩区域获取到分数: {score}分")
                    return score
            
            print("未能自动获取分数")
            return None
            
        except Exception as e:
            print(f"获取分数时出错: {e}")
            return None
    
    def navigate_to_exam(self):
        """导航到考试页面"""
        try:
            print("正在查找'我的考试'选项...")
            
            # 根据HTML结构,精确查找"我的考试"链接
            exam_link = self.find_element_safe(
                By.XPATH,
                "//a[@href='/University/User/Student/ExaminationQuery.aspx?m=wdks']",
                timeout=10
            )
            
            if exam_link:
                print("找到'我的考试'链接")
                self.highlight_element(exam_link)
                exam_link.click()
                self.wait_for_page_load()
                print("已进入考试页面")
                return True
            
            print("可能已在考试页面,继续...")
            return True
            
        except Exception as e:
            print(f"导航到考试页面失败: {e}")
            return False
    
    def get_unfinished_exams(self):
        """获取未完成的考试列表"""
        try:
            print("正在查找未完成的考试...")
            
            # 方法1: 点击"未完成"标签
            unfinished_tab = self.find_element_safe(
                By.CSS_SELECTOR,
                'a[data-isfinined="1"]',
                timeout=3
            )
            
            if unfinished_tab:
                print("点击'未完成'标签")
                unfinished_tab.click()
                time.sleep(2)
            else:
                # 方法2: 尝试查找包含"未完成"文字的标签
                print("尝试查找'未完成'文字标签...")
                unfinished_tab = self.find_element_safe(
                    By.XPATH,
                    "//a[contains(text(), '未完成')]",
                    timeout=3
                )
                if unfinished_tab:
                    print("找到'未完成'标签")
                    unfinished_tab.click()
                    time.sleep(2)
            
            # 查找考试列表（尝试多种选择器）
            exam_items = []
            
            # 尝试1: 使用class="exam-list"
            exam_items = self.driver.find_elements(By.CLASS_NAME, "exam-list")
            if exam_items:
                print(f"使用exam-list找到 {len(exam_items)} 个考试")
            
            # 尝试2: 使用其他可能的class
            if not exam_items:
                exam_items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='exam']")
                if exam_items:
                    print(f"使用exam相关class找到 {len(exam_items)} 个考试")
            
            # 尝试3: 查找包含"考试"文字的元素
            if not exam_items:
                exam_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'list')]")
                if exam_items:
                    print(f"使用list相关class找到 {len(exam_items)} 个项目")
            
            if not exam_items:
                print("未找到考试列表")
                return []
            
            print(f"找到 {len(exam_items)} 个考试项")
            
            # 筛选出真正未完成的考试
            uncompleted_exams = []
            for item in exam_items:
                try:
                    # 尝试多种方式查找考试状态
                    status_text = ""
                    
                    # 方法1: 查找em标签
                    try:
                        status_elem = item.find_element(By.CSS_SELECTOR, "em")
                        status_text = status_elem.text.strip()
                    except:
                        pass
                    
                    # 方法2: 查找包含状态的任何元素
                    if not status_text:
                        try:
                            status_elem = item.find_element(By.XPATH, ".//*[contains(text(), '未考') or contains(text(), '未完成')]")
                            status_text = status_elem.text.strip()
                        except:
                            pass
                    
                    # 如果找到未完成状态，或者没有找到状态（可能是未开始）
                    if "未考试" in status_text or "未完成" in status_text or not status_text:
                        # 获取考试名称
                        exam_name = "未知考试"
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, "span")
                            exam_name = title_elem.text.strip()
                        except:
                            try:
                                title_elem = item.find_element(By.XPATH, ".//span | .//p | .//div")
                                exam_name = title_elem.text.strip()
                            except:
                                pass
                        
                        if exam_name and exam_name != "未知考试":
                            print(f"  - {exam_name} [{status_text if status_text else '未开始'}]")
                            uncompleted_exams.append(item)
                        
                except Exception as e:
                    continue
            
            return uncompleted_exams
            
        except Exception as e:
            print(f"获取考试列表失败: {e}")
            return []
    
    def start_exam(self, exam_item):
        """开始一个考试"""
        try:
            # 获取考试名称
            title_elem = exam_item.find_element(By.CSS_SELECTOR, "p.mes-title span")
            exam_name = title_elem.text.strip()
            
            print(f"\n{'='*80}")
            print(f"准备开始考试: {exam_name}")
            print(f"{'='*80}")
            
            # 记录当前窗口
            main_window = self.driver.current_window_handle
            all_windows_before = self.driver.window_handles
            
            # 点击下拉菜单按钮（带箭头的那个）
            try:
                # 先尝试找到下拉按钮（el-dropdown__caret-button）
                dropdown_btn = exam_item.find_element(
                    By.CSS_SELECTOR,
                    ".el-dropdown__caret-button"
                )
                
                self.highlight_element(dropdown_btn)
                dropdown_btn.click()
                print("点击下拉菜单按钮")
                time.sleep(0.5)
                
                # 等待下拉菜单出现并点击"开始考试"按钮
                # 下拉菜单中的"开始考试"是一个button元素
                start_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@class='el-dropdown-menu__item']//button[contains(., '开始考试')]"))
                )
                start_button.click()
                print("点击'开始考试'按钮")
                
            except Exception as e:
                print(f"下拉菜单方式失败: {e}")
                # 备用方案：直接点击"操作"按钮
                print("尝试直接点击操作按钮...")
                operation_btn = exam_item.find_element(
                    By.CSS_SELECTOR,
                    ".el-button.el-button--primary"
                )
                self.highlight_element(operation_btn)
                operation_btn.click()
            
            time.sleep(1.5)
            
            # 检查是否打开了新窗口
            all_windows_after = self.driver.window_handles
            if len(all_windows_after) > len(all_windows_before):
                # 切换到新窗口
                new_window = [w for w in all_windows_after if w not in all_windows_before][0]
                self.driver.switch_to.window(new_window)
                print("已切换到考试窗口")
                self.wait_for_page_load()
            else:
                print("考试在当前窗口打开")
            
            return True
            
        except Exception as e:
            print(f"开始考试失败: {e}")
            return False
    
    def answer_exam_questions(self):
        """回答考试题目"""
        try:
            print("\n正在分析试题...")
            time.sleep(1)
            
            # 获取所有题目
            questions = self.driver.find_elements(By.CLASS_NAME, "exam_question")
            
            if not questions:
                print("未找到题目")
                return False
            
            total_questions = len(questions)
            print(f"共有 {total_questions} 道题目\n")
            
            answered_count = 0
            
            for idx, question in enumerate(questions, 1):
                try:
                    # 获取题目标题
                    question_title_elem = question.find_element(By.CLASS_NAME, "exam_question_title")
                    question_title = question_title_elem.text
                    
                    print(f"\n[{idx}/{total_questions}] {question_title[:80]}{'...' if len(question_title) > 80 else ''}")
                    
                    # 判断题目类型
                    if "[单选题]" in question_title or "[判断题]" in question_title:
                        answered = self.answer_single_choice_exam(question, question_title)
                    elif "[多选题]" in question_title:
                        answered = self.answer_multiple_choice_exam(question, question_title)
                    else:
                        print("未知题型，跳过")
                        continue
                    
                    if answered:
                        answered_count += 1
                        print(f"第 {idx} 题已完成")
                    else:
                        print(f"第 {idx} 题提交失败")
                    
                    # 随机延迟，模拟人类答题（使用配置文件中的设置）
                    delay = random.uniform(
                        self.config.get("exam", {}).get("answer_delay_min", 0.1),
                        self.config.get("exam", {}).get("answer_delay_max", 0.3)
                    )
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"处理第 {idx} 题时出错: {e}")
                    continue
            
            print(f"\n{'='*80}")
            print(f"答题完成: {answered_count}/{total_questions}")
            print(f"{'='*80}\n")
            return True
            
        except Exception as e:
            print(f"答题过程出错: {e}")
            return False
    
    def answer_single_choice_exam(self, question_element, question_title):
        """回答单选题/判断题（考试）"""
        try:
            # 获取所有选项
            options = question_element.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            
            if not options:
                print("  未找到选项")
                return False
            
            # 获取选项文本
            option_texts = []
            option_elements = question_element.find_elements(By.CLASS_NAME, "select_detail")
            for opt in option_elements:
                option_texts.append(opt.text.strip())
            
            # 检查是否使用AI答题
            if self.USE_AI:
                
                # 构建完整题目文本
                full_question = f"{question_title}\n\n选项:\n"
                for i, text in enumerate(option_texts):
                    full_question += f"{chr(65+i)}. {text}\n"
                
                # 调用AI获取答案
                answer = self.answer_with_ai(full_question)
                
                if answer:
                    print(f"→ AI选择: {answer}")
                    
                    # 根据AI返回的答案选择对应选项
                    answer_index = ord(answer.upper()) - ord('A')
                    if 0 <= answer_index < len(options):
                        self.driver.execute_script("arguments[0].click();", options[answer_index])
                        return True
                else:
                    # AI调用失败，停止任务
                    print("\n" + "=" * 80)
                    print("AI调用失败，任务已暂停")
                    print("请检查AI配置后重新运行")
                    print("=" * 80)
                    raise Exception("AI调用失败，任务终止")
            
            # 如果不使用AI，随机选择
            selected_option = random.choice(options)
            self.driver.execute_script("arguments[0].click();", selected_option)
            print(f"→ 随机选择")
            return True
            
        except Exception as e:
            print(f"  回答单选题失败: {e}")
            return False
    
    def answer_multiple_choice_exam(self, question_element, question_title):
        """回答多选题（考试）"""
        try:
            # 获取所有选项
            options = question_element.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            
            if not options:
                print("  未找到选项")
                return False
            
            # 获取选项文本
            option_texts = []
            option_elements = question_element.find_elements(By.CLASS_NAME, "select_detail")
            for opt in option_elements:
                option_texts.append(opt.text.strip())
            
            # 检查是否使用AI答题
            if self.USE_AI:
                
                # 构建完整题目文本
                full_question = f"{question_title}\n\n选项:\n"
                for i, text in enumerate(option_texts):
                    full_question += f"{chr(65+i)}. {text}\n"
                full_question += "\n这是多选题，请返回所有正确答案的字母，用逗号分隔（如：A,C,D）"
                
                # 调用AI获取答案
                answer_raw = self.answer_with_ai(full_question)
                
                if answer_raw:
                    # 解析多个答案
                    answers = [a.strip().upper() for a in answer_raw.replace('，', ',').split(',') if a.strip()]
                    print(f"→ AI选择: {', '.join(answers)}")
                    
                    # 根据AI返回的答案选择对应选项
                    for answer in answers:
                        answer_index = ord(answer) - ord('A')
                        if 0 <= answer_index < len(options):
                            self.driver.execute_script("arguments[0].click();", options[answer_index])
                    
                    return True
                else:
                    # AI调用失败，停止任务
                    print("\n" + "=" * 80)
                    print("AI调用失败，任务已暂停")
                    print("请检查AI配置后重新运行")
                    print("=" * 80)
                    raise Exception("AI调用失败，任务终止")
            
            # 如果不使用AI，随机选择2-3个选项
            num_to_select = random.randint(2, min(3, len(options)))
            selected_options = random.sample(options, num_to_select)
            
            for option in selected_options:
                self.driver.execute_script("arguments[0].click();", option)
            
            print(f"→ 随机选择 {num_to_select} 个")
            return True
            
        except Exception as e:
            print(f"  回答多选题失败: {e}")
            return False
    
    def submit_exam(self):
        """提交考试"""
        try:
            print("\n准备提交考试...")
            
            # 查找交卷按钮
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '交卷')]")
            
            if not submit_buttons:
                submit_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), '交卷')]")
            
            if not submit_buttons:
                print("未找到交卷按钮")
                return False
            
            # 检查是否自动提交
            if not self.AUTO_SUBMIT:
                print("配置为不自动提交，请手动提交")
                return False
            
            # 点击交卷按钮
            print("点击交卷按钮...")
            self.highlight_element(submit_buttons[0])
            submit_buttons[0].click()
            time.sleep(2)
            
            # 确认提交（如果有确认对话框）
            try:
                confirm_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '确定')]"))
                )
                confirm_btn.click()
                print("考试已提交")
                time.sleep(2)
            except:
                print("考试已提交（无需确认）")
                time.sleep(2)
            
            # 等待考试结束页面加载
            print("等待考试结束页面...")
            time.sleep(1)
            
            # 直接返回首页
            print("返回首页...")
            self.driver.get(self.config["website"]["url"])
            time.sleep(2)
            print("已返回首页")
            
            return True
            
        except Exception as e:
            print(f"提交考试失败: {e}")
            return False
    
    def do_all_exams(self):
        """完成所有考试"""
        try:
            print("\n" + "=" * 80)
            print("开始批量完成考试")
            print("=" * 80)
            
            # 如果使用AI，初始化AI客户端
            if self.USE_AI:
                print("\n正在初始化AI客户端...")
                if not self.init_ai_client():
                    print("\n" + "=" * 80)
                    print("错误: AI客户端初始化失败")
                    print("请检查config.json中的AI配置")
                    print("=" * 80)
                    return False
                print("AI客户端初始化完成\n")
            
            completed_count = 0
            exam_number = 0
            
            # 循环处理考试，每次只处理第一个
            while True:
                exam_number += 1
                
                # 导航到考试页面
                if not self.navigate_to_exam():
                    print("无法进入考试页面")
                    break
                
                # 获取未完成的考试列表
                exam_items = self.get_unfinished_exams()
                
                if not exam_items:
                    print("\n没有更多未完成的考试")
                    break
                
                # 只处理第一个考试
                try:
                    print(f"\n{'='*80}")
                    print(f"处理第 {exam_number} 个考试 (剩余 {len(exam_items)} 个)")
                    print(f"{'='*80}")
                    
                    # 开始考试（使用第一个考试项）
                    if not self.start_exam(exam_items[0]):
                        print("开始考试失败，跳过")
                        continue
                    
                    # 回答题目
                    if not self.answer_exam_questions():
                        print("答题失败，跳过")
                        continue
                    
                    # 提交考试（会自动返回首页）
                    if self.submit_exam():
                        completed_count += 1
                        print(f"\n第 {exam_number} 个考试已完成")
                    else:
                        print(f"\n第 {exam_number} 个考试提交失败")
                    
                    # 短暂延迟后继续下一个
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"处理考试时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # 尝试返回首页继续
                    try:
                        print("\n尝试返回首页...")
                        self.driver.get(self.config["website"]["url"])
                        time.sleep(2)
                    except:
                        print("返回首页失败，停止任务")
                        break
                    continue
            
            print(f"\n{'='*80}")
            print(f"考试完成统计: 共完成 {completed_count} 个考试")
            print(f"{'='*80}")
            return True
            
        except Exception as e:
            print(f"完成考试过程出错: {e}")
            return False
    
    def run(self):
        """运行主程序"""
        try:
            # 1. 启动浏览器并访问网站
            if not self.setup_browser():
                return
            
            # 2. 自动登录
            if not self.auto_login():
                print("登录失败，程序退出")
                return
            
            print("\n请选择要执行的任务:")
            print("1. 学习课程视频")
            print("2. 完成作业")
            print("3. 完成考试")
            print("4. 学习课程 + 完成作业")
            print("5. 完成作业 + 完成考试")
            print("6. 全部任务（视频 + 作业 + 考试）")
            
            choice = input("请输入选择 (1-6): ").strip()
            
            # 执行任务
            if choice in ['1', '4', '6']:
                print("\n开始学习课程...")
                self.navigate_to_courses()
                self.play_first_video()
            
            if choice in ['2', '4', '5', '6']:
                print("\n开始完成作业...")
                self.navigate_to_homework()
                self.do_all_homework()
            
            if choice in ['3', '5', '6']:
                print("\n开始完成考试...")
                self.do_all_exams()
            
            print("\n所有任务执行完成!")
            input("按回车键退出...")
            
        except KeyboardInterrupt:
            print("\n用户中断执行")
        except Exception as e:
            print(f"\n执行过程中出现错误: {e}")
        finally:
            # 不关闭浏览器，保持打开状态
            print("脚本执行完成，浏览器保持打开状态")
            print("如需关闭浏览器，请手动关闭")

def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("欢迎使用湖南外国语职业学院自动化学习脚本!".center(70))
    print("=" * 70)
    print("本脚本完全开源免费，仅供学习交流使用".center(68))
    print("禁止用于商业用途和任何违法违规行为".center(68))
    print("=" * 70)
    print("\n脚本将自动启动浏览器、访问网站并登录")
    print("所有配置都在config.json文件中")
    print("=" * 70 + "\n")
    
    try:
        # 直接创建并运行机器人
        bot = AutoStudyBot()
        
        # 验证必要属性
        if not hasattr(bot, 'AI_PROVIDER'):
            print("错误: AI配置未正确加载")
            print("请检查config.json文件是否正确")
            input("按回车键退出...")
            return
        
        bot.run()
    except Exception as e:
        print(f"\n程序初始化失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
