import os
import shutil
import subprocess
import sys

def clean_dist():
    """删除 dist 目录中的旧分发包"""
    dist_dir = os.path.join(os.getcwd(), "dist")
    if os.path.exists(dist_dir):
        print("正在删除旧的分发包...")
        shutil.rmtree(dist_dir)
    else:
        print("dist 目录不存在，无需清理。")

def build_package():
    """构建新的分发包"""
    print("正在构建新的分发包...")
    subprocess.run([sys.executable, "-m", "build"], check=True)

def upload_package():
    """上传分发包到 PyPI"""
    print("正在上传分发包到 PyPI...")
    subprocess.run(["twine", "upload", "dist/*"], check=True)

if __name__ == "__main__":
    clean_dist()
    build_package()
    upload_package()