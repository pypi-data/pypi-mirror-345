# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/27 21:14
# 文件名称： wechat_draft_test.py
# 项目描述： 
# 开发工具： PyCharm
from dataclasses import dataclass
from wechat_draft import WechatDraft


@dataclass
class WechatConfig:
    """微信公众号配置"""

    app_id: str = "wx44bb72cca0ea65d6"
    app_secret: str = "c9f743480b9debcda8440c4b06c33253"


def main():
    wechat = WechatDraft(WechatConfig.app_id, WechatConfig.app_secret)

    # # 封面图片
    # image_info = wechat.add_permanent_material(material_type="image", file_path="./test.jpg")
    # cover_image_id = image_info.get('media_id')
    # print(cover_image_id)

    wechat.create_draft(
        title="测试文章3",
        content="xxx",
        cover_pic='./test.jpg'

    )


if __name__ == '__main__':
    main()
