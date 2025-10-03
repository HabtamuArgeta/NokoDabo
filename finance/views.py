# finance/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import Transaction
import plotly.graph_objs as go
import plotly.io as pio

# ---------------- Graph View using Plotly ----------------
def finance_graph(request):
    # Calculate revenue and expense totals
    revenues = Transaction.objects.filter(transaction_type="revenue")
    expenses = Transaction.objects.filter(transaction_type="expense")

    revenue_sum = sum([r.total_amount for r in revenues])
    expense_sum = sum([e.total_amount for e in expenses])

    # Create bar chart
    fig = go.Figure(data=[go.Bar(x=["Revenue", "Expense"], y=[revenue_sum, expense_sum], marker_color=['green','red'])])
    fig.update_layout(title="Finance Report: Revenue vs Expense", yaxis_title="Amount (Birr)")

    # Generate HTML div
    graph_div = pio.to_html(fig, full_html=False)

    return render(request, "finance/report_graph.html", {"graph_div": graph_div})