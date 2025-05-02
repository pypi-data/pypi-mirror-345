from PySide6.QtWidgets import QProgressBar, QStyleOptionProgressBar, QStyle
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Signal, Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QLinearGradient

class CustomProgressBar(QProgressBar):
    """
    增强型进度条组件，支持主题切换、动画效果和渐变颜色。
    """
    valueChanged = Signal(int)  # 值变化时发出信号

    # 预定义主题
    THEMES = {
        'default': {
            'bar': """
                QProgressBar {
                    border: 1px solid #DCDFE6;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #E9ECEF;
                    color: #1C1E21;
                    height: 20px;
                }
            """,
            'chunk': """
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 4px;
                    margin: 1px;
                }
            """
        },
        'dark': {
            'bar': """
                QProgressBar {
                    border: 1px solid #444;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #333;
                    color: #FFF;
                    height: 20px;
                }
            """,
            'chunk': """
                QProgressBar::chunk {
                    background-color: #3498db;
                    border-radius: 4px;
                    margin: 1px;
                }
            """
        },
        'light': {
            'bar': """
                QProgressBar {
                    border: 1px solid #E0E0E0;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #F5F5F5;
                    color: #333;
                    height: 20px;
                }
            """,
            'chunk': """
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    border-radius: 4px;
                    margin: 1px;
                }
            """
        },
        'blue': {
            'bar': """
                QProgressBar {
                    border: 1px solid #BBDEFB;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #E3F2FD;
                    color: #0D47A1;
                    height: 20px;
                }
            """,
            'chunk': """
                QProgressBar::chunk {
                    background-color: #2196F3;
                    border-radius: 4px;
                    margin: 1px;
                }
            """
        }
    }

    def __init__(self, parent=None, bar_style=None, chunk_style=None, 
                 animated=False, animation_duration=500, theme='default',
                 gradient=False, start_color=None, end_color=None):
        """
        初始化自定义进度条。
        
        Args:
            parent: 父窗口
            bar_style: 可选；进度条样式
            chunk_style: 可选；进度块样式
            animated: 可选；是否启用动画效果
            animation_duration: 可选；动画持续时间（毫秒）
            theme: 可选；使用的主题，可选值：'default', 'dark', 'light', 'blue'
            gradient: 可选；是否使用渐变色
            start_color: 可选；渐变起始颜色
            end_color: 可选；渐变结束颜色
        """
        super().__init__(parent)
        
        # 存储自定义样式
        self._custom_bar_style = bar_style
        self._custom_chunk_style = chunk_style
        
        # 初始化渐变相关属性
        self._gradient = False  # 默认不使用渐变
        self._start_color = QColor("#2196F3")  # 默认起始颜色：蓝色
        self._end_color = QColor("#4CAF50")    # 默认结束颜色：绿色
        
        # 初始化动画相关属性
        self._animated = animated
        self._animation_duration = animation_duration
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 设置主题
        if theme in self.THEMES:
            self._theme = theme
        else:
            self._theme = 'default' if not bar_style else 'custom'
            
        # 应用初始样式
        self._apply_initial_style()
        
        # 设置渐变颜色（如果提供）
        if start_color:
            self._start_color = QColor(start_color) if isinstance(start_color, str) else start_color
        if end_color:
            self._end_color = QColor(end_color) if isinstance(end_color, str) else end_color
            
        # 如果初始需要启用渐变，则启用
        if gradient:
            self.set_gradient(True)
    
    def _apply_initial_style(self):
        """应用初始样式"""
        if self._theme == 'custom' and self._custom_bar_style:
            # 应用自定义样式
            bar_style = self._custom_bar_style or ""
            chunk_style = self._custom_chunk_style or ""
            self.setStyleSheet(f"{bar_style}{chunk_style}")
        else:
            # 应用主题样式
            theme_data = self.THEMES.get(self._theme, self.THEMES['default'])
            self.setStyleSheet(f"{theme_data['bar']}{theme_data['chunk']}")
    
    def set_theme(self, theme_name):
        """
        设置主题。
        
        Args:
            theme_name: 主题名称
        """
        if theme_name not in self.THEMES:
            return
            
        old_theme = self._theme
        self._theme = theme_name
        
        # 如果当前使用的是渐变，则保持渐变状态
        if self._gradient:
            # 仅更新基本样式，保持渐变效果
            self.setStyleSheet(self.THEMES[theme_name]['bar'])
        else:
            # 如果不使用渐变，应用完整主题样式
            self._apply_initial_style()
    
    def set_gradient(self, enabled, start_color=None, end_color=None):
        """
        启用或禁用渐变效果。
        
        Args:
            enabled: 是否启用渐变
            start_color: 可选；渐变起始颜色
            end_color: 可选；渐变结束颜色
        """
        # 保存旧状态用于比较
        old_gradient = self._gradient
        
        # 更新颜色（如果指定）
        if start_color is not None:
            if isinstance(start_color, str):
                self._start_color = QColor(start_color)
            else:
                self._start_color = start_color
        
        if end_color is not None:
            if isinstance(end_color, str):
                self._end_color = QColor(end_color)
            else:
                self._end_color = end_color
                
        # 更新渐变状态
        self._gradient = enabled
        
        # 如果状态发生变化，需要更新样式
        if old_gradient != enabled:
            # 清除所有样式设置并重新应用
            self.style().unpolish(self)
            
            if enabled:
                # 启用渐变时，只应用基础样式（不包含chunk部分）
                if self._theme == 'custom' and self._custom_bar_style:
                    self.setStyleSheet(self._custom_bar_style)
                else:
                    self.setStyleSheet(self.THEMES[self._theme]['bar'])
            else:
                # 禁用渐变时，恢复完整样式
                self._apply_initial_style()
                
            # 强制Qt重新应用样式
            self.style().polish(self)
        elif enabled and (start_color is not None or end_color is not None):
            # 如果已经启用渐变，且更改了颜色，需要强制更新
            print("颜色已更改，强制更新渐变")
            self.style().unpolish(self)
            self.style().polish(self)
        
        # 在任何情况下强制更新显示
        self.update()
        return True  # 返回成功状态，方便测试脚本检查
    
    def setValue(self, value):
        """设置进度值，支持动画效果"""
        if self._animated and self.isVisible():
            # 使用动画效果
            self._animation.setDuration(self._animation_duration)
            self._animation.setStartValue(self.value())
            self._animation.setEndValue(value)
            self._animation.start()
        else:
            # 直接设置值
            super().setValue(value)
        
        # 发出自定义信号
        self.valueChanged.emit(value)
    
    def set_animated(self, animated, duration=None):
        """
        启用或禁用动画效果。
        
        Args:
            animated: 是否启用动画
            duration: 可选；动画持续时间（毫秒）
        """
        self._animated = animated
        if duration is not None:
            self._animation_duration = max(100, min(5000, duration))
    
    def paintEvent(self, event):
        """自定义绘制事件，支持渐变效果"""
        # 如果不使用渐变，使用默认绘制
        if not self._gradient:
            return super().paintEvent(event)
        
        # 渐变模式下的自定义绘制
        painter = QPainter(self)
        
        # 获取样式选项
        option = QStyleOptionProgressBar()
        self.initStyleOption(option)
        
        # 绘制进度条背景
        rect = self.rect()
        self.style().drawControl(QStyle.CE_ProgressBarGroove, option, painter, self)
        
        # 获取进度条内容区域
        contents_rect = self.style().subElementRect(QStyle.SE_ProgressBarContents, option, self)
        
        # 计算进度宽度
        progress = (self.value() - self.minimum()) / max(1.0, self.maximum() - self.minimum())
        progress_width = int(contents_rect.width() * progress)
        
        if progress_width > 0:
            # 创建进度区域矩形
            progress_rect = QRect(contents_rect.left(), contents_rect.top(),
                                  progress_width, contents_rect.height())
            
            # 创建渐变对象
            gradient = QLinearGradient(progress_rect.left(), 0, progress_rect.right(), 0)
            gradient.setColorAt(0, self._start_color)
            gradient.setColorAt(1, self._end_color)

            # 绘制圆角渐变进度
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(progress_rect, 4, 4)
        
        # 绘制文本 - 确保居中显示
        if self.isTextVisible():
            text = self.text()
            text_rect = rect  # 使用整个进度条区域作为文本区域以确保居中
            painter.setPen(self.palette().color(self.foregroundRole()))
            painter.drawText(text_rect, Qt.AlignCenter, text)
    
    def sizeHint(self):
        """返回建议大小"""
        size = super().sizeHint()
        return QSize(max(size.width(), 100), max(size.height(), 20))