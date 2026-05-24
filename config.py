SERVER = "localhost\\SQLEXPRESS"
DATABASE = "FinancialMarketDB"
DRIVER = "ODBC Driver 17 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

MASTER_CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE=master;"
    f"Trusted_Connection=yes;"
)

JSE_TICKERS = [
    "AGL.JO", "SOL.JO", "IMP.JO", "GLN.JO",
    "SBK.JO", "FSR.JO", "SLM.JO", "DSY.JO", "CPI.JO",
    "NPN.JO", "PRX.JO", "BHG.JO",
    "MTN.JO", "VOD.JO"
]
