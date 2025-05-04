# 开发人员： Xiaoqiang
# 微信公众号:  XiaoqiangClub
# 开发时间： 2025-04-19
# 文件名称： tests/test_example.py
# 项目描述： 测试示例文件
# 开发工具： PyCharm
from dataclasses import dataclass
from wechat_draft import WechatDraft  # 假设你的 WechatDraft 类在 wechat_draft.py 文件中
import os


@dataclass
class WechatConfig:
    """微信公众号配置"""
    app_id: str = "wx44bb72cca0ea65d6"
    app_secret: str = "c9f743480b9debcda8440c4b06c33253"
    access_token_file: str = None  # 替换为你希望保存 access_token 的文件路径
    log_level: str = 'DEBUG'  # 设置日志级别


def main():
    """主函数，用于演示 WechatDraft 的使用"""

    # 1. 加载配置
    config = WechatConfig()

    # 2. 初始化 WechatDraft 实例
    wechat = WechatDraft(
        app_id=config.app_id,
        app_secret=config.app_secret,
        access_token_file=config.access_token_file,
        log_level=config.log_level
    )
    #
    # # 3. 获取 Access Token
    # access_token = wechat.get_access_token()
    # if access_token:
    #     print(f"成功获取 Access Token: {access_token}")
    # else:
    #     print("获取 Access Token 失败，请检查配置。")
    #     return  # 停止执行
    #
    # # 4.  这里可以根据你的需求，调用 WechatDraft 类的其他方法
    # # 例如，以下是一些示例：
    #
    # # a. 统计草稿数量
    # draft_count = wechat.count_drafts()
    # if draft_count is not None:
    #     print(f"草稿箱中共有 {draft_count} 篇文章。")
    # else:
    #     print("统计草稿数量失败。")
    #
    # # b. 获取草稿列表（只获取概要信息，不包含内容）

    # if draft_list:
    #     print("获取到草稿列表：")
    #     for item in draft_list.get('item'):
    #         print(f"- 标题: {item['content']['news_item'][0]['title']}, 更新时间: {item['update_time']}")
    # else:
    #     print("获取草稿列表失败。")

    # # c. 上传图片
    # image_path = "test.jpg"  # 替换为你的图片路径
    # if os.path.exists(image_path):
    #     image_url = wechat.upload_news_image(image_path)
    #     if image_url:
    #         print(f"图片上传成功，URL: {image_url}")
    #     else:
    #         print("图片上传失败。")
    # else:
    #     print(f"{image_path} 文件不存在，请提供图片路径。")
    #
    # # d. 检查草稿箱开关状态
    # switch_state = wechat.check_draft_switch_state()
    # if switch_state is True:
    #     print(f"草稿箱开关状态: {'开启' if switch_state else '关闭'}")
    # else:
    #     print("检查草稿箱开关状态失败。")

    # 开启草稿箱
    # print(wechat.open_draft())
    # print(wechat.count_drafts())
    # print(wechat.get_publish_list())
    # print(wechat.get_publish_article('_XTsMkhP1p2Sp2CLblH9zXpDBKJSdtRgb7tSQToJyiCY3XkNSfNmEHehubeoFmd9'))

    # e. 创建草稿
    # 示例：新增永久图片素材
    # {"media_id": "7W9OX-_svPHG2Ejnx73Q22iE2s4cfhO99CdzIbf_LqAt9gNEkeVDpT7OQ_5hbKRS", "url": "http://mmbiz.qpic.cn/sz_mmbiz_jpg/OAeCMzEJygII1wAl7lwrFiclUJAXfHcWOa9gs1iammZ7omzqicc0H1CdFb5Oqx4HuoN8NsJahdicqCIibCxIvulC8ZQ/0?wx_fmt=jpeg", "item": []}
    image_info = wechat.add_permanent_material(material_type="image", file_path="./test.jpg")
    cover_image_id = image_info.get('media_id')
    print(cover_image_id)
    # cover_image_id = "7W9OX-_svPHG2Ejnx73Q22iE2s4cfhO99CdzIbf_LqAt9gNEkeVDpT7OQ_5hbKRS"
    # crop_percent_list = wechat.get_crop_params('test.jpeg', (100, 150), 2500).get('crop_percent_list')
    #
    # # 示例：创建图文消息草稿，使用新增的图片素材作为封面
    # if cover_image_id:
    #     wechat.create_draft(
    #         title="测试图文消息",
    #         content="<p>这是图文消息内容，包含<em>富文本</em>和图片</p><img src=\"图片URL\">",
    #         article_type="news",
    #         thumb_media_id=cover_image_id,
    #         author="XiaoqiangClub",
    #         digest="这是图文消息摘要",
    #         crop_percent_list=crop_percent_list,
    #         need_open_comment=1,
    #         only_fans_can_comment=0
    #     )

    # print(wechat.get_permanent_material("7W9OX-_svPHG2Ejnx73Q201O3lqOYmeZm-xRfAqQ-0TRoTe8FRB3dZiv2cuOCW8W"))
    # print(wechat.delete_permanent_material("7W9OX-_svPHG2Ejnx73Q201O3lqOYmeZm-xRfAqQ-0TRoTe8FRB3dZiv2cuOCW8W"))
    # print(wechat.get_material_list())
    # print(wechat.get_all_permanent_news(save_path="./draft_list.json"))
    # print(wechat.get_publish_list())
    print(wechat.get_draft_list())
    #7W9OX-_svPHG2Ejnx73Q2xU6CLMKYhmwz_mwSIFPFC2-kGsVkX31IQaFNYTizCFS
    # print(wechat.mass_publish_mpnews('7W9OX-_svPHG2Ejnx73Q2xU6CLMKYhmwz_mwSIFPFC2-kGsVkX31IQaFNYTizCFS'))
if __name__ == "__main__":
    main()
