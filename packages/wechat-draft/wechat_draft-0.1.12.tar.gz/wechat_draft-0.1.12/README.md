# WechatDraft: 微信公众号草稿与永久素材管理工具

## 项目简介

WechatDraft 是基于 Python 的微信公众号开发工具，提供**草稿箱全生命周期管理**、**永久素材精细化操作**及**内容发布流程支持**
。新增图片消息管理、发布状态追踪、素材列表检索等功能，支持图文/图片消息混合操作，覆盖公众号内容管理全场景，助力开发者高效完成内容运营。

## 新增特性（2025.04 更新）

### 0.1.0

- **文章发布历史获取：** 新增 PublishHistory 类，使用 DrissionPage 获取微信公众号文章发布记录。该类仅支持在windows下使用，并且需要安装
  `pypiwin32`，可以使用pip install -U wechat_draft[windows] 安装

### 0.0.8

- **草稿箱增强**
    - 支持**图片消息（newspic）**创建，可批量上传最多20张图片
    - 新增草稿列表查询`get_draft_list()`、草稿总数统计`count_drafts()`
    - 通用裁剪参数`crop_percent_list`支持多比例混合裁剪（1:1/16:9/2.35:1）

- **永久素材扩展**
    - 支持素材列表分页查询`get_material_list()`，可按类型（image/video/news）筛选
    - 新增素材总数统计`get_material_total()`，实时监控素材库存状态

- **内容发布管理**
    - 提供发布任务提交`publish_article()`、状态查询`get_publish_status()`、发布记录检索`get_publish_list()`
    - 支持已发布文章删除`delete_publish_article()`，含单篇/全量删除模式

- **功能优化**
    - 新增日志级别控制`log_level`参数，支持DEBUG/INFO等多级日志
    - 图片素材校验升级，支持PNG格式及更精准的尺寸警告
    - 错误处理增强，覆盖发布失败、素材超限等新增场景

## 准备工作

1. 使用该功能需要先准备微信公众号账号，并获取 AppID 和 AppSecret。

    - 进入[微信公众号后台页面](https://mp.weixin.qq.com/)，依次进入 `设置与开发 > 开发接口管理 > 基本设置` 获取 `AppID` 和
      `AppSecret`。

2. 将服务器IP地址（测试环境的IP地址）加入`IP白名单`。

## 安装

```bash
pip install -U wechat_draft
```

## 快速开始

### 一、初始化（新增日志配置）

```python
from wechat_draft import WechatDraft

# 初始化客户端（新增log_level参数，默认INFO）
app = WechatDraft(
    app_id="你的APP ID",
    app_secret="你的APP Secret",
    log_level="DEBUG"  # 开启调试日志
)
```

### 二、图片消息草稿创建（新增）

```python
# 上传图片素材获取永久ID
image_media_id = app.add_permanent_material(
    material_type="image",
    file_path="image1.jpg"
)[0]

# 构建图片消息结构
image_info = {
    "image_list": [
        {"image_media_id": image_media_id},
        {"image_media_id": app.add_permanent_material("image", "image2.jpg")[0]}
    ]
}

# 创建图片消息草稿
draft_id = app.create_draft(
    title="旅行摄影集",
    content="风景图片合集",  # 图片消息正文仅支持纯文本
    article_type="newspic",  # 指定为图片消息类型
    image_info=image_info,
    need_open_comment=1
)
print(f"图片消息草稿创建成功，ID：{draft_id}")
```

### 三、发布管理示例（新增）

```python
# 发布草稿
publish_id = app.publish_article(draft_id)
print(f"发布任务提交成功，ID：{publish_id}")

# 监控发布状态（轮询直至完成）
while True:
    status = app.get_publish_status(publish_id)
    if status["publish_status"] == 1:
        time.sleep(5)  # 发布中，等待5秒重试
    else:
        print(f"最终状态：{status['errmsg']}")
        break
```

## API 参考（新增与更新部分）

### 类初始化参数（更新）

| 参数                  | 类型    | 说明                                                              |
|---------------------|-------|-----------------------------------------------------------------|
| `log_level`         | `str` | 日志级别（DEBUG/INFO/WARNING/ERROR），默认INFO                           |
| `access_token_file` | `str` | Access Token 缓存路径，默认存储于系统临时目录下的`wechat_draft_access_token.json` |

### 新增核心方法

#### 1. 永久素材管理

- **`get_material_total(material_type=None)`**
    - 功能：获取指定类型素材总数（image/video/voice/news）
    - 参数：`material_type` 可选，默认返回全部类型统计
    - 返回：`dict` 如 `{"image_count": 100, "news_count": 50}`

- **`get_material_list(material_type='news', offset=0, count=20)`**
    - 功能：分页查询永久素材列表
    - 参数：
        - `material_type`：素材类型（image/video/voice/news），默认news
        - `offset`：偏移量，从0开始
        - `count`：每页数量（1-20）
    - 返回：`dict` 包含`total_count`（总数）和`item`（素材列表）

#### 2. 草稿箱管理

- **`get_draft_list(offset=0, count=20, no_content=True)`**
    - 功能：分页获取草稿列表
    - 参数：`no_content` 设为True可省略正文内容，提升性能
    - 返回：`dict` 包含草稿基本信息（标题、类型、创建时间）

- **`count_drafts()`**
    - 功能：统计草稿总数
    - 返回：`int` 草稿数量

#### 3. 发布管理

- **`publish_article(media_id)`**
    - 功能：提交草稿发布任务
    - 参数：`media_id` 草稿ID
    - 返回：`publish_id` 发布任务ID

- **`get_publish_status(publish_id)`**
    - 功能：查询发布状态
    - 返回：`dict` 包含`publish_status`（0-成功，1-进行中，2-原创失败等）

#### 4. 图片消息支持（`create_draft`参数更新）

| 参数             | 类型     | 说明                                                               |
|----------------|--------|------------------------------------------------------------------|
| `article_type` | `str`  | 设为`newspic`时创建图片消息                                               |
| `image_info`   | `dict` | 图片列表，格式：`{"image_list": [{"image_media_id": "ID"}, ...]}`        |
| `product_info` | `dict` | 商品信息（需开通权限），格式：`{"footer_product_info": {"product_key": "xxx"}}` |

## 注意事项（新增）

1. **图片消息限制**
    - 单条图片消息最多包含20张图片，总大小不超过10MB
    - 图片需先上传为永久素材，不支持临时素材ID

2. **发布机制**
    - 发布任务提交后需通过`get_publish_status`轮询状态
    - 原创声明失败、审核不通过等异常会在状态中返回具体错误码

3. **权限依赖**
    - 商品功能需公众号开通电商类目，并配置微信小店权限
    - 发布接口调用频率限制为200次/分钟

## 注意事项

1. **草稿箱开关**：`open_draft()` 为不可逆操作，开启后需等待服务器生效。
2. **素材限制**：
    - 永久图片素材大小 ≤10MB，支持 `bmp/png/jpeg/jpg/gif`。
    - 图文消息正文图片需通过 `upload_news_image()` 上传（≤1MB，JPEG格式）。
3. **裁剪参数**：优先使用 `crop_percent_list` 通用参数，传统坐标参数（如 `pic_crop_235_1`）将逐步淘汰。
4. **权限问题**：部分接口（如商品功能）需公众号开通对应权限。
5. 使用中如有问题，可通过日志输出（`log_level=DEBUG`）定位问题，或联系开发者获取代码级支持。

## 贡献与反馈（更新）

- **项目地址**：[Gitee仓库](https://gitee.com/xiaoqiangclub/wechat_draft)
- **反馈渠道**：
    - 微信公众号「xiaoqiangclub」留言
    - Gitee Issues 提交功能请求或BUG报告
- **开发路线图**：即将支持多公众号管理、定时发布计划

## 开发者信息

- **维护者**：Xiaoqiang
- **更新日志**：2025.04 新增发布管理模块，优化素材校验逻辑
