import sys
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QGridLayout, QFrame, QLineEdit,
    QSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QHeaderView, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon

# ===================== COLOR SCHEME =====================
COLORS = {
    "primary": "#4A90E2",
    "secondary": "#7B68EE",
    "light_bg": "#F5F7FA",
    "white": "#FFFFFF",
    "text_dark": "#2C3E50",
    "text_light": "#7F8C8D",
    "card_1": "#FF6B6B",
    "card_2": "#4ECDC4",
    "card_3": "#45B7D1",
    "card_4": "#FFA07A",
    "card_5": "#98D8C8",
    "card_6": "#F7DC6F",
    "sidebar": "#ECF0F1",
    "hover": "#D5DBEA",
    "success": "#27AE60",
    "error": "#E74C3C",
    "warning": "#F39C12",
}

# ===================== JSON FILE MANAGEMENT =====================
class ProductManager:
    """Manage products in JSON file"""
    
    FILE_NAME = r"F:\inventory app\products.json"
    
    @staticmethod
    def load_products():
        """Load products from JSON file"""
        try:
            with open(ProductManager.FILE_NAME, "r", encoding="utf-8") as f:
                data = f.read().strip()
                return json.loads(data) if data else []
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_products(products):
        """Save products to JSON file"""
        with open(ProductManager.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def get_statistics():
        """Get statistics from products"""
        products = ProductManager.load_products()
        
        total_products = len(products)
        total_quantity = sum(p.get("quantity", 0) for p in products)
        total_value = sum(p.get("s_price", 0) * p.get("quantity", 0) for p in products)
        
        return {
            "total_products": total_products,
            "total_quantity": total_quantity,
            "total_value": total_value,
            "products": products
        }
    
    @staticmethod
    def add_product(name, product_type, p_price, s_price, quantity, supplier):
        """Add a new product"""
        products = ProductManager.load_products()
        
        # Check if product exists
        if any(p["name"].lower() == name.lower() for p in products):
            return False, "Product already exists!"
        
        new_product = {
            "id": len(products) + 1 if products else 1,
            "name": name,
            "type": product_type,
            "p_price": p_price,
            "s_price": s_price,
            "quantity": quantity,
            "supplier": supplier,
            "added_date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        }
        
        products.append(new_product)
        ProductManager.save_products(products)
        return True, "Product added successfully!"
    
    @staticmethod
    def update_product(product_id, name, product_type, p_price, s_price, quantity, supplier):
        """Update an existing product"""
        products = ProductManager.load_products()
        
        for product in products:
            if product["id"] == product_id:
                product["name"] = name
                product["type"] = product_type
                product["p_price"] = p_price
                product["s_price"] = s_price
                product["quantity"] = quantity
                product["supplier"] = supplier
                ProductManager.save_products(products)
                return True, "Product updated successfully!"
        
        return False, "Product not found!"
    
    @staticmethod
    def delete_product(product_id):
        """Delete a product"""
        products = ProductManager.load_products()
        products = [p for p in products if p["id"] != product_id]
        ProductManager.save_products(products)
        return True, "Product deleted successfully!"
    
    @staticmethod
    def search_products(search_key):
        """Search products by name"""
        products = ProductManager.load_products()
        return [p for p in products if search_key.lower() in p["name"].lower()]
    
# =====================Customer Mangement ===========================



# ===================== MAIN APPLICATION WINDOW =====================
class InventoryManagementApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        # Main container
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar and content
        self.sidebar = SideBar(self)
        self.content_area = QStackedWidget()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area, 1)
        
        # Initialize pages
        self.init_pages()
        
        # Connect sidebar buttons
        self.sidebar.dashboard_btn.clicked.connect(lambda: self.show_page(0))
        self.sidebar.products_btn.clicked.connect(lambda: self.show_page(1))
        self.sidebar.customers_btn.clicked.connect(lambda: self.show_page(2))
        self.sidebar.suppliers_btn.clicked.connect(lambda: self.show_page(3))
        self.sidebar.employees_btn.clicked.connect(lambda: self.show_page(4))
        self.sidebar.expired_btn.clicked.connect(lambda: self.show_page(5))
        self.sidebar.analysis_btn.clicked.connect(lambda: self.show_page(6))
        
        self.show_page(0)
    
    def init_pages(self):
        """Initialize all pages"""
        self.dashboard_page = DashboardPage()
        self.products_page = ProductsPage()
        
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.products_page)
        self.content_area.addWidget(PlaceholderPage("Customers"))
        self.content_area.addWidget(PlaceholderPage("Suppliers"))
        self.content_area.addWidget(PlaceholderPage("Employees"))
        self.content_area.addWidget(PlaceholderPage("Expired Products"))
        self.content_area.addWidget(DataAnalysisPage())
    
    def show_page(self, index):
        """Switch to the specified page"""
        # Refresh products page data
        if index == 1:
            self.products_page.refresh_data()
        # Refresh dashboard data
        elif index == 0:
            self.dashboard_page.refresh_statistics()
        
        self.content_area.setCurrentIndex(index)


# ===================== SIDEBAR COMPONENT =====================
class SideBar(QWidget):
    """Left sidebar with navigation buttons"""
    
    def __init__(self, parent):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {COLORS['sidebar']}; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Inventory System")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['text_dark']}; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Navigation buttons
        button_style = self.create_button_style()
        
        self.dashboard_btn = self.create_nav_button("📊 Dashboard", button_style)
        layout.addWidget(self.dashboard_btn)
        
        self.products_btn = self.create_nav_button("📦 Products", button_style)
        layout.addWidget(self.products_btn)
        
        self.customers_btn = self.create_nav_button("👥 Customers", button_style)
        layout.addWidget(self.customers_btn)
        
        self.suppliers_btn = self.create_nav_button("🏭 Suppliers", button_style)
        layout.addWidget(self.suppliers_btn)
        
        self.employees_btn = self.create_nav_button("👔 Employees", button_style)
        layout.addWidget(self.employees_btn)
        
        self.expired_btn = self.create_nav_button("⏰ Expired Products", button_style)
        layout.addWidget(self.expired_btn)
        
        self.analysis_btn = self.create_nav_button("📈 Data Analysis", button_style)
        layout.addWidget(self.analysis_btn)
        
        layout.addStretch()
    
    def create_nav_button(self, text, style):
        """Create a styled navigation button"""
        btn = QPushButton(text)
        btn.setStyleSheet(style)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(45)
        btn.setFont(self.create_button_font())
        return btn
    
    def create_button_style(self):
        """Create button stylesheet"""
        return f"""
            QPushButton {{
                background-color: {COLORS['white']};
                color: {COLORS['text_dark']};
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                text-align: left;
                padding-left: 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                border: 1px solid {COLORS['primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
            }}
        """
    
    def create_button_font(self):
        """Create button font"""
        font = QFont()
        font.setPointSize(12)
        return font


# ===================== PRODUCTS PAGE =====================
class ProductsPage(QWidget):
    """Products management page with Add and View modes"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Horizontal layout for two modes
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        
        # Left sidebar (mode selection)
        self.mode_panel = self.create_mode_panel()
        h_layout.addWidget(self.mode_panel, 0)
        
        # Right content area (stacked)
        self.content_stack = QStackedWidget()
        self.add_product_widget = AddProductWidget(self)
        self.view_product_widget = ViewProductWidget(self)
        
        self.content_stack.addWidget(self.add_product_widget)
        self.content_stack.addWidget(self.view_product_widget)
        
        h_layout.addWidget(self.content_stack, 1)
        
        main_layout.addLayout(h_layout)
    
    def create_mode_panel(self):
        """Create left panel with mode buttons"""
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"background-color: {COLORS['white']}; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Products")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        # Add Product button
        add_btn = QPushButton("➕ Add Product")
        add_btn.setStyleSheet(self.get_mode_button_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.show_add_mode)
        layout.addWidget(add_btn)
        
        # View Product button
        view_btn = QPushButton("👁️ View Product")
        view_btn.setStyleSheet(self.get_mode_button_style())
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setFixedHeight(45)
        view_btn.clicked.connect(self.show_view_mode)
        layout.addWidget(view_btn)
        
        layout.addStretch()
        return panel
    
    def get_mode_button_style(self):
        """Get style for mode buttons"""
        return f"""
            QPushButton {{
                background-color: {COLORS['light_bg']};
                color: {COLORS['text_dark']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def show_add_mode(self):
        """Switch to Add Product mode"""
        self.content_stack.setCurrentIndex(0)
    
    def show_view_mode(self):
        """Switch to View Product mode"""
        self.content_stack.setCurrentIndex(1)
        self.view_product_widget.load_products()
    
    def refresh_data(self):
        """Refresh data in both modes"""
        self.add_product_widget.reset_form()
        self.view_product_widget.load_products()


# ===================== ADD PRODUCT WIDGET =====================
class AddProductWidget(QWidget):
    """Widget for adding new products"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # ===== Top Section: Add Product Form =====
        form_frame = QFrame()
        form_frame.setFixedHeight(550)
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(25, 20, 25, 20)
        form_layout.setSpacing(20)
        
        # Title
        form_title = QLabel("Add New Product")
        form_title_font = QFont()
        form_title_font.setPointSize(20)
        form_title_font.setBold(True)
        form_title.setFont(form_title_font)
        form_title.setStyleSheet(f"color: {COLORS['text_dark']};")
        form_layout.addWidget(form_title)
        form_title.setMinimumHeight(50)
        form_title.setContentsMargins(0, 0, 0, 20)  # top=20, bottom=20

        # Form fields in grid
        grid = QGridLayout()
        grid.setSpacing(18)
        
        # Product Name
        form_layout.addWidget(self.create_label("Product Name:"))
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(35)
        self.name_input.setStyleSheet(self.get_input_style())
        form_layout.addWidget(self.name_input)
        form_title.setContentsMargins(0, 0, 15, 0)
        self.name_input.setStyleSheet(self.get_input_style() + "font-size: 24px;")
        # Type
        form_layout.addWidget(self.create_label("Type:"))
        self.type_input = QLineEdit()
        self.type_input.setFixedHeight(35)
        self.type_input.setStyleSheet(self.get_input_style())
        form_layout.addWidget(self.type_input)

        # Purchase Price & Sell Price
       # Purchase Price & Sell Price & Quantity (Side by Side)
        three_label_layout = QHBoxLayout()
        three_label_layout.addWidget(self.create_label("Purchase Price:"))
        three_label_layout.addSpacing(160)
        
        three_label_layout.addWidget(self.create_label("Sell Price:"))
        three_label_layout.addSpacing(192)
        
        three_label_layout.addWidget(self.create_label("Quantity:"))
        three_label_layout.addSpacing(0)
        three_label_layout.addStretch()
        form_layout.addLayout(three_label_layout)

        three_input_layout = QHBoxLayout()

        self.p_price_input = QLineEdit()
        self.p_price_input.setFixedHeight(32)
        self.p_price_input.setFixedWidth(200)
        self.p_price_input.setPlaceholderText("0")
        self.p_price_input.setStyleSheet(self.get_input_style())
        three_input_layout.addWidget(self.p_price_input)

        three_input_layout.addSpacing(60)

        self.s_price_input = QLineEdit()
        self.s_price_input.setFixedHeight(32)
        self.s_price_input.setFixedWidth(200)
        self.s_price_input.setPlaceholderText("0")
        self.s_price_input.setStyleSheet(self.get_input_style())
        three_input_layout.addWidget(self.s_price_input)

        three_input_layout.addSpacing(60)

        self.quantity_input = QLineEdit()
        self.quantity_input.setFixedHeight(32)
        self.quantity_input.setFixedWidth(200)
        self.quantity_input.setPlaceholderText("0")
        self.quantity_input.setStyleSheet(self.get_input_style())
        three_input_layout.addWidget(self.quantity_input)

        three_input_layout.addStretch()
        form_layout.addLayout(three_input_layout)
        
        # Supplier
        form_layout.addWidget(self.create_label("Supplier Name:"))
        self.supplier_input = QLineEdit()
        self.supplier_input.setFixedHeight(35)
        self.supplier_input.setStyleSheet(self.get_input_style())
        form_layout.addWidget(self.supplier_input)
        form_title.setContentsMargins(0, 10, 0, 3)
        main_layout.addWidget(form_frame)
        
        # Add button
        add_btn = QPushButton("Add Product")
        add_btn.setFixedHeight(45)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_product)
        main_layout.addWidget(add_btn)
        
        # ===== Bottom Section: Products List =====
        list_title = QLabel("All Products")
        list_title_font = QFont()
        list_title_font.setPointSize(12)
        list_title_font.setBold(True)
        list_title.setFont(list_title_font)
        list_title.setStyleSheet(f"color: {COLORS['text_dark']}; margin-top: 20px;")
        main_layout.addWidget(list_title)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Type", "Purchase Price", "Sell Price", "Quantity", "Supplier"]
        )
        self.products_table.setStyleSheet(self.get_table_style())
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.products_table, 1)
        
        self.load_products()
    
    def load_products(self):
        """Load products into table"""
        products = ProductManager.load_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.products_table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.products_table.setItem(row, 2, QTableWidgetItem(product["type"]))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product["p_price"])))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product["s_price"])))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product["quantity"])))
            self.products_table.setItem(row, 6, QTableWidgetItem(product["supplier"]))
    
    def add_product(self):
        """Handle add product"""
        name = self.name_input.text().strip()
        product_type = self.type_input.text().strip()
        try:
             p_price = int(self.p_price_input.text()) if self.p_price_input.text() else 0
             s_price = int(self.s_price_input.text()) if self.s_price_input.text() else 0
             quantity = int(self.quantity_input.text()) if self.quantity_input.text() else 0
        except ValueError:
             QMessageBox.warning(self, "Error", "Prices and Quantity must be numbers!")
             return
        supplier = self.supplier_input.text().strip()
        
        # Validation
        if not all([name, product_type, supplier]) or p_price == 0 or s_price == 0 or quantity == 0:
            QMessageBox.warning(self, "Error", "Please fill all fields with valid values!")
            return
        
        # Add product
        success, message = ProductManager.add_product(name, product_type, p_price, s_price, quantity, supplier)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.reset_form()
            self.load_products()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def reset_form(self):
        """Reset form fields"""
        self.name_input.clear()
        self.type_input.clear()
        self.p_price_input.clear()
        self.s_price_input.clear()
        self.quantity_input.clear()
        self.supplier_input.clear()
        self.load_products()
    
    def create_label(self, text):
        """Create styled label"""
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;  font-size:14px;")
        return label
    
    def get_input_style(self):
        """Get input field style"""
        return f"""
            QLineEdit, QSpinBox {{
                background-color: {COLORS['light_bg']};
                color: {COLORS['text_dark']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def get_table_style(self):
        """Get table style"""
        return f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                gridline-color: #E0E0E0;
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {COLORS['text_dark']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """


# ===================== VIEW PRODUCT WIDGET =====================
class ViewProductWidget(QWidget):
    """Widget for viewing and editing products"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)
        
        # ===== Top Section: Search (30% height) =====
        search_frame = QFrame()
        search_frame.setFixedHeight(120)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(20, 15, 20, 15)
        search_layout.setSpacing(10)
        
        search_title = QLabel("Search Product")
        search_title_font = QFont()
        search_title_font.setPointSize(12)
        search_title_font.setBold(True)
        search_title.setFont(search_title_font)
        search_title.setStyleSheet(f"color: {COLORS['text_dark']};")
        search_layout.addWidget(search_title)
        
        # Search input with button
        search_h_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        self.search_input.setPlaceholderText("Enter product name...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['light_bg']};
                color: {COLORS['text_dark']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """)
        search_h_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setFixedWidth(120)
        search_btn.setFixedHeight(40)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #3A7BC8;
            }}
        """)
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.clicked.connect(self.search_products)
        search_h_layout.addWidget(search_btn)
        
        search_layout.addLayout(search_h_layout)
        main_layout.addWidget(search_frame)
        
        # ===== Bottom Section: Results Table (70% height) =====
        results_title = QLabel("Search Results")
        results_title_font = QFont()
        results_title_font.setPointSize(12)
        results_title_font.setBold(True)
        results_title.setFont(results_title_font)
        results_title.setStyleSheet(f"color: {COLORS['text_dark']}; margin-top: 10px;")
        main_layout.addWidget(results_title)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Type", "P.Price", "S.Price", "Quantity", "Supplier", "Action"]
        )
        self.results_table.setStyleSheet(self.get_table_style())
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.results_table, 1)
    
    def search_products(self):
        """Search for products"""
        search_key = self.search_input.text().strip()
        
        if not search_key:
            QMessageBox.warning(self, "Error", "Please enter a product name to search!")
            return
        
        products = ProductManager.search_products(search_key)
        
        if not products:
            QMessageBox.information(self, "No Results", "No products found!")
            self.results_table.setRowCount(0)
            return
        
        self.display_results(products)
    
    def display_results(self, products):
        """Display search results in table"""
        self.results_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # ID
            self.results_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            # Name
            self.results_table.setItem(row, 1, QTableWidgetItem(product["name"]))
            # Type
            self.results_table.setItem(row, 2, QTableWidgetItem(product["type"]))
            # Purchase Price
            self.results_table.setItem(row, 3, QTableWidgetItem(str(product["p_price"])))
            # Sell Price
            self.results_table.setItem(row, 4, QTableWidgetItem(str(product["s_price"])))
            # Quantity
            self.results_table.setItem(row, 5, QTableWidgetItem(str(product["quantity"])))
            # Supplier
            self.results_table.setItem(row, 6, QTableWidgetItem(product["supplier"]))
            
            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(5)
            
            # Edit button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedWidth(80)
            edit_btn.setStyleSheet(self.get_action_button_style(COLORS['warning']))
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            action_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedWidth(80)
            delete_btn.setStyleSheet(self.get_action_button_style(COLORS['error']))
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, p_id=product["id"]: self.delete_product(p_id))
            action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.results_table.setCellWidget(row, 7, action_widget)
    
    def edit_product(self, product):
        """Open edit dialog for product"""
        dialog = EditProductDialog(self, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.search_products()
    
    def delete_product(self, product_id):
        """Delete a product"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = ProductManager.delete_product(product_id)
            QMessageBox.information(self, "Success", message)
            self.search_products()
    
    def load_products(self):
        """Load all products"""
        products = ProductManager.load_products()
        self.display_results(products)
    
    def get_action_button_style(self, color):
        """Get style for action buttons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS['white']};
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10px;
                padding: 5px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """
    
    def get_table_style(self):
        """Get table style"""
        return f"""
            QTableWidget {{
                background-color: {COLORS['white']};
                gridline-color: #E0E0E0;
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {COLORS['text_dark']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """


# ===================== EDIT PRODUCT DIALOG =====================
class EditProductDialog(QDialog):
    """Dialog for editing product details"""
    
    def __init__(self, parent, product):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle(f"Edit Product - {product['name']}")
        self.setGeometry(150, 150, 500, 450)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel(f"Edit Product: {product['name']}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        # Product Name
        layout.addWidget(self.create_label("Product Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(product["name"])
        self.name_input.setFixedHeight(35)
        self.name_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.name_input)
        
        # Type
        layout.addWidget(self.create_label("Type:"))
        self.type_input = QLineEdit()
        self.type_input.setText(product["type"])
        self.type_input.setFixedHeight(35)
        self.type_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.type_input)
        
        # Purchase Price
        layout.addWidget(self.create_label("Purchase Price:"))
        self.p_price_input = QSpinBox()
        self.p_price_input.setValue(product["p_price"])
        
        self.p_price_input.setMaximum(999999)
        self.p_price_input.setFixedHeight(35)
        self.p_price_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.p_price_input)
        
        # Sell Price
        layout.addWidget(self.create_label("Sell Price:"))
        self.s_price_input = QSpinBox()
        self.s_price_input.setValue(product["s_price"])
        self.s_price_input.setMaximum(999999)
        self.s_price_input.setFixedHeight(35)
        self.s_price_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.s_price_input)
        
        # Quantity
        layout.addWidget(self.create_label("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setValue(product["quantity"])
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setFixedHeight(35)
        self.quantity_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.quantity_input)
        
        # Supplier
        layout.addWidget(self.create_label("Supplier Name:"))
        self.supplier_input = QLineEdit()
        self.supplier_input.setText(product["supplier"])
        self.supplier_input.setFixedHeight(35)
        self.supplier_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.supplier_input)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        save_btn.clicked.connect(self.save_changes)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_light']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #95A5A6;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def save_changes(self):
        """Save product changes"""
        name = self.name_input.text().strip()
        product_type = self.type_input.text().strip()
        p_price = self.p_price_input.value()
        s_price = self.s_price_input.value()
        quantity = self.quantity_input.value()
        supplier = self.supplier_input.text().strip()
        
        if not all([name, product_type, supplier]) or p_price == 0 or s_price == 0 or quantity == 0:
            QMessageBox.warning(self, "Error", "Please fill all fields with valid values!")
            return
        
        success, message = ProductManager.update_product(
            self.product["id"], name, product_type, p_price, s_price, quantity, supplier
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def create_label(self, text):
        """Create styled label"""
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold; font-size: 10px;")
        return label
    
    def get_input_style(self):
        """Get input style"""
        return f"""
            QLineEdit, QSpinBox {{
                background-color: {COLORS['light_bg']};
                color: {COLORS['text_dark']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
# =====================customer widget======================


# ===================== DASHBOARD PAGE =====================
class DashboardPage(QWidget):
    """Dashboard page with statistics cards"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Page Title
        title = QLabel("Dashboard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']}; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        # Statistics Cards Grid
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(20)
        
        # Create card references for updating
        self.cards_data = {}
        self.update_statistics()
        
        main_layout.addLayout(self.cards_layout)
        main_layout.addStretch()
    
    def update_statistics(self):
        """Update statistics from products.json"""
        # Clear old cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get fresh statistics
        stats = ProductManager.get_statistics()
        
        cards_data = [
            ("Total Products", str(stats['total_products']), COLORS['card_1']),
            ("Total Customers", "342", COLORS['card_2']),
            ("Total Suppliers", "48", COLORS['card_3']),
            ("Total Employees", "156", COLORS['card_4']),
            ("Total Quantity", str(stats['total_quantity']), COLORS['card_5']),
            ("Stock Value", f"${stats['total_value']:,}", COLORS['card_6']),
        ]
        
        for index, (title_text, value, color) in enumerate(cards_data):
            row = index // 3
            col = index % 3
            card = StatisticCard(title_text, value, color)
            self.cards_layout.addWidget(card, row, col)
    
    def refresh_statistics(self):
        """Refresh statistics when page is shown"""
        self.update_statistics()


# ===================== STATISTIC CARD COMPONENT =====================
class StatisticCard(QFrame):
    """A single statistics card"""
    
    def __init__(self, title, value, color):
        super().__init__()
        self.setFixedHeight(150)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border-left: 5px solid {color};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(11)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['text_light']}; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        layout.addStretch()


# ===================== DATA ANALYSIS PAGE =====================
class DataAnalysisPage(QWidget):
    """Data Analysis page"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Data Analysis")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']}; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Content Frame
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Placeholder
        placeholder = QLabel("📊 Charts and Analytics Area\n\nPlaceholder for data visualization, sales trends, product performance, and customer analytics.\n\nUpcoming features: Line charts, Bar charts, Pie charts, Tables, and Reports")
        placeholder_font = QFont()
        placeholder_font.setPointSize(13)
        placeholder.setFont(placeholder_font)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"color: {COLORS['text_light']}; line-height: 1.8;")
        
        content_layout.addWidget(placeholder, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(content_frame, 1)
        layout.addStretch()


# ===================== PLACEHOLDER PAGE =====================
class PlaceholderPage(QWidget):
    """Generic placeholder page"""
    
    def __init__(self, page_name):
        super().__init__()
        self.page_name = page_name
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel(f"{page_name}")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        # Content Frame
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Placeholder Text
        placeholder_text = QLabel(f"This is the {page_name} management page.\n\nContent for {page_name} will be displayed here.")
        placeholder_font = QFont()
        placeholder_font.setPointSize(12)
        placeholder_text.setFont(placeholder_font)
        placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_text.setStyleSheet(f"color: {COLORS['text_light']};")
        
        content_layout.addWidget(placeholder_text)
        
        layout.addWidget(content_frame, 1)
        layout.addStretch()


# ===================== APPLICATION ENTRY POINT =====================
def main():
    """Initialize and run the application"""
    app = QApplication(sys.argv)
    
    window = InventoryManagementApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


