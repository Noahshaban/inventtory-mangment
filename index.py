import sys
import os
import json
import shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QGridLayout, QFrame, QLineEdit,
    QSpinBox, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QHeaderView, QDialog, QTextEdit, QFileDialog, QDateEdit
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap

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
    def filter_products(search_key="", product_type=None, min_price=None, max_price=None):
        """Filter products by optional name, type, and sell price range"""
        products = ProductManager.load_products()
        results = []
        search_key = (search_key or "").lower()
        product_type = (product_type or "").lower()
        
        for product in products:
            name = product.get("name", "")
            type_value = product.get("type", "")
            sell_price = product.get("s_price", 0)
            
            if search_key and search_key not in name.lower():
                continue
            if product_type and product_type != "all" and product_type != type_value.lower():
                continue
            if min_price is not None and sell_price < min_price:
                continue
            if max_price is not None and sell_price > max_price:
                continue
            results.append(product)
        return results
    
    @staticmethod
    def search_products(search_key):
        """Backward compatible name search"""
        return ProductManager.filter_products(search_key=search_key)
    
    @staticmethod
    def get_distinct_product_types():
        """Return sorted unique product types"""
        products = ProductManager.load_products()
        types = sorted({p.get("type", "").strip() for p in products if p.get("type")})
        return types
    
# =====================Customer Management ===========================
class CustomerManager:
    """Manage customers stored in JSON file"""
    
    FILE_NAME = os.path.join(os.path.dirname(__file__), "customers.json")
    
    @staticmethod
    def _ensure_directory():
        directory = os.path.dirname(CustomerManager.FILE_NAME)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def load_customers():
        """Load customers from JSON file"""
        try:
            with open(CustomerManager.FILE_NAME, "r", encoding="utf-8") as f:
                data = f.read().strip()
                return json.loads(data) if data else []
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_customers(customers):
        """Persist customers to JSON file"""
        CustomerManager._ensure_directory()
        with open(CustomerManager.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(customers, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def generate_customer_code(first_name, second_name, number):
        """Generate customer code based on initials and last digits"""
        first_initial = first_name.strip()[:1].upper()
        second_initial = second_name.strip()[:1].upper()
        digits = "".join(ch for ch in number if ch.isdigit())
        
        if not first_initial or not second_initial or not digits:
            return ""
        
        last_digits = digits[-3:] if len(digits) >= 3 else digits
        return f"{first_initial}{second_initial}{last_digits}"
    
    @staticmethod
    def add_customer(first_name, second_name, number, address, customer_type, purchase_value, notes):
        """Add a customer entry"""
        customers = CustomerManager.load_customers()
        code = CustomerManager.generate_customer_code(first_name, second_name, number)
        
        if not code:
            return False, "Unable to generate code. Please check the provided data.", None
        
        if any(cust["code"] == code and cust["number"] == number for cust in customers):
            return False, "Customer already exists!", None
        
        full_name = f"{first_name.strip().title()} {second_name.strip().title()}".strip()
        new_customer = {
            "code": code,
            "first_name": first_name.strip(),
            "second_name": second_name.strip(),
            "full_name": full_name,
            "number": number.strip(),
            "address": address.strip(),
            "customer_type": customer_type,
            "purchase_value": purchase_value,
            "notes": notes.strip(),
            "added_date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        }
        
        customers.append(new_customer)
        CustomerManager.save_customers(customers)
        return True, "Customer added successfully!", new_customer
    
    @staticmethod
    def get_total_customers():
        """Return total number of customers"""
        return len(CustomerManager.load_customers())
    
    @staticmethod
    def get_customers():
        """Return list of customers"""
        return CustomerManager.load_customers()
    
    @staticmethod
    def search_customers(search_key="", customer_type=None, min_purchase=None, max_purchase=None):
        """Search customers by name/code/number with optional filters"""
        customers = CustomerManager.load_customers()
        key = search_key.strip().lower()
        results = []
        for cust in customers:
            full_name = cust.get("full_name", "")
            code = cust.get("code", "")
            number = cust.get("number", "")
            purchase_value = float(cust.get("purchase_value", 0))
            cust_type = cust.get("customer_type", "")
            
            if key and (
                key not in full_name.lower()
                and key not in code.lower()
                and key not in number.lower()
            ):
                continue
            if customer_type and customer_type.lower() != "all" and cust_type.lower() != customer_type.lower():
                continue
            if min_purchase is not None and purchase_value < min_purchase:
                continue
            if max_purchase is not None and purchase_value > max_purchase:
                continue
            results.append(cust)
        return results
    
    @staticmethod
    def delete_customer(code):
        """Delete customer by code"""
        customers = CustomerManager.load_customers()
        updated = [cust for cust in customers if cust.get("code") != code]
        if len(updated) == len(customers):
            return False, "Customer not found!"
        CustomerManager.save_customers(updated)
        return True, "Customer deleted successfully!"

    @staticmethod
    def update_customer(original_code, first_name, second_name, number, address, customer_type, purchase_value, notes):
        """Update existing customer details"""
        customers = CustomerManager.load_customers()
        new_code = CustomerManager.generate_customer_code(first_name, second_name, number)
        
        if not new_code:
            return False, "Unable to generate code. Please check the provided data.", None
        
        digits = "".join(ch for ch in number if ch.isdigit())
        if not digits:
            return False, "Customer number must contain digits.", None
        
        for cust in customers:
            if cust.get("code") != original_code and cust.get("code") == new_code and cust.get("number") == number:
                return False, "Another customer with same info already exists!", None
        
        for customer in customers:
            if customer.get("code") == original_code:
                customer["code"] = new_code
                customer["first_name"] = first_name.strip()
                customer["second_name"] = second_name.strip()
                customer["full_name"] = f"{first_name.strip().title()} {second_name.strip().title()}".strip()
                customer["number"] = number.strip()
                customer["address"] = address.strip()
                customer["customer_type"] = customer_type
                customer["purchase_value"] = purchase_value
                customer["notes"] = notes.strip()
                customer["updated_date"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                CustomerManager.save_customers(customers)
                return True, "Customer updated successfully!", customer
        
        return False, "Customer not found!", None


class SupplierManager:
    """Manage suppliers stored in JSON file"""
    
    FILE_NAME = os.path.join(os.path.dirname(__file__), "suppliers.json")
    
    @staticmethod
    def _ensure_directory():
        directory = os.path.dirname(SupplierManager.FILE_NAME)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def load_suppliers():
        try:
            with open(SupplierManager.FILE_NAME, "r", encoding="utf-8") as f:
                data = f.read().strip()
                return json.loads(data) if data else []
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_suppliers(suppliers):
        SupplierManager._ensure_directory()
        with open(SupplierManager.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(suppliers, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def generate_supplier_code(name, number):
        name_part = "".join(filter(str.isalpha, name.strip()))[:2].upper()
        digits = "".join(ch for ch in number if ch.isdigit())
        return f"{name_part or 'SP'}{digits[-3:] if digits else ''}"
    
    @staticmethod
    def add_supplier(code, name, number, supply_type, address, stock_value, supplier_type, notes):
        suppliers = SupplierManager.load_suppliers()
        code = code.strip() or SupplierManager.generate_supplier_code(name, number)
        
        if any(sup.get("code") == code for sup in suppliers):
            return False, "Supplier code already exists!", None
        
        new_supplier = {
            "code": code,
            "name": name.strip(),
            "number": number.strip(),
            "supply_type": supply_type.strip(),
            "address": address.strip(),
            "stock_value": stock_value,
            "supplier_type": supplier_type,
            "notes": notes.strip(),
            "added_date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        }
        
        suppliers.append(new_supplier)
        SupplierManager.save_suppliers(suppliers)
        return True, "Supplier added successfully!", new_supplier
    
    @staticmethod
    def get_total_suppliers():
        return len(SupplierManager.load_suppliers())
    
    @staticmethod
    def get_suppliers():
        return SupplierManager.load_suppliers()
    
    @staticmethod
    def search_suppliers(search_key="", supplier_type=None, supply_type=None, min_stock=None, max_stock=None):
        suppliers = SupplierManager.load_suppliers()
        key = (search_key or "").lower()
        results = []
        
        for sup in suppliers:
            matches_key = (
                key in sup.get("name", "").lower()
                or key in sup.get("code", "").lower()
                or key in sup.get("number", "").lower()
            ) if key else True
            
            if not matches_key:
                continue
            
            type_match = (
                True if not supplier_type or supplier_type.lower() == "all"
                else sup.get("supplier_type", "").lower() == supplier_type.lower()
            )
            if not type_match:
                continue
            
            if supply_type and supply_type.lower() != "all":
                if supply_type.lower() not in sup.get("supply_type", "").lower():
                    continue
                continue
            
            stock_value = float(sup.get("stock_value", 0))
            if min_stock is not None and stock_value < min_stock:
                continue
            if max_stock is not None and stock_value > max_stock:
                continue
            
            results.append(sup)
        
        return results
    
    @staticmethod
    def delete_supplier(code):
        suppliers = SupplierManager.load_suppliers()
        filtered = [sup for sup in suppliers if sup.get("code") != code]
        if len(filtered) == len(suppliers):
            return False, "Supplier not found!"
        SupplierManager.save_suppliers(filtered)
        return True, "Supplier deleted successfully!"
    
    @staticmethod
    def update_supplier(original_code, code, name, number, supply_type, address, stock_value, supplier_type, notes):
        suppliers = SupplierManager.load_suppliers()
        code = code.strip() or SupplierManager.generate_supplier_code(name, number)
        
        if any(
            sup.get("code") == code and sup.get("code") != original_code
            for sup in suppliers
        ):
            return False, "Another supplier already uses this code!", None
        
        for sup in suppliers:
            if sup.get("code") == original_code:
                sup["code"] = code
                sup["name"] = name.strip()
                sup["number"] = number.strip()
                sup["supply_type"] = supply_type.strip()
                sup["address"] = address.strip()
                sup["stock_value"] = stock_value
                sup["supplier_type"] = supplier_type
                sup["notes"] = notes.strip()
                sup["updated_date"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                SupplierManager.save_suppliers(suppliers)
                return True, "Supplier updated successfully!", sup
        
        return False, "Supplier not found!", None
    
    @staticmethod
    def get_supplier_types():
        suppliers = SupplierManager.load_suppliers()
        return sorted({sup.get("supplier_type", "") for sup in suppliers if sup.get("supplier_type")})


class EmployeeManager:
    """Manage employees stored in JSON"""
    
    FILE_NAME = os.path.join(os.path.dirname(__file__), "employees.json")
    PHOTO_DIR = os.path.join(os.path.dirname(__file__), "employee_photos")
    CODE_PREFIX = "AML"
    
    @staticmethod
    def _ensure_directory(path=None):
        directory = path or os.path.dirname(EmployeeManager.FILE_NAME)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def load_employees():
        try:
            with open(EmployeeManager.FILE_NAME, "r", encoding="utf-8") as f:
                data = f.read().strip()
                return json.loads(data) if data else []
        except FileNotFoundError:
            return []
    
    @staticmethod
    def save_employees(employees):
        EmployeeManager._ensure_directory()
        with open(EmployeeManager.FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(employees, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def _save_photo(photo_path):
        if not photo_path or not os.path.isfile(photo_path):
            return ""
        EmployeeManager._ensure_directory(EmployeeManager.PHOTO_DIR)
        _, ext = os.path.splitext(photo_path)
        safe_ext = ext if ext else ".png"
        filename = f"employee_{int(datetime.now().timestamp())}{safe_ext}"
        dest_path = os.path.join(EmployeeManager.PHOTO_DIR, filename)
        try:
            shutil.copyfile(photo_path, dest_path)
            return dest_path
        except Exception:
            return ""
    
    @staticmethod
    def generate_employee_code(number):
        digits = "".join(ch for ch in (number or "") if ch.isdigit())
        last_digits = digits[-3:] if digits else "000"
        return f"{EmployeeManager.CODE_PREFIX}{last_digits}"
    
    @staticmethod
    def add_employee(name, number, address, salary, position, status, start_date, department, emergency_contact, photo_path):
        employees = EmployeeManager.load_employees()
        code = EmployeeManager.generate_employee_code(number)
        
        if any(emp.get("code") == code for emp in employees):
            code = f"{code}{len(employees)+1}"
        
        stored_photo = EmployeeManager._save_photo(photo_path)
        
        new_employee = {
            "code": code,
            "name": name.strip(),
            "number": number.strip(),
            "address": address.strip(),
            "salary": salary,
            "position": position.strip(),
            "status": status,
            "start_date": start_date,
            "department": department.strip(),
            "emergency_contact": emergency_contact.strip(),
            "photo_path": stored_photo,
            "added_date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        }
        
        employees.append(new_employee)
        EmployeeManager.save_employees(employees)
        return True, "Employee added successfully!", new_employee
    
    @staticmethod
    def get_total_employees():
        return len(EmployeeManager.load_employees())
    
    @staticmethod
    def search_employees(search_key="", status=None, department=None, min_salary=None, max_salary=None):
        employees = EmployeeManager.load_employees()
        key = (search_key or "").lower()
        results = []
        for emp in employees:
            name = emp.get("name", "")
            code = emp.get("code", "")
            number = emp.get("number", "")
            emp_status = emp.get("status", "")
            emp_department = emp.get("department", "")
            salary = float(emp.get("salary", 0))
            
            if key and key not in name.lower() and key not in code.lower() and key not in number.lower():
                continue
            if status and status.lower() != "all" and emp_status.lower() != status.lower():
                continue
            if department and department.lower() != "all" and emp_department.lower() != department.lower():
                continue
            if min_salary is not None and salary < min_salary:
                continue
            if max_salary is not None and salary > max_salary:
                continue
            results.append(emp)
        return results
    
    @staticmethod
    def delete_employee(code):
        employees = EmployeeManager.load_employees()
        filtered = [emp for emp in employees if emp.get("code") != code]
        if len(filtered) == len(employees):
            return False, "Employee not found!"
        EmployeeManager.save_employees(filtered)
        return True, "Employee deleted successfully!"
    
    @staticmethod
    def update_employee(original_code, name, number, address, salary, position, status, start_date, department, emergency_contact, photo_path=None):
        employees = EmployeeManager.load_employees()
        for emp in employees:
            if emp.get("code") == original_code:
                if photo_path:
                    stored_photo = EmployeeManager._save_photo(photo_path)
                    if stored_photo:
                        emp["photo_path"] = stored_photo
                emp["name"] = name.strip()
                emp["number"] = number.strip()
                emp["address"] = address.strip()
                emp["salary"] = salary
                emp["position"] = position.strip()
                emp["status"] = status
                emp["start_date"] = start_date
                emp["department"] = department.strip()
                emp["emergency_contact"] = emergency_contact.strip()
                emp["updated_date"] = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
                EmployeeManager.save_employees(employees)
                return True, "Employee updated successfully!", emp
        return False, "Employee not found!", None
    
    @staticmethod
    def get_departments():
        employees = EmployeeManager.load_employees()
        return sorted({emp.get("department", "") for emp in employees if emp.get("department")})


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
        self.customers_page = CustomersPage()
        self.suppliers_page = SuppliersPage()
        self.employees_page = EmployeesPage()
        
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.products_page)
        self.content_area.addWidget(self.customers_page)
        self.content_area.addWidget(self.suppliers_page)
        self.content_area.addWidget(self.employees_page)
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
        elif index == 2:
            self.customers_page.refresh_data()
        elif index == 3:
            self.suppliers_page.refresh_data()
        elif index == 4:
            self.employees_page.refresh_data()
        
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
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.type_filter = QComboBox()
        self.type_filter.setFixedHeight(36)
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
            }}
        """)
        self.type_filter.addItem("All")
        filter_layout.addWidget(QLabel("Type"))
        filter_layout.addWidget(self.type_filter, 1)
        
        self.min_price_filter = QDoubleSpinBox()
        self.min_price_filter.setPrefix("$")
        self.min_price_filter.setMaximum(9999999.99)
        self.min_price_filter.setDecimals(2)
        self.min_price_filter.setFixedHeight(36)
        self.min_price_filter.setStyleSheet(self.type_filter.styleSheet())
        
        self.max_price_filter = QDoubleSpinBox()
        self.max_price_filter.setPrefix("$")
        self.max_price_filter.setMaximum(9999999.99)
        self.max_price_filter.setDecimals(2)
        self.max_price_filter.setFixedHeight(36)
        self.max_price_filter.setStyleSheet(self.type_filter.styleSheet())
        
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Min Price"))
        price_layout.addWidget(self.min_price_filter)
        price_layout.addWidget(QLabel("Max Price"))
        price_layout.addWidget(self.max_price_filter)
        filter_layout.addLayout(price_layout, 2)
        
        apply_filter_btn = QPushButton("Apply Filters")
        apply_filter_btn.setFixedWidth(140)
        apply_filter_btn.setFixedHeight(36)
        apply_filter_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        apply_filter_btn.clicked.connect(self.search_products)
        filter_layout.addWidget(apply_filter_btn)
        
        search_layout.addLayout(filter_layout)
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
        
        self.update_type_filter_options()
    
    def search_products(self):
        """Search for products"""
        search_key = self.search_input.text().strip()
        selected_type = self.type_filter.currentText()
        min_price = self.min_price_filter.value()
        max_price = self.max_price_filter.value()
        
        min_price_value = min_price if min_price > 0 else None
        max_price_value = max_price if max_price > 0 else None
        if min_price_value and max_price_value and min_price_value > max_price_value:
            QMessageBox.warning(self, "Invalid Range", "Min price cannot be greater than max price.")
            return
        
        products = ProductManager.filter_products(
            search_key=search_key,
            product_type=selected_type if selected_type != "All" else None,
            min_price=min_price_value,
            max_price=max_price_value
        )
        
        if not products:
            QMessageBox.information(self, "No Results", "No products found!")
            self.results_table.setRowCount(0)
            return
        
        self.display_results(products)
    
    def update_type_filter_options(self):
        current = self.type_filter.currentText()
        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        self.type_filter.addItem("All")
        for product_type in ProductManager.get_distinct_product_types():
            self.type_filter.addItem(product_type)
        index = self.type_filter.findText(current)
        self.type_filter.setCurrentIndex(index if index != -1 else 0)
        self.type_filter.blockSignals(False)
    
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
        self.update_type_filter_options()
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

# ===================== CUSTOMERS PAGE =====================
class CustomersPage(QWidget):
    """Customers management page with Add and View modes"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        
        self.mode_panel = self.create_mode_panel()
        h_layout.addWidget(self.mode_panel, 0)
        
        self.content_stack = QStackedWidget()
        self.add_customer_widget = AddCustomerWidget(self)
        self.view_customer_widget = ViewCustomerWidget(self)
        
        self.content_stack.addWidget(self.add_customer_widget)
        self.content_stack.addWidget(self.view_customer_widget)
        
        h_layout.addWidget(self.content_stack, 1)
        main_layout.addLayout(h_layout)
    
    def create_mode_panel(self):
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"background-color: {COLORS['white']}; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        title = QLabel("Customers")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        add_btn = QPushButton("➕ Add Customer")
        add_btn.setStyleSheet(self.get_mode_button_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.show_add_mode)
        layout.addWidget(add_btn)
        
        view_btn = QPushButton("👁️ View Customers")
        view_btn.setStyleSheet(self.get_mode_button_style())
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setFixedHeight(45)
        view_btn.clicked.connect(self.show_view_mode)
        layout.addWidget(view_btn)
        
        layout.addStretch()
        return panel
    
    def get_mode_button_style(self):
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
        self.content_stack.setCurrentIndex(0)
    
    def show_view_mode(self):
        self.content_stack.setCurrentIndex(1)
        self.view_customer_widget.load_customers()
    
    def refresh_data(self):
        self.add_customer_widget.reset_form()
        self.view_customer_widget.load_customers()


class AddCustomerWidget(QWidget):
    """Widget for adding customers"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("Add Customer")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        
        self.first_name_input = self.create_line_edit("First Name")
        self.second_name_input = self.create_line_edit("Second Name")
        self.number_input = self.create_line_edit("Customer Number (e.g., phone)")
        self.address_input = self.create_line_edit("Address")
        
        self.customer_type_input = QComboBox()
        self.customer_type_input.addItems(["Regular", "Wholesale", "VIP", "Business"])
        self.customer_type_input.setStyleSheet(self.get_input_style())
        self.customer_type_input.setFixedHeight(36)
        
        self.purchase_value_input = QDoubleSpinBox()
        self.purchase_value_input.setPrefix("$")
        self.purchase_value_input.setMaximum(9999999.99)
        self.purchase_value_input.setDecimals(2)
        self.purchase_value_input.setStyleSheet(self.get_input_style())
        self.purchase_value_input.setFixedHeight(36)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setStyleSheet(self.get_input_style())
        self.notes_input.setFixedHeight(80)
        
        form_layout.addWidget(self.create_label("First Name"))
        form_layout.addWidget(self.first_name_input)
        form_layout.addWidget(self.create_label("Second Name"))
        form_layout.addWidget(self.second_name_input)
        form_layout.addWidget(self.create_label("Number"))
        form_layout.addWidget(self.number_input)
        form_layout.addWidget(self.create_label("Address"))
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.create_label("Customer Type"))
        form_layout.addWidget(self.customer_type_input)
        form_layout.addWidget(self.create_label("Purchases Value"))
        form_layout.addWidget(self.purchase_value_input)
        form_layout.addWidget(self.create_label("Notes"))
        form_layout.addWidget(self.notes_input)
        
        self.code_preview_label = QLabel("Customer Code: ---")
        self.code_preview_label.setStyleSheet(f"color: {COLORS['text_light']}; font-weight: bold;")
        form_layout.addWidget(self.code_preview_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("➕ Add Customer")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        add_btn.clicked.connect(self.handle_add_customer)
        
        reset_btn = QPushButton("Reset Form")
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_light']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #95A5A6;
            }}
        """)
        reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(reset_btn)
        form_layout.addLayout(btn_layout)
        form_layout.addStretch()
        
        main_layout.addWidget(form_frame, 0)
        main_layout.addStretch()
        
        self.first_name_input.textChanged.connect(self.update_code_preview)
        self.second_name_input.textChanged.connect(self.update_code_preview)
        self.number_input.textChanged.connect(self.update_code_preview)
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def create_field_group(self, label_text, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        label = self.create_label(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return container
    
    def create_line_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedHeight(36)
        line_edit.setStyleSheet(self.get_input_style())
        return line_edit
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def update_code_preview(self):
        code = CustomerManager.generate_customer_code(
            self.first_name_input.text(),
            self.second_name_input.text(),
            self.number_input.text()
        )
        self.code_preview_label.setText(f"Customer Code: {code if code else '---'}")
    
    def handle_add_customer(self):
        first_name = self.first_name_input.text().strip()
        second_name = self.second_name_input.text().strip()
        number = self.number_input.text().strip()
        address = self.address_input.text().strip()
        customer_type = self.customer_type_input.currentText()
        purchase_value = round(self.purchase_value_input.value(), 2)
        notes = self.notes_input.toPlainText().strip()
        
        if not all([first_name, second_name, number, address]):
            QMessageBox.warning(self, "Missing Data", "Please fill all required fields.")
            return
        
        digits = "".join(ch for ch in number if ch.isdigit())
        if len(digits) == 0:
            QMessageBox.warning(self, "Invalid Number", "Customer number must contain at least one digit.")
            return
        
        success, message, customer = CustomerManager.add_customer(
            first_name,
            second_name,
            number,
            address,
            customer_type,
            purchase_value,
            notes
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.code_preview_label.setText(f"Customer Code: {customer['code']}")
            if self.parent_page:
                self.parent_page.view_customer_widget.load_customers()
            self.reset_form()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def reset_form(self):
        self.first_name_input.clear()
        self.second_name_input.clear()
        self.number_input.clear()
        self.address_input.clear()
        self.customer_type_input.setCurrentIndex(0)
        self.purchase_value_input.setValue(0.0)
        self.notes_input.clear()
        self.code_preview_label.setText("Customer Code: ---")


class ViewCustomerWidget(QWidget):
    """Widget for viewing and managing customers"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.current_customers = []
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("View Customers")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, code, or number...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet(self.get_input_style())
        self.search_input.textChanged.connect(self.handle_search)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_customers)
        search_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(search_layout)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.customer_type_filter = QComboBox()
        self.customer_type_filter.addItems(["All", "Regular", "Wholesale", "VIP", "Business"])
        self.customer_type_filter.setFixedHeight(36)
        self.customer_type_filter.setStyleSheet(self.get_input_style())
        self.customer_type_filter.currentIndexChanged.connect(self.load_customers)
        filter_layout.addWidget(QLabel("Type"))
        filter_layout.addWidget(self.customer_type_filter)
        
        self.min_purchase_filter = QDoubleSpinBox()
        self.min_purchase_filter.setPrefix("$")
        self.min_purchase_filter.setMaximum(9999999.99)
        self.min_purchase_filter.setDecimals(2)
        self.min_purchase_filter.setFixedHeight(36)
        self.min_purchase_filter.setStyleSheet(self.get_input_style())
        
        self.max_purchase_filter = QDoubleSpinBox()
        self.max_purchase_filter.setPrefix("$")
        self.max_purchase_filter.setMaximum(9999999.99)
        self.max_purchase_filter.setDecimals(2)
        self.max_purchase_filter.setFixedHeight(36)
        self.max_purchase_filter.setStyleSheet(self.get_input_style())
        
        filter_layout.addWidget(QLabel("Min Purchases"))
        filter_layout.addWidget(self.min_purchase_filter)
        filter_layout.addWidget(QLabel("Max Purchases"))
        filter_layout.addWidget(self.max_purchase_filter)
        
        apply_customer_filters = QPushButton("Apply Filters")
        apply_customer_filters.setFixedHeight(36)
        apply_customer_filters.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        apply_customer_filters.clicked.connect(self.load_customers)
        filter_layout.addWidget(apply_customer_filters)
        
        content_layout.addLayout(filter_layout)
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "Code", "Name", "Number", "Address", "Type", "Purchases Value", "Notes"
        ])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.customers_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                gridline-color: #E0E0E0;
            }
        """)
        content_layout.addWidget(self.customers_table)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.setFixedHeight(40)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        edit_btn.clicked.connect(self.edit_selected_customer)
        
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setFixedHeight(40)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
        """)
        delete_btn.clicked.connect(self.delete_selected_customer)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_frame, 1)
        self.load_customers()
    
    def get_input_style(self):
        return f"""
            QLineEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def load_customers(self):
        search_key = self.search_input.text().strip()
        customer_type = self.customer_type_filter.currentText()
        min_purchase = self.min_purchase_filter.value()
        max_purchase = self.max_purchase_filter.value()
        
        min_value = min_purchase if min_purchase > 0 else None
        max_value = max_purchase if max_purchase > 0 else None
        if min_value and max_value and min_value > max_value:
            QMessageBox.warning(self, "Invalid Range", "Min purchase cannot exceed max purchase.")
            return
        
        customers = CustomerManager.search_customers(
            search_key=search_key,
            customer_type=customer_type if customer_type != "All" else None,
            min_purchase=min_value,
            max_purchase=max_value
        )
        self.populate_table(customers)
    
    def populate_table(self, customers):
        self.current_customers = customers
        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            row_data = [
                customer.get("code", ""),
                customer.get("full_name", ""),
                customer.get("number", ""),
                customer.get("address", ""),
                customer.get("customer_type", ""),
                f"${customer.get('purchase_value', 0):,.2f}",
                customer.get("notes", "")
            ]
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.customers_table.setItem(row, col, item)
    
    def handle_search(self):
        self.load_customers()
    
    def get_selected_customer(self):
        row = self.customers_table.currentRow()
        if row == -1 or row >= len(self.current_customers):
            return None
        return self.current_customers[row]
    
    def edit_selected_customer(self):
        customer = self.get_selected_customer()
        if not customer:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return
        
        dialog = EditCustomerDialog(self, customer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def delete_selected_customer(self):
        customer = self.get_selected_customer()
        if not customer:
            QMessageBox.warning(self, "No Selection", "Please select a customer to delete.")
            return
        
        code = customer.get("code", "")
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete customer with code {code}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = CustomerManager.delete_customer(code)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_customers()
                if self.parent_page:
                    self.parent_page.add_customer_widget.reset_form()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def refresh_data(self):
        self.load_customers()


class SuppliersPage(QWidget):
    """Suppliers management page with Add and View modes"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        
        self.mode_panel = self.create_mode_panel()
        h_layout.addWidget(self.mode_panel, 0)
        
        self.content_stack = QStackedWidget()
        self.add_supplier_widget = AddSupplierWidget(self)
        self.view_supplier_widget = ViewSupplierWidget(self)
        
        self.content_stack.addWidget(self.add_supplier_widget)
        self.content_stack.addWidget(self.view_supplier_widget)
        
        h_layout.addWidget(self.content_stack, 1)
        main_layout.addLayout(h_layout)
    
    def create_mode_panel(self):
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"background-color: {COLORS['white']}; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        title = QLabel("Suppliers")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        add_btn = QPushButton("➕ Add Supplier")
        add_btn.setStyleSheet(self.get_mode_button_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.show_add_mode)
        layout.addWidget(add_btn)
        
        view_btn = QPushButton("👁️ View Suppliers")
        view_btn.setStyleSheet(self.get_mode_button_style())
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setFixedHeight(45)
        view_btn.clicked.connect(self.show_view_mode)
        layout.addWidget(view_btn)
        
        layout.addStretch()
        return panel
    
    def get_mode_button_style(self):
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
        self.content_stack.setCurrentIndex(0)
    
    def show_view_mode(self):
        self.content_stack.setCurrentIndex(1)
        self.view_supplier_widget.load_suppliers()
    
    def refresh_data(self):
        self.add_supplier_widget.reset_form()
        self.view_supplier_widget.load_suppliers()


class AddSupplierWidget(QWidget):
    """Widget for adding suppliers"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("Add Supplier")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        
        self.code_input = self.create_line_edit("Auto-generated if empty")
        self.name_input = self.create_line_edit("Supplier Name")
        self.number_input = self.create_line_edit("Contact Number")
        self.supply_type_input = self.create_line_edit("Supply Type (e.g., Electronics)")
        self.address_input = self.create_line_edit("Address")
        
        self.stock_value_input = QDoubleSpinBox()
        self.stock_value_input.setPrefix("$")
        self.stock_value_input.setMaximum(9999999.99)
        self.stock_value_input.setDecimals(2)
        self.stock_value_input.setFixedHeight(36)
        self.stock_value_input.setStyleSheet(self.get_input_style())
        
        self.supplier_type_input = QComboBox()
        self.supplier_type_input.addItems(["Regular", "Wholesale", "VIP", "Business"])
        self.supplier_type_input.setFixedHeight(36)
        self.supplier_type_input.setStyleSheet(self.get_input_style())
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setFixedHeight(90)
        self.notes_input.setStyleSheet(self.get_input_style())
        
        form_layout.addWidget(self.create_label("Code"))
        form_layout.addWidget(self.code_input)
        form_layout.addWidget(self.create_label("Name"))
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.create_label("Number"))
        form_layout.addWidget(self.number_input)
        form_layout.addWidget(self.create_label("Supply Type"))
        form_layout.addWidget(self.supply_type_input)
        form_layout.addWidget(self.create_label("Address"))
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.create_label("Stock Value"))
        form_layout.addWidget(self.stock_value_input)
        form_layout.addWidget(self.create_label("Supplier Type"))
        form_layout.addWidget(self.supplier_type_input)
        form_layout.addWidget(self.create_label("Notes"))
        form_layout.addWidget(self.notes_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        auto_code_btn = QPushButton("Generate Code")
        auto_code_btn.setFixedHeight(36)
        auto_code_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['hover']};
                border: 1px solid {COLORS['primary']};
                border-radius: 6px;
            }}
        """)
        auto_code_btn.clicked.connect(self.generate_code_from_inputs)
        btn_layout.addWidget(auto_code_btn)
        
        add_btn = QPushButton("➕ Add Supplier")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        add_btn.clicked.connect(self.handle_add_supplier)
        
        reset_btn = QPushButton("Reset Form")
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_light']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #95A5A6;
            }}
        """)
        reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(reset_btn)
        form_layout.addLayout(btn_layout)
        form_layout.addStretch()
        
        main_layout.addWidget(form_frame, 0)
        main_layout.addStretch()
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def create_field_group(self, label_text, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        label = self.create_label(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return container
    
    def create_line_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedHeight(36)
        line_edit.setStyleSheet(self.get_input_style())
        return line_edit
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def generate_code_from_inputs(self):
        generated = SupplierManager.generate_supplier_code(self.name_input.text(), self.number_input.text())
        self.code_input.setText(generated)
    
    def handle_add_supplier(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        supply_type = self.supply_type_input.text().strip()
        address = self.address_input.text().strip()
        stock_value = round(self.stock_value_input.value(), 2)
        supplier_type = self.supplier_type_input.currentText()
        notes = self.notes_input.toPlainText().strip()
        
        if not all([name, number, supply_type, address]):
            QMessageBox.warning(self, "Missing Data", "Please fill in name, number, supply type, and address.")
            return
        
        success, message, supplier = SupplierManager.add_supplier(
            code, name, number, supply_type, address, stock_value, supplier_type, notes
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_page:
                self.parent_page.view_supplier_widget.load_suppliers()
            self.reset_form()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def reset_form(self):
        self.code_input.clear()
        self.name_input.clear()
        self.number_input.clear()
        self.supply_type_input.clear()
        self.address_input.clear()
        self.stock_value_input.setValue(0.0)
        self.supplier_type_input.setCurrentIndex(0)
        self.notes_input.clear()


class ViewSupplierWidget(QWidget):
    """Widget for viewing suppliers"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.current_suppliers = []
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("View Suppliers")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, code, or number...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet(self.get_input_style())
        self.search_input.textChanged.connect(self.load_suppliers)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_suppliers)
        search_layout.addWidget(refresh_btn)
        
        content_layout.addLayout(search_layout)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.supplier_type_filter = QComboBox()
        self.supplier_type_filter.addItems(["All", "Regular", "Wholesale", "VIP", "Business"])
        self.supplier_type_filter.setFixedHeight(36)
        self.supplier_type_filter.setStyleSheet(self.get_input_style())
        self.supplier_type_filter.currentIndexChanged.connect(self.load_suppliers)
        filter_layout.addWidget(QLabel("Supplier Type"))
        filter_layout.addWidget(self.supplier_type_filter)
        
        self.supply_type_filter = QLineEdit()
        self.supply_type_filter.setPlaceholderText("Supply Type (All)")
        self.supply_type_filter.setFixedHeight(36)
        self.supply_type_filter.setStyleSheet(self.get_input_style())
        self.supply_type_filter.textChanged.connect(self.load_suppliers)
        filter_layout.addWidget(QLabel("Supply Type"))
        filter_layout.addWidget(self.supply_type_filter)
        
        self.min_stock_filter = QDoubleSpinBox()
        self.min_stock_filter.setPrefix("$")
        self.min_stock_filter.setMaximum(9999999.99)
        self.min_stock_filter.setDecimals(2)
        self.min_stock_filter.setFixedHeight(36)
        self.min_stock_filter.setStyleSheet(self.get_input_style())
        
        self.max_stock_filter = QDoubleSpinBox()
        self.max_stock_filter.setPrefix("$")
        self.max_stock_filter.setMaximum(9999999.99)
        self.max_stock_filter.setDecimals(2)
        self.max_stock_filter.setFixedHeight(36)
        self.max_stock_filter.setStyleSheet(self.get_input_style())
        
        filter_layout.addWidget(QLabel("Min Value"))
        filter_layout.addWidget(self.min_stock_filter)
        filter_layout.addWidget(QLabel("Max Value"))
        filter_layout.addWidget(self.max_stock_filter)
        
        apply_filters_btn = QPushButton("Apply Filters")
        apply_filters_btn.setFixedHeight(36)
        apply_filters_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        apply_filters_btn.clicked.connect(self.load_suppliers)
        filter_layout.addWidget(apply_filters_btn)
        
        content_layout.addLayout(filter_layout)
        
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(8)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Code", "Name", "Number", "Supply Type", "Address", "Stock Value", "Supplier Type", "Notes"
        ])
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.suppliers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.suppliers_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.suppliers_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                gridline-color: #E0E0E0;
            }
        """)
        content_layout.addWidget(self.suppliers_table)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        edit_btn = QPushButton("✏️ Edit Selected")
        edit_btn.setFixedHeight(40)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        edit_btn.clicked.connect(self.edit_selected_supplier)
        
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setFixedHeight(40)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
        """)
        delete_btn.clicked.connect(self.delete_selected_supplier)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_frame, 1)
        self.load_suppliers()
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def load_suppliers(self):
        search_key = self.search_input.text().strip()
        supplier_type = self.supplier_type_filter.currentText()
        supply_type = self.supply_type_filter.text().strip()
        min_stock = self.min_stock_filter.value()
        max_stock = self.max_stock_filter.value()
        
        min_value = min_stock if min_stock > 0 else None
        max_value = max_stock if max_stock > 0 else None
        if min_value and max_value and min_value > max_value:
            QMessageBox.warning(self, "Invalid Range", "Min stock value cannot exceed max value.")
            return
        
        suppliers = SupplierManager.search_suppliers(
            search_key=search_key,
            supplier_type=supplier_type if supplier_type != "All" else None,
            supply_type=supply_type if supply_type else None,
            min_stock=min_value,
            max_stock=max_value
        )
        self.populate_table(suppliers)
    
    def populate_table(self, suppliers):
        self.current_suppliers = suppliers
        self.suppliers_table.setRowCount(len(suppliers))
        for row, sup in enumerate(suppliers):
            row_data = [
                sup.get("code", ""),
                sup.get("name", ""),
                sup.get("number", ""),
                sup.get("supply_type", ""),
                sup.get("address", ""),
                f"${sup.get('stock_value', 0):,.2f}",
                sup.get("supplier_type", ""),
                sup.get("notes", "")
            ]
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.suppliers_table.setItem(row, col, item)
    
    def get_selected_supplier(self):
        row = self.suppliers_table.currentRow()
        if row == -1 or row >= len(self.current_suppliers):
            return None
        return self.current_suppliers[row]
    
    def edit_selected_supplier(self):
        supplier = self.get_selected_supplier()
        if not supplier:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to edit.")
            return
        
        dialog = EditSupplierDialog(self, supplier)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_suppliers()
    
    def delete_selected_supplier(self):
        supplier = self.get_selected_supplier()
        if not supplier:
            QMessageBox.warning(self, "No Selection", "Please select a supplier to delete.")
            return
        
        code = supplier.get("code", "")
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete supplier with code {code}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = SupplierManager.delete_supplier(code)
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.load_suppliers()
                if self.parent_page:
                    self.parent_page.add_supplier_widget.reset_form()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def refresh_data(self):
        self.load_suppliers()


class EditSupplierDialog(QDialog):
    """Dialog for editing supplier details"""
    
    def __init__(self, parent, supplier):
        super().__init__(parent)
        self.original_code = supplier.get("code", "")
        self.setWindowTitle(f"Edit Supplier - {supplier.get('name', '')}")
        self.setGeometry(220, 220, 450, 520)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel(f"Edit Supplier: {supplier.get('name', '')}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        layout.addWidget(self.create_label("Code"))
        self.code_input = QLineEdit(supplier.get("code", ""))
        self.code_input.setFixedHeight(35)
        self.code_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.code_input)
        
        layout.addWidget(self.create_label("Name"))
        self.name_input = QLineEdit(supplier.get("name", ""))
        self.name_input.setFixedHeight(35)
        self.name_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.name_input)
        
        layout.addWidget(self.create_label("Number"))
        self.number_input = QLineEdit(supplier.get("number", ""))
        self.number_input.setFixedHeight(35)
        self.number_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.number_input)
        
        layout.addWidget(self.create_label("Supply Type"))
        self.supply_type_input = QLineEdit(supplier.get("supply_type", ""))
        self.supply_type_input.setFixedHeight(35)
        self.supply_type_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.supply_type_input)
        
        layout.addWidget(self.create_label("Address"))
        self.address_input = QLineEdit(supplier.get("address", ""))
        self.address_input.setFixedHeight(35)
        self.address_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.address_input)
        
        layout.addWidget(self.create_label("Stock Value"))
        self.stock_value_input = QDoubleSpinBox()
        self.stock_value_input.setPrefix("$")
        self.stock_value_input.setMaximum(9999999.99)
        self.stock_value_input.setDecimals(2)
        self.stock_value_input.setValue(float(supplier.get("stock_value", 0.0)))
        self.stock_value_input.setFixedHeight(35)
        self.stock_value_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.stock_value_input)
        
        layout.addWidget(self.create_label("Supplier Type"))
        self.supplier_type_input = QComboBox()
        self.supplier_type_input.addItems(["Regular", "Wholesale", "VIP", "Business"])
        type_index = self.supplier_type_input.findText(supplier.get("supplier_type", "Regular"))
        self.supplier_type_input.setCurrentIndex(max(0, type_index))
        self.supplier_type_input.setFixedHeight(35)
        self.supplier_type_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.supplier_type_input)
        
        layout.addWidget(self.create_label("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(supplier.get("notes", ""))
        self.notes_input.setFixedHeight(90)
        self.notes_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.notes_input)
        
        layout.addStretch()
        
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
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def save_changes(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        supply_type = self.supply_type_input.text().strip()
        address = self.address_input.text().strip()
        stock_value = round(self.stock_value_input.value(), 2)
        supplier_type = self.supplier_type_input.currentText()
        notes = self.notes_input.toPlainText().strip()
        
        if not all([name, number, supply_type, address]):
            QMessageBox.warning(self, "Missing Data", "Please fill in all required fields.")
            return
        
        success, message, updated_supplier = SupplierManager.update_supplier(
            self.original_code,
            code,
            name,
            number,
            supply_type,
            address,
            stock_value,
            supplier_type,
            notes
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)


# ===================== EMPLOYEES PAGE =====================
class EmployeesPage(QWidget):
    """Employees management page with Add and View modes"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        
        self.mode_panel = self.create_mode_panel()
        h_layout.addWidget(self.mode_panel, 0)
        
        self.content_stack = QStackedWidget()
        self.add_employee_widget = AddEmployeeWidget(self)
        self.view_employee_widget = ViewEmployeeWidget(self)
        
        self.content_stack.addWidget(self.add_employee_widget)
        self.content_stack.addWidget(self.view_employee_widget)
        
        h_layout.addWidget(self.content_stack, 1)
        main_layout.addLayout(h_layout)
    
    def create_mode_panel(self):
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet(f"background-color: {COLORS['white']}; border-right: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        title = QLabel("Employees")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        add_btn = QPushButton("➕ Add Employee")
        add_btn.setStyleSheet(self.get_mode_button_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.show_add_mode)
        layout.addWidget(add_btn)
        
        view_btn = QPushButton("👁️ View Employees")
        view_btn.setStyleSheet(self.get_mode_button_style())
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setFixedHeight(45)
        view_btn.clicked.connect(self.show_view_mode)
        layout.addWidget(view_btn)
        
        layout.addStretch()
        return panel
    
    def get_mode_button_style(self):
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
        self.content_stack.setCurrentIndex(0)
    
    def show_view_mode(self):
        self.content_stack.setCurrentIndex(1)
        self.view_employee_widget.load_employees()
    
    def refresh_data(self):
        self.add_employee_widget.reset_form()
        self.view_employee_widget.load_employees()


class AddEmployeeWidget(QWidget):
    """Widget for adding employees"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.photo_path = ""
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("Add Employee")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.name_input = self.create_line_edit("Employee Name")
        self.number_input = self.create_line_edit("Phone Number")
        self.address_input = self.create_line_edit("Address")
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setPrefix("$")
        self.salary_input.setMaximum(9999999.99)
        self.salary_input.setDecimals(2)
        self.salary_input.setFixedHeight(36)
        self.salary_input.setStyleSheet(self.get_input_style())
        self.position_input = self.create_line_edit("Position")
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Suspended"])
        self.status_input.setFixedHeight(36)
        self.status_input.setStyleSheet(self.get_input_style())
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setFixedHeight(36)
        self.start_date_input.setStyleSheet(self.get_input_style())
        self.department_input = self.create_line_edit("Department")
        self.emergency_input = QTextEdit()
        self.emergency_input.setPlaceholderText("Emergency Contacts / Notes")
        self.emergency_input.setFixedHeight(90)
        self.emergency_input.setStyleSheet(self.get_input_style())
        
        field_pairs = [
            ("Name", self.name_input),
            ("Number", self.number_input),
            ("Address", self.address_input),
            ("Salary", self.salary_input),
            ("Position", self.position_input),
            ("Department", self.department_input),
            ("Status", self.status_input),
            ("Start Date", self.start_date_input),
        ]
        
        for idx, (label, widget) in enumerate(field_pairs):
            row = idx // 2
            col = idx % 2
            container = self.create_field_group(label, widget)
            grid.addWidget(container, row, col)
        
        form_layout.addLayout(grid)
        
        photo_layout = QHBoxLayout()
        photo_layout.setSpacing(15)
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(120, 120)
        self.photo_preview.setStyleSheet("border: 1px dashed #BDC3C7; border-radius: 8px; background: #F8F9FA;")
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setText("No Photo")
        photo_layout.addWidget(self.photo_preview)
        
        upload_btn = QPushButton("Upload Photo")
        upload_btn.setFixedHeight(36)
        upload_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        upload_btn.clicked.connect(self.select_photo)
        photo_layout.addWidget(upload_btn)
        photo_layout.addStretch()
        form_layout.addLayout(photo_layout)
        
        form_layout.addWidget(self.create_label("Emergency Contacts / Notes"))
        form_layout.addWidget(self.emergency_input)
        
        self.code_preview = QLabel("Employee Code: ---")
        self.code_preview.setStyleSheet(f"color: {COLORS['text_light']}; font-weight: bold;")
        form_layout.addWidget(self.code_preview)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("➕ Add Employee")
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        add_btn.clicked.connect(self.handle_add_employee)
        
        reset_btn = QPushButton("Reset Form")
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_light']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #95A5A6;
            }}
        """)
        reset_btn.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(reset_btn)
        form_layout.addLayout(btn_layout)
        
        main_layout.addWidget(form_frame, 0)
        main_layout.addStretch()
        
        self.number_input.textChanged.connect(self.update_code_preview)
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def create_field_group(self, label_text, widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        label = self.create_label(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return container
    
    def create_line_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedHeight(36)
        line_edit.setStyleSheet(self.get_input_style())
        return line_edit
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit, QDateEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QDateEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def update_code_preview(self):
        code = EmployeeManager.generate_employee_code(self.number_input.text())
        self.code_preview.setText(f"Employee Code: {code}")
    
    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.photo_preview.setPixmap(pixmap)
    
    def handle_add_employee(self):
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        address = self.address_input.text().strip()
        salary = round(self.salary_input.value(), 2)
        position = self.position_input.text().strip()
        status = self.status_input.currentText()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        department = self.department_input.text().strip()
        emergency_contact = self.emergency_input.toPlainText().strip()
        
        if not all([name, number, address, position, department]):
            QMessageBox.warning(self, "Missing Data", "Please fill all required fields.")
            return
        
        success, message, employee = EmployeeManager.add_employee(
            name, number, address, salary, position, status, start_date, department, emergency_contact, self.photo_path
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_page:
                self.parent_page.view_employee_widget.load_employees()
            self.reset_form()
        else:
            QMessageBox.warning(self, "Error", message)
    
    def reset_form(self):
        self.name_input.clear()
        self.number_input.clear()
        self.address_input.clear()
        self.salary_input.setValue(0.0)
        self.position_input.clear()
        self.status_input.setCurrentIndex(0)
        self.start_date_input.setDate(QDate.currentDate())
        self.department_input.clear()
        self.emergency_input.clear()
        self.photo_path = ""
        self.photo_preview.setPixmap(QPixmap())
        self.photo_preview.setText("No Photo")
        self.update_code_preview()


class ViewEmployeeWidget(QWidget):
    """Widget for viewing employees"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_page = parent
        self.current_employees = []
        self.setStyleSheet(f"background-color: {COLORS['light_bg']};")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("View Employees")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        main_layout.addWidget(title)
        
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, code, or number...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet(self.get_input_style())
        self.search_input.textChanged.connect(self.load_employees)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_employees)
        search_layout.addWidget(refresh_btn)
        content_layout.addLayout(search_layout)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Suspended"])
        self.status_filter.setFixedHeight(36)
        self.status_filter.setStyleSheet(self.get_input_style())
        self.status_filter.currentIndexChanged.connect(self.load_employees)
        filter_layout.addWidget(QLabel("Status"))
        filter_layout.addWidget(self.status_filter)
        
        self.department_filter = QComboBox()
        self.department_filter.setFixedHeight(36)
        self.department_filter.setStyleSheet(self.get_input_style())
        self.department_filter.addItem("All")
        self.department_filter.currentIndexChanged.connect(self.load_employees)
        filter_layout.addWidget(QLabel("Department"))
        filter_layout.addWidget(self.department_filter)
        
        self.min_salary_filter = QDoubleSpinBox()
        self.min_salary_filter.setPrefix("$")
        self.min_salary_filter.setMaximum(9999999.99)
        self.min_salary_filter.setDecimals(2)
        self.min_salary_filter.setFixedHeight(36)
        self.min_salary_filter.setStyleSheet(self.get_input_style())
        
        self.max_salary_filter = QDoubleSpinBox()
        self.max_salary_filter.setPrefix("$")
        self.max_salary_filter.setMaximum(9999999.99)
        self.max_salary_filter.setDecimals(2)
        self.max_salary_filter.setFixedHeight(36)
        self.max_salary_filter.setStyleSheet(self.get_input_style())
        
        filter_layout.addWidget(QLabel("Min Salary"))
        filter_layout.addWidget(self.min_salary_filter)
        filter_layout.addWidget(QLabel("Max Salary"))
        filter_layout.addWidget(self.max_salary_filter)
        
        apply_filters_btn = QPushButton("Apply Filters")
        apply_filters_btn.setFixedHeight(36)
        apply_filters_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        apply_filters_btn.clicked.connect(self.load_employees)
        filter_layout.addWidget(apply_filters_btn)
        content_layout.addLayout(filter_layout)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "Code", "Name", "Position", "Department", "Status", "Salary", "Start Date"
        ])
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.employees_table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
                gridline-color: #E0E0E0;
            }
        """)
        self.employees_table.doubleClicked.connect(self.open_selected_employee)
        content_layout.addWidget(self.employees_table)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        view_btn = QPushButton("👁️ View Profile")
        view_btn.setFixedHeight(40)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        view_btn.clicked.connect(self.open_selected_employee)
        
        btn_layout.addWidget(view_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content_frame, 1)
        self.load_departments()
        self.load_employees()
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def load_departments(self):
        current = self.department_filter.currentText()
        self.department_filter.blockSignals(True)
        self.department_filter.clear()
        self.department_filter.addItem("All")
        for dept in EmployeeManager.get_departments():
            self.department_filter.addItem(dept)
        index = self.department_filter.findText(current)
        self.department_filter.setCurrentIndex(index if index != -1 else 0)
        self.department_filter.blockSignals(False)
    
    def load_employees(self):
        search_key = self.search_input.text().strip()
        status = self.status_filter.currentText()
        department = self.department_filter.currentText()
        min_salary = self.min_salary_filter.value()
        max_salary = self.max_salary_filter.value()
        
        min_value = min_salary if min_salary > 0 else None
        max_value = max_salary if max_salary > 0 else None
        if min_value and max_value and min_value > max_value:
            QMessageBox.warning(self, "Invalid Range", "Min salary cannot exceed max salary.")
            return
        
        employees = EmployeeManager.search_employees(
            search_key=search_key,
            status=status if status != "All" else None,
            department=department if department != "All" else None,
            min_salary=min_value,
            max_salary=max_value
        )
        self.populate_table(employees)
        self.load_departments()
    
    def populate_table(self, employees):
        self.current_employees = employees
        self.employees_table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            row_data = [
                emp.get("code", ""),
                emp.get("name", ""),
                emp.get("position", ""),
                emp.get("department", ""),
                emp.get("status", ""),
                f"${emp.get('salary', 0):,.2f}",
                emp.get("start_date", "")
            ]
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.employees_table.setItem(row, col, item)
    
    def get_selected_employee(self):
        row = self.employees_table.currentRow()
        if row == -1 or row >= len(self.current_employees):
            return None
        return self.current_employees[row]
    
    def open_selected_employee(self):
        employee = self.get_selected_employee()
        if not employee:
            QMessageBox.warning(self, "No Selection", "Please select an employee to view.")
            return
        dialog = EmployeeDetailsDialog(self, employee)
        dialog.exec()
        self.load_employees()
    
    def refresh_data(self):
        self.load_employees()


class EmployeeDetailsDialog(QDialog):
    """Display employee details with photo and actions"""
    
    def __init__(self, parent, employee):
        super().__init__(parent)
        self.employee = employee
        self.setWindowTitle(f"Employee - {employee.get('name', '')}")
        self.setGeometry(250, 250, 500, 600)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        top_layout = QHBoxLayout()
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(150, 150)
        self.photo_label.setStyleSheet("border: 1px solid #E0E0E0; border-radius: 10px; background:#F8F9FA;")
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.load_photo(employee.get("photo_path", ""))
        top_layout.addWidget(self.photo_label)
        
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.create_info_label("Name", employee.get("name", "")))
        info_layout.addWidget(self.create_info_label("Code", employee.get("code", "")))
        info_layout.addWidget(self.create_info_label("Position", employee.get("position", "")))
        info_layout.addWidget(self.create_info_label("Department", employee.get("department", "")))
        info_layout.addWidget(self.create_info_label("Status", employee.get("status", "")))
        top_layout.addLayout(info_layout)
        layout.addLayout(top_layout)
        
        details = [
            ("Phone", employee.get("number", "")),
            ("Address", employee.get("address", "")),
            ("Salary", f"${employee.get('salary', 0):,.2f}"),
            ("Start Date", employee.get("start_date", "")),
        ]
        
        for label, value in details:
            layout.addWidget(self.create_info_label(label, value))
        
        emergency_box = QLabel(f"Emergency Contacts / Notes:\n{employee.get('emergency_contact', '')}")
        emergency_box.setStyleSheet(f"""
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 10px;
            color: {COLORS['text_dark']};
        """)
        emergency_box.setWordWrap(True)
        layout.addWidget(emergency_box)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        edit_btn.clicked.connect(self.edit_employee)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        delete_btn.clicked.connect(self.delete_employee)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def load_photo(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("No Photo")
    
    def create_info_label(self, title, value):
        label = QLabel(f"<b>{title}:</b> {value}")
        label.setStyleSheet(f"color: {COLORS['text_dark']};")
        label.setWordWrap(True)
        return label
    
    def edit_employee(self):
        dialog = EditEmployeeDialog(self, self.employee)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.employee = dialog.employee
            self.load_photo(self.employee.get("photo_path", ""))
            self.close()
    
    def delete_employee(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = EmployeeManager.delete_employee(self.employee.get("code"))
            if success:
                QMessageBox.information(self, "Deleted", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)


class EditEmployeeDialog(QDialog):
    """Dialog to edit employee details"""
    
    def __init__(self, parent, employee):
        super().__init__(parent)
        self.employee = employee
        self.photo_path = ""
        self.setWindowTitle(f"Edit Employee - {employee.get('name', '')}")
        self.setGeometry(250, 250, 480, 520)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        self.name_input = QLineEdit(employee.get("name", ""))
        self.number_input = QLineEdit(employee.get("number", ""))
        self.address_input = QLineEdit(employee.get("address", ""))
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setPrefix("$")
        self.salary_input.setMaximum(9999999.99)
        self.salary_input.setDecimals(2)
        self.salary_input.setValue(float(employee.get("salary", 0)))
        self.position_input = QLineEdit(employee.get("position", ""))
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Suspended"])
        status_index = self.status_input.findText(employee.get("status", "Active"))
        self.status_input.setCurrentIndex(max(0, status_index))
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        try:
            start_date = QDate.fromString(employee.get("start_date", ""), "yyyy-MM-dd")
            if start_date.isValid():
                self.start_date_input.setDate(start_date)
            else:
                self.start_date_input.setDate(QDate.currentDate())
        except Exception:
            self.start_date_input.setDate(QDate.currentDate())
        self.department_input = QLineEdit(employee.get("department", ""))
        self.emergency_input = QTextEdit()
        self.emergency_input.setPlainText(employee.get("emergency_contact", ""))
        
        fields = [
            ("Name", self.name_input),
            ("Number", self.number_input),
            ("Address", self.address_input),
            ("Salary", self.salary_input),
            ("Position", self.position_input),
            ("Status", self.status_input),
            ("Start Date", self.start_date_input),
            ("Department", self.department_input),
            ("Emergency Contacts / Notes", self.emergency_input),
        ]
        
        for label_text, widget in fields:
            layout.addWidget(self.create_label(label_text))
            layout.addWidget(widget)
        
        photo_layout = QHBoxLayout()
        self.photo_label = QLabel("Current Photo")
        photo_layout.addWidget(self.photo_label)
        upload_btn = QPushButton("Upload New Photo")
        upload_btn.clicked.connect(self.select_photo)
        photo_layout.addWidget(upload_btn)
        layout.addLayout(photo_layout)
        
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        save_btn.clicked.connect(self.save_changes)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_light']};
                color: {COLORS['white']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                padding: 10px 20px;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def select_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(os.path.basename(file_path))
    
    def save_changes(self):
        name = self.name_input.text().strip()
        number = self.number_input.text().strip()
        address = self.address_input.text().strip()
        salary = round(self.salary_input.value(), 2)
        position = self.position_input.text().strip()
        status = self.status_input.currentText()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        department = self.department_input.text().strip()
        emergency_contact = self.emergency_input.toPlainText().strip()
        
        if not all([name, number, address, position, department]):
            QMessageBox.warning(self, "Missing Data", "Please fill all required fields.")
            return
        
        success, message, updated_employee = EmployeeManager.update_employee(
            self.employee.get("code"),
            name,
            number,
            address,
            salary,
            position,
            status,
            start_date,
            department,
            emergency_contact,
            self.photo_path
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.employee = updated_employee
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)

class EditCustomerDialog(QDialog):
    """Dialog for editing customer details"""
    
    def __init__(self, parent, customer):
        super().__init__(parent)
        self.customer = customer
        self.original_code = customer.get("code", "")
        self.setWindowTitle(f"Edit Customer - {customer.get('full_name', '')}")
        self.setGeometry(200, 200, 450, 500)
        self.setStyleSheet(f"background-color: {COLORS['white']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        title = QLabel(f"Edit Customer: {customer.get('full_name', '')}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_dark']};")
        layout.addWidget(title)
        
        layout.addWidget(self.create_label("First Name"))
        self.first_name_input = QLineEdit()
        self.first_name_input.setText(customer.get("first_name", ""))
        self.first_name_input.setFixedHeight(35)
        self.first_name_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.first_name_input)
        
        layout.addWidget(self.create_label("Second Name"))
        self.second_name_input = QLineEdit()
        self.second_name_input.setText(customer.get("second_name", ""))
        self.second_name_input.setFixedHeight(35)
        self.second_name_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.second_name_input)
        
        layout.addWidget(self.create_label("Number"))
        self.number_input = QLineEdit()
        self.number_input.setText(customer.get("number", ""))
        self.number_input.setFixedHeight(35)
        self.number_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.number_input)
        
        layout.addWidget(self.create_label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setText(customer.get("address", ""))
        self.address_input.setFixedHeight(35)
        self.address_input.setStyleSheet(self.get_input_style())
        layout.addWidget(self.address_input)
        
        layout.addWidget(self.create_label("Customer Type"))
        self.customer_type_input = QComboBox()
        self.customer_type_input.addItems(["Regular", "Wholesale", "VIP", "Business"])
        type_index = self.customer_type_input.findText(customer.get("customer_type", "Regular"))
        self.customer_type_input.setCurrentIndex(max(0, type_index))
        self.customer_type_input.setStyleSheet(self.get_input_style())
        self.customer_type_input.setFixedHeight(35)
        layout.addWidget(self.customer_type_input)
        
        layout.addWidget(self.create_label("Purchases Value"))
        self.purchase_value_input = QDoubleSpinBox()
        self.purchase_value_input.setPrefix("$")
        self.purchase_value_input.setMaximum(9999999.99)
        self.purchase_value_input.setDecimals(2)
        self.purchase_value_input.setValue(float(customer.get("purchase_value", 0.0)))
        self.purchase_value_input.setStyleSheet(self.get_input_style())
        self.purchase_value_input.setFixedHeight(35)
        layout.addWidget(self.purchase_value_input)
        
        layout.addWidget(self.create_label("Notes"))
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(customer.get("notes", ""))
        self.notes_input.setStyleSheet(self.get_input_style())
        self.notes_input.setFixedHeight(90)
        layout.addWidget(self.notes_input)
        
        layout.addStretch()
        
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
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {COLORS['text_dark']}; font-weight: bold;")
        return label
    
    def get_input_style(self):
        return f"""
            QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
                background-color: {COLORS['light_bg']};
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
        """
    
    def save_changes(self):
        first_name = self.first_name_input.text().strip()
        second_name = self.second_name_input.text().strip()
        number = self.number_input.text().strip()
        address = self.address_input.text().strip()
        customer_type = self.customer_type_input.currentText()
        purchase_value = round(self.purchase_value_input.value(), 2)
        notes = self.notes_input.toPlainText().strip()
        
        if not all([first_name, second_name, number, address]):
            QMessageBox.warning(self, "Missing Data", "Please fill all required fields.")
            return
        
        success, message, updated_customer = CustomerManager.update_customer(
            self.original_code,
            first_name,
            second_name,
            number,
            address,
            customer_type,
            purchase_value,
            notes
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.customer = updated_customer
            self.accept()
        else:
            QMessageBox.warning(self, "Error", message)

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
        total_customers = CustomerManager.get_total_customers()
        
        total_suppliers = SupplierManager.get_total_suppliers()
        total_employees = EmployeeManager.get_total_employees()
        
        cards_data = [
            ("Total Products", str(stats['total_products']), COLORS['card_1']),
            ("Total Customers", str(total_customers), COLORS['card_2']),
            ("Total Suppliers", str(total_suppliers), COLORS['card_3']),
            ("Total Employees", str(total_employees), COLORS['card_4']),
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
