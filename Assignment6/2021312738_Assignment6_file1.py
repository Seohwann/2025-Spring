from datetime import datetime
from collections import defaultdict

class Store:
    def __init__(self, ID, Name, Address, Tel):
        self.__ID = ID
        self.__Name = Name
        self.__Address = Address
        self.__Tel = Tel

    @property
    def ID(self):
        return self.__ID

    @property
    def Name(self):
        return self.__Name

    @property
    def Address(self):
        return self.__Address

    @property
    def Tel(self):
        return self.__Tel

    @ID.setter
    def ID(self, ID):
        self.__ID = ID

    @Name.setter
    def Name(self, Name):
        self.__Name = Name

    @Address.setter
    def Address(self, Address):
        self.__Address = Address

    @Tel.setter
    def Tel(self, Tel):
        self.__Tel = Tel

    def __str__(self):
        return f"Welcome to {self.__Name}"
    
class Staff:
    def __init__(self, ID, SSN, Name, Address, JobTitle, Salary):
        self.__ID = ID
        self.__SSN = SSN
        self.__Name = Name
        self.__Address = Address
        self.__JobTitle = JobTitle
        self.__Salary = Salary

    @property
    def ID(self):
        return self.__ID

    @property
    def SSN(self):
        return self.__SSN

    @property
    def Name(self):
        return self.__Name

    @property
    def Address(self):
        return self.__Address

    @property
    def JobTitle(self):
        return self.__JobTitle

    @property
    def Salary(self):
        return self.__Salary

    @ID.setter
    def ID(self, ID):
        self.__ID = ID

    @SSN.setter
    def SSN(self, SSN):
        self.__SSN = SSN

    @Name.setter
    def Name(self, Name):
        self.__Name = Name

    @Address.setter
    def Address(self, Address):
        self.__Address = Address

    @JobTitle.setter
    def JobTitle(self, JobTitle):
        self.__JobTitle = JobTitle

    @Salary.setter
    def Salary(self, Salary):
        self.__Salary = Salary

    def __str__(self):
        return f"Staff: {self.__Name}"

class Customer:
    def __init__(self, SSN, Name, Address, Purchasing_Points, Tel, Membership):
        self.__SSN = SSN
        self.__Name = Name
        self.__Address = Address
        self.__Purchasing_Points = Purchasing_Points
        self.__Tel = Tel
        self.__Membership = Membership if Membership is not None else []

    @property
    def SSN(self):
        return self.__SSN

    @property
    def Name(self):
        return self.__Name

    @property
    def Address(self):
        return self.__Address

    @property
    def Purchasing_Points(self):
        return self.__Purchasing_Points

    @property
    def Tel(self):
        return self.__Tel

    @property
    def Membership(self):
        return " ".join(self.__Membership)

    @SSN.setter
    def SSN(self, SSN):
        self.__SSN = SSN

    @Name.setter
    def Name(self, Name):
        self.__Name = Name

    @Address.setter
    def Address(self, Address):
        self.__Address = Address

    @Purchasing_Points.setter
    def Purchasing_Points(self, Purchasing_Points):
        self.__Purchasing_Points = Purchasing_Points

    @Tel.setter
    def Tel(self, Tel):
        self.__Tel = Tel

    @Membership.setter
    def Membership(self, Membership):
        self.__Membership = Membership

    def __str__(self):
        return f"Customer ID: {self.__SSN}"

class Product:
    def __init__(self, ProductCode, Name, Description, Price, Points):
        self.__ProductCode = ProductCode
        self.__Name = Name
        self.__Description = Description
        self.__Price = Price
        self.__Points = Points

    @property
    def ProductCode(self):
        return self.__ProductCode

    @property
    def Name(self):
        return self.__Name

    @property
    def Description(self):
        return self.__Description

    @property
    def Price(self):
        return self.__Price

    @property
    def Points(self):
        return self.__Points

    @ProductCode.setter
    def ProductCode(self, ProductCode):
        self.__ProductCode = ProductCode

    @Name.setter
    def Name(self, Name):
        self.__Name = Name

    @Description.setter
    def Description(self, Description):
        self.__Description = Description

    @Price.setter
    def Price(self, Price):
        self.__Price = Price

    @Points.setter
    def Points(self, Points):
        self.__Points = Points

    def __str__(self):
        return f"{self.__Name.ljust(15)}{self.__ProductCode.ljust(15)}{f'{self.__Price:.2f}'.ljust(8)}"

class Order:
    def __init__(self, Store_object, Customer_object, Staff_object, Product_objects=None, Quantity=None):
        self.Store_object = Store_object
        self.Customer_object = Customer_object
        self.Staff_object = Staff_object
        self.Product_objects = Product_objects if Product_objects is not None else []
        self.Quantity = Quantity
        self.product_quantities = defaultdict(int)

    def addProduct(self, product, quantity):
        self.Product_objects.append(product)
        self.product_quantities[product] += quantity

    def printReceipt(self):
        total = 0
        total_points = 0
        self.Quantity = 0
        
        print(self.Store_object)
        print(self.Staff_object)
        print(self.Customer_object)
        print("\nRECEIPT")
        print(datetime.now().strftime("%m/%d/%Y \n%H:%M:%S"))
        print(f"ST # {self.Store_object.ID}\n")
        print("ProductName".ljust(15) + "ProductCode".ljust(15) + "Price".ljust(8) + "Q")
        
        for product, qty in self.product_quantities.items():
            subtotal = product.Price * qty
            total += subtotal
            total_points += product.Points * qty
            self.Quantity += qty
            print(f"{product.Name.ljust(15)}{product.ProductCode.ljust(15)}{f'{subtotal:.2f}'.ljust(8)}{str(qty).ljust(5)}")

        print(f"\nTOTAL\n${total:.2f}")
        print(f"# ITEMS SOLD {self.Quantity}")
        print(f"\nTOTAL POINTS: {total_points}")
        print("\n***CUSTOMER COPY***")
        
        self.Customer_object.Purchasing_Points = self.Customer_object.Purchasing_Points + total_points
        
def main():
    store = Store(1235, "HomeStore", "123 Main St", "123-456-7890")
    print(f"create new store ! Name : {store.Name} / ID : {store.ID} / Address : {store.Address} / Tel : {store.Tel}")

    customer1 = Customer("102155222554", "Park JiMin", "321 Elm St", 0, "987-654-3210", ["yogiyo", "bbq"])
    customer2 = Customer("202155333554", "Jung SooJin", "654 Birch St", 0, "456-789-1234", [])
    print(f"create new staff ! SSN : {customer1.SSN} / Name : {customer1.Name} / Address : {customer1.Address} / Tel : {customer1.Tel} / Memberships : {customer1.Membership}")
    print(f"create new staff ! SSN : {customer2.SSN} / Name : {customer2.Name} / Address : {customer2.Address} / Tel : {customer2.Tel} / Memberships : {customer2.Membership}")

    staff1 = Staff(1, "111-22-3333", "Kim YoungJae", "456 Oak St", "Cashier", 30000)
    staff2 = Staff(2, "222-33-4444", "Lee MinHo", "789 Pine St", "Manager", 50000)
    print(f"create new staff ! ID : {staff1.ID} / SSN : {staff1.SSN} / Name : {staff1.Name} / Address : {staff1.Address}")
    print(f"create new staff ! ID : {staff2.ID} / SSN : {staff2.SSN} / Name : {staff2.Name} / Address : {staff2.Address}")
    
    products = [
        Product("013231788393", "PRODUCT", "Description 1", 8.16, 2),
        Product("012784545789", "PRODUCT", "Description 2", 5.56, 1),
        Product("007855114259", "MILK", "Description 3", 3.58, 1),
        Product("007874237152", "PRODUCT", "Description 4", 2.24, 1)
    ]

    order = Order(store, customer1, staff1)
    print("\nAvailable Products:")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product}")
    
    while True:
        choice = input("\nEnter product number to add (or 'q' to finish): ")
        if choice.lower() == 'q':
            break
        product_idx = int(choice) - 1
        if 0 <= product_idx < len(products):
            qty = int(input(f"Enter quantity for {products[product_idx].Name}: "))
            order.addProduct(products[product_idx], qty)
        else:
            print("Invalid product number!")
    print()
    order.printReceipt()

if __name__ == "__main__":
    main()