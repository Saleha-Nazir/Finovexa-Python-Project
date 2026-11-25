import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Finovexa | Financial Analysis", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp {background:#f3f6fb;color:#152941}
[data-testid="stSidebar"] {background:#102a43}
[data-testid="stSidebar"] * {color:#eaf3f8}
h1,h2,h3 {color:#102a43}
div[data-testid="stMetric"] {background:white;border:1px solid #e4ebf3;padding:16px;border-radius:14px}
div.stButton > button {background:#19a7a1;color:white;border:0;border-radius:9px;font-weight:700}
div.stButton > button:hover {background:#128e89;color:white}
.hero {background:linear-gradient(115deg,#102a43,#164e63);padding:28px 32px;border-radius:20px;color:white;margin-bottom:20px}
.hero h1 {color:white;margin:0}
.hero p {color:#d0e3ed;margin-bottom:0}
</style>
""", unsafe_allow_html=True)

def npf_irr(values):
    # Newton iteration for periodic cash flows; returns None if no convergence.
    x=0.1
    for _ in range(200):
        f=sum(v/(1+x)**i for i,v in enumerate(values))
        df=sum(-i*v/(1+x)**(i+1) for i,v in enumerate(values) if i)
        if abs(df)<1e-12: raise ValueError("No IRR")
        nxt=x-f/df
        if nxt<=-0.999999: nxt=(x-0.999999)/2
        if abs(nxt-x)<1e-10: return nxt
        x=nxt
    raise ValueError("IRR did not converge")


st.sidebar.markdown("## 🟩 FINOVEXA")
st.sidebar.caption("Financial Innovation & Analysis")
page = st.sidebar.radio("WORKSPACE", [
    "Overview", "Investment analysis", "Loan calculator",
    "Interest comparison", "Annuity calculator", "Sensitivity analysis"
])
st.sidebar.markdown("---")
st.sidebar.caption("Educational decision-support tool. Not financial advice.")

def money(x):
    return f"PKR {x:,.2f}"

def metric_row(items):
    cols=st.columns(len(items))
    for c,(label,val) in zip(cols,items):
        c.metric(label,val)

def chart_line(title, xs, ys, labels):
    fig,ax=plt.subplots(figsize=(7,3))
    for y,label in zip(ys,labels):
        ax.plot(xs,y,marker="o",label=label)
    ax.set_title(title); ax.grid(alpha=.2); ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.caption("FINANCIAL WORKSPACE  /  FINOVEXA PROTOTYPE")
if page=="Overview":
    st.markdown('<div class="hero"><h1>Make sense of your financial decisions.</h1><p>Explore investments, understand borrowing costs, and compare financial scenarios with clear, formula-based tools.</p></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.subheader("↗ Investment tools")
        st.write("PV · FV · NPV · IRR")
        st.caption("Evaluate cash flows and investment value over time.")
    with b:
        st.subheader("▤ Borrowing tools")
        st.write("Payments · Interest")
        st.caption("Estimate installments, repayment totals, and interest costs.")
    with c:
        st.subheader("⌁ Scenario tools")
        st.write("Compare · Explore")
        st.caption("See how changing assumptions affects outcomes.")
    st.subheader("About Finovexa")
    st.info("Finovexa is an educational financial analysis prototype. It uses user-entered assumptions and does not connect to banks, execute trades, or guarantee investment returns.")
    st.write("Choose a calculator from the sidebar to begin.")

elif page=="Investment analysis":
    st.header("Investment analysis")
    st.caption("Present value, future value, NPV, and estimated IRR.")
    left,right=st.columns([.85,1.4])
    with left:
        initial=st.number_input("Initial investment (PKR)",min_value=0.0,value=100000.0,step=5000.0)
        rate=st.number_input("Annual discount / growth rate (%)",value=10.0,step=.5)/100
        years=st.number_input("Investment period (years)",min_value=1,max_value=100,value=5)
        end_amount=st.number_input("Expected amount at end (PKR)",min_value=0.0,value=180000.0,step=5000.0)
        cash=st.number_input("Annual cash flow (PKR)",min_value=0.0,value=25000.0,step=1000.0)
    flows=[-initial]+[cash]*int(years)
    flows[-1]+=end_amount
    pv=sum(cash/(1+rate)**t for t in range(1,int(years)+1))+end_amount/(1+rate)**int(years) if rate>-1 else float("nan")
    fv=initial*(1+rate)**int(years)
    npv=-initial+pv
    try:
        irr=float(npf_irr(flows))
        irr_text=f"{irr*100:.2f}%"
    except Exception:
        irr_text="Not available"
    with right:
        st.subheader("Analysis results")
        metric_row([("Present value",money(pv)),("Future value",money(fv))])
        metric_row([("Net present value",money(npv)),("Estimated IRR",irr_text)])
        years_x=np.arange(0,int(years)+1)
        values=[initial*(1+rate)**t for t in years_x]
        chart_line("Illustrative investment growth",years_x,[values],["Projected value"])
    st.caption("Cash-flow convention: initial investment at year 0, annual cash flows at each year, and expected end amount added in the final year.")

elif page=="Loan calculator":
    st.header("Loan calculator")
    st.caption("Estimate periodic installments and total borrowing cost.")
    left,right=st.columns([.85,1.4])
    with left:
        principal=st.number_input("Loan amount (PKR)",min_value=0.0,value=500000.0,step=10000.0)
        annual=st.number_input("Annual interest rate (%)",min_value=0.0,max_value=100.0,value=15.0,step=.25)/100
        term=st.number_input("Repayment period (years)",min_value=1,max_value=50,value=5)
        freq=st.selectbox("Payments per year",[("Monthly",12),("Quarterly",4),("Half-yearly",2),("Yearly",1)],format_func=lambda x:x[0])[1]
    n=int(term*freq); r=annual/freq
    payment=principal/n if r==0 else principal*r/(1-(1+r)**(-n))
    total=payment*n; interest=total-principal
    with right:
        st.subheader("Repayment breakdown")
        metric_row([("Payment per period",money(payment)),("Total repayment",money(total))])
        metric_row([("Total interest",money(interest)),("Number of payments",f"{n:,}")])
        periods=np.arange(1,n+1)
        balances=[max(0,principal*(1+r)**k-payment*((1+r)**k-1)/r) if r else max(0,principal-payment*k) for k in periods]
        chart_line("Remaining loan balance",periods,[balances],["Balance"])
    st.caption("Assumes a fixed rate and equal payments. Fees, taxes, and changing rates are not included.")

elif page=="Interest comparison":
    st.header("Interest comparison")
    st.caption("Compare simple and compound growth over time.")
    left,right=st.columns([.85,1.4])
    with left:
        p=st.number_input("Principal (PKR)",min_value=0.0,value=100000.0,step=5000.0)
        r=st.number_input("Annual interest rate (%)",min_value=0.0,max_value=100.0,value=12.0,step=.5)/100
        y=st.number_input("Period (years)",min_value=1,max_value=100,value=5)
        freq=st.selectbox("Compounding frequency",[("Yearly",1),("Half-yearly",2),("Quarterly",4),("Monthly",12),("Daily",365)],format_func=lambda x:x[0])[1]
    simple=p*(1+r*y); compound=p*(1+r/freq)**(freq*y)
    with right:
        st.subheader("Growth comparison")
        metric_row([("Simple interest total",money(simple)),("Compound interest total",money(compound))])
        metric_row([("Simple interest earned",money(simple-p)),("Compound interest earned",money(compound-p))])
        xs=np.arange(0,int(y)+1)
        chart_line("Value over time",xs,[[p*(1+r*t) for t in xs],[p*(1+r/freq)**(freq*t) for t in xs]],["Simple","Compound"])

elif page=="Annuity calculator":
    st.header("Annuity calculator")
    st.caption("Estimate the present and future value of equal periodic payments.")
    c1,c2=st.columns(2)
    with c1:
        payment=st.number_input("Payment per period (PKR)",min_value=0.0,value=20000.0,step=1000.0)
        annual=st.number_input("Annual interest rate (%)",min_value=0.0,max_value=100.0,value=8.0,step=.5)/100
        years=st.number_input("Number of years",min_value=1,max_value=100,value=10)
    with c2:
        freq=st.selectbox("Payments per year",[("Monthly",12),("Quarterly",4),("Half-yearly",2),("Yearly",1)],format_func=lambda x:x[0])[1]
        timing=st.selectbox("Payment timing",["End of period (ordinary)","Beginning of period (due)"])
        n=int(years*freq); r=annual/freq
        pv=payment*n if r==0 else payment*(1-(1+r)**(-n))/r
        fv=payment*n if r==0 else payment*((1+r)**n-1)/r
        if timing.startswith("Beginning"):
            pv*=1+r; fv*=1+r
        metric_row([("Present value",money(pv)),("Future value",money(fv))])
        st.metric("Total payments",money(payment*n))
    st.info("This estimate assumes equal payments and a constant rate. It excludes fees, taxes, and inflation.")

elif page=="Sensitivity analysis":
    st.header("Sensitivity analysis")
    st.caption("Explore how changing the discount rate affects an investment's NPV.")
    c1,c2,c3=st.columns(3)
    with c1:
        initial=st.number_input("Initial investment (PKR)",min_value=0.0,value=100000.0,step=5000.0)
    with c2:
        cash=st.number_input("Annual cash flow (PKR)",min_value=0.0,value=30000.0,step=1000.0)
    with c3:
        years=st.number_input("Years",min_value=1,max_value=100,value=5)
    rates=np.arange(0,0.301,.01)
    npvs=[-initial+sum(cash/(1+rate)**t for t in range(1,int(years)+1)) for rate in rates]
    selected=st.slider("Selected discount rate (%)",0.0,30.0,10.0,.5)/100
    selected_npv=-initial+sum(cash/(1+selected)**t for t in range(1,int(years)+1))
    st.metric("NPV at selected rate",money(selected_npv))
    chart_line("NPV sensitivity by discount rate",[f"{r*100:.0f}%" for r in rates],[npvs],["NPV"])
    st.caption("NPV is calculated as the present value of annual cash flows minus the initial investment.")


st.markdown("---")
st.caption("Finovexa • Educational prototype • Results depend on the assumptions entered.")
