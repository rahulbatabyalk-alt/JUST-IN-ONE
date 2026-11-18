import streamlit as st
import time
from datetime import datetime
import os
from flask import Flask, request, jsonify, send_file
import json as json_module

app = Flask(__name__)
users = {}
orders = []

class json:
    """Concrete JSON utility implementation."""

    @staticmethod
    def dumps(value):
        return json_module.dumps(value, ensure_ascii=False)

    @staticmethod
    def loads(value):
        return json_module.loads(value)

    @staticmethod
    def dump(value, file, **kwargs):
        return json_module.dump(value, file, ensure_ascii=False, **kwargs)

    @staticmethod
    def load(file, **kwargs):
        return json_module.load(file, **kwargs)

@app.route("/")
def home():
    folder = os.path.dirname(os.path.abspath(__file__))
    return send_file(os.path.join(folder, "app.html"))


# 2. This saves new user accounts from the Frontend
@app.route("/api/users", methods=["POST"])
def save_user():
    data = request.json
    users[data["phone"]] = data
    return jsonify(data)

# 3. This sends & receives orders between Frontend and Backend
@app.route("/api/orders", methods=["GET", "POST"])
def handle_orders():
    if request.method == "POST":
        data = request.json
        data["id"] = f"ORD-{101 + len(orders)}"
        data["status"] = "🟡 Waiting for Shop"
        orders.insert(0, data)
        return jsonify(data)
    return jsonify(orders)

if __name__ == "__main__":
    app.run(debug=True, port=5000)



# Page configuration for a clean mobile-like view
st.set_page_config(page_title="Just One - Essentials Delivery", page_icon="🛍️", layout="centered")

# Custom CSS to make buttons large and accessible for elderly/disabled users
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px !important;
        font-weight: bold;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize temporary database in session state
if "orders" not in st.session_state:
    st.session_state.orders = []

# Top Header
st.title("🛍️ JUST ONE")
st.subheader("Essential Groceries & Medicines at Your Doorstep")

# Role Switcher for 3-Hour Prototype Demo
role = st.radio(
    "Select View (Demo Mode):",
    ["👤 Customer (Order Essentials)", "🏪 Local Shop & Delivery Partner"],
    horizontal=True
)

st.divider()

# ==========================================
# VIEW 1: CUSTOMER INTERFACE (ACCESSIBLE)
# ==========================================
if role == "👤 Customer (Order Essentials)":
    st.header("What do you need today?")
    
    # Large Category Selection
    category = st.selectbox(
        "1. Choose Category:",
        ["🥦 Daily Groceries", "💊 Medicines & First Aid", "🆘 Urgent Survival Kit"]
    )
    
    # Quick Select Common Items + Custom Input
    quick_items = st.multiselect(
        "2. Tap to add common items:",
        ["Rice / Atta (5kg)", "Milk & Bread", "Drinking Water (20L)", "Paracetamol / Basic Meds", "Blood Pressure / Sugar Meds", "Fruits & Vegetables"]
    )
    
    custom_note = st.text_area(
        "3. Write extra items or special instructions (e.g., 'Ring bell loudly, need help carrying inside'):",
        height=100
    )
    
    # Customer Details
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Your Name", placeholder="e.g., Ramesh Sharma")
    with col2:
        cust_phone = st.text_input("Phone Number", placeholder="e.g., 9876543210")
        
    cust_address = st.text_input("Full Home Address", placeholder="House No, Street, Landmark")
    
    st.info("💵 Payment Mode: **Cash on Delivery (COD)** — Pay safely when items arrive.")
    
    # One-Tap Place Order Button
    if st.button("✅ PLACE ORDER NOW", type="primary"):
        if not cust_name or not cust_phone or not cust_address:
            st.error("⚠️ Please enter your Name, Phone Number, and Address so our delivery partner can reach you.")
        elif not quick_items and not custom_note:
            st.error("⚠️ Please select at least one item or write what you need.")
        else:
            new_order = {
                "id": f"ORD-{100 + len(st.session_state.orders) + 1}",
                "time": datetime.now().strftime("%I:%M %p"),
                "name": cust_name,
                "phone": cust_phone,
                "address": cust_address,
                "category": category,
                "items": ", ".join(quick_items) if quick_items else "Custom Note Only",
                "note": custom_note if custom_note else "None",
                "status": "🟡 Waiting for Local Shop"
            }
            st.session_state.orders.insert(0, new_order)
            st.success(f"🎉 Order **{new_order['id']}** placed! A nearby shop is reviewing it now.")

    # Live Order Tracking for Customer
    if st.session_state.orders:
        st.divider()
        st.subheader("📦 Your Live Order Status")
        for order in st.session_state.orders:
            with st.container(border=True):
                st.markdown(f"### {order['id']} — {order['status']}")
                st.write(f"**Category:** {order['category']} | **Ordered at:** {order['time']}")
                st.write(f"**Items:** {order['items']}")
                if order['note'] != "None":
                    st.write(f"**Special Note:** {order['note']}")

# ==========================================
# VIEW 2: SHOPKEEPER & DELIVERY INTERFACE
# ==========================================
else:
    st.header("🏪 Incoming Orders (Shop & Delivery Dashboard)")
    
    if not st.session_state.orders:
        st.info("No orders yet. Switch to the **Customer** tab above to place a test order!")
    else:
        for idx, order in enumerate(st.session_state.orders):
            with st.container(border=True):
                st.markdown(f"### {order['id']} | {order['category']}")
                st.write(f"**Status:** {order['status']}")
                st.write(f"**Customer:** {order['name']} (📞 `{order['phone']}`)")
                st.write(f"**Address:** 📍 {order['address']}")
                st.write(f"**Items:** {order['items']}")
                st.warning(f"**Accessibility / Doorstep Note:** {order['note']}")
                
                # Action Buttons for Shop & Delivery Rider
                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("📦 Pack Order", key=f"pack_{idx}"):
                        st.session_state.orders[idx]["status"] = "🔵 Packed by Local Shop"
                        st.rerun()
                with btn2:
                    if st.button("🛵 Out for Delivery", key=f"ship_{idx}"):
                        st.session_state.orders[idx]["status"] = "🟠 Delivery Partner on the Way"
                        st.rerun()
                with btn3:
                    if st.button("✅ Mark Delivered", key=f"done_{idx}"):
                        st.session_state.orders[idx]["status"] = "🟢 Delivered Safely"
                        st.rerun()
