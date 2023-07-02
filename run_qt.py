import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMenuBar,
    QMenu,
    QAction,
    QMainWindow,
)

import numpy as np
from run_color_correction import parse_options, MyWorker
from subprocess import run
from PyQt5.QtGui import QPixmap
from RGB_Average_Calculator import rgb_average_run_main
import cv2
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QLabel


class ColorCorrectionThread(QThread):
    # 定义一个信号，用于在处理完成时发送信号给主线程
    result_signal = pyqtSignal(str)
    image_signal = pyqtSignal(str)  # 新增信号
    image_save_signal = pyqtSignal(str)  # 新增信号
    imagenum_signal = pyqtSignal(str)

    def __init__(self, card_file, input_folder, output_folder):
        super().__init__()
        self.card_file = card_file
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        opts = {
            "-c": self.card_file.replace("\\", "/"),
            "-d": "[-20,20,50]",
            "-f": None,
            "-i": self.input_folder.replace("\\", "/"),
            "-l": None,
            "-n": None,
            "-o": self.output_folder.replace("\\", "/"),
            "-s": "[0.5,1.5,50]",
            "-t": None,
            "-v": False,
        }
        Options = parse_options(opts)
        worker = MyWorker()  # Create an instance of MyWorker
        worker.image_processed.connect(self.update_image_display)
        worker.image_save.connect(self.update_image_save_display)
        worker.progress_signal.connect(self.handle_progress_signal)
        Process_state = worker.main(opts["-i"], opts["-o"], opts["-c"], Options)
        self.result_signal.emit(str(Process_state))

    def update_image_display(self, image):
        self.image_signal.emit(image)

    def update_image_save_display(self, image):
        self.image_save_signal.emit(image)

    def handle_progress_signal(self, message):
        self.imagenum_signal.emit(message)


class ColorCorrectionGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Correction")
        self.resize(1280, 720)  # 设置窗口大小
        # self.setStyleSheet("background-color: #F0FFFF;")
        self.show_author_info = "dingyong.prc@foxmail.com"
        # Set the application icon
        app_icon = QIcon("Project_daily/other/Color_correction-master/Icon/icon.png")
        self.setWindowIcon(app_icon)
        # Create other interface components...
        self.layout = QHBoxLayout()

        # 左侧布局
        self.left_layout = QVBoxLayout()

        self.card_button = QPushButton("选择色卡文件")
        self.card_button.setFixedSize(220, 100)
        self.card_button.clicked.connect(self.select_card)
        self.left_layout.addWidget(self.card_button)

        self.input_button = QPushButton("选择输入图像文件夹")
        self.input_button.setFixedSize(220, 100)
        self.input_button.clicked.connect(self.select_input)
        self.left_layout.addWidget(self.input_button)

        self.output_button = QPushButton("选择输出图像文件夹")
        self.output_button.setFixedSize(220, 100)
        self.output_button.clicked.connect(self.select_output)
        self.left_layout.addWidget(self.output_button)

        self.run_button = QPushButton("运行")
        self.run_button.setFixedSize(220, 100)
        self.run_button.clicked.connect(self.run_color_correction_main)
        self.left_layout.addWidget(self.run_button)

        self.rgb_button = QPushButton("计算RGB平均值")
        self.rgb_button.setFixedSize(220, 100)
        self.rgb_button.clicked.connect(self.rgb_average_run)
        self.left_layout.addWidget(self.rgb_button)

        # 右侧布局
        self.right_layout = QVBoxLayout()
        # 创建水平布局
        self.layout_h = QHBoxLayout()

        self.card_image = QLabel()
        self.image_label = QLabel()
        self.layout_h.addWidget(self.card_image)
        self.layout_h.addWidget(self.image_label)
        self.right_layout.addLayout(self.layout_h)

        self.result_text = QTextEdit()
        self.right_layout.addWidget(self.result_text)

        self.layout.addLayout(self.left_layout)
        self.layout.addLayout(self.right_layout)

        self.setLayout(self.layout)

        self.card_file = ""
        self.input_folder = ""
        self.output_folder = ""
        self.result_text.setText("⭐功能一 校色：点击 选择色卡文件→选择输入图像文件夹→选择输出图像文件夹→运行")
        self.result_text.append("⭐功能二 计算图像区域RGB平均值：点击 计算RGB平均值")

        self.result_text.append(
            "----------------------------注意：无法打开路径中带有中文的文件！---------------------------"
        )

    def update_image_display(self, image):
        pixmap = QPixmap(image)
        # Set the pixmap on the QLabel
        self.card_image.setPixmap(pixmap.scaledToWidth(500))

    def update_image_save_display(self, image):
        pixmap = QPixmap(image)
        # Set the pixmap on the QLabel
        self.image_label.setPixmap(pixmap.scaledToWidth(500))

    def select_card(self):
        file_dialog = QFileDialog()
        card_file, _ = file_dialog.getOpenFileName(self, "选择色卡文件")
        if card_file:
            self.card_file = card_file
            pixmap = QPixmap(card_file)
            self.image_label.clear()
            self.card_image.setPixmap(pixmap.scaledToWidth(500))

    def select_input(self):
        file_dialog = QFileDialog()
        input_folder = file_dialog.getExistingDirectory(self, "选择输入图像文件夹")
        if input_folder:
            self.input_folder = input_folder
            self.result_text.append("输入图像文件夹路径：" + str(input_folder))

    def select_output(self):
        file_dialog = QFileDialog()
        output_folder = file_dialog.getExistingDirectory(self, "选择输出图像文件夹")
        if output_folder:
            self.output_folder = output_folder
            self.result_text.append("输出图像文件夹路径：" + str(output_folder))

    def run_color_correction_main(self):
        self.result_text.append("正在处理，请勿关闭该窗口！")
        if self.card_file and self.input_folder and self.output_folder:
            # 创建子线程并启动
            self.color_correction_thread = ColorCorrectionThread(
                self.card_file, self.input_folder, self.output_folder
            )
            self.color_correction_thread.result_signal.connect(
                self.processing_completed
            )
            self.color_correction_thread.image_signal.connect(self.update_image_display)
            self.color_correction_thread.imagenum_signal.connect(
                self.handle_progress_signal
            )
            self.color_correction_thread.image_save_signal.connect(
                self.update_image_save_display
            )
            self.color_correction_thread.start()

        else:
            self.result_text.append("请先选择色卡文件、输入图像文件夹和输出文件夹")

    def handle_progress_signal(self, message):
        self.result_text.append("校色成功：" + str(message))
        self.card_image.clear()
        self.image_label.clear()

    def processing_completed(self, process_state):
        self.result_text.append("完成处理，总耗时：" + str(process_state) + "s")

    def rgb_average_run(self):
        file_dialog = QFileDialog()
        img_path, _ = file_dialog.getOpenFileName(self, "选择要计算rgb的文件")
        pixmap = QPixmap(img_path)
        self.image_label.clear()
        self.card_image.setPixmap(pixmap.scaledToWidth(500))

        rgb_result = rgb_average_run_main(img_path)
        self.result_text.append("计算RGB平均值结果：" + str(rgb_result))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ColorCorrectionGUI()
    gui.show()

    sys.exit(app.exec_())
