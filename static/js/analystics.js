const fmt = v =>
  v >= 1_000_000 ? (v / 1_000_000).toFixed(1) + "M" : v.toLocaleString();

const C = {
  blue: "#4f46e5",
  green: "#22c55e",
  cyan: "#06b6d4",
  pie: ["#4f46e5", "#22c55e", "#06b6d4", "#f97316", "#ef4444"]
};

// 🔹 Top Sales
new Chart(topSalesChart,{
  type:"bar",
  data:{
    labels: ANALYTICS.topSales.labels,
    datasets:[{
      label: I18N.sold,
      data: ANALYTICS.topSales.values,
      backgroundColor:"#4f46e5",
      borderRadius:8
    }]
  }
});

// 🔹 Top Profit
new Chart(document.getElementById("topProfitChart"), {
  type: "bar",
  data: {
    labels: ANALYTICS.topProfit.labels,
    datasets: [{
      label: I18N.profit,
      data: ANALYTICS.topProfit.values,
      backgroundColor: C.green,
      borderRadius: 8
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: { y: { ticks: { callback: v => fmt(v) } } }
  }
});

// 🔹 Revenue vs Profit
new Chart(productBarChart,{
  type:"bar",
  data:{
    labels: ANALYTICS.bar.labels,
    datasets:[
      {
        label: I18N.revenue,
        data: ANALYTICS.bar.revenue,
        backgroundColor:"#06b6d4"
      },
      {
        label: I18N.profit,
        data: ANALYTICS.bar.profit,
        backgroundColor:"#22c55e"
      }
    ]
  }
});

// 🔹 Pie
new Chart(document.getElementById("salesPieChart"), {
  type: "pie",
  data: {
    labels: ANALYTICS.pie.labels,
    datasets: [{
      data: ANALYTICS.pie.values,
      backgroundColor: C.pie
    }]
  }
});
