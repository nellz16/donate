from flask import Flask, render_template, request, redirect, url_for, session
import random, sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'YFVUYfayuFBFbfHhfHBFgfDd'

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        trx_id TEXT PRIMARY KEY,
        name TEXT,
        message TEXT,
        original_amount INTEGER,
        unique_fee INTEGER,
        final_amount INTEGER,
        status TEXT DEFAULT 'Pending',
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Halaman utama: form donasi
@app.route('/')
def index():
    return render_template('index.html')

# Proses donasi, generate TRX-ID dan hitung final amount
@app.route('/process', methods=['POST'])
def process():
    name = request.form.get('name')
    if request.form.get('anon') == 'on':
        name = 'Anonim'
    message = request.form.get('message')
    
    # Hapus pemisah titik dan ubah ke integer
    donation_input = request.form.get('donation').replace('.', '')
    try:
        original_amount = int(donation_input)
    except:
        original_amount = 0

    # Validasi minimal donasi Rp 1.000
    if original_amount < 1000:
        error = "Minimal donasi adalah Rp 1.000"
        # Kembalikan form dengan pesan error
        return render_template('index.html', error=error, name=name, message=message, donation= request.form.get('donation'))

    # Lanjutkan pembuatan transaksi jika valid
    trx_id = "TRX" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(100, 999))
    unique_fee = random.randint(100, 999)
    final_amount = original_amount + unique_fee

    # Simpan ke database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO transactions 
              (trx_id, name, message, original_amount, unique_fee, final_amount, status, created_at)
              VALUES (?,?,?,?,?,?,?,?)""",
              (trx_id, name, message, original_amount, unique_fee, final_amount, 'Pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return render_template('confirm.html', trx_id=trx_id, name=name, message=message,
                           original_amount=original_amount, unique_fee=unique_fee, final_amount=final_amount)

# Halaman detail transaksi user (misal setelah klik "Saya sudah bayar")
@app.route('/detail/<trx_id>')
def detail(trx_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT trx_id, name, message, original_amount, unique_fee, final_amount, created_at FROM transactions WHERE trx_id=?", (trx_id,))
    transaction = c.fetchone()
    conn.close()
    if transaction:
        return render_template('detail.html', transaction=transaction)
    else:
        return "Transaction not found", 404

# Halaman login admin
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Cek sederhana, jangan gunakan cara ini untuk production
        if username == 'adminRdwn' and password == 'NeLL28052007':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# Dashboard admin: tampilkan maksimal 5 transaksi terbaru
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT trx_id, final_amount, status FROM transactions ORDER BY created_at DESC LIMIT 5")
    transactions = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', transactions=transactions)

# Halaman detail transaksi admin (dengan nominal asli sesuai input user)
@app.route('/admin/detail/<trx_id>')
def admin_detail(trx_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT trx_id, name, message, original_amount, unique_fee, final_amount, created_at FROM transactions WHERE trx_id=?", (trx_id,))
    transaction = c.fetchone()
    conn.close()
    if transaction:
        return render_template('admin_detail.html', transaction=transaction)
    else:
        return "Transaction not found", 404

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

@app.route('/admin/update_status/<trx_id>')
def update_status(trx_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE transactions SET status = 'Sukses' WHERE trx_id = ?", (trx_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_detail', trx_id=trx_id))

@app.route('/admin/delete/<trx_id>')
def delete_transaction(trx_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE trx_id = ?", (trx_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
