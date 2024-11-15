from flask import Flask, Blueprint, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np

FCF_bp = Blueprint('FCF', __name__)

def future_EBIT(ticker):
    # getting stock
    stock = yf.Ticker(ticker)

    # getting stock financials
    income_statement = stock.financials

    # past growth rates
    ebit_data = income_statement.loc['EBIT'].iloc[:4]
    growth_rate = (((ebit_data.iloc[3] - ebit_data.iloc[2]) / ebit_data.iloc[3]) + 
                    ((ebit_data.iloc[2] - ebit_data.iloc[1]) / ebit_data.iloc[2]) + 
                    ((ebit_data.iloc[1] - ebit_data.iloc[0]) / ebit_data.iloc[1])) / -3

    # future ebit
    current = ebit_data.iloc[0]
    future_ebit = []
    for i in range(5):
        current *= (1 + growth_rate)
        future_ebit.append(current)

    return future_ebit

def future_tax_rate(ticker):
    # getting stock
    stock = yf.Ticker(ticker)

    # getting stock financials
    income_statement = stock.financials
    
    # past tax rates & future tax rate
    tp_data = income_statement.loc['Tax Provision'].iloc[:3]
    pti_data = income_statement.loc['Pretax Income'].iloc[:3]
    tax_rate = ((tp_data.iloc[2] / pti_data.iloc[2]) + 
                 (tp_data.iloc[1] / pti_data.iloc[1]) + 
                 (tp_data.iloc[0] / pti_data.iloc[0])) / 3
    
    return tax_rate

def future_dep_amort(ticker):
    # getting stock
    stock = yf.Ticker(ticker)

    # getting stock financials
    cash_flow = stock.cash_flow
    
    # past dep/amort values & growth rate
    dep_amort_data = cash_flow.loc['Depreciation And Amortization'].iloc[:4]
    growth_rate = (((dep_amort_data.iloc[3] - dep_amort_data.iloc[2]) / dep_amort_data.iloc[3]) + 
                    ((dep_amort_data.iloc[2] - dep_amort_data.iloc[1]) / dep_amort_data.iloc[2]) + 
                    ((dep_amort_data.iloc[1] - dep_amort_data.iloc[0]) / dep_amort_data.iloc[1])) / -3

    # getting future dep/amort
    current = dep_amort_data.iloc[0]
    future_dep_amort = []
    for i in range(5):
        current *= (1 + growth_rate)
        future_dep_amort.append(current)
    
    return future_dep_amort

def future_capex(ticker):
    # getting stock
    stock = yf.Ticker(ticker)

    # getting stock financials
    cash_flow = stock.cash_flow

    # past capex values & growth rate
    capex_data = cash_flow.loc['Capital Expenditure'].iloc[:4]
    growth_rate = (((capex_data.iloc[3] - capex_data.iloc[2]) / capex_data.iloc[3]) + 
                    ((capex_data.iloc[2] - capex_data.iloc[1]) / capex_data.iloc[2]) + 
                    ((capex_data.iloc[1] - capex_data.iloc[0]) / capex_data.iloc[1])) / -3

    # getting future capex
    current = capex_data.iloc[0]
    future_capex = []
    for i in range(5):
        current *= (1 + growth_rate)
        future_capex.append(current)
    
    return future_capex

def future_nwc(ticker):
    # getting stock
    stock = yf.Ticker(ticker)

    # getting stock financials
    balance_sheet = stock.balance_sheet
    current_assets = balance_sheet.loc['Current Assets'].iloc[:4]
    current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[:4]

    # calculating nwc & growth rate
    nwc = current_assets - current_liabilities
    growth_rate = (((nwc.iloc[3] - nwc.iloc[2]) / nwc.iloc[3]) + 
                    ((nwc.iloc[2] - nwc.iloc[1]) / nwc.iloc[2]) + 
 ((nwc.iloc[1] - nwc.iloc[0]) / nwc.iloc[1])) / -3

    # getting future nwc
    current = nwc.iloc[0]
    future_nwc = []
    for i in range(5):
        current *= (1 + growth_rate)
        future_nwc.append(current)

    return future_nwc

def future_FCF(ebit, tax_rate, dep_amort, capex, nwc):
    # Ebit*(1-tax rate) + Depreciation/Amortization - capital expenditures + increase in net working capital
    future_FCF = []
    for i in range(5):
        current = ebit[i] * (1 - tax_rate) + dep_amort[i] - capex[i] + nwc[i]
        future_FCF.append(current)
    
    return future_FCF

def five_year_fcf(ticker):
    ebit = future_EBIT(ticker)
    tax_rate = future_tax_rate(ticker)
    dep_amort = future_dep_amort(ticker)
    capex = future_capex(ticker)
    nwc = future_nwc(ticker)
    fcf = future_FCF(ebit, tax_rate, dep_amort, capex, nwc)

    results = {
        'year_one_fcf': round(fcf[0], 2),
        'year_two_fcf': round(fcf[1], 2),
        'year_three_fcf': round(fcf[2], 2),
        'year_four_fcf': round(fcf[3], 2),
        'year_five_fcf': round(fcf[4], 2),
    }

    return results

@FCF_bp.route('/FCF', methods=['GET', 'POST'])
def FCF():
    if request.method == 'POST':
        ticker = request.form['ticker']
        results = five_year_fcf(ticker)
        return render_template('FCF.html', results=results)
    else:
        return render_template('FCF.html')