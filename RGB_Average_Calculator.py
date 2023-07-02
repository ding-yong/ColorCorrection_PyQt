import cv2


def calculate_rgb_average(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    original_height, original_width = image.shape[:2]

    scale_ratio = 1280 / float(original_width)
    target_width = 1280
    target_height = int(original_height * scale_ratio)

    image = cv2.resize(image, (target_width, target_height))

    # 创建窗口并设置鼠标事件回调函数
    cv2.namedWindow("Select Region")
    cv2.setMouseCallback("Select Region", select_region_callback)

    # 显示图像，等待用户选择区域
    selected_region = cv2.selectROI(
        "Select Region", image, fromCenter=False, showCrosshair=True
    )

    # 获取选定区域的像素数据
    region_pixels = image[
        int(selected_region[1]) : int(selected_region[1] + selected_region[3]),
        int(selected_region[0]) : int(selected_region[0] + selected_region[2]),
    ]

    # 计算RGB均值
    avg_rgb = cv2.mean(region_pixels)[:3]
    avg_rgb = [avg_rgb[2], avg_rgb[1], avg_rgb[0]]  # 将B和R通道的值交换位置得到RGB顺序的结果

    # 关闭窗口
    cv2.destroyAllWindows()

    return avg_rgb


# 鼠标事件回调函数，用于处理用户选择区域
def select_region_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global selected_region
        selected_region = (x, y, 0, 0)  # 初始化选定区域的坐标
    elif event == cv2.EVENT_LBUTTONUP:
        selected_region = (
            selected_region[0],
            selected_region[1],
            x - selected_region[0],
            y - selected_region[1],
        )


def rgb_average_run_main(img_path):
    avg_rgb = calculate_rgb_average(img_path)
    return avg_rgb
