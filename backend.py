from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Seed dataset for evaluation reference
subscriptions = [
    {"id": 1, "name": "Netflix Premium", "cost": 649.0, "billingCycle": "Monthly", "renewalDate": "2026-06-28", "active": True},
    {"id": 2, "name": "Adobe Creative Cloud", "cost": 2390.0, "billingCycle": "Monthly", "renewalDate": "2026-06-30", "active": True},
    {"id": 3, "name": "AWS Cloud Hosting", "cost": 12000.0, "billingCycle": "Yearly", "renewalDate": "2026-06-24", "active": True},
    {"id": 4, "name": "Spotify Premium", "cost": 179.0, "billingCycle": "Monthly", "renewalDate": "2026-07-15", "active": False}
]

def calculate_metrics():
    total_monthly_burn = 0.0
    upcoming_alerts_count = 0
    fixed_current_date = datetime.strptime("2026-06-22", "%Y-%m-%d")
    processed_subs = []

    for sub in subscriptions:
        cost = float(sub["cost"])
        # Cost Uniformity Engine
        monthly_normalized = cost / 12.0 if sub["billingCycle"] == "Yearly" else cost
        
        if sub["active"]:
            total_monthly_burn += monthly_normalized

        # Date Intersect Calculator
        renewal_dt = datetime.strptime(sub["renewalDate"], "%Y-%m-%d")
        days_remaining = (renewal_dt - fixed_current_date).days
        
        renewing_soon = 0 <= days_remaining <= 7
        if sub["active"] and renewing_soon:
            upcoming_alerts_count += 1

        processed_sub = sub.copy()
        processed_sub["monthlyNormalizedCost"] = f"{monthly_normalized:.2f}"
        processed_sub["renewingSoon"] = renewing_soon
        processed_subs.append(processed_sub)

    return {
        "totalMonthlyBurn": f"{total_monthly_burn:.2f}",
        "upcomingAlertsCount": upcoming_alerts_count,
        "subscriptions": processed_subs
    }

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify(calculate_metrics())

@app.route('/api/subscriptions', methods=['POST'])
def add_subscription():
    data = request.json
    new_sub = {
        "id": len(subscriptions) + 1,
        "name": data["name"],
        "cost": float(data["cost"]),
        "billingCycle": data["billingCycle"],
        "renewalDate": data["renewalDate"],
        "active": True
    }
    subscriptions.append(new_sub)
    return jsonify(calculate_metrics()), 201

@app.route('/api/subscriptions/<int:sub_id>/toggle', methods=['PATCH'])
def toggle_subscription(sub_id):
    for sub in subscriptions:
        if sub["id"] == sub_id:
            sub["active"] = not sub["active"]
            return jsonify(calculate_metrics())
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
