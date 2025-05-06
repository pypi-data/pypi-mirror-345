# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/28 10:31
# 文件名称： check_dp_login.py
# 项目描述： 检测DrissionPage是否登录指定网站
# 开发工具： PyCharm
from typing import Union, Tuple
from wechat_draft.utils.logger import log
from DrissionPage import (Chromium, ChromiumOptions)
from DrissionPage._pages.chromium_tab import ChromiumTab


def dp_is_login(url: str, login_text: str,
                fuzzy_search: bool = False,
                timeout: int = 10,
                max_screen: bool = True,
                dp_browser: Chromium = None,
                hide_browser: bool = False,
                close_browser: bool = True,
                return_browser: bool = False
                ) -> Union[bool, Tuple[bool, Chromium, ChromiumTab]]:
    """
    检查是否已经使用DrissionPage预先登录了指定的网站
    https://drissionpage.cn/tutorials/functions/headless/

    :param url: 要访问的网址
    :param login_text: 登录成功后的标志文本：出现了该文本，则认为已经登录成功
    :param fuzzy_search: 是否模糊搜索，默认为False，表示精确匹配。如果为True，则表示模糊搜索，即只要包含login_text的文本，都视为登录成功。
    :param max_screen: 是否最大化窗口，默认为True
    :param timeout: 超时时间，单位为秒。你可以将时间设置的长一点，然后等待手动登录。
    :param dp_browser: 使用的DrissionPage对象
    :param hide_browser: 是否隐藏浏览器窗口，该模式下 dp_browser  参数将失效！
    :param close_browser: 是否关闭浏览器窗口
    :param return_browser: 是否返回浏览器对象，如果为True，则返回[登录成功标志，浏览器对象，Tab对象]，并且此时 close_browser  参数将失效！
    :return:
    """
    if hide_browser:
        co = ChromiumOptions()
        # 隐藏浏览器窗口
        co.headless(True)
        co.set_argument('--no-sandbox')  # 无沙盒模式
        browser = Chromium(co)
    else:
        browser = dp_browser or Chromium()

    tab = browser.latest_tab
    if max_screen:
        # 最大化窗口
        tab.set.window.max()

    tab.get(url)

    try:
        # https://drissionpage.cn/browser_control/get_elements/sheet
        if fuzzy_search:
            ret = tab.ele(f'text:{login_text}', timeout=timeout)
        else:
            ret = tab.ele(f'text={login_text}', timeout=timeout)
        result = bool(ret)
    except Exception as e:
        log.error(f"等待登录标志文本时发生错误：{e}")
        result = False

    if return_browser:
        return result, browser, tab

    if close_browser:
        try:
            tab.close(others=True)
            browser.quit()
        except Exception as e:
            log.error(f"关闭浏览器窗口时发生错误：{e}")

    return result
