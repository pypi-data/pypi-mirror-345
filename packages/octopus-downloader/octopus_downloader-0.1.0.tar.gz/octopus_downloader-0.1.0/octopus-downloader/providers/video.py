from providers.video_providers.tiktok import TikTokProvider
from providers.video_providers.youtube import YouTubeProvider
from providers.video_providers.douyin import DouYinProvider


# 一个工厂类，用于根据 URL 创建对应的 Provider 实例
class ProviderFactory:
    # 定义平台特征字符串到 Provider 类的映射
    platform_mapping = {
        "tiktok.com": TikTokProvider,
        "youtube.com": YouTubeProvider,
        "youtu.be": YouTubeProvider,
        "douyin.com": DouYinProvider
    }

    @staticmethod
    def create_provider(url):
        for key in ProviderFactory.platform_mapping:
            if key in url:
                return ProviderFactory.platform_mapping[key]()
        raise ValueError(f"Unsupported platform for URL: {url}")
    