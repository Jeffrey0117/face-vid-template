from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re
from typing import List, Dict, Any, Optional


class InstagramScraper:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None

    def _init_driver(self, headless: bool = True):
        """初始化 WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def _cleanup(self):
        """清理"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def get_account_info(self, username: str) -> Dict[str, Any]:
        """獲取帳號基本資訊"""
        try:
            self._init_driver(headless=True)

            url = f"https://www.instagram.com/{username}/"
            self.driver.get(url)

            time.sleep(3)

            # 檢查帳號是否存在
            if "Sorry, this page isn't available" in self.driver.page_source:
                return {"error": "帳號不存在"}

            # 嘗試獲取帳號資訊
            info = {
                "username": username,
                "exists": True
            }

            # 獲取粉絲數等資訊（可能被擋）
            try:
                meta_elements = self.driver.find_elements(By.CSS_SELECTOR, "meta[property='og:description']")
                if meta_elements:
                    description = meta_elements[0].get_attribute("content")
                    # 解析 "123 Followers, 456 Following, 789 Posts"
                    info["description"] = description
            except:
                pass

            return info

        except Exception as e:
            return {"error": str(e)}

        finally:
            self._cleanup()

    def get_reels_urls(self, username: str, max_reels: int = 50) -> Dict[str, Any]:
        """獲取帳號的 Reels URL 列表"""
        try:
            self._init_driver(headless=True)

            # 訪問 Reels 頁面
            url = f"https://www.instagram.com/{username}/reels/"
            self.driver.get(url)

            # 等待頁面載入
            time.sleep(5)

            # 嘗試處理 cookie 彈窗
            try:
                cookie_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept') or contains(text(), 'Decline')]")
                if cookie_btns:
                    cookie_btns[0].click()
                    time.sleep(1)
            except:
                pass

            page_src = self.driver.page_source

            # 檢查頁面
            if "Sorry, this page isn't available" in page_src:
                return {"error": "帳號不存在", "urls": []}

            # 先檢查私人帳號（比登入檢查優先）
            if "This account is private" in page_src or "此帳號為私人帳號" in page_src:
                return {"error": "這是私人帳號", "urls": []}

            # 檢查是否需要登入（只有在沒有找到 reel 連結時才報錯）
            has_login_prompt = "登入" in page_src or "/accounts/login/" in page_src or "Log in" in page_src

            reels_urls = set()
            last_count = 0
            no_new_count = 0

            # 滾動加載更多
            for scroll_count in range(20):  # 最多滾動 20 次
                # 找所有 reel 連結 - 嘗試多種選擇器
                links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/reel/']")

                # 如果找不到，嘗試其他選擇器
                if not links:
                    links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")

                # 也嘗試找 /reels/ 連結
                if not links:
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/reels/']")

                for link in links:
                    href = link.get_attribute("href")
                    if href and "/reel/" in href:
                        # 清理 URL
                        match = re.search(r'https://www\.instagram\.com/reel/([^/]+)', href)
                        if match:
                            clean_url = f"https://www.instagram.com/reel/{match.group(1)}/"
                            reels_urls.add(clean_url)

                # 檢查是否有新的
                if len(reels_urls) == last_count:
                    no_new_count += 1
                    if no_new_count >= 3:
                        break
                else:
                    no_new_count = 0
                    last_count = len(reels_urls)

                # 達到上限
                if len(reels_urls) >= max_reels:
                    break

                # 滾動
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            urls = list(reels_urls)[:max_reels]

            # 如果沒找到任何 reels 且有登入提示，回報登入錯誤
            if len(urls) == 0 and has_login_prompt:
                return {"error": "Instagram 需要登入才能查看此帳號的 Reels。請嘗試使用網址模式直接貼上 Reel 連結。", "urls": []}

            return {
                "username": username,
                "count": len(urls),
                "urls": urls
            }

        except TimeoutException:
            return {"error": "頁面載入逾時", "urls": []}

        except WebDriverException as e:
            return {"error": f"瀏覽器錯誤: {str(e)[:50]}", "urls": []}

        except Exception as e:
            return {"error": str(e), "urls": []}

        finally:
            self._cleanup()


# 全域實例
scraper = InstagramScraper()
