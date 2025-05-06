# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/26 10:48
# 文件名称： get_publish_data.py
# 项目描述： 获取文章发布历史数据
# 开发工具： PyCharm

from wechat_draft import PublishHistory


async def get_publish_data():
    publish_history = PublishHistory('./publish_history.json', hide_browser=True, pages_num=2,stop_to_date='04月17日')
    return publish_history.run()


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(get_publish_data()))
