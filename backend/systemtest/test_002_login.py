from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Test002():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_002(self):
        self.driver.get("https://bbs.nansin.top/")
        self.driver.set_window_size(1294, 766)

        # 点击登录按钮
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-btn:nth-child(1)"))
        )
        login_btn.click()

        # 悬停操作
        actions = ActionChains(self.driver)
        actions.move_to_element(login_btn).perform()

        # 输入用户名和密码
        self.driver.find_element(By.ID, "normal_login_name").send_keys("kiwitest1")
        self.driver.find_element(By.ID, "normal_login_password").send_keys("kiwi4567")

        # 点击登录按钮
        self.driver.find_element(By.CSS_SELECTOR, ".login-form-button").click()

        # 等待头像加载（注意：等待时间应为秒）
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//img[@alt='kiwitest1']"))
        )

        # 验证头像是否存在
        elements = self.driver.find_elements(By.XPATH, "//img[@alt='kiwitest1']")
        assert len(elements) > 0
