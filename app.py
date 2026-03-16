import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, abort

app = Flask(__name__)
app.secret_key = 'NEON_PINK_SHOPPING_SECRET'

# Create a fake secret file for the Path Traversal challenge
def create_secret_file():
    with open("secret_flag.txt", "w") as f:
        f.write("CTF{PATH_TRAVERSAL_MASTER_77}\n")

create_secret_file()

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('shop'))

# VULNERABILITY 1: Business Logic Flaw (Price Manipulation)
@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if request.method == 'POST':
        item = request.form.get('item_name')
        price = request.form.get('price') # VULNERABILITY: Trusting the client's price!
        
        try:
            price = float(price)
            session['cart_item'] = item
            session['cart_price'] = price
            return redirect(url_for('cart'))
        except:
            return "Invalid Price Format."

    return render_template('shop.html')

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    item = session.get('cart_item', 'Empty Cart')
    price = session.get('cart_price', 0)
    
    flag = None
    if request.method == 'POST':
        if price == 0 and item == "Admin Access Token":
            flag = "CTF{BUSINESS_LOGIC_BYPASS_F12}"
        elif price > 0:
            return render_template('cart.html', item=item, price=price, error="You do not have enough funds to purchase this.")
            
    return render_template('cart.html', item=item, price=price, flag=flag)

# VULNERABILITY 2: Path Traversal
@app.route('/download')
def download():
    filename = request.args.get('file')
    
    if not filename:
        return render_template('download.html')
        
    # VULNERABILITY: We don't filter "../" from the filename!
    try:
        # In a real app, this is dangerous. We allow them to traverse back.
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found.", 404
    except Exception as e:
        return "Error reading file."

# VULNERABILITY 3: Command Injection (Stock Checker)
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    output = None
    if request.method == 'POST':
        ip = request.form.get('ip')
        
        # AI Trap / Safe Execution:
        # Instead of actually running os.system() which could crash your Render server,
        # we parse their input to see if they figured out the syntax.
        
        if ";" in ip or "&&" in ip or "|" in ip:
            if "cat" in ip and "flag" in ip:
                output = "Warehouse Server Output:\nroot@warehouse:~# \nCTF{CMD_INJECTION_ROOT_ACCESS}"
            elif "ls" in ip:
                output = "Warehouse Server Output:\nflag.txt  warehouse_db.sqlite  config.yaml"
            elif "whoami" in ip:
                output = "Warehouse Server Output:\nroot"
            else:
                output = f"Warehouse Server Output:\nsh: 1: command not found"
        else:
            # Normal behavior
            output = f"Pinging {ip}...\n64 bytes from {ip}: icmp_seq=1 ttl=64 time=0.034 ms\n1 packets transmitted, 1 received, 0% packet loss."
            
    return render_template('stock.html', output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)