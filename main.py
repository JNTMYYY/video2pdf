import sys
import os
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.utils import platform

# ===================== 平台判断与ffmpeg封装 =====================
IS_ANDROID = hasattr(sys, "getandroidapilevel")
FFmpegKit = None

if IS_ANDROID:
    try:
        from ffmpeg_kit_python import FFmpegKit
    except ImportError:
        FFmpegKit = None


def run_ffmpeg(args_list):
    """
    统一ffmpeg调用接口
    args_list: 和subprocess格式一致，例 ["ffmpeg","-i","in.mp4","out.mp4"]
    返回值：0成功，非0失败
    """
    if IS_ANDROID:
        if FFmpegKit is None:
            return -999
        # 安卓：去掉列表第一个"ffmpeg"，参数做简单引号处理避免空格路径bug
        cmd_parts = []
        for arg in args_list[1:]:
            if " " in arg:
                cmd_parts.append(f'"{arg}"')
            else:
                cmd_parts.append(arg)
        cmd_str = " ".join(cmd_parts)
        session = FFmpegKit.execute(cmd_str)
        rc = session.getReturnCode()
        return rc
    else:
        # Windows / Linux本机，继续subprocess调用系统ffmpeg
        ret = subprocess.run(args_list, capture_output=True)
        return ret.returncode


def get_work_root():
    """获取可用工作目录，自动适配Windows和安卓外部存储"""
    if platform == "android":
        from android.storage import primary_external_storage_path
        root = primary_external_storage_path()
    else:
        root = os.getcwd()
    return root


# ===================== Kivy UI =====================
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        self.label_tip = Label(text="视频处理工具", font_size=20)
        self.add_widget(self.label_tip)

        self.in_path_input = TextInput(hint_text="输入视频完整路径", size_hint_y=None, height=40)
        self.add_widget(self.in_path_input)

        self.btn_run = Button(text="执行视频抽帧", size_hint_y=None, height=45)
        self.btn_run.bind(on_press=self.do_extract_frame)
        self.add_widget(self.btn_run)

    def do_extract_frame(self, instance):
        """示例功能：视频按1fps抽帧，等价原ffmpeg命令 ffmpeg -i input.mp4 -vf fps=1 out_%04d.jpg"""
        work_dir = get_work_root()
        input_file = self.in_path_input.text.strip()

        if not os.path.exists(input_file):
            self.label_tip.text = "错误：文件不存在"
            return

        output_pattern = os.path.join(work_dir, "frame_%04d.jpg")

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", "fps=1",
            "-y",
            output_pattern
        ]
        ret_code = run_ffmpeg(ffmpeg_cmd)

        if ret_code == 0:
            self.label_tip.text = f"抽帧完成，输出目录:{work_dir}"
        elif ret_code == -999:
            self.label_tip.text = "错误：FFmpegKit库未加载"
        else:
            self.label_tip.text = f"ffmpeg执行失败，返回码:{ret_code}"


class VideoToolApp(App):
    def build(self):
        self.title = "VideoTool"
        return MainLayout()


if __name__ == "__main__":
    VideoToolApp().run()
