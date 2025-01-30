from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel)
from views.components.course_list_widget import CourseListWidget
import logging

class CartPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("<h2>Shopping Cart</h2>")
        self.clear_button = QPushButton("Clear Cart")
        self.clear_button.clicked.connect(self.clear_cart)  # 连接清空购物车的槽函数
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.clear_button)
        self.layout.addLayout(header_layout)

        # Course list - specify this is a cart list
        self.course_list = CourseListWidget(is_cart=True)
        self.course_list.course_added.connect(self.update_cart_display)
        self.course_list.course_removed.connect(self.update_cart_display)  # 连接课程移除的信号
        self.layout.addWidget(self.course_list)

        # Generate button
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Timetable")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_button.clicked.connect(self.generate_timetable)  # 连接生成时间表的槽函数
        button_layout.addStretch()
        button_layout.addWidget(self.generate_button)
        self.layout.addLayout(button_layout)

    def set_courses(self, courses):
        """Set the courses in the cart list"""
        self.course_list.set_courses(courses)

    def update_cart_display(self):
        """Update the cart display with current courses"""
        courses = self.get_cart_courses()  # 假设这个方法返回当前购物车中的课程列表
        self.set_courses(courses)

    def get_cart_courses(self):
        """Get the courses in the cart"""
        # 这里应该是获取购物车课程的逻辑，例如从数据库或内存中获取
        # 暂时返回一个空列表作为示例
        return []

    def clear_cart(self):
        """Clear all courses from the cart"""
        # 这里应该是清空购物车的逻辑，例如从数据库或内存中删除所有课程
        # 暂时打印一条消息作为示例
        logging.info("Clearing cart")
        self.set_courses([])  # 更新UI显示为空

    def generate_timetable(self):
        """Generate the timetable based on the current cart courses"""
        # 这里应该是生成时间表的逻辑
        logging.info("Generating timetable")