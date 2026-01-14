
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Folder to store chart images
CHART_FOLDER = "static/charts"
if not os.path.exists(CHART_FOLDER):
    os.makedirs(CHART_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')
# ====================================================
@app.route('/reset', methods=['POST'])
def reset():
    # Simply reload page with no dashboard data
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    try:
        # ---- Read CSV ----
        file = request.files['csvfile']
        df = pd.read_csv(file)

        # ---- Validate Columns ----
        required_columns = {'Date', 'Member', 'Category', 'Amount'}
        if not required_columns.issubset(df.columns):
            return render_template('index.html',
                error="CSV must contain Date, Member, Category, Amount columns")

        # ---- Convert Amount ----
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        if df['Amount'].isnull().any():
            return render_template('index.html',
                error="Amount column contains invalid values")

        # ---- Convert Date ----
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if df['Date'].isnull().any():
            return render_template('index.html',
                error="Date column contains invalid values")

        # =====================================================
        # UNIVERSAL CALCULATIONS (Works for both CSV types)
        # =====================================================

        # If negative values exist → Income & Expense mode
        if (df['Amount'] < 0).any():
            total_income = df[df['Amount'] > 0]['Amount'].sum()
            total_expenses = df[df['Amount'] < 0]['Amount'].sum() * -1
            current_balance = total_income - total_expenses
            total_amount = total_income + total_expenses
        else:
            # Expense-only mode
            total_income = 0
            total_expenses = df['Amount'].sum()
            current_balance = total_income - total_expenses
            total_amount = total_expenses

        # =====================================================
        # CATEGORY PIE CHART
        # =====================================================

        category_sum = df.groupby('Category')['Amount'].sum().abs()

        plt.figure(figsize=(5,5))
        plt.pie(category_sum, labels=category_sum.index, autopct='%1.1f%%')
        plt.title("Category-wise Expenses")
        pie_path = os.path.join(CHART_FOLDER, "category_pie.png")
        plt.savefig(pie_path)
        plt.close()

        # =====================================================
        # MEMBER BAR CHART
        # =====================================================

        member_sum = df.groupby('Member')['Amount'].sum().abs().reset_index()

        plt.figure(figsize=(6,4))
        sns.barplot(x='Member', y='Amount', data=member_sum)
        plt.title("Member-wise Expenses")
        bar_path = os.path.join(CHART_FOLDER, "member_bar.png")
        plt.savefig(bar_path)
        plt.close()

        # =====================================================
        # WEEKLY / MONTHLY / YEARLY CHARTS
        # =====================================================

        df['Week'] = df['Date'].dt.to_period('W').astype(str)
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        df['Year'] = df['Date'].dt.year.astype(str)

        # Weekly
        weekly_sum = df.groupby('Week')['Amount'].sum().abs().reset_index()
        plt.figure(figsize=(7,4))
        sns.barplot(x='Week', y='Amount', data=weekly_sum)
        plt.xticks(rotation=45)
        plt.title("Weekly Expenses")
        weekly_path = os.path.join(CHART_FOLDER, "weekly.png")
        plt.savefig(weekly_path, bbox_inches='tight')
        plt.close()

        # Monthly
        monthly_sum = df.groupby('Month')['Amount'].sum().abs().reset_index()
        plt.figure(figsize=(7,4))
        sns.barplot(x='Month', y='Amount', data=monthly_sum)
        plt.xticks(rotation=45)
        plt.title("Monthly Expenses")
        monthly_path = os.path.join(CHART_FOLDER, "monthly.png")
        plt.savefig(monthly_path, bbox_inches='tight')
        plt.close()

        # Yearly
        yearly_sum = df.groupby('Year')['Amount'].sum().abs().reset_index()
        plt.figure(figsize=(6,4))
        sns.barplot(x='Year', y='Amount', data=yearly_sum)
        plt.title("Yearly Expenses")
        yearly_path = os.path.join(CHART_FOLDER, "yearly.png")
        plt.savefig(yearly_path, bbox_inches='tight')
        plt.close()

        # =====================================================
        # RETURN RESULTS TO DASHBOARD
        # =====================================================

        return render_template('index.html',
            totalAmount=total_amount,
            totalExpenses=total_expenses,
            currentBalance=current_balance,
            pieChart=pie_path,
            barChart=bar_path,
            weeklyChart=weekly_path,
            monthlyChart=monthly_path,
            yearlyChart=yearly_path,
            showDashboard=True)

    except Exception as e:
        print("ERROR:", e)  # shows real error in terminal
        return render_template('index.html',
            error="Error processing CSV file. Please check CSV format.")

# =====================================================

if __name__ == '__main__':
    app.run(debug=True)
