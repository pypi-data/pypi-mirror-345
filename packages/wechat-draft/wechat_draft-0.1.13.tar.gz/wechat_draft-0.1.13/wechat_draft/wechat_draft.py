# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/4/19 16:17
# 文件名称： wechat_draft.py
# 项目描述： 微信公众号文章草稿和永久素材管理
# 开发工具： PyCharm
import os
import time
import json
import requests
import tempfile
from PIL import Image
from typing import Optional, Tuple, Dict
from wechat_draft.utils.logger import log
from wechat_draft.utils.error_code import handle_error


class WechatDraft:
    """
    微信公众号文章草稿和永久素材管理
    """

    def __init__(self, app_id: str, app_secret: str, access_token_file: str = None):
        """
        初始化微信公众号文章草稿和永久素材管理

        :param app_id: 公众号app_id
        :param app_secret: 公众号app_secret
        :param access_token_file: access_token 缓存文件路径，默认保存在系统临时目录下的 wechat_draft_access_token.json
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token_file = access_token_file or os.path.join(tempfile.gettempdir(),
                                                                   'wechat_draft_access_token.json')
        self.access_token = None
        self.access_token_expire_time = 0

    # ====================== Access Token 管理 ======================
    def get_access_token(self) -> Optional[str]:
        """
        获取并管理access_token（自动处理缓存和刷新）
        https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html
        """
        if self._load_access_token():
            current_time = time.time()
            if self.access_token and current_time < self.access_token_expire_time:
                log.debug("正在使用本地缓存的 access_token")
                return self.access_token

        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"

        try:
            response = requests.get(url, timeout=10)
            data = self._parse_response(response)
            if data.get("errcode"):
                log.error(f"获取access_token失败: 错误代码 {data['errcode']}, 错误信息 {data['errmsg']}")
                return None

            self.access_token = data["access_token"]
            self._save_access_token(expires_in=data.get("expires_in", 7200))
            return self.access_token

        except Exception as e:
            log.error(f"获取access_token网络请求失败: {e}")
            return None

    def _load_access_token(self) -> bool:
        """
        从本地文件加载access_token
        """
        if os.path.exists(self.access_token_file):
            try:
                with open(self.access_token_file, "r") as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.access_token_expire_time = data.get("expire_time", 0)
                log.debug("成功加载本地缓存的 access_token")
            except json.JSONDecodeError:
                log.warning(f"access_token 文件 {self.access_token_file} JSON解码失败，将重新获取")
                return False
            except Exception as e:
                log.error(f"加载 access_token 文件失败: {e}")
                return False
            return True
        return False

    def _save_access_token(self, expires_in: int = 7200):
        """
        保存access_token到本地文件（提前10分钟过期）
        """
        current_time = time.time()
        self.access_token_expire_time = current_time + expires_in - 600  # 提前10分钟
        try:
            with open(self.access_token_file, "w") as f:
                json.dump({
                    "access_token": self.access_token,
                    "expire_time": self.access_token_expire_time
                }, f)
            log.info(f"access_token 已保存到文件 {self.access_token_file}")
        except Exception as e:
            log.error(f"保存 access_token 失败: {e}")

    # ====================== 错误处理 ======================
    def _parse_response(self, response: requests.Response,
                        error_key: str = "errcode", utf8: bool = True) -> Optional[dict]:
        """
        统一解析 API 响应结果，并处理错误

        :param response: API 响应对象
        :param error_key: API 错误返回结果的键名
        :param utf8: 是否将响应内容转换为UTF-8编码，默认为True
        :return:
        """
        # 检查HTTP状态码
        response.raise_for_status()
        if utf8:
            # 指定响应内容的编码为 UTF - 8
            response.encoding = 'utf-8'

        try:
            result: dict = response.json()
            log.debug(f"API 响应内容: {json.dumps(result, ensure_ascii=False)}")  # 记录完整的响应内容

            if error_key in result and result[error_key] != 0:  # 显式检查 errcode 是否为 0 表示成功
                handle_error(result, log)
                return None
            else:
                return result
        except Exception as e:
            log.error(f"API 响应内容解析失败: {e}")
            return None

    # ====================== 素材校验 ======================
    def _validate_permanent_image_material(self, file_path: str, max_size_mb: int = 10):
        """
        校验永久图片素材的文件约束 (大小, 格式)
        主要校验文件大小和格式 (API 强制要求), 尺寸为 WeChat 平台展示效果建议.
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html

        :param file_path: 图片文件路径
        :param max_size_mb: 最大文件大小 (MB)
        :return: 如果验证通过（或仅警告）为True，如果严重错误（未找到文件，格式/大小超过限制）为False
        """
        supported_formats = ["bmp", "png", "jpeg", "jpg", "gif"]
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # 转换为 MB
            file_format = file_path.split('.')[-1].lower()  # 获取文件扩展名并转为小写

            if file_size_mb > max_size_mb:
                log.error(
                    f"图片文件大小超出限制 {max_size_mb}MB (当前文件大小: {file_size_mb:.2f}MB)。请压缩图片文件。")
                return False

            if file_format not in supported_formats:
                log.error(
                    f"图片文件格式不支持 (当前格式: '{file_format}'，支持格式: {supported_formats})。请使用 bmp, png, jpeg, jpg, gif 格式。")
                return False

            return True

        except FileNotFoundError:
            log.error(f"文件未找到: {file_path}")
            return False
        except Exception as e:
            log.error(f"校验图片素材时出错: {e}")
            return False

    # ====================== 永久素材管理接口 ======================
    def add_permanent_material(self, material_type: str,
                               file_path: str,
                               title: str = None,
                               introduction: str = None) -> Optional[dict]:
        """
        新增永久素材
        支持 image, voice, video, thumb 类型。
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html
        注意：公众号的素材库保存总数量有上限：图文消息素材、图片素材上限为100000，其他类型为1000。

        :param material_type: 素材类型，如 'image', 'video', 'voice', 'thumb'
        :param file_path: 素材文件路径
        :param title: 视频素材标题（仅 material_type='video' 时需要）
        :param introduction: 视频素材描述（仅 material_type='video' 时需要）
        :return:
        """
        if not material_type or material_type not in ['image', 'voice', 'video', 'thumb']:
            log.error(
                f"素材类型 (material_type) 必须是 'image', 'voice', 'video', 'thumb' 其中之一，当前类型: '{material_type}'")
            return None

        if not os.path.exists(file_path):
            log.error(f"文件不存在: {file_path}")
            return None

        if material_type == "image":
            if not self._validate_permanent_image_material(file_path):  # 现在使用优化后的图片素材校验函数
                return None  # 如果校验失败 (文件大小/格式错误), 提前返回

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={material_type}"
        files = {'media': open(file_path, 'rb')}
        data = {}  # 初始化 data 为空字典

        if material_type == 'video':
            if not title:
                log.error("错误：新增视频素材需要提供标题 (title)")
                return None
            if not introduction:
                log.error("错误：新增视频素材需要提供描述 (introduction)")
                return None
            data['description'] = json.dumps({'title': title, 'introduction': introduction}, ensure_ascii=False)

        try:
            response = requests.post(url, files=files, data=data)
            return self._parse_response(response)
        except Exception as e:
            log.error(f"新增永久素材请求失败: {e}")
            return None

    def get_permanent_material(self, media_id: str):
        """
        获取永久素材
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Getting_Permanent_Assets.html

        :param media_id: 素材ID
        :return: 素材内容 (根据素材类型返回不同格式) 或 None
        """
        if not media_id:
            log.error("参数 media_id 不能为空")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={access_token}"
        data = {"media_id": media_id}

        try:
            response = requests.post(url, json=data)  # GET 请求改为 POST，并使用 JSON body

            # 根据 Content-Type 判断返回类型，图片/视频/语音等返回二进制，图文等返回 JSON
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:  # JSON 响应
                return self._parse_response(response)
            else:  # 二进制流 (图片/视频/语音)
                return response.content  # 直接返回二进制内容

        except Exception as e:
            log.error(f"获取永久素材请求失败: {e}")
            return None

    def delete_permanent_material(self, media_id: str):
        """
        删除永久素材
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Deleting_Permanent_Assets.html

        :param media_id: 素材ID
        :return: True if successful, False otherwise
        """
        if not media_id:
            log.error("参数 media_id 不能为空")
            return False

        access_token = self.get_access_token()
        if not access_token:
            return False

        url = f"https://api.weixin.qq.com/cgi-bin/material/del_material?access_token={access_token}"
        data = {"media_id": media_id}

        try:
            response = requests.post(url, json=data)  # DELETE 请求改为 POST，并使用 JSON body
            result = self._parse_response(response)
            return True if result.get("errcode") == 0 else False
        except Exception as e:
            log.error(f"删除永久素材请求失败: {e}")
            return False

    def get_material_total(self, material_type: str = None) -> Optional[int]:
        """
        获取永久素材总数
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Get_the_total_of_all_materials.html

        :param material_type: 素材类型，支持image/video/voice/news
        :return: {
                  "voice_count":COUNT,  # 语音总数量
                  "video_count":COUNT,  # 视频总数量
                  "image_count":COUNT,  # 图片总数量
                  "news_count":COUNT   # 图文总数量
                }
        """
        if material_type and material_type not in ["image", "video", "voice", "news"]:
            log.error("素材类型错误，支持image/video/voice/news")
            return None
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token={access_token}"

        try:
            response = requests.get(url, timeout=10)
            result = self._parse_response(response)

            if result:
                if material_type is None:
                    return result
                return result.get(material_type + "_count", 0)  # 返回对应类型的数量，默认0

        except Exception as e:
            log.error(f"获取素材总数失败: {str(e)}")
        return None

    def get_material_list(self, material_type: str = 'news', offset: int = 0, count: int = 20) -> Optional[Dict]:
        """
        获取永久素材列表
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Get_materials_list.html

        :param material_type: 素材的类型，图片（image）、视频（video）、语音 （voice）、图文（news），默认为news
        :param offset: 偏移量，从全部素材的该偏移位置开始返回，0表示从第一个素材返回，默认0
        :param count: 返回素材的数量，取值在1到20之间
        :return:
        """
        valid_types = {"image", "video", "voice", "news"}
        if material_type not in valid_types:
            log.error(f"无效的素材类型，支持{valid_types}")
            return None
        if offset < 0:
            log.error("offset不能为负数")
            return None
        if not (1 <= count <= 20):
            log.error("count必须在1-20之间")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}"
        data = {
            "type": material_type,
            "offset": offset,
            "count": count
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            result = self._parse_response(response)

            if result:
                total_count = result.get("total_count", 0)
                items = result.get("item", [])
                log.info(f"获取{material_type}素材列表成功，共{total_count}条，本次获取{len(items)}条")
                return result

        except Exception as e:
            log.error(f"获取{material_type}素材列表失败: {str(e)}")
        return None

    # ====================== 草稿箱管理接口 ======================
    def check_draft_switch_state(self) -> Optional[bool]:
        """
        检测草稿箱开关状态
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Temporary_MP_Switch.html

        :return: 开关状态 (True: 开启, False: 关闭, None: 获取失败)
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/switch?access_token={access_token}&checkonly=1"
        try:
            response = requests.post(url)
            result = self._parse_response(response)
            if result.get("is_open", 0) == 1:
                return True
            return False

        except Exception as e:
            log.error(f"检测草稿箱开关状态请求失败: {e}")
            return None

    def open_draft(self) -> Optional[bool]:
        """
        开启草稿箱功能（不可逆操作！）
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Temporary_MP_Switch.html

        :return:成功时返回True，失败时返回False，请求失败时，返回None。开启状态需要等待一段时间服务器才能生效。
        """
        access_token = self.get_access_token()
        if not access_token:
            return False

        log.warning("警告：开启草稿箱功能不可逆！操作后服务器后台生效需要一些时间，请耐心等待。")
        url = f"https://api.weixin.qq.com/cgi-bin/draft/switch?access_token={access_token}"
        try:
            response = requests.post(url)

            result = self._parse_response(response)
            if result.get("is_open", 0) == 1:
                log.info(
                    "已发送开启草稿箱功能请求，后台将尽快生效，请耐心等待，可调用 check_draft_switch_state() 方法检查草稿箱功能是否开启。")
                return True

            return False
        except Exception as e:
            log.error(f"开启草稿箱功能请求失败: {e}")
            return None

    # ====================== 草稿箱内容处理 ======================
    def upload_news_image(self, image_path: str) -> Optional[str]:
        """
        上传图文消息内的图片获取URL（用于正文图片）
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html
        该接口用于上传图文消息正文中的图片，返回的URL可直接在图文内容中使用，
        图片仅支持JPEG格式，大小不超过1MB，建议像素为900*700。
        上传图文消息内的图片获取URL"接口所上传的图片，不占用公众号的素材库中图片数量的100000个的限制，图片仅支持jpg/png格式，大小必须在1MB以下。

        :param image_path: 本地图片文件路径（JPEG格式）
        :return: 图片URL（如：http://mmbiz.qpic.cn/...）或None（失败时）
        """
        if not os.path.exists(image_path):
            log.error(f"错误：图片文件不存在 - {image_path}")
            return None

        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in ('.jpg', '.jpeg', '.png'):
            log.error(f"错误：仅支持JPEG/PNG格式图片，当前文件格式为{file_ext}")
            return None

        file_size = os.path.getsize(image_path)
        if file_size > 1 * 1024 * 1024:  # 1MB限制
            log.error(f"错误：图片大小超过限制（1MB），当前大小为{file_size / 1024 / 1024:.2f}MB")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
        files = {'media': open(image_path, 'rb')}

        try:
            response = requests.post(url, files=files, timeout=10)
            result = self._parse_response(response)
            if result.get("url"):
                url = result.get("url")
                log.info(f"上传图文图片成功，URL：{url}")
                return url
        except Exception as e:
            log.error(f"上传图文图片请求失败：{str(e)}")
        return None

    @staticmethod
    def _apply_cover_crop(article: dict, crop_params: list):
        """将通用裁剪参数转换为官方坐标格式"""
        for params in crop_params:
            ratio = params.get("ratio")
            x1 = f"{params.get('x1', 0):.6f}"  # 保留6位小数
            y1 = f"{params.get('y1', 0):.6f}"
            x2 = f"{params.get('x2', 1):.6f}"
            y2 = f"{params.get('y2', 1):.6f}"
            if ratio == "2.35_1":
                article["pic_crop_235_1"] = f"{x1}_{y1}_{x2}_{y2}"
            elif ratio == "1_1":
                article["pic_crop_1_1"] = f"{x1}_{y1}_{x2}_{y2}"
            elif ratio == "16_9":  # 新增 16:9 裁剪比例支持
                article["pic_crop_16_9"] = f"{x1}_{y1}_{x2}_{y2}"

    @staticmethod
    def _format_crop_percent(crop_list: list) -> list:
        """格式化裁剪参数为官方要求的精度"""
        return [{
            "ratio": item["ratio"],
            "x1": float(f"{item['x1']:.6f}"),  # 确保是 float 类型并格式化
            "y1": float(f"{item['y1']:.6f}"),
            "x2": float(f"{item['x2']:.6f}"),
            "y2": float(f"{item['y2']:.6f}")
        } for item in crop_list]

    @staticmethod
    def _format_crop(params: dict) -> str:
        """格式化裁剪参数为字符串（x1_y1_x2_y2）"""
        return f"{params.get('x1', 0)}_{params.get('y1', 0)}_{params.get('x2', 1)}_{params.get('y2', 1)}"

    def get_crop_params(self, image_file_path: str,
                        start_point: Tuple[int, int],
                        crop_width_px: int,
                        auto_adjust_if_exceed: bool = True) -> Optional[dict]:
        """
        根据用户设定的图片文件路径、截图起点和横轴方向剪切像素，返回微信公众号草稿箱接口所需的裁剪参数。
        新增 auto_adjust_if_exceed 参数，控制当裁剪尺寸超出图片边界时是否自动调整。
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html

        :param image_file_path: 图片文件路径，字符串类型。
        :param start_point: 截图的起点坐标 (x, y)，元组类型，元素为整数。
        :param crop_width_px: 横轴方向剪切的像素宽度，整数类型。
        :param auto_adjust_if_exceed: 布尔类型，默认为 True。
                                      True: 当裁剪尺寸超出图片边界时，自动调整 crop_width_px 和 crop_height_px 到最大可能值，保持比例。
                                      False: 当裁剪尺寸超出图片边界时，抛出 ValueError 异常。
        :return: 包含 pic_crop_235_1, pic_crop_1_1, crop_percent_list 参数的字典。
                 pic_crop_235_1 和 pic_crop_1_1 的值为字符串类型，crop_percent_list 的值为列表类型。
                 如果发生错误 (FileNotFoundError 或 ValueError 且 auto_adjust_if_exceed 为 False)，返回空字典。
        :raises ValueError: 当 auto_adjust_if_exceed 为 False 且裁剪尺寸超出图片边界时。
        """
        try:
            image = Image.open(image_file_path)
            original_width, original_height = image.size
            log.debug(f"图片原始尺寸：宽度={original_width}px, 高度={original_height}px")

            start_x_px, start_y_px = start_point
            log.debug(f"截图起点（像素坐标）：x={start_x_px}px, y={start_y_px}px")
            log.debug(f"横轴剪切宽度（像素）：{crop_width_px}px")
            log.debug(f"自动调整超出边界参数：{'开启' if auto_adjust_if_exceed else '关闭'}")

            crop_params_dict = {}
            ratios = {"2.35_1": 1 / 2.35, "1_1": 1, "16_9": 9 / 16}  # 存储比例和对应的height/width比值
            crop_percent_list = []

            for ratio_name, ratio_hw in ratios.items():
                current_crop_width_px = crop_width_px  # 使用一个变量在循环内调整，避免影响外层 crop_width_px
                crop_height_px = int(current_crop_width_px * ratio_hw)
                end_x_px = start_x_px + current_crop_width_px
                end_y_px = start_y_px + crop_height_px

                # 检查是否超出边界并进行调整或报错
                if end_x_px > original_width or end_y_px > original_height:
                    if auto_adjust_if_exceed:
                        log.warning(f"比例 {ratio_name} 裁剪尺寸超出图片边界，尝试自动调整...")
                        # 优先调整宽度，确保宽度不超过边界
                        if end_x_px > original_width:
                            current_crop_width_px = original_width - start_x_px
                            if current_crop_width_px < 0:
                                current_crop_width_px = 0  # 避免起点超出图片导致宽度为负数
                            crop_height_px = int(current_crop_width_px * ratio_hw)
                            end_x_px = start_x_px + current_crop_width_px
                            end_y_px = start_y_px + crop_height_px
                            log.warning(f"宽度超出边界，已调整 crop_width_px 为 {current_crop_width_px}px")

                        # 调整宽度后，再次检查高度，并调整高度 (实际上宽度调整已经大概率可以解决高度问题，但再次检查更稳妥)
                        if end_y_px > original_height:
                            crop_height_px = original_height - start_y_px
                            if crop_height_px < 0:
                                crop_height_px = 0  # 避免起点超出图片导致高度为负数
                            current_crop_width_px = int(crop_height_px / ratio_hw)  # 根据调整后的高度反算宽度，保证比例
                            end_x_px = start_x_px + current_crop_width_px
                            end_y_px = start_y_px + crop_height_px
                            log.warning(
                                f"高度超出边界，已调整 crop_height_px 为 {crop_height_px}px，并同步调整 crop_width_px 为 {current_crop_width_px}px 以保持比例")

                        log.debug(f"比例 {ratio_name} 自动调整后裁剪参数:")
                        log.debug(
                            f"  调整后裁剪区域（像素坐标）：左上角=({start_x_px}px, {start_y_px}px), 右下角=({end_x_px}px, {end_y_px}px)")

                    else:
                        raise ValueError(f"比例 {ratio_name} 裁剪参数超出图片边界。"
                                         f"起点 ({start_x_px}, {start_y_px}), 剪切宽度 {crop_width_px}px，计算出的裁剪区域右下角坐标为 ({end_x_px}, {end_y_px})"
                                         f"，超出图片尺寸 (宽度={original_width}px, 高度={original_height}px)。"
                                         f"请调整 start_point 或 crop_width_px 参数，或开启 auto_adjust_if_exceed 参数以自动调整。")

                # 归一化坐标
                x1_normalized = start_x_px / original_width
                y1_normalized = start_y_px / original_height
                x2_normalized = end_x_px / original_width
                y2_normalized = end_y_px / original_height

                # 格式化为字符串，保留6位小数
                x1_str = f"{x1_normalized:.6f}"
                y1_str = f"{y1_normalized:.6f}"
                x2_str = f"{x2_normalized:.6f}"
                y2_str = f"{y2_normalized:.6f}"

                log.debug(f"比例 {ratio_name} 裁剪参数:")
                log.debug(
                    f"  裁剪区域（像素坐标）：左上角=({start_x_px}px, {start_y_px}px), 右下角=({end_x_px}px, {end_y_px}px)")
                log.debug(f"  归一化坐标：x1={x1_str}, y1={y1_str}, x2={x2_str}, y2={y2_str}")

                if ratio_name == "2.35_1":
                    crop_params_dict["pic_crop_235_1"] = f"{x1_str}_{y1_str}_{x2_str}_{y2_str}"
                elif ratio_name == "1_1":
                    crop_params_dict["pic_crop_1_1"] = f"{x1_str}_{y1_str}_{x2_str}_{y2_str}"
                elif ratio_name == "16_9":
                    crop_params_dict["pic_crop_16_9"] = f"{x1_str}_{y1_str}_{x2_str}_{y2_str}"

                crop_percent_list.append({
                    "ratio": ratio_name.replace("_", "_"),  # 保持ratio参数为 "1_1", "16_9", "2.35_1" 符合文档
                    "x1": float(x1_str),
                    "y1": float(y1_str),
                    "x2": float(x2_str),
                    "y2": float(y2_str)
                })

            crop_params_dict["crop_percent_list"] = crop_percent_list
            log.debug(f"裁剪参数字典：{crop_params_dict}")
            return crop_params_dict

        except FileNotFoundError:
            log.error(f"错误：图片文件未找到：{image_file_path}")
            return None
        except ValueError as ve:
            if not auto_adjust_if_exceed:
                log.error(f"参数错误: {ve}")  # 只有在不自动调整时才记录 ValueError，否则自动调整已经warning了
                return None
            else:  # 如果开启了自动调整，但还是有其他ValueError，例如 Pillow 库的错误，也需要捕获并返回空字典
                log.error(f"处理图片时发生错误: {ve}")
                return None
        except Exception as e:
            log.error(f"处理图片时发生未知错误: {e}")
            return None

    def get_thumb_media_id(self, image_file_path: str) -> Optional[str]:
        """
        获取缩略图 media_id（封面图片）

        :param image_file_path: 图片文件路径
        :return:
        """
        img_info = self.add_permanent_material(material_type="image",
                                               file_path=image_file_path)
        if img_info:
            log.info(f"获取封面图 media_id：{img_info['media_id']}")
            return img_info["media_id"]
        return None

    def create_draft(self,
                     title: str,
                     content: str,
                     cover_pic: str = "",
                     article_type: str = "news",
                     author: str = "",
                     digest: str = "",
                     content_source_url: str = None,
                     need_open_comment: bool = False,
                     only_fans_can_comment: bool = True,
                     pic_crop_235_1: str = "",
                     pic_crop_1_1: str = "",
                     pic_crop_16_9: str = "",  # 新增 16:9 裁剪参数
                     image_info: dict = None,
                     crop_percent_list: list = None,
                     product_info: dict = None
                     ):
        """
        创建公众号草稿（完整参数版，严格对齐官方文档）
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html

        :param title: 标题（必填，≤64字）
        :param content: 图文消息的具体内容，支持HTML标签，必须少于2万字符，小于1M，且此处会去除JS,涉及图片url必须来源 "上传图文消息内的图片获取URL"接口获取。外部图片url将被过滤。 图片消息则仅支持纯文本和部分特殊功能标签如商品，商品个数不可超过50个
        :param cover_pic: 封面图片文件，当类型为 news 时，封面图片是必填项！
        :param article_type: 文章类型，分别有图文消息（news）、图片消息（newspic），不填默认为图文消息（news）
        :param author: 作者（可选）
        :param digest: 图文摘要（可选，单图文有效，未填则截取正文前54字）
        :param content_source_url: 原文链接（可选）
        :param need_open_comment: 是否打开评论，True-打开评论，False-关闭评论（默认为False）
        :param only_fans_can_comment: 是否粉丝可评论，True-打开评论，False-关闭评论（默认为False）
        :param pic_crop_235_1: 2.35:1封面裁剪坐标（格式：X1_Y1_X2_Y2，精度≤6位小数）
        :param pic_crop_1_1: 1:1封面裁剪坐标（格式同上）
        :param pic_crop_16_9: 16:9封面裁剪坐标 (格式同上) # 新增参数文档
        :param image_info: 图片消息图片列表（newspic类型必填，最多20张）
            结构：{"image_list": [{"image_media_id": "永久素材ID"}, ...]}
        :param crop_percent_list: 通用封面裁剪参数（支持1_1、16_9、2.35_1比例， 优先使用此参数，可替代 pic_crop_xx_x 参数）
            示例：[{"ratio": "16_9", "x1": 0.1, "y1": 0, "x2": 0.9, "y2": 0.8}]
        :param product_info: 商品信息（仅newspic支持，需开通权限）
            结构：{"footer_product_info": {"product_key": "商品Key"}}
        :return: draft_id (草稿 media_id) 或 None
        """
        # 基础必填参数校验
        if not title:
            log.error("错误：标题（title）为必填参数")
            return None
        if len(title) > 64:
            log.error(f"错误：标题长度{len(title)}超过限制（最多64字，当前 {len(title)} 字）")
            return None
        if not content:
            log.error("错误：内容（content）为必填参数")
            return None

        # 类型相关参数校验
        if article_type not in ["news", "newspic"]:
            log.error("错误：article_type仅支持 news（图文） 或 newspic（图片消息）")
            return None

        # 构建单篇文章结构
        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": content_source_url,
            "article_type": article_type,
            "need_open_comment": 1 if need_open_comment else 0,
            "only_fans_can_comment": 1 if only_fans_can_comment else 0,
        }

        # 处理图文消息特有参数（news类型）
        if article_type == "news":
            thumb_media_id = self.get_thumb_media_id(cover_pic)

            if not thumb_media_id:
                log.error("错误：图文消息（news）必须提供封面素材ID（thumb_media_id）")
                return None
            article["thumb_media_id"] = thumb_media_id
            # 应用裁剪参数（优先使用crop_percent_list，兼容旧版坐标参数）
            if crop_percent_list:
                self._apply_cover_crop(article, crop_percent_list)
            else:
                article["pic_crop_235_1"] = pic_crop_235_1
                article["pic_crop_1_1"] = pic_crop_1_1
                article["pic_crop_16_9"] = pic_crop_16_9  # 应用 16:9 裁剪参数

        # 处理图片消息特有参数（newspic类型）
        elif article_type == "newspic":
            if not image_info or not image_info.get("image_list"):
                log.error("错误：图片消息（newspic）必须提供 image_info.image_list")
                return None
            if len(image_info["image_list"]) > 20:
                log.error("错误：图片消息最多支持20张图片，当前 {len(image_info['image_list'])} 张")
                return None
            article["image_info"] = image_info
            # 应用通用裁剪参数
            if crop_percent_list:
                article["cover_info"] = {"crop_percent_list": self._format_crop_percent(crop_percent_list)}
            # 处理商品信息
            if product_info:
                article["product_info"] = product_info

        # 构建请求数据（支持单篇/多图文，此处仅单篇，多图文可扩展为列表）
        draft_data = {"articles": [article]}

        # 发送请求（强制UTF-8编码）
        access_token = self.get_access_token()
        if not access_token:
            return None

        try:
            response = requests.post(
                f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}",
                data=json.dumps(draft_data, ensure_ascii=False).encode('utf-8'),
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            result = self._parse_response(response)  # 成功时返回 draft 的 media_id
            if result:
                media_id = result.get("media_id")
                log.info(f"新增草稿成功，media_id: {media_id}")
                return media_id

        except Exception as e:
            log.error(f"新增草稿请求失败: {str(e)}")
        return None

    def get_draft_list(self, offset: int = 0, count: int = 20, no_content: bool = True,
                       order_by_update_time: bool = True) -> Optional[dict]:
        """
        获取草稿列表
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Get_draft_list.html

        :param offset: 从全部素材的该偏移位置开始返回，0表示从第一个素材返回
        :param count: 返回素材的数量，取值在1到20之间
        :param no_content: 是否不返回 content 字段
        :param order_by_update_time: 是否以修改时间戳从小到大排序，默认为True
        :return: 包含草稿列表信息的字典或 None
        """
        if offset < 0:
            log.error("offset 必须大于等于 0")
            return None
        if not (1 <= count <= 20):
            log.error("count 必须在 1 到 20 之间")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}"
        data = {
            "offset": offset,
            "count": count,
            "no_content": 1 if no_content else 0
        }

        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                if order_by_update_time:
                    result["item"].sort(key=lambda x: x["update_time"])
                return result
        except Exception as e:
            log.error(f"获取草稿列表请求失败: {e}")
        return None

    def count_drafts(self) -> Optional[int]:
        """
        统计草稿总数
        https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Count_drafts.html

        :return: 草稿总数
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/draft/count?access_token={access_token}"

        try:
            response = requests.get(url, timeout=10)
            result = self._parse_response(response)

            if result:
                total_count = result.get("total_count")
                log.info(f"草稿总数: {total_count}")
                return total_count

        except Exception as e:
            log.error(f"获取草稿总数失败: {str(e)}")
        return None

    # ====================== 文章发布接口 ======================
    def mass_publish_mpnews(self, media_id: str, send_ignore_reprint: int = False) -> Optional[dict]:
        """
        群发图文消息
        https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Batch_Sends_and_Originality_Checks.html#2

        :param media_id: 图文素材的 media_id
        :param send_ignore_reprint: 当判定为转载的内容时，是否继续进行发送
        :return:
        """
        access_token = self.get_access_token()
        if not access_token:
            return None
        url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"
        data = {
            "filter": {
                "is_to_all": True
            },
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews",
            "send_ignore_reprint": 1 if send_ignore_reprint else 0
        }
        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                return result
        except Exception as e:
            log.error(f"群发图文消息请求失败: {str(e)}")
        return None

    def publish_article(self, media_id: str) -> Optional[str]:
        """
        发布草稿为文章，发布后需要等待一段时间，可调用 get_publish_status() 获取发布状态，
        https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html
        注意：正常情况下调用成功时，errcode将为0，此时只意味着发布任务提交成功，并不意味着此时发布已经完成，所以，仍有可能在后续的发布过程中出现异常情况导致发布失败，如原创声明失败、平台审核不通过等。

        :param media_id: 草稿 media_id
        :return: publish_id
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        data = {
            "media_id": media_id
        }
        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                publish_id = result.get("publish_id")
                log.info(f"发布文章成功，publish_id: {publish_id}")
                return publish_id
        except Exception as e:
            log.error(f"发布文章请求失败: {str(e)}")
        return None

    def get_publish_status(self, publish_id: str) -> Optional[dict]:
        """
        获取发布状态
        https://developers.weixin.qq.com/doc/offiaccount/Publish/Get_status.html
        发布状态详情如下：
        0:成功
        1:发布中
        2:原创失败
        3: 常规失败
        4:平台审核不通过
        5:成功后用户删除所有文章
        6: 成功后系统封禁所有文章

        :param publish_id: 发布任务ID：publish_article()方法的返回值
        :return: 发布状态
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={access_token}"
        data = {
            "publish_id": publish_id
        }

        all_publish_status = {
            "0": "成功",
            "1": "发布中",
            "2": "原创失败",
            "3": "常规失败",
            "4": "平台审核不通过",
            "5": "成功后用户删除所有文章",
            "6": "成功后系统封禁所有文章"
        }

        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                publish_status = str(result.get("publish_status"))
                log.info(f"发布状态: {all_publish_status.get(publish_status)}")
                return result
        except Exception as e:
            log.error(f"获取发布状态请求失败: {str(e)}")
        return None

    def get_publish_list(self, offset: int = 0, count: int = 20, no_content: bool = True) -> Optional[dict]:
        """
        获取已发布的文章列表
        https://developers.weixin.qq.com/doc/offiaccount/Publish/Get_publication_records.html

        :param offset: 偏移量，从全部素材的该偏移位置开始返回，0表示从第一个素材返回，默认为0
        :param count: 返回素材的数量，取值在1到20之间，默认为20
        :param no_content: 是否不返回 content 字段
        :return: 文章列表
        """
        if offset < 0:
            log.error("offset 不能小于0")
            return None
        if count < 1 or count > 20:
            log.error("count 取值在1到20之间，默认为20")
            return None

        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token={access_token}"
        data = {
            "offset": offset,
            "count": count,
            "no_content": 1 if no_content else 0
        }
        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                log.info(
                    f"成功发布素材的总数: {result.get('total_count', 0)}，本次调用获取的素材的数量: {result.get('item_count', 0)}")
                return result
        except Exception as e:
            log.error(f"获取已发布的文章列表请求失败: {str(e)}")
        return None

    def get_publish_article(self, article_id: str) -> Optional[dict]:
        """
        获取已发布的文章
        https://developers.weixin.qq.com/doc/offiaccount/Publish/Get_article_from_id.html

        :param article_id: 文章article_id
        :return:
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/getarticle?access_token={access_token}"
        data = {
            "article_id": article_id
        }
        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                return result
        except Exception as e:
            log.error(f"获取已发布的文章请求失败: {str(e)}")
        return None

    def delete_publish_article(self, article_id: str, index: int = 0) -> Optional[bool]:
        """
        删除已发布的文章
        https://developers.weixin.qq.com/doc/offiaccount/Publish/Delete_posts.html
        注意：此操作不可逆，请谨慎操作！

        :param article_id: 文章article_id
        :param index: 要删除的文章在图文消息中的位置，第一篇编号为1，该字段不填或填0会删除全部文章
        :return: True: 成功，False: 失败，None: 请求失败
        """
        access_token = self.get_access_token()
        if not access_token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/delete?access_token={access_token}"
        data = {
            "article_id": article_id,
            "index": index
        }
        try:
            response = requests.post(url, json=data)
            result = self._parse_response(response)
            if result:
                return True
            return False
        except Exception as e:
            log.error(f"删除已发布的文章请求失败: {str(e)}")
            return None

    def get_all_permanent_news(self, save_path: str = None, simple_data: bool = True) -> list:
        """
        遍历获取永久图文素材
        https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Get_materials_list.html

        :param save_path: 保存路径，默认为不保存
        :param simple_data: 是否只返回简单数据(title + url + date)，默认为True
        :return:
        """
        all_permanent_news = []
        offset = 0
        while True:
            offset_data = self.get_material_list(offset=offset * 20)
            items = offset_data.get("item", [])
            if not items:
                break

            if simple_data:
                for item in items:
                    all_permanent_news.append({
                        "title": item.get("content", {}).get("news_item", [{}])[0].get("title", ""),  # 标题
                        "url": item.get("content", {}).get("news_item", [{}])[0].get("url", ""),  # url
                        "create_time": item.get("content", {}).get("create_time", 0)  # 时间戳
                    })
            else:
                all_permanent_news.extend(items)

            log.info(
                f"获取永久图文素材成功，当前偏移量: {offset * 20}，共 {len(all_permanent_news)} 条，即将获取下一批数据...")
            # 偏移量加1
            offset += 1

            # 休息一秒
            time.sleep(1)

        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(all_permanent_news, f, ensure_ascii=False, indent=4)
                log.info(f"保存永久图文素材成功，保存路径: {save_path}")

        log.info(f"获取永久图文素材成功，共 {len(all_permanent_news)} 条")
        return all_permanent_news
