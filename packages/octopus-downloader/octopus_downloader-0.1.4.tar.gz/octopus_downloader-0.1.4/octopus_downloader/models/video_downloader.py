"""视频下载模型定义"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse
from pathlib import Path


class VideoModel(BaseModel):
    """视频模型"""
    download_url: str = Field(..., description="视频链接")
    play_url: Optional[str] = Field(None, description="播放链接")
    title: Optional[str] = Field(..., description="视频标题")
    duration: Optional[int] = Field(None, description="视频时长（秒）")
    size: Optional[int] = Field(None, description="视频大小（字节）")
    resolution: Optional[str] = Field(None, description="视频分辨率")
    format: Optional[str] = Field(None, description="视频格式")
    thumbnail_url: Optional[str] = Field(None, description="缩略图链接")

    @field_validator("download_url")
    def validate_download_url(cls, value: str) -> str:
        """验证下载链接格式"""
        parsed_url = urlparse(value)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid download URL format.")
        return value
    
    @field_validator("play_url")
    def validate_play_url(cls, value: str) -> str:
        """验证播放链接格式"""
        parsed_url = urlparse(value)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid play URL format.")
        return value
    
    @field_validator("thumbnail_url")
    def validate_thumbnail_url(cls, value: str) -> str:
        """验证缩略图链接格式"""
        parsed_url = urlparse(value)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid thumbnail URL format.")
        return value


class VideoDownloaderOptions(BaseModel):
    """视频下载选项"""
    url: str = Field(..., description="视频链接")
    output_dir: Optional[Path] = Field(None, description="输出目录")
    filename: Optional[str] = Field(None, description="文件名")

    @field_validator("url")
    def validate_url(cls, value: str) -> str:
        """验证URL格式"""
        parsed_url = urlparse(value)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid URL format.")
        return value
    

class ResultModel(BaseModel):
    """结果模型"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")
    data: Optional[Dict[str, Any]] = Field(None, description="数据")
    error: Optional[str] = Field(None, description="错误信息")