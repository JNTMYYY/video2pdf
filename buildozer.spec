[app]

title = VideoTool
package.name = videotool
package.domain = org.videotool

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy,ffmpeg‑kit‑python

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO
android.api = 33
android.ndk = 25b
android.arch = arm64‑v8a

[buildozer]
log_level = 2
warn_on_root = 1
