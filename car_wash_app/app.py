from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

@app.route('/')
def index():
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)

@app.route('/services')
def services():
    current_year = datetime.now().year
    return render_template('services.html', current_year=current_year)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        flash(f'Спасибо, {name}! Ваша заявка принята.', 'success')
        return redirect(url_for('services'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)