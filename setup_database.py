# setup_database.py

import pyodbc
from config import DATABASE, CONNECTION_STRING, MASTER_CONNECTION_STRING


def create_database():
    """Create database if it does not exist"""

    conn = pyodbc.connect(
        MASTER_CONNECTION_STRING,
        autocommit=True
    )

    cursor = conn.cursor()

    cursor.execute(f"SELECT DB_ID('{DATABASE}')")

    exists = cursor.fetchone()[0]

    if exists:
        print(f"Database '{DATABASE}' already exists.")

    else:
        cursor.execute(f"CREATE DATABASE {DATABASE}")

        print(
            f"Database '{DATABASE}' created successfully."
        )

    conn.close()


def create_tables():
    """Create schema and tables"""

    conn = pyodbc.connect(CONNECTION_STRING)

    cursor = conn.cursor()

    # =====================================
    # CREATE SCHEMA
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.schemas
        WHERE name = 'Market'
    )
    BEGIN
        EXEC('CREATE SCHEMA Market')
    END
    """)

    # =====================================
    # SECTORS TABLE
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.tables
        WHERE name = 'Sectors'
        AND schema_id = SCHEMA_ID('Market')
    )

    CREATE TABLE Market.Sectors (

        SectorID INT IDENTITY(1,1)
        PRIMARY KEY,

        SectorName NVARCHAR(100)
        UNIQUE NOT NULL,

        SectorDescription NVARCHAR(MAX),

        CreatedAt DATETIME2
        DEFAULT GETDATE()
    )
    """)

    # =====================================
    # COMPANIES TABLE
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.tables
        WHERE name = 'Companies'
        AND schema_id = SCHEMA_ID('Market')
    )

    CREATE TABLE Market.Companies (

        CompanyID INT IDENTITY(1,1)
        PRIMARY KEY,

        Ticker NVARCHAR(20)
        UNIQUE NOT NULL,

        CompanyName NVARCHAR(200)
        NOT NULL,

        SectorID INT NOT NULL,

        Exchange NVARCHAR(50)
        DEFAULT 'JSE',

        IsActive BIT
        DEFAULT 1,

        CreatedAt DATETIME2
        DEFAULT GETDATE(),

        CONSTRAINT FK_Companies_Sectors
        FOREIGN KEY (SectorID)
        REFERENCES Market.Sectors(SectorID)
    )
    """)

    # =====================================
    # CALENDAR DATES TABLE
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.tables
        WHERE name = 'CalendarDates'
        AND schema_id = SCHEMA_ID('Market')
    )

    CREATE TABLE Market.CalendarDates (

        DateID INT IDENTITY(1,1)
        PRIMARY KEY,

        [Date] DATE
        UNIQUE NOT NULL,

        DayOfWeek INT NOT NULL,
        [Month] INT NOT NULL,
        [Quarter] INT NOT NULL,
        [Year] INT NOT NULL,

        IsTradingDay BIT
        DEFAULT 1
    )
    """)

    # =====================================
    # STOCK PRICES TABLE
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.tables
        WHERE name = 'StockPrices'
        AND schema_id = SCHEMA_ID('Market')
    )

    CREATE TABLE Market.StockPrices (

        PriceID INT IDENTITY(1,1)
        PRIMARY KEY,

        CompanyID INT NOT NULL,
        DateID INT NOT NULL,

        OpenPrice DECIMAL(18,4)
        NOT NULL,

        HighPrice DECIMAL(18,4)
        NOT NULL,

        LowPrice DECIMAL(18,4)
        NOT NULL,

        ClosePrice DECIMAL(18,4)
        NOT NULL,

        Volume BIGINT
        NOT NULL,

        CreatedAt DATETIME2
        DEFAULT GETDATE(),

        CONSTRAINT FK_StockPrices_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES Market.Companies(CompanyID),

        CONSTRAINT FK_StockPrices_Dates
        FOREIGN KEY (DateID)
        REFERENCES Market.CalendarDates(DateID),

        CONSTRAINT UQ_StockPrices
        UNIQUE (CompanyID, DateID),

        CONSTRAINT CK_Prices
        CHECK (
            HighPrice >= LowPrice
            AND OpenPrice BETWEEN LowPrice AND HighPrice
            AND ClosePrice BETWEEN LowPrice AND HighPrice
        )
    )
    """)

    # =====================================
    # TECHNICAL INDICATORS TABLE
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM sys.tables
        WHERE name = 'TechnicalIndicators'
        AND schema_id = SCHEMA_ID('Market')
    )

    CREATE TABLE Market.TechnicalIndicators (

        IndicatorID INT IDENTITY(1,1)
        PRIMARY KEY,

        CompanyID INT NOT NULL,
        DateID INT NOT NULL,

        SMA20 DECIMAL(18,4),
        SMA50 DECIMAL(18,4),
        RSI14 DECIMAL(18,4),

        MACDLine DECIMAL(18,4),
        MACDSignal DECIMAL(18,4),
        MACDHistogram DECIMAL(18,4),

        CreatedAt DATETIME2
        DEFAULT GETDATE(),

        CONSTRAINT FK_TI_Companies
        FOREIGN KEY (CompanyID)
        REFERENCES Market.Companies(CompanyID),

        CONSTRAINT FK_TI_Dates
        FOREIGN KEY (DateID)
        REFERENCES Market.CalendarDates(DateID),

        CONSTRAINT UQ_TI
        UNIQUE (CompanyID, DateID)
    )
    """)

    conn.commit()

    conn.close()

    print("Tables created successfully.")


def insert_reference_data():
    """Insert sectors and companies"""

    conn = pyodbc.connect(CONNECTION_STRING)

    cursor = conn.cursor()

    # =====================================
    # INSERT SECTORS
    # =====================================

    cursor.execute("""
    IF NOT EXISTS (
        SELECT *
        FROM Market.Sectors
    )

    INSERT INTO Market.Sectors
    (
        SectorName,
        SectorDescription
    )

    VALUES
    (
        'Financials',
        'Banks and financial services'
    ),
    (
        'Mining',
        'Mining companies'
    ),
    (
        'Technology',
        'Technology companies'
    ),
    (
        'Telecommunications',
        'Telecom providers'
    )
    """)

    # =====================================
    # INSERT COMPANIES
    # =====================================

    cursor.execute("""
    INSERT INTO Market.Companies
    (
        Ticker,
        CompanyName,
        SectorID
    )

    SELECT
        v.Ticker,
        v.CompanyName,
        s.SectorID

    FROM (VALUES

        ('AGL.JO', 'Anglo American plc', 'Mining'),
        ('SOL.JO', 'Sasol Ltd', 'Mining'),
        ('IMP.JO', 'Impala Platinum Holdings Ltd', 'Mining'),
        ('GLN.JO', 'Glencore plc', 'Mining'),

        ('SBK.JO', 'Standard Bank Group Ltd', 'Financials'),
        ('FSR.JO', 'FirstRand Ltd', 'Financials'),
        ('SLM.JO', 'Sanlam Ltd', 'Financials'),
        ('DSY.JO', 'Discovery Ltd', 'Financials'),
        ('CPI.JO', 'Capitec Bank Holdings Ltd', 'Financials'),

        ('NPN.JO', 'Naspers Ltd', 'Technology'),
        ('PRX.JO', 'Prosus NV', 'Technology'),
        ('BHG.JO', 'Bytes Technology Group plc', 'Technology'),

        ('MTN.JO', 'MTN Group Ltd', 'Telecommunications'),
        ('VOD.JO', 'Vodacom Group Ltd', 'Telecommunications')

    ) v(Ticker, CompanyName, SectorName)

    JOIN Market.Sectors s
        ON s.SectorName = v.SectorName

    WHERE NOT EXISTS (
        SELECT 1
        FROM Market.Companies c
        WHERE c.Ticker = v.Ticker
    )
    """)

    conn.commit()

    conn.close()

    print("Reference data inserted successfully.")


def create_stored_procedures():
    """Create stored procedures"""

    conn = pyodbc.connect(CONNECTION_STRING)

    cursor = conn.cursor()

    # =====================================
    # TOP GAINERS
    # =====================================

    cursor.execute("""
    CREATE OR ALTER PROCEDURE Market.GetTopGainers
        @TopN INT = 5

    AS

    BEGIN

        WITH PriceChanges AS (

            SELECT

                c.Ticker,
                c.CompanyName,
                sp.ClosePrice,

                LAG(sp.ClosePrice)
                OVER (
                    PARTITION BY c.CompanyID
                    ORDER BY cd.Date
                ) AS PreviousPrice

            FROM Market.StockPrices sp

            JOIN Market.Companies c
                ON sp.CompanyID = c.CompanyID

            JOIN Market.CalendarDates cd
                ON sp.DateID = cd.DateID
        )

        SELECT TOP (@TopN)

            Ticker,
            CompanyName,

            ClosePrice AS CurrentPrice,

            CAST(
                (
                    (
                        ClosePrice - PreviousPrice
                    ) / PreviousPrice
                ) * 100
                AS DECIMAL(18,2)
            ) AS DailyReturn

        FROM PriceChanges

        WHERE PreviousPrice IS NOT NULL

        ORDER BY DailyReturn DESC

    END
    """)

    # =====================================
    # MACD SIGNALS
    # =====================================

    cursor.execute("""
    CREATE OR ALTER PROCEDURE Market.GetMACrossoverSignals

    AS

    BEGIN

        SELECT

            c.Ticker,
            cd.Date,
            ti.SMA20,
            ti.SMA50,

            CASE

                WHEN ti.SMA20 > ti.SMA50
                    THEN 'BUY SIGNAL'

                WHEN ti.SMA20 < ti.SMA50
                    THEN 'SELL SIGNAL'

                ELSE 'HOLD'

            END AS Signal

        FROM Market.TechnicalIndicators ti

        JOIN Market.Companies c
            ON ti.CompanyID = c.CompanyID

        JOIN Market.CalendarDates cd
            ON ti.DateID = cd.DateID

    END
    """)

    conn.commit()

    conn.close()

    print("Stored procedures created successfully.")


if __name__ == "__main__":

    print("=" * 60)
    print("FINANCIAL MARKET DATABASE SETUP")
    print("=" * 60)

    create_database()

    create_tables()

    insert_reference_data()

    create_stored_procedures()

    print("\nDatabase setup completed successfully.")
