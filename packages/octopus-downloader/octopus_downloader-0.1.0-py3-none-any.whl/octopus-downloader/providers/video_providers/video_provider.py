from abc import ABC, abstractmethod
from rich.console import Console


# 定义一个抽象基类，所有平台的 Provider 都要继承这个类
class VideoProvider(ABC):
    """
    视频解析器的抽象基类，定义了视频解析和下载的接口
    所有视频解析器都需要继承这个类并实现其方法
    """
    def __init__(self):
        """
        初始化视频解析器
        """
        self.console = Console()

    @abstractmethod
    def get_video_info(self, url):
        """
        解析视频信息的抽象方法，需要在子类中实现
        :param url: 视频的 URL
        :return: 解析后的视频信息字典
        """
        pass

    @abstractmethod
    def download_video(self, download_url, output_path):
        """
        下载视频的抽象方法，需要在子类中实现
        :param download_url: 解析后的视频文件地址
        :param output_path: 视频保存的路径
        :return: 下载是否成功的布尔值
        """
        pass
