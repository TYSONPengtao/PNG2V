import cv2
import os
import numpy as np
from natsort import natsorted

def format_year(year):
    """格式化年份显示"""
    if year < 0:
        return f"公元前{abs(year)}年"
    elif year > 0:
        return f"公元{year}年"
    else:
        return "未知年份"

def extract_year(filename):
    # 从文件名中提取年份，支持以下格式：
    # 公元前：map_-3500.png
    # 公元后：map_1500.png
    import re
    # 尝试匹配带负号的年份（公元前）
    match = re.search(r'map_-(\d+)\.png', filename)
    if match:
        return -int(match.group(1))  # 公元前返回负数
    # 尝试匹配不带负号的年份（公元后）
    match = re.search(r'map_(\d+)\.png', filename)
    if match:
        return int(match.group(1))  # 公元后返回正数
    return 0  # 无法识别的格式返回0

def create_video_from_images(input_folder, output_path=None):
    """
    从指定文件夹中的图片创建视频
    :param input_folder: 输入文件夹路径
    :param output_path: 输出视频文件路径，如果不指定则根据输入文件夹自动生成
    """
    if output_path is None:
        # 从输入文件夹名称生成输出文件名，保存到 E:\历史地图 目录
        folder_name = os.path.basename(input_folder)
        output_dir = r"E:\历史地图"
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f"{folder_name}_video.mp4")

    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误：输入文件夹 {input_folder} 不存在！")
        return

    # 获取所有图片文件
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    if not image_files:
        print("错误：文件夹中没有找到图片文件！")
        return    # 按照年份排序（从早到晚）
    image_files = sorted(image_files, key=extract_year)
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 显示排序后的文件顺序
    print("\n排序后的文件顺序：")
    for f in image_files:
        year = extract_year(f)
        print(f"{format_year(year)} - {f}")

    # 读取第一张图片来获取尺寸
    try:
        first_image_path = os.path.join(input_folder, image_files[0])
        with open(first_image_path, 'rb') as f:
            first_image_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
        first_image = cv2.imdecode(first_image_bytes, cv2.IMREAD_COLOR)
        if first_image is None:
            print(f"错误：无法读取图片 {image_files[0]}")
            return
    except Exception as e:
        print(f"错误：读取图片时出错 {image_files[0]} - {str(e)}")
        return

    height, width, layers = first_image.shape
    print(f"视频尺寸将为: {width}x{height}")    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 10  # 基础帧率设为10，这样写入3帧就是0.3秒，写入10帧就是1秒
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 处理每张图片
    total_frames = len(image_files)
    for i, image_file in enumerate(image_files, 1):
        try:
            image_path = os.path.join(input_folder, image_file)
            with open(image_path, 'rb') as f:
                image_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
            
            if frame is None:
                print(f"警告：跳过无法读取的图片 {image_file}")
                continue
            
            # 确保所有图片大小一致
            if frame.shape[0] != height or frame.shape[1] != width:
                frame = cv2.resize(frame, (width, height))

            # 获取年份
            year = extract_year(image_file)
            
            # 根据年份决定重复写入的次数（公元前0.3秒，公元后1秒）
            repeat_frames = 3 if year < 0 else 10
            
            # 写入帧
            for _ in range(repeat_frames):
                video.write(frame)
            
            print(f"处理进度: {i}/{total_frames} - {format_year(year)} - 显示{repeat_frames/10}秒")
        
        except Exception as e:
            print(f"警告：处理图片时出错 {image_file} - {str(e)}")
            continue

    # 释放资源
    video.release()
    print(f"\n视频已成功保存到: {output_path}")

if __name__ == "__main__":
    # 可以处理的文件夹列表
    folders = [
        r"E:\测试",

    ]
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"\n处理文件夹: {folder}")
            create_video_from_images(folder)
