-- Customer Dimension
CREATE TABLE DimCustomer (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Region TEXT,
    JoinDate DATE,
    OpenInvoices INTEGER,
    RetentionCategory TEXT
);

-- Product Dimension
CREATE TABLE DimProduct (
    ProductID INTEGER PRIMARY KEY,
    ProductName TEXT NOT NULL,
    Category TEXT,
    UnitPrice DECIMAL(10,2),
    RestockTimeDays INTEGER,
    Supplier TEXT
);

-- Date Dimension
CREATE TABLE DimDate (
    DateID INTEGER PRIMARY KEY,
    SaleDate DATE,
    DayOfWeek TEXT,
    Month INTEGER,
    Quarter INTEGER,
    Year INTEGER
);

-- Sales Fact Table
CREATE TABLE FactSales (
    TransactionID INTEGER PRIMARY KEY,
    SaleDate DATE NOT NULL,
    CustomerID INTEGER,
    ProductID INTEGER,
    StoreID INTEGER,
    CampaignID INTEGER,
    SaleAmount DECIMAL(12,2),
    DiscountPct DECIMAL(5,2),
    PaymentType TEXT,
    FOREIGN KEY (CustomerID) REFERENCES DimCustomer(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES DimProduct(ProductID)
);
