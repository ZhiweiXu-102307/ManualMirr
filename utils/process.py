import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance
import os
import random
import shutil
from datetime import datetime

class ImageMirrorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ManualMirr")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.original_image = None
        self.current_image = None
        self.image_path = None
        
        # 批量处理相关变量
        self.folder_path = None  # 选择的文件夹路径
        self.image_files = []    # 文件夹中的所有图像文件
        self.preview_image_path = None  # 预览图像的路径
        self.operations_history = []  # 记录对预览图像执行的所有操作
        self.batch_mode = False  # 是否处于批量处理模式
        
        # 图像调整参数，默认值为1（不调整）
        self.brightness_value = 1.0
        self.contrast_value = 1.0
        self.saturation_value = 1.0
        self.color_temperature = 1.0
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部按钮区域
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)
        
        # 创建图像调整区域
        adjustment_frame = tk.LabelFrame(main_frame, text="图像调整", bg="#f0f0f0", font=("Arial", 10, "bold"))
        adjustment_frame.pack(fill=tk.X, pady=5)
        
        # 亮度调整
        brightness_frame = tk.Frame(adjustment_frame, bg="#f0f0f0")
        brightness_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(brightness_frame, text="亮度:", bg="#f0f0f0", width=8).pack(side=tk.LEFT)
        self.brightness_scale = ttk.Scale(brightness_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                        value=1.0, command=self.update_brightness)
        # 注意：ttk.Scale不支持resolution参数，我们将在回调函数中处理步长
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 允许滑块拖拽，但防止点击轨道时滑块跳到极端位置
        self.brightness_scale.bind("<Button-1>", self.on_scale_click)
        self.brightness_value_label = tk.Label(brightness_frame, text="1.0", bg="#f0f0f0", width=4)
        self.brightness_value_label.pack(side=tk.LEFT)
        
        # 对比度调整
        contrast_frame = tk.Frame(adjustment_frame, bg="#f0f0f0")
        contrast_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(contrast_frame, text="对比度:", bg="#f0f0f0", width=8).pack(side=tk.LEFT)
        self.contrast_scale = ttk.Scale(contrast_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                      value=1.0, command=self.update_contrast)
        # 注意：ttk.Scale不支持resolution参数，我们将在回调函数中处理步长
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 允许滑块拖拽，但防止点击轨道时滑块跳到极端位置
        self.contrast_scale.bind("<Button-1>", self.on_scale_click)
        self.contrast_value_label = tk.Label(contrast_frame, text="1.0", bg="#f0f0f0", width=4)
        self.contrast_value_label.pack(side=tk.LEFT)
        
        # 饱和度调整
        saturation_frame = tk.Frame(adjustment_frame, bg="#f0f0f0")
        saturation_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(saturation_frame, text="饱和度:", bg="#f0f0f0", width=8).pack(side=tk.LEFT)
        self.saturation_scale = ttk.Scale(saturation_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                        value=1.0, command=self.update_saturation)
        # 注意：ttk.Scale不支持resolution参数，我们将在回调函数中处理步长
        self.saturation_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 允许滑块拖拽，但防止点击轨道时滑块跳到极端位置
        self.saturation_scale.bind("<Button-1>", self.on_scale_click)
        self.saturation_value_label = tk.Label(saturation_frame, text="1.0", bg="#f0f0f0", width=4)
        self.saturation_value_label.pack(side=tk.LEFT)
        
        # 色温调整
        color_temp_frame = tk.Frame(adjustment_frame, bg="#f0f0f0")
        color_temp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(color_temp_frame, text="色温:", bg="#f0f0f0", width=8).pack(side=tk.LEFT)
        self.color_temp_scale = ttk.Scale(color_temp_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, 
                                        value=1.0, command=self.update_color_temperature)
        # 注意：ttk.Scale不支持resolution参数，我们将在回调函数中处理步长
        self.color_temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 允许滑块拖拽，但防止点击轨道时滑块跳到极端位置
        self.color_temp_scale.bind("<Button-1>", self.on_scale_click)
        self.color_temp_value_label = tk.Label(color_temp_frame, text="1.0", bg="#f0f0f0", width=4)
        self.color_temp_value_label.pack(side=tk.LEFT)
        
        # 重置调整按钮
        reset_adjustments_btn = tk.Button(adjustment_frame, text="重置调整", command=self.reset_adjustments, 
                                        bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"), width=10)
        reset_adjustments_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 加载图像按钮
        self.load_btn = tk.Button(button_frame, text="加载图像", command=self.load_image, 
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                                 width=12, height=2)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # 水平镜像按钮
        self.h_mirror_btn = tk.Button(button_frame, text="水平镜像", command=self.horizontal_mirror, 
                                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"), 
                                     width=12, height=2, state=tk.DISABLED)
        self.h_mirror_btn.pack(side=tk.LEFT, padx=5)
        
        # 垂直镜像按钮
        self.v_mirror_btn = tk.Button(button_frame, text="垂直镜像", command=self.vertical_mirror, 
                                     bg="#2196F3", fg="white", font=("Arial", 10, "bold"), 
                                     width=12, height=2, state=tk.DISABLED)
        self.v_mirror_btn.pack(side=tk.LEFT, padx=5)
        
        # 顺时针旋转按钮
        self.rotate_cw_btn = tk.Button(button_frame, text="顺时针旋转", command=self.rotate_clockwise, 
                                     bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), 
                                     width=12, height=2, state=tk.DISABLED)
        self.rotate_cw_btn.pack(side=tk.LEFT, padx=5)
        
        # 逆时针旋转按钮
        self.rotate_ccw_btn = tk.Button(button_frame, text="逆时针旋转", command=self.rotate_counterclockwise, 
                                      bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), 
                                      width=12, height=2, state=tk.DISABLED)
        self.rotate_ccw_btn.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        self.reset_btn = tk.Button(button_frame, text="重置图像", command=self.reset_image, 
                                  bg="#F44336", fg="white", font=("Arial", 10, "bold"), 
                                  width=12, height=2, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        self.save_btn = tk.Button(button_frame, text="保存图像", command=self.save_image, 
                                 bg="#FF9800", fg="white", font=("Arial", 10, "bold"), 
                                 width=12, height=2, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建图像显示区域（带滚动条）
        self.image_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建Canvas用于显示图像和支持滚动
        self.canvas = tk.Canvas(self.image_frame, bg="white")
        
        # 创建水平和垂直滚动条
        self.h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        # 配置Canvas的滚动区域
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # 放置滚动条和Canvas
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建图像标签并放置在Canvas上
        self.image_label = tk.Label(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window(0, 0, window=self.image_label, anchor="nw")
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪. 请加载一张图像开始操作.")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_image(self):
        # 弹出选择对话框，让用户选择加载单个文件还是文件夹
        choice = messagebox.askquestion("选择加载模式", "是否要批量处理文件夹中的图像？\n选择'是'将加载文件夹，选择'否'将加载单个文件")
        
        if choice == 'yes':  # 批量处理模式
            self.load_folder()
        else:  # 单文件模式
            self.load_single_file()
    
    def load_folder(self):
        """加载文件夹中的图像进行批量处理"""
        folder_path = filedialog.askdirectory(title="选择包含图像的文件夹")
        if not folder_path:  # 用户取消选择
            return
            
        # 获取文件夹中所有支持的图像文件
        image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        image_files = []
        
        for file in os.listdir(folder_path):
            if file.lower().endswith(image_extensions):
                image_files.append(os.path.join(folder_path, file))
        
        if not image_files:
            messagebox.showerror("错误", "所选文件夹中没有支持的图像文件")
            return
        
        # 设置批量处理模式
        self.batch_mode = True
        self.folder_path = folder_path
        self.image_files = image_files
        self.operations_history = []  # 清空操作历史
        
        # 随机选择一张图片作为预览
        preview_image_path = random.choice(image_files)
        self.preview_image_path = preview_image_path
        
        try:
            # 加载预览图像
            self.image_path = preview_image_path
            self.original_image = Image.open(preview_image_path)
            self.current_image = self.original_image.copy()
            self.display_image()
            
            # 更新状态栏
            self.status_var.set(f"批量处理模式 | 预览图像: {os.path.basename(preview_image_path)} | 文件夹中共有 {len(image_files)} 张图像")
            
            # 启用按钮和滑块
            self.enable_controls()
            
            # 重置调整参数
            self.reset_adjustments()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载预览图像: {str(e)}")
    
    def load_single_file(self):
        """加载单个图像文件"""
        file_path = filedialog.askopenfilename(title="选择图像文件", 
                                             filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), 
                                                        ("所有文件", "*.*")])
        if not file_path:  # 用户取消选择
            return
            
        try:
            # 设置为非批量处理模式
            self.batch_mode = False
            self.folder_path = None
            self.image_files = []
            self.preview_image_path = None
            self.operations_history = []
            
            # 加载图像
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.current_image = self.original_image.copy()
            self.display_image()
            
            # 更新状态栏
            self.status_var.set(f"已加载图像: {os.path.basename(file_path)}")
            
            # 启用按钮和滑块
            self.enable_controls()
            
            # 重置调整参数
            self.reset_adjustments()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图像: {str(e)}")
    
    def enable_controls(self):
        """启用所有控制按钮和滑块"""
        # 启用按钮
        self.h_mirror_btn.config(state=tk.NORMAL)
        self.v_mirror_btn.config(state=tk.NORMAL)
        self.rotate_cw_btn.config(state=tk.NORMAL)
        self.rotate_ccw_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
        
        # 启用调整滑块
        self.brightness_scale.config(state=tk.NORMAL)
        self.contrast_scale.config(state=tk.NORMAL)
        self.saturation_scale.config(state=tk.NORMAL)
        self.color_temp_scale.config(state=tk.NORMAL)
    
    def display_image(self):
        # 检查窗口是否仍然存在
        try:
            if not self.root.winfo_exists():
                return  # 如果窗口已被销毁，则退出函数
        except:
            return  # 捕获任何异常并退出
            
        if self.current_image:
            # 调整图像大小以适应窗口
            display_image = self.resize_image_to_fit()
            
            # 转换为Tkinter可用的格式
            self.tk_image = ImageTk.PhotoImage(display_image)
            
            # 更新标签
            self.image_label.config(image=self.tk_image)
            self.image_label.image = self.tk_image  # 保持引用
            
            # 更新Canvas的滚动区域
            try:
                self.image_label.update()
                self.canvas.config(scrollregion=self.canvas.bbox("all"))
            except:
                return  # 如果更新过程中出错，则退出函数
            
            # 获取图像尺寸
            img_width, img_height = self.current_image.size
            display_width, display_height = display_image.size
            
            # 更新状态栏显示图像尺寸
            self.status_var.set(f"原始尺寸: {img_width}x{img_height} 像素 | 显示尺寸: {display_width}x{display_height} 像素 | {os.path.basename(self.image_path) if self.image_path else ''}")
            
            # 如果图像小于显示区域，则居中显示
            try:
                self.center_image_if_smaller()
            except:
                pass  # 忽略居中过程中的错误
    
    def resize_image_to_fit(self):
        if not self.current_image:
            return None
        
        try:
            # 检查窗口和Canvas是否仍然存在
            if not self.root.winfo_exists() or not self.canvas.winfo_exists():
                return self.current_image  # 如果窗口已被销毁，则返回原始图像
                
            # 获取Canvas可见区域的尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 确保尺寸有效
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 700
                canvas_height = 400
            
            # 获取原始图像尺寸
            img_width, img_height = self.current_image.size
            
            # 计算缩放比例
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            ratio = min(width_ratio, height_ratio)
            
            # 计算新尺寸
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # 调整图像大小
            return self.current_image.resize((new_width, new_height), Image.LANCZOS)
        except Exception as e:
            print(f"调整图像大小时出错: {str(e)}")
            return self.current_image  # 出错时返回原始图像
    
    def center_image_if_smaller(self):
        """如果图像小于Canvas可见区域，则将图像居中显示"""
        # 检查窗口和组件是否仍然存在
        try:
            if not self.root.winfo_exists() or not self.canvas.winfo_exists():
                return
        except:
            return  # 如果检查过程中出错，则退出函数
        
        try:
            # 获取Canvas可见区域的尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 获取图像尺寸
            img_width, img_height = self.tk_image.width(), self.tk_image.height()
            
            # 计算居中位置的坐标
            x_pos = max(0, (canvas_width - img_width) // 2)
            y_pos = max(0, (canvas_height - img_height) // 2)
            
            # 更新图像在Canvas中的位置
            self.canvas.coords(self.canvas_window, x_pos, y_pos)
        except Exception as e:
            print(f"居中显示图像时出错: {str(e)}")
            # 错误发生时不做任何操作，保持当前显示状态
    
    def horizontal_mirror(self):
        if self.current_image:
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_image()
            self.status_var.set("已应用水平镜像")
            
            # 如果是批量处理模式，记录操作
            if self.batch_mode:
                self.operations_history.append(("horizontal_mirror", None))
    
    def vertical_mirror(self):
        if self.current_image:
            self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.display_image()
            self.status_var.set("已应用垂直镜像")
            
            # 如果是批量处理模式，记录操作
            if self.batch_mode:
                self.operations_history.append(("vertical_mirror", None))
    
    def rotate_clockwise(self):
        """顺时针旋转图像90度"""
        if self.current_image:
            self.current_image = self.current_image.transpose(Image.ROTATE_270)  # PIL中ROTATE_270实际是顺时针旋转90度
            self.display_image()
            self.status_var.set("已顺时针旋转90度")
            
            # 如果是批量处理模式，记录操作
            if self.batch_mode:
                self.operations_history.append(("rotate_clockwise", None))
    
    def rotate_counterclockwise(self):
        """逆时针旋转图像90度"""
        if self.current_image:
            self.current_image = self.current_image.transpose(Image.ROTATE_90)  # PIL中ROTATE_90实际是逆时针旋转90度
            self.display_image()
            self.status_var.set("已逆时针旋转90度")
            
            # 如果是批量处理模式，记录操作
            if self.batch_mode:
                self.operations_history.append(("rotate_counterclockwise", None))
    
    def reset_image(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.reset_adjustments()
            self.display_image()
            self.status_var.set("图像已重置")
            
            # 如果是批量处理模式，清空操作历史
            if self.batch_mode:
                self.operations_history = []
    
    def on_scale_click(self, event):
        """处理滑块点击事件，允许拖拽滑块但禁止点击轨道"""
        # 在ttk主题中，我们无法直接获取滑块的位置
        # 但我们可以通过检查鼠标事件的类型来区分
        # 如果是滑块拖拽，会触发<B1-Motion>事件
        
        # 为了允许滑块拖拽，我们需要在点击后立即绑定Motion事件
        widget = event.widget
        
        # 记录初始点击位置
        self._scale_click_x = event.x
        self._scale_click_y = event.y
        
        # 绑定鼠标移动和释放事件
        widget.bind("<B1-Motion>", self.on_scale_drag)
        widget.bind("<ButtonRelease-1>", self.on_scale_release)
        
        # 默认阻止点击事件传播，除非确定是在滑块上点击
        return "break"
    
    def on_scale_drag(self, event):
        """处理滑块拖拽事件"""
        # 如果鼠标移动了足够的距离，认为是拖拽操作
        if abs(event.x - self._scale_click_x) > 5 or abs(event.y - self._scale_click_y) > 5:
            # 获取滑块当前值
            widget = event.widget
            # 计算新的值（基于拖拽距离）
            width = widget.winfo_width()
            if width > 0:
                new_value = float(event.x) / width * 2.0  # 2.0是滑块的最大值
                # 确保值在有效范围内
                new_value = max(0.0, min(2.0, new_value))  # 0.0是最小值，2.0是最大值
                # 设置新值
                widget.set(new_value)
        return "break"
    
    def on_scale_release(self, event):
        """处理鼠标释放事件"""
        # 解除临时绑定
        widget = event.widget
        widget.unbind("<B1-Motion>")
        widget.unbind("<ButtonRelease-1>")
        return "break"
    
    def reset_adjustments(self):
        """重置所有图像调整参数为默认值"""
        try:
            # 检查窗口是否仍然存在
            if not self.root.winfo_exists():
                return
                
            # 重置参数值
            self.brightness_value = 1.0
            self.contrast_value = 1.0
            self.saturation_value = 1.0
            self.color_temperature = 1.0
            
            # 更新滑块位置
            self.brightness_scale.set(1.0)
            self.contrast_scale.set(1.0)
            self.saturation_scale.set(1.0)
            self.color_temp_scale.set(1.0)
            
            # 更新标签文本
            self.brightness_value_label.config(text="1.0")
            self.contrast_value_label.config(text="1.0")
            self.saturation_value_label.config(text="1.0")
            self.color_temp_value_label.config(text="1.0")
            
            # 如果是批量处理模式，更新操作历史中的调整参数
            if self.batch_mode:
                # 移除所有调整参数操作
                self.operations_history = [(op_type, op_value) for op_type, op_value in self.operations_history 
                                         if op_type not in ("brightness", "contrast", "saturation", "color_temperature")]
            
            # 如果有图像，则重新应用调整
            if self.original_image:
                # 直接从原始图像创建新的当前图像
                self.current_image = self.original_image.copy()
                self.display_image()
                self.status_var.set("图像调整已重置")
        except Exception as e:
            print(f"重置调整时出错: {str(e)}")  # 打印错误信息以便调试
    
    def update_brightness(self, value):
        """更新亮度值并应用调整"""
        try:
            if not self.root.winfo_exists():
                return  # 如果窗口已被销毁，则退出函数
            # 将值四舍五入到最接近的0.1
            value = round(float(value), 1)
            # 确保值在有效范围内
            if value < 0.0:
                value = 0.0
            elif value > 2.0:
                value = 2.0
            
            # 如果值发生变化，且处于批量处理模式，记录操作
            if self.batch_mode and self.brightness_value != value:
                # 更新或添加亮度调整操作
                # 检查是否已有亮度调整操作
                for i, (op_type, op_value) in enumerate(self.operations_history):
                    if op_type == "brightness":
                        # 更新现有操作
                        self.operations_history[i] = ("brightness", value)
                        break
                else:
                    # 没有找到现有操作，添加新操作
                    self.operations_history.append(("brightness", value))
            
            self.brightness_value = value
            self.brightness_value_label.config(text=f"{self.brightness_value:.1f}")
            self.apply_adjustments()
        except Exception as e:
            print(f"更新亮度时出错: {str(e)}")  # 打印错误信息以便调试
    
    def update_contrast(self, value):
        """更新对比度值并应用调整"""
        try:
            if not self.root.winfo_exists():
                return  # 如果窗口已被销毁，则退出函数
            # 将值四舍五入到最接近的0.1
            value = round(float(value), 1)
            # 确保值在有效范围内
            if value < 0.0:
                value = 0.0
            elif value > 2.0:
                value = 2.0
                
            # 如果值发生变化，且处于批量处理模式，记录操作
            if self.batch_mode and self.contrast_value != value:
                # 更新或添加对比度调整操作
                for i, (op_type, op_value) in enumerate(self.operations_history):
                    if op_type == "contrast":
                        # 更新现有操作
                        self.operations_history[i] = ("contrast", value)
                        break
                else:
                    # 没有找到现有操作，添加新操作
                    self.operations_history.append(("contrast", value))
            
            self.contrast_value = value
            self.contrast_value_label.config(text=f"{self.contrast_value:.1f}")
            self.apply_adjustments()
        except Exception as e:
            print(f"更新对比度时出错: {str(e)}")  # 打印错误信息以便调试
    
    def update_saturation(self, value):
        """更新饱和度值并应用调整"""
        try:
            if not self.root.winfo_exists():
                return  # 如果窗口已被销毁，则退出函数
            # 将值四舍五入到最接近的0.1
            value = round(float(value), 1)
            # 确保值在有效范围内
            if value < 0.0:
                value = 0.0
            elif value > 2.0:
                value = 2.0
                
            # 如果值发生变化，且处于批量处理模式，记录操作
            if self.batch_mode and self.saturation_value != value:
                # 更新或添加饱和度调整操作
                for i, (op_type, op_value) in enumerate(self.operations_history):
                    if op_type == "saturation":
                        # 更新现有操作
                        self.operations_history[i] = ("saturation", value)
                        break
                else:
                    # 没有找到现有操作，添加新操作
                    self.operations_history.append(("saturation", value))
            
            self.saturation_value = value
            self.saturation_value_label.config(text=f"{self.saturation_value:.1f}")
            self.apply_adjustments()
        except Exception as e:
            print(f"更新饱和度时出错: {str(e)}")  # 打印错误信息以便调试
    
    def update_color_temperature(self, value):
        """更新色温值并应用调整"""
        try:
            if not self.root.winfo_exists():
                return  # 如果窗口已被销毁，则退出函数
            # 将值四舍五入到最接近的0.1
            value = round(float(value), 1)
            # 确保值在有效范围内
            if value < 0.0:
                value = 0.0
            elif value > 2.0:
                value = 2.0
                
            # 如果值发生变化，且处于批量处理模式，记录操作
            if self.batch_mode and self.color_temperature != value:
                # 更新或添加色温调整操作
                for i, (op_type, op_value) in enumerate(self.operations_history):
                    if op_type == "color_temperature":
                        # 更新现有操作
                        self.operations_history[i] = ("color_temperature", value)
                        break
                else:
                    # 没有找到现有操作，添加新操作
                    self.operations_history.append(("color_temperature", value))
            
            self.color_temperature = value
            self.color_temp_value_label.config(text=f"{self.color_temperature:.1f}")
            self.apply_adjustments()
        except Exception as e:
            print(f"更新色温时出错: {str(e)}")  # 打印错误信息以便调试
    
    def apply_adjustments(self):
        """应用所有图像调整"""
        # 检查窗口是否仍然存在
        try:
            self.root.winfo_exists()
        except:
            return  # 如果窗口已被销毁，则退出函数
            
        if self.original_image:
            # 从原始图像开始，应用所有调整
            img = self.original_image.copy()
            
            # 应用亮度调整
            if self.brightness_value != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(self.brightness_value)
            
            # 应用对比度调整
            if self.contrast_value != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(self.contrast_value)
            
            # 应用饱和度调整
            if self.saturation_value != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(self.saturation_value)
            
            # 应用色温调整（通过调整RGB通道的比例）
            if self.color_temperature != 1.0:
                # 确保图像是RGB模式
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                r, g, b = img.split()
                if self.color_temperature > 1.0:  # 偏暖色
                    r = ImageEnhance.Brightness(r).enhance(self.color_temperature)
                    b = ImageEnhance.Brightness(b).enhance(2.0 - self.color_temperature)
                else:  # 偏冷色
                    r = ImageEnhance.Brightness(r).enhance(self.color_temperature)
                    b = ImageEnhance.Brightness(b).enhance(2.0 - self.color_temperature)
                img = Image.merge("RGB", (r, g, b))
            
            # 更新当前图像并显示
            self.current_image = img
            self.display_image()
    
    def save_image(self):
        if self.current_image:
            file_types = [("PNG文件", "*.png"), 
                         ("JPEG文件", "*.jpg"), 
                         ("BMP文件", "*.bmp"), 
                         ("所有文件", "*.*")]
            
            default_ext = os.path.splitext(self.image_path)[1] if self.image_path else ".png"
            default_name = f"mirrored{default_ext}"
            
            save_path = filedialog.asksaveasfilename(
                title="保存图像", 
                defaultextension=default_ext,
                initialfile=default_name,
                filetypes=file_types
            )
            
            if save_path:
                try:
                    self.current_image.save(save_path)
                    self.status_var.set(f"图像已保存至: {os.path.basename(save_path)}")
                    messagebox.showinfo("成功", "图像已成功保存!")
                except Exception as e:
                    messagebox.showerror("错误", f"保存图像时出错: {str(e)}")

# 主程序入口
    def save_image(self):
        """保存处理后的图像"""
        if not self.current_image:
            messagebox.showerror("错误", "没有可保存的图像")
            return
            
        if self.batch_mode:  # 批量处理模式
            self.save_batch_images()
        else:  # 单文件模式
            self.save_single_image()
    
    def save_single_image(self):
        """保存单个处理后的图像"""
        file_path = filedialog.asksaveasfilename(
            title="保存图像",
            defaultextension=".png",
            filetypes=[("PNG图像", "*.png"), ("JPEG图像", "*.jpg"), ("BMP图像", "*.bmp"), ("GIF图像", "*.gif")]
        )
        
        if not file_path:  # 用户取消保存
            return
            
        try:
            # 保存当前图像
            self.current_image.save(file_path)
            self.status_var.set(f"图像已保存至: {file_path}")
            messagebox.showinfo("成功", f"图像已成功保存至:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图像时出错: {str(e)}")
    
    def save_batch_images(self):
        """批量处理并保存所有图像"""
        if not self.folder_path or not self.image_files:
            messagebox.showerror("错误", "没有可处理的图像文件夹")
            return
            
        # 创建输出文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join(os.path.dirname(self.folder_path), f"processed_{os.path.basename(self.folder_path)}_{timestamp}")
        
        try:
            # 创建输出文件夹
            os.makedirs(output_folder, exist_ok=True)
            
            # 显示进度对话框
            progress_window = tk.Toplevel(self.root)
            progress_window.title("批量处理进度")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.root)  # 设置为主窗口的子窗口
            progress_window.grab_set()  # 模态窗口
            
            # 进度标签
            progress_label = tk.Label(progress_window, text="正在处理图像...", font=("Arial", 10))
            progress_label.pack(pady=10)
            
            # 进度条
            progress_bar = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=350, mode="determinate")
            progress_bar.pack(pady=10, padx=25)
            
            # 当前处理文件标签
            file_label = tk.Label(progress_window, text="", font=("Arial", 9))
            file_label.pack(pady=5)
            
            # 设置进度条最大值
            progress_bar["maximum"] = len(self.image_files)
            
            # 处理每个图像文件
            for i, image_file in enumerate(self.image_files):
                # 更新进度
                progress_bar["value"] = i
                file_label.config(text=f"处理: {os.path.basename(image_file)}")
                progress_window.update()
                
                try:
                    # 加载原始图像
                    img = Image.open(image_file)
                    
                    # 应用所有操作
                    processed_img = self.apply_operations_to_image(img)
                    
                    # 保存处理后的图像
                    output_path = os.path.join(output_folder, os.path.basename(image_file))
                    processed_img.save(output_path)
                except Exception as e:
                    print(f"处理图像 {image_file} 时出错: {str(e)}")
            
            # 完成处理
            progress_bar["value"] = len(self.image_files)
            file_label.config(text="处理完成!")
            progress_window.update()
            
            # 显示完成消息
            messagebox.showinfo("完成", f"批量处理完成!\n所有处理后的图像已保存至:\n{output_folder}")
            
            # 关闭进度窗口
            progress_window.destroy()
            
            # 更新状态栏
            self.status_var.set(f"批量处理完成 | 已处理 {len(self.image_files)} 张图像 | 保存至: {output_folder}")
        except Exception as e:
            messagebox.showerror("错误", f"批量处理图像时出错: {str(e)}")
    
    def apply_operations_to_image(self, image):
        """将所有记录的操作应用到给定图像"""
        # 创建图像副本
        img = image.copy()
        
        # 应用所有操作
        for op_type, op_value in self.operations_history:
            if op_type == "horizontal_mirror":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif op_type == "vertical_mirror":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
            elif op_type == "rotate_clockwise":
                img = img.transpose(Image.ROTATE_270)
            elif op_type == "rotate_counterclockwise":
                img = img.transpose(Image.ROTATE_90)
            elif op_type == "brightness" and op_value is not None:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(op_value)
            elif op_type == "contrast" and op_value is not None:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(op_value)
            elif op_type == "saturation" and op_value is not None:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(op_value)
            elif op_type == "color_temperature" and op_value is not None:
                # 确保图像是RGB模式
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                r, g, b = img.split()
                if op_value > 1.0:  # 偏暖色
                    r = ImageEnhance.Brightness(r).enhance(op_value)
                    b = ImageEnhance.Brightness(b).enhance(2.0 - op_value)
                else:  # 偏冷色
                    r = ImageEnhance.Brightness(r).enhance(op_value)
                    b = ImageEnhance.Brightness(b).enhance(2.0 - op_value)
                img = Image.merge("RGB", (r, g, b))
        
        return img

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMirrorApp(root)
    root.mainloop()