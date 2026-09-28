"""Historical CME equity cash proxy, reverse DCF and valuation uncertainty."""
from .data import Market
from .math import equity_dcf, reverse_dcf


def run():
    m=Market()
    inputs={"cfo_m":3453.8,"capex_m":76.4,"sbc_m":82.9,"common_shares_m":359.5,"participating_securities_m":4.584}
    cash=(inputs["cfo_m"]-inputs["capex_m"]-inputs["sbc_m"])/(inputs["common_shares_m"]+inputs["participating_securities_m"])
    price=m.row(m.post,"CME","2024-09-27",exact=True)["close"]
    value,tv=equity_dcf(cash,.08,.09,.03)
    grid=[{"growth":g,"discount":r,"value":equity_dcf(cash,g,r,.03)[0],"upside":equity_dcf(cash,g,r,.03)[0]/price-1}
          for g in [.02,.05,.08,.11,.14] for r in [.07,.08,.09,.10,.11]]
    scenarios=[]
    for name,g,r,t in [("Bear",.02,.11,.02),("Base",.08,.09,.03),("Bull",.12,.08,.035)]:
        v,terminal=equity_dcf(cash,g,r,t)
        scenarios.append({"scenario":name,"growth":g,"discount":r,"terminal_growth":t,"value":v,"terminal_share":terminal,"upside":v/price-1})
    return {"company":"CME Group","financial_period":"FY2023","information_cutoff":"2024-09-27", "inputs":inputs,
            "cash_per_share":cash,"reference_price":price,"base_value":value,"terminal_value_share":tv,
            "implied_five_year_cash_growth":reverse_dcf(cash,price,.09,.03),"grid":grid,"scenarios":scenarios,
            "limitation":"CFO less capex less SBC is a deliberately conservative proxy, not a full FCFE forecast. No financing forecast; participating securities added conservatively to denominator. No incremental net-cash add-on. September-2024 valuation exercise, not a current target or proof of a historical decision."}
