import sys
import os
import subprocess
import importlib.util
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QLabel,
    QMenu, QAction, QFileDialog, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QDesktopWidget,
    QHBoxLayout, QListWidget, QSplitter, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import xml.etree.ElementTree as ET
import marshal  # 用于加载 .pyc 文件

# 获取程序所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 设置文件路径
SETTING_FILE = os.path.join(BASE_DIR, "setting.xml")


def create_default_settings():
    """创建默认的 setting.xml 文件"""
    # 默认工作目录为用户主文件夹下的 pyfilemanager 文件夹
    default_work_dir = os.path.join(os.path.expanduser("~"), "pyfilemanager")
    
    # 如果目录不存在则创建
    if not os.path.exists(default_work_dir):
        os.makedirs(default_work_dir)
    
    # 创建 XML 结构
    root = ET.Element("settings")
    ET.SubElement(root, "python_command").text = "python"
    ET.SubElement(root, "pip_command").text = "python -m pip"
    ET.SubElement(root, "work_dir").text = default_work_dir
    ET.SubElement(root, "check_interval").text = "60000"
    
    # 保存到文件
    tree = ET.ElementTree(root)
    tree.write(SETTING_FILE, encoding="utf-8", xml_declaration=True)
    
    return default_work_dir


class InstallDependenciesThread(QThread):
    """安装依赖的线程"""
    finished = pyqtSignal(bool, str)  # 信号：安装完成（是否成功，错误信息）

    def __init__(self, pip_command, dependencies):
        super().__init__()
        self.pip_command = pip_command
        self.dependencies = dependencies

    def run(self):
        """执行安装依赖"""
        try:
            for dep in self.dependencies:
                if self.pip_command.startswith("python"):
                    # 如果 Pip 命令是 "python -m pip"，拆分为列表
                    command = self.pip_command.split() + ["install", dep.strip()]
                else:
                    command = [self.pip_command, "install", dep.strip()]
                subprocess.run(command, check=True)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class ConfigDialog(QDialog):
    def __init__(self, python_command, pip_command, parent=None):
        super().__init__(parent)
        self.setWindowTitle("配置")
        self.setGeometry(200, 200, 400, 150)

        # 设置字体颜色为黑色
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: black;
                font-family: "微软雅黑";
            }
            QLineEdit {
                color: black;
                font-family: "微软雅黑";
            }
            QPushButton {
                font-family: "微软雅黑";
            }
        """)

        # 创建表单布局
        layout = QFormLayout(self)

        # Python 命令输入框
        self.python_input = QLineEdit(python_command)
        layout.addRow("Python 命令:", self.python_input)

        # Pip 命令输入框
        self.pip_input = QLineEdit(pip_command)
        layout.addRow("Pip 命令:", self.pip_input)

        # 确认和取消按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_commands(self):
        """获取用户输入的 Python 和 Pip 命令"""
        return self.python_input.text(), self.pip_input.text()


class PyFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小工具管理器")
        self.setGeometry(100, 100, 1000, 600)

        # 默认配置
        self.python_command = "python"  # 启动 Python 的命令
        self.pip_command = "python -m pip"  # 安装依赖的命令

        # 检查并创建 setting.xml 文件（如果不存在）
        if not os.path.exists(SETTING_FILE):
            self.work_dir = create_default_settings()
        else:
            # 加载工作目录
            self.work_dir = self.load_work_dir()
            if not self.work_dir:
                # 如果 setting.xml 中没有 work_dir，创建默认设置
                self.work_dir = create_default_settings()

        # 确保工作目录存在
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

        # 数据持久化文件路径
        self.data_file = os.path.join(self.work_dir, "pytools.xml")  # 将 pytools.xml 保存到工作目录

        # 加载配置
        self.load_config()

        # 设置灰色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QToolBar {
                background-color: black;  /* 工具栏背景为黑色 */
                border: none;
            }
            QToolButton {
                color: #FFFFFF;
                font-family: "微软雅黑";
                font-size: 14px;
            }
            QListWidget {
                background-color: #3E3E3E;
                color: #FFFFFF;
                border: none;
            }
            QLabel {
                color: #FFFFFF;
                font-family: "微软雅黑";
            }
            QMenu {
                background-color: #3E3E3E;
                color: #FFFFFF;
                font-family: "微软雅黑";
            }
            QMenu::item:selected {
                background-color: #555555;
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: black;
                font-family: "微软雅黑";
            }
            QMessageBox QPushButton {
                font-family: "微软雅黑";
            }
            QLineEdit {
                font-family: "微软雅黑";
                font-size: 14px;
                background-color: #555555;  /* 搜索栏背景颜色 */
                color: white;  /* 搜索栏字体颜色 */
            }
            QSplitter::handle {
                background-color: black;  /* 分隔条颜色 */
            }
        """)

        # 初始化 UI
        self.init_ui()

        # 加载数据
        self.load_data()

        # 居中显示窗口
        self.center()

    def load_work_dir(self):
        """从 setting.xml 中加载工作目录"""
        try:
            tree = ET.parse(SETTING_FILE)
            root = tree.getroot()
            work_dir = root.find("work_dir").text
            return work_dir
        except Exception as e:
            print(f"加载 setting.xml 失败: {str(e)}")
            return None

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def init_ui(self):
        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 添加导入文件按钮
        import_action = QAction("导入文件", self)
        import_action.setFont(QFont("微软雅黑", 14))
        import_action.triggered.connect(self.import_file)
        toolbar.addAction(import_action)

        # 添加安装 WHL 按钮
        install_whl_action = QAction("安装 WHL", self)
        install_whl_action.setFont(QFont("微软雅黑", 14))
        install_whl_action.triggered.connect(self.install_whl)
        toolbar.addAction(install_whl_action)

        # 添加配置按钮
        config_action = QAction("配置", self)
        config_action.setFont(QFont("微软雅黑", 14))
        config_action.triggered.connect(self.configure_commands)
        toolbar.addAction(config_action)

        # 添加关于按钮
        about_action = QAction("关于", self)
        about_action.setFont(QFont("微软雅黑", 14))
        about_action.triggered.connect(self.show_about_dialog)
        toolbar.addAction(about_action)

        # 添加搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索小工具")
        self.search_input.setFont(QFont("微软雅黑", 12))
        self.search_input.textChanged.connect(self.search_files)  # 实时搜索
        self.search_input.setFixedWidth(int(self.width() / 3))  # 搜索框宽度为窗口宽度的三分之一

        # 添加一个弹簧将搜索框推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        toolbar.addWidget(self.search_input)

        # 创建主布局
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # 左侧分组列表
        self.group_list = QListWidget()
        self.group_list.setFont(QFont("微软雅黑", 12))
        self.group_list.addItem("全部")
        self.group_list.itemClicked.connect(self.filter_by_group)
        self.splitter.addWidget(self.group_list)

        # 右侧文件列表
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.execute_file)  # 双击触发
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.setDragDropMode(QListWidget.InternalMove)  # 支持拖动排序
        self.splitter.addWidget(self.file_list)

        # 设置分组栏宽度为界面的五分之一
        self.splitter.setSizes([int(self.width() / 5), int(self.width() * 4 / 5)])

        # 启用拖放功能
        self.setAcceptDrops(True)


    def install_whl(self):
        """选择并安装 WHL 文件"""
        whl_path, _ = QFileDialog.getOpenFileName(self, "选择 WHL 文件", "", "WHL Files (*.whl)")
        if whl_path:
            try:
                # 使用配置的 pip 命令安装 WHL 文件
                if self.pip_command.startswith("python"):
                    # 如果 Pip 命令是 "python -m pip"，拆分为列表
                    command = self.pip_command.split() + ["install", whl_path]
                else:
                    command = [self.pip_command, "install", whl_path]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                if result.returncode == 0:
                    QMessageBox.information(self, "成功", "WHL 文件安装成功！")
                else:
                    QMessageBox.warning(self, "失败", f"WHL 文件安装失败：{result.stderr}")
            except subprocess.CalledProcessError as e:
                QMessageBox.warning(self, "失败", f"WHL 文件安装失败：{e.stderr}")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"发生未知错误：{str(e)}")

    def show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.information(self, "关于", "清粥小菜，411703730@qq.com")

    def import_file(self):
        """通过文件对话框导入文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 Python 文件", "", "Python Files (*.py *.pyc)")
        if file_path:
            self.add_file_to_list(file_path)

    def create_list_item(self, name, version, description, file_path, group):
        """创建自定义的列表项"""
        item = QListWidgetItem()
        widget = QWidget()
        layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("微软雅黑", 14, QFont.Bold))  # 标题加粗
        version_label = QLabel(f"版本: {version}")
        version_label.setFont(QFont("微软雅黑", 10))
        description_label = QLabel(f"简介: {description}")
        description_label.setFont(QFont("微软雅黑", 10))
        layout.addWidget(name_label)
        layout.addWidget(version_label)
        layout.addWidget(description_label)
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, {"path": file_path, "group": group})  # 保存文件路径和分组信息
        return item, widget

    def add_file_to_list(self, file_path):
        """将文件添加到列表并保存信息"""
        try:
            # 动态导入文件并获取信息
            if file_path.endswith(".py"):
                spec = importlib.util.spec_from_file_location("module.name", file_path)
                if spec is None:
                    raise ImportError(f"无法加载文件: {file_path}")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            elif file_path.endswith(".pyc"):
                # 对于 .pyc 文件，使用 marshal 加载字节码
                with open(file_path, "rb") as f:
                    # 跳过 .pyc 文件的前 16 个字节（魔数和时间戳）
                    f.seek(16)
                    code = marshal.load(f)
                # 创建一个空的模块
                module = type(sys)("module.name")
                exec(code, module.__dict__)
            else:
                raise ValueError("不支持的文件类型")

            easy_inf = getattr(module, "EasyInf", None)
            if easy_inf:
                inf = easy_inf()
                name = inf.get("软件名称", "未知")
                version = inf.get("版本号", "未知")
                description = inf.get("功能介绍", "无简介")
                pid = inf.get("PID", "未知")  # 获取 PID
                group = inf.get("分组", "未分组")  # 获取分组
            else:
                # 如果没有 EasyInf 函数，弹出对话框让用户填写信息
                dialog = QDialog(self)
                dialog.setWindowTitle("填写工具信息")
                dialog.setGeometry(200, 200, 400, 300)

                # 设置对话框样式表，确保字体为黑色
                dialog.setStyleSheet("""
                    QDialog {
                        background-color: white;
                    }
                    QLabel {
                        color: black;
                        font-family: "微软雅黑";
                    }
                    QLineEdit {
                        color: black;
                        font-family: "微软雅黑";
                    }
                    QPushButton {
                        font-family: "微软雅黑";
                    }
                """)

                layout = QFormLayout(dialog)

                # 软件名称
                name_input = QLineEdit(os.path.basename(file_path))
                layout.addRow("软件名称:", name_input)

                # 版本号
                version_input = QLineEdit("1.0.0")
                layout.addRow("版本号:", version_input)

                # 功能介绍
                description_input = QLineEdit("无简介")
                layout.addRow("功能介绍:", description_input)

                # PID
                pid_input = QLineEdit(os.path.basename(file_path))
                layout.addRow("PID:", pid_input)

                # 分组
                group_input = QLineEdit("未分组")
                layout.addRow("分组:", group_input)

                # 确认和取消按钮
                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, dialog)
                buttons.accepted.connect(dialog.accept)
                buttons.rejected.connect(dialog.reject)
                layout.addRow(buttons)

                # 居中显示对话框
                screen_geometry = QDesktopWidget().screenGeometry()
                dialog_geometry = dialog.geometry()
                dialog.move(
                    (screen_geometry.width() - dialog_geometry.width()) // 2,
                    (screen_geometry.height() - dialog_geometry.height()) // 2
                )

                # 设置对话框为最前方显示
                dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)

                if dialog.exec_() == QDialog.Accepted:
                    name = name_input.text()
                    version = version_input.text()
                    description = description_input.text()
                    pid = pid_input.text()
                    group = group_input.text()
                else:
                    return  # 用户取消，不导入文件

            # 检查 PID 是否已存在
            existing_item = self.find_item_by_pid(pid)
            if existing_item:
                self.file_list.takeItem(self.file_list.row(existing_item))
                self.remove_data_by_pid(pid)

            # 创建自定义的列表项
            item, widget = self.create_list_item(name, version, description, file_path, group)
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, widget)

            # 保存文件信息
            self.save_data(file_path, name, version, description, pid, group)

            # 更新分组列表
            self.update_group_list()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法导入文件: {str(e)}")
        
    def update_group_list(self):
        """更新分组列表"""
        groups = set()
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            group = item.data(Qt.UserRole)["group"]
            groups.add(group)
        self.group_list.clear()
        self.group_list.addItem("全部")
        for group in sorted(groups):
            self.group_list.addItem(group)

    def filter_by_group(self, item):
        """根据分组过滤文件"""
        group = item.text()
        for i in range(self.file_list.count()):
            file_item = self.file_list.item(i)
            file_group = file_item.data(Qt.UserRole)["group"]
            if group == "全部" or file_group == group:
                file_item.setHidden(False)
            else:
                file_item.setHidden(True)

    def search_files(self):
        """搜索文件"""
        keyword = self.search_input.text().strip().lower()
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            name = self.file_list.itemWidget(item).layout().itemAt(0).widget().text().lower()
            if keyword in name:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def execute_file(self, item):
        """非阻塞地执行选中的 Python 文件"""
        file_path = item.data(Qt.UserRole)["path"]
        if file_path:
            if not os.path.exists(file_path):
                print(f"文件无法找到: {file_path}")
                self.remove_data_by_file_path(file_path)  # 从 XML 中移除文件
                self.file_list.takeItem(self.file_list.row(item))  # 从列表中移除
                return
            try:
                # 使用配置的 Python 命令执行文件
                subprocess.Popen([self.python_command, file_path], shell=True)
            except Exception as e:
                print(f"执行文件失败: {str(e)}")

    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.file_list.itemAt(position)
        if item:
            menu = QMenu()

            # 添加"运行"选项
            run_action = QAction("运行", self)
            run_action.triggered.connect(lambda: self.execute_file(item))
            menu.addAction(run_action)

            # 添加"移除"选项
            remove_action = QAction("移除", self)
            remove_action.triggered.connect(lambda: self.remove_file(item))
            menu.addAction(remove_action)

            # 添加"安装依赖"选项
            install_deps_action = QAction("安装依赖", self)
            install_deps_action.triggered.connect(lambda: self.install_dependencies(item))
            menu.addAction(install_deps_action)

            # 添加"文件位置"选项
            open_location_action = QAction("文件位置", self)
            open_location_action.triggered.connect(lambda: self.open_file_location(item))
            menu.addAction(open_location_action)

            # 显示菜单
            menu.exec_(self.file_list.mapToGlobal(position))

    def open_file_location(self, item):
        """打开文件所在目录并选中文件"""
        file_path = item.data(Qt.UserRole)["path"]
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "错误", "文件路径无效或文件不存在！")
            return
        
        try:
            # 获取文件的绝对路径
            abs_path = os.path.abspath(file_path)
            file_dir = os.path.dirname(abs_path)
            
            # 根据不同操作系统打开文件位置
            if sys.platform == "win32":
                # Windows: 使用explorer /select命令选中文件
                subprocess.Popen(f'explorer /select,"{abs_path}"', shell=True)
            elif sys.platform == "darwin":
                # macOS: 使用open -R命令在Finder中显示文件
                subprocess.Popen(["open", "-R", abs_path])
            else:
                # Linux或其他系统: 使用xdg-open打开文件所在目录
                subprocess.Popen(["xdg-open", file_dir])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件位置: {str(e)}")

    def remove_file(self, item):
        """移除文件"""
        file_path = item.data(Qt.UserRole)["path"]
        if file_path:
            self.file_list.takeItem(self.file_list.row(item))
            self.remove_data_by_file_path(file_path)
            self.update_group_list()

    def install_dependencies(self, item):
        """异步安装依赖包"""
        file_path = item.data(Qt.UserRole)["path"]
        if file_path:
            try:
                spec = importlib.util.spec_from_file_location("module.name", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                easy_inf = getattr(module, "EasyInf", None)
                if easy_inf:
                    inf = easy_inf()
                    dependencies = inf.get("依赖", "").split(",") if inf.get("依赖") else []

                    # 启动线程安装依赖
                    self.install_thread = InstallDependenciesThread(self.pip_command, dependencies)
                    self.install_thread.finished.connect(self.on_install_finished)
                    self.install_thread.start()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载文件失败: {str(e)}")

    def on_install_finished(self, success, error_message):
        """安装依赖完成后的回调"""
        if success:
            QMessageBox.information(self, "成功", "依赖安装完成")
        else:
            QMessageBox.warning(self, "错误", f"安装依赖失败: {error_message}")

    def configure_commands(self):
        """打开配置对话框"""
        dialog = ConfigDialog(self.python_command, self.pip_command, self)
        dialog.setWindowModality(Qt.ApplicationModal)  # 设置为模态对话框
        dialog.move(self.geometry().center() - dialog.rect().center())  # 居中弹出
        if dialog.exec_() == QDialog.Accepted:
            self.python_command, self.pip_command = dialog.get_commands()
            self.save_config()  # 保存配置

    def save_config(self):
        """保存配置到 XML"""
        if not os.path.exists(self.data_file):
            root = ET.Element("pytools")
        else:
            tree = ET.parse(self.data_file)
            root = tree.getroot()

        # 更新或添加配置
        config = root.find("config")
        if config is None:
            config = ET.SubElement(root, "config")
        python_command = config.find("python_command")
        if python_command is None:
            python_command = ET.SubElement(config, "python_command")
        python_command.text = self.python_command
        pip_command = config.find("pip_command")
        if pip_command is None:
            pip_command = ET.SubElement(config, "pip_command")
        pip_command.text = self.pip_command

        # 保存到文件
        tree = ET.ElementTree(root)
        tree.write(self.data_file, encoding="utf-8", xml_declaration=True)

    def load_config(self):
        """从 XML 加载配置"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            config = root.find("config")
            if config is not None:
                python_cmd = config.find("python_command")
                pip_cmd = config.find("pip_command")
                if python_cmd is not None:
                    self.python_command = python_cmd.text
                if pip_cmd is not None:
                    self.pip_command = pip_cmd.text

    def save_data(self, file_path, name, version, description, pid, group):
        """保存文件信息到 XML"""
        if not os.path.exists(self.data_file):
            root = ET.Element("pytools")
        else:
            tree = ET.parse(self.data_file)
            root = tree.getroot()

        # 检查是否已存在
        for tool in root.findall("tool"):
            if tool.get("pid") == pid:
                root.remove(tool)

        # 添加新信息
        tool = ET.SubElement(root, "tool", path=file_path, pid=pid, group=group)
        ET.SubElement(tool, "name").text = name
        ET.SubElement(tool, "version").text = version
        ET.SubElement(tool, "description").text = description

        # 保存到文件
        tree = ET.ElementTree(root)
        tree.write(self.data_file, encoding="utf-8", xml_declaration=True)

    def load_data(self):
        """从 XML 加载文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            tools_to_remove = []  # 记录需要移除的工具
            for tool in root.findall("tool"):
                file_path = tool.get("path")
                if not os.path.exists(file_path):
                    print(f"文件无法找到: {file_path}")
                    tools_to_remove.append(tool)  # 记录需要移除的工具
                    continue

                name = tool.find("name").text
                version = tool.find("version").text
                description = tool.find("description").text
                pid = tool.get("pid")
                group = tool.get("group", "未分组")

                # 创建自定义的列表项
                item, widget = self.create_list_item(name, version, description, file_path, group)
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, widget)

            # 移除不存在的文件
            for tool in tools_to_remove:
                root.remove(tool)
                tree.write(self.data_file, encoding="utf-8", xml_declaration=True)

            # 更新分组列表
            self.update_group_list()

    def remove_data_by_file_path(self, file_path):
        """从 XML 中移除文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            for tool in root.findall("tool"):
                if tool.get("path") == file_path:
                    root.remove(tool)
                    tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
                    break

    def remove_data_by_pid(self, pid):
        """从 XML 中移除指定 PID 的文件信息"""
        if os.path.exists(self.data_file):
            tree = ET.parse(self.data_file)
            root = tree.getroot()
            for tool in root.findall("tool"):
                if tool.get("pid") == pid:
                    root.remove(tool)
                    tree.write(self.data_file, encoding="utf-8", xml_declaration=True)
                    break

    def find_item_by_pid(self, pid):
        """根据 PID 查找列表项"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = item.data(Qt.UserRole)["path"]
            if file_path:
                tree = ET.parse(self.data_file)
                root = tree.getroot()
                for tool in root.findall("tool"):
                    if tool.get("path") == file_path and tool.get("pid") == pid:
                        return item
        return None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".py") or file_path.endswith(".pyc"):
                self.add_file_to_list(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyFileManager()
    window.show()
    sys.exit(app.exec_())
