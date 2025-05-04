# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/26 08:52
# 文件名称： set_publish_params.py
# 项目描述： 设置微信公众号文章群发参数
# 开发工具： PyCharm
import time
from typing import List, Union
from DrissionPage import Chromium
from wechat_draft.utils.logger import log
from DrissionPage._functions.keys import Keys


class SetPublishParams:
    def __init__(self, titles: Union[str, List[str]] = None, set_digest: str = None, set_original: bool = False,
                 author: str = "XiaoqiangClub", quick_reprint: bool = False, open_comment: bool = False,
                 set_praise: bool = False, set_pay: bool = False, set_collect: str = None,
                 original_link: str = None, hide_browser: bool = False):
        """
        设置微信公众号文章群发参数
        注意：该类仅支持windows下使用，安装命令：pip install -U wechat_draft[windows]

        :param titles: 文章标题列表，支持单个标题或列表，为None，表示所有文章
        :param set_digest: 文章摘要，默认为None，不设置摘要
        :param set_original: 是否设置原创，默认为False
        :param author: 文章作者，默认为None，当设置原创的时候需要用到该参数，默认为：XiaoqiangClub
        :param quick_reprint: 是否开启快捷转载，默认为False。注意：当 set_pay 为True 时，该参数自动设置为False
        :param open_comment: 是否开启留言，默认为False
        :param set_praise: 是否开启赞赏，默认为False
        :param set_pay: 是否开启付费，默认为False，该功能作者暂时用不到，以后再写
        :param set_collect: 设置合集，默认为None
        :param original_link: 原文链接，默认为None
        :param hide_browser: 是否隐藏浏览器窗口，默认为False，限制在Windows系统下有效，并且需要安装 pypiwin32库
        """
        self.titles: list = [titles] if isinstance(titles, str) else titles
        self.set_digest = set_digest
        self.set_original = set_original
        self.author = author
        self.quick_reprint = quick_reprint
        self.open_comment = open_comment
        self.set_praise = set_praise
        self.set_pay = set_pay
        self.set_collect = set_collect
        # 合集总长度不能超过30个字符
        if self.set_collect and len(''.join(self.set_collect)) > 30:
            log.error('合集总长度不能超过30个字符')
            raise ValueError('合集总长度不能超过30个字符')
        self.original_link = original_link
        self.hide_browser = hide_browser
        self.homepage = 'https://mp.weixin.qq.com'

    def __init_browser(self):
        """初始化浏览器"""
        self.browser = Chromium()
        self.tab = self.browser.latest_tab
        # 设置全屏:https://drissionpage.cn/browser_control/page_operation/#%EF%B8%8F%EF%B8%8F-%E7%AA%97%E5%8F%A3%E7%AE%A1%E7%90%86
        # self.tab.set.window.max()  # 设置全屏
        self.tab.set.window.show()  # 显示浏览器窗口

    def __login_homepage(self) -> None:
        """
        登录公众号后台
        """
        try:
            self.tab.get(self.homepage)
            click_login = self.tab.ele('#jumpUrl', timeout=3)
            if click_login:
                click_login.click()
                log.info("成功点击登录按钮")
        except Exception as e:
            log.error(f"登录公众号后台出错: {e}")

    def __enter_draft_box(self) -> None:
        """
        进入草稿箱
        """
        log.info('等待手动登入进入后台主页面🚬🚬🚬')
        try:
            # 等待元素出现
            if not self.tab.wait.ele_displayed('@text()=首页', timeout=60 * 5):
                log.error('登录超时，请手动登录...')
                raise TimeoutError

            if self.hide_browser:
                log.info('隐藏浏览器 主页窗口...')
                self.tab.set.window.hide()
                time.sleep(1)

            # 点击 内容管理
            self.tab.ele('@text()=内容管理').click()
            # 点击 草稿箱，新建标签页
            self.tab.ele('@text()=草稿箱').click()
            # 切换草稿显示为列表视图
            self.tab.ele('#js_listview').click()

        except Exception as e:
            log.error(f"进入草稿箱出错: {e}")

    def __set_params(self, url) -> List[dict]:
        """设置参数"""
        self.tab.get(url)

        if self.hide_browser:
            log.info('隐藏浏览器 编辑窗口...')
            self.tab.set.window.hide()
            time.sleep(1)

        # 将页面滚动到最底部
        log.info('将页面滚动到最底部...')
        self.tab.ele('.tool_bar__fold-btn fold').click()
        time.sleep(1)

        # 设置文章摘要
        if self.set_digest:
            try:
                log.info(f'设置文章摘要: {self.set_digest}')
                self.tab.actions.click('#js_description').type(Keys.CTRL_A).type(Keys.DELETE).input(
                    self.set_digest).type(Keys.CTRL_A).type(Keys.CTRL_C).type(Keys.CTRL_V)
            except Exception as e:
                log.error(f"设置文章摘要出错: {e}")

        # 设置原创
        if self.set_original:
            try:
                self.tab.ele('.js_unset_original_title').click()

                #  输入作者
                log.info(f'设置文章作者: {self.author}')
                try:
                    if self.tab.ele('.js_reward_author_uneditable'):
                        log.info('作者已填写，不可编写，请手动修改')
                    else:
                        self.tab.actions.click(
                            'xpath://*[@id="js_original_edit_box"]/div/div[3]/div[2]/div/div/span[2]').type(
                            Keys.CTRL_A).type(Keys.BACKSPACE).input(self.author).type(Keys.CTRL_A).type(
                            Keys.CTRL_C).type(Keys.CTRL_V)
                except Exception as e:
                    log.error(f"设置文章作者出错: {e}")

                # 开启 快捷转载
                try:
                    if self.quick_reprint:
                        not_open = self.tab.ele('@text()=未开启，只有白名单账号才能转载此文章')
                        if not_open:
                            log.info('开启 快捷转载')
                            not_open.prev().click()
                    else:
                        is_open = self.tab.ele('@text()=已开启，所有账号均可转载此文章')
                        if is_open:
                            log.info('关闭 快捷转载')
                            is_open.prev().click()
                except Exception as e:
                    log.error(f"开启 快捷转载出错: {e}")

                # 勾选协议和确定
                log.info('点击确定')
                self.tab.ele('@text()=确定').click()
                time.sleep(1)
                if not self.tab.ele('.js_author_explicit').text:
                    try:
                        # 勾选协议
                        log.info('勾选协议')
                        self.tab.ele('.weui-desktop-icon-checkbox').click()
                        log.info('点击确定')
                        self.tab.ele('@text()=确定').click()
                    except Exception as e:
                        log.error(f"勾选协议出错: {e}")
            except Exception as e:
                log.error(f"设置原创出错: {e}")

        # 打开赞赏
        try:
            if self.set_praise:
                log.info('即将设置打开赞赏，确保已经设置了赞赏账户！')
                if self.tab.ele('.setting-group__switch-tips js_reward_setting_tips').text != '不开启':
                    log.info('原草稿已开启了赞赏，无需设置')
                else:
                    log.info('开启赞赏...')
                    self.tab.ele('.setting-group__switch-tips js_reward_setting_tips').click()
                    # 点击确认
                    self.tab.ele('@text()=确定').click()

            else:
                if self.tab.ele('.setting-group__switch-tips js_reward_setting_tips').text != '不开启':
                    log.info('关闭赞赏...')
                    self.tab.ele('.setting-group__switch-tips js_reward_setting_tips').click()
                    self.tab.ele('@text()=赞赏类型').parent().ele('@text()=不开启').click()

                    # 点击确认
                    self.tab.ele('@text()=确定').click()

        except Exception as e:
            log.error(f"设置赞赏出错: {e}")

        # 付费，暂时用不到，以后再写
        try:
            # 留言
            if self.open_comment:
                if 'selected' not in self.tab.ele('.setting-group__switch-tips_default').parent().attr('class'):
                    log.info('开启留言...')
                    self.tab.ele('.setting-group__switch-tips_default').click()
                    # 点击开启
                    self.tab.ele('@text()=留言开关').parent().ele('@text()=开启').click()
                    # 点击确认
                    self.tab.ele('xpath://*[@id="vue_app"]/div[3]/div[1]/div/div[3]/div/div[1]/button').click()
            else:
                if 'selected' in self.tab.ele('.setting-group__switch-tips_default').parent().attr('class'):
                    log.info('关闭留言...')
                    self.tab.ele('.setting-group__switch-tips js_interaction_content').click()
                    self.tab.ele('@text()=留言开关').parent().ele('@text()=不开启').click()
                    # 点击确认
                    self.tab.ele('xpath://*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div/div[1]/button').click()
        except Exception as e:
            log.error(f"设置赞赏出错: {e}")

        # 设置合集
        try:
            # 进入合集设置界面
            self.tab.actions.click('xpath://*[@id="js_article_tags_area"]/label/div')
            time.sleep(1)

            for span in self.tab.eles('.weui-desktop-dropdown__list-ele__text'):
                if span.text.strip() == self.set_collect:
                    log.info(f'添加到合集: {self.set_collect}')
                    # 展开合集选项
                    self.tab.actions.click('@tag()=dt')
                    time.sleep(1)
                    # 点击合集
                    self.tab.actions.click(span)
                    # 点击确认
                    self.tab.ele('xpath://*[@id="vue_app"]/div[2]/div[1]/div/div[3]/div[1]/button').click()
                    break
        except Exception as e:
            log.error(f"设置合集失败: {e}")

        time.sleep(1)
        # 设置原文链接
        if self.original_link:
            try:
                self.tab.actions.click('xpath://*[@id="js_article_url_area"]/label/div')
                self.tab.actions.click('xpath:/html/body/div[17]/div/div[1]/div/div/div/span/input').type(
                    Keys.CTRL_A).type(Keys.DELETE).input(self.original_link)
                time.sleep(0.5)
                # 点击确认
                self.tab.actions.click('xpath:/html/body/div[17]/div/div[2]/a[1]')
                time.sleep(0.5)
            except Exception as e:
                log.error(f"设置原文链接出错: {e}")

        # 点击保存为草稿
        log.info('点击保存为草稿...')
        self.tab.ele('@text()=保存为草稿').click()

        # 等待保存为草稿成功
        self.tab.wait.ele_displayed('@text()=首页')
        log.info('草稿保存成功！')

    def __set_publish_params(self) -> int:
        """
        设置文章群发参数
        :return: 处理的文章数量
        """
        draft_box_url = self.tab.url
        url_params = draft_box_url.split('&action=list_card')[-1]
        # 判断标题是否为None，则获取全部文章

        page_num = 1  # 初始化页码为1
        parse_num = 0  # 初始化解析数量为0
        while True:
            log.info(f'\n====================草稿箱第 {page_num} 页数据====================')
            # 使用静态元素定位，避免动态加载的元素：https://drissionpage.cn/browser_control/get_elements/find_in_object/#%EF%B8%8F%EF%B8%8F-%E9%9D%99%E6%80%81%E6%96%B9%E5%BC%8F%E6%9F%A5%E6%89%BE
            for tr in self.tab.s_eles('css:.weui-desktop-media__list-wrp tbody.weui-desktop-table__bd tr'):
                try:
                    # 标题
                    title = tr.ele('css:.weui-desktop-vm_primary span').text
                    # 找到编辑
                    edit = tr.ele('@text()=编辑')
                    # 查找当前元素之前第一个符合条件的兄弟节点
                    div = edit.prev(1, '@tag=a')
                    url = div.attr('href') + url_params
                    if self.titles is None or title in self.titles:
                        log.info(f"正在设置文章:《{title}》的发布参数：\n{url}")
                        # 设置参数
                        self.__set_params(url)
                        parse_num += 1

                except Exception as e:
                    log.error(f"设置文章参数出错: {e}")
                    continue

            try:
                self.tab.get(draft_box_url)
                next_page_btn = self.tab.ele('@text()=下一页')
                if next_page_btn:
                    page_num += 1
                    if self.titles is not None and parse_num >= len(self.titles):
                        break

                    next_page_btn.click()
                    time.sleep(0.5)
                else:
                    break
            except Exception as e:
                log.error(f"点击下一页出错: {e}")
                break

        log.info(f'共设置了 {parse_num} 篇文章的发布参数!')
        return parse_num

    def close_browser(self) -> None:
        """
        关闭浏览器
        """
        try:
            self.tab.close()
            self.browser.quit()
            log.info("浏览器已关闭")
        except Exception as e:
            log.error(f"关闭浏览器出错: {e}")

    def run(self) -> List[dict]:
        """
        执行整个爬取流程
        """
        log.info("初始化浏览器...")
        self.__init_browser()

        log.info("尝试登录首页...")
        self.__login_homepage()

        log.info("进入草稿箱...")
        self.__enter_draft_box()

        log.info("开始设置发布参数...")
        parse_num = self.__set_publish_params()

        log.info("爬取完成，关闭浏览器...")
        self.close_browser()

        return parse_num
