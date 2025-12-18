"""
Currency Exchange Service - Enhanced GUI Version
Flask REST API + Tkinter Desktop GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from flask import Flask, request, jsonify
import os
from functools import lru_cache
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask App Setup
app = Flask(__name__)

# Configuration
API_KEY = os.getenv('EXCHANGE_API_KEY', 'your_api_key_here')
BASE_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}'

# Supported currencies
SUPPORTED_CURRENCIES = ['GBP', 'USD', 'EUR', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY']

# Currency symbols
CURRENCY_SYMBOLS = {
    'GBP': '£', 'USD': '$', 'EUR': '€', 'JPY': '¥',
    'AUD': 'A$', 'CAD': 'C$', 'CHF': 'Fr', 'CNY': '¥'
}

# Cache settings
CACHE_DURATION = timedelta(hours=1)


@lru_cache(maxsize=128)
def get_exchange_rates(base_currency, timestamp_key):
    """Fetch exchange rates with caching"""
    try:
        url = f'{BASE_URL}/latest/{base_currency}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result') == 'success':
            return data.get('conversion_rates', {})
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rates: {e}")
        return None


def get_cache_key():
    """Generate hourly cache key"""
    now = datetime.now()
    cache_period = now - timedelta(
        minutes=now.minute % 60,
        seconds=now.second,
        microseconds=now.microsecond
    )
    return cache_period.isoformat()


def validate_currency(currency):
    """Validate currency code"""
    return currency.upper() in SUPPORTED_CURRENCIES


# Flask REST API Endpoints
@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Currency Exchange Service',
        'status': 'running',
        'version': '2.0.0',
        'supported_currencies': SUPPORTED_CURRENCIES,
        'features': ['REST API', 'Desktop GUI'],
        'endpoints': {
            'convert': '/api/v1/convert?from_currency=GBP&to_currency=USD&amount=100',
            'rates': '/api/v1/rates?base_currency=GBP'
        }
    }), 200


@app.route('/api/v1/convert', methods=['GET'])
def convert_currency():
    """Convert currency endpoint"""
    try:
        from_currency = request.args.get('from_currency', '').upper()
        to_currency = request.args.get('to_currency', '').upper()
        amount_str = request.args.get('amount', '')
        
        if not from_currency or not to_currency or not amount_str:
            return jsonify({
                'error': 'Missing required parameters',
                'required': ['from_currency', 'to_currency', 'amount']
            }), 400
        
        if not validate_currency(from_currency):
            return jsonify({
                'error': f'Unsupported currency: {from_currency}',
                'supported_currencies': SUPPORTED_CURRENCIES
            }), 400
        
        if not validate_currency(to_currency):
            return jsonify({
                'error': f'Unsupported currency: {to_currency}',
                'supported_currencies': SUPPORTED_CURRENCIES
            }), 400
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            return jsonify({
                'error': 'Invalid amount',
                'message': 'Amount must be a positive number'
            }), 400
        
        cache_key = get_cache_key()
        rates = get_exchange_rates(from_currency, cache_key)
        
        if rates is None:
            return jsonify({
                'error': 'Failed to fetch exchange rates',
                'message': 'External API unavailable'
            }), 503
        
        if to_currency not in rates:
            return jsonify({
                'error': f'Exchange rate not available for {to_currency}'
            }), 404
        
        exchange_rate = rates[to_currency]
        converted_amount = amount * exchange_rate
        
        return jsonify({
            'from': {
                'currency': from_currency,
                'amount': amount
            },
            'to': {
                'currency': to_currency,
                'amount': round(converted_amount, 2)
            },
            'exchange_rate': exchange_rate,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/v1/rates', methods=['GET'])
def get_rates():
    """Get all exchange rates"""
    try:
        base_currency = request.args.get('base_currency', 'GBP').upper()
        
        if not validate_currency(base_currency):
            return jsonify({
                'error': f'Unsupported currency: {base_currency}',
                'supported_currencies': SUPPORTED_CURRENCIES
            }), 400
        
        cache_key = get_cache_key()
        all_rates = get_exchange_rates(base_currency, cache_key)
        
        if all_rates is None:
            return jsonify({
                'error': 'Failed to fetch exchange rates',
                'message': 'External API unavailable'
            }), 503
        
        filtered_rates = {
            currency: rate 
            for currency, rate in all_rates.items() 
            if currency in SUPPORTED_CURRENCIES
        }
        
        return jsonify({
            'base_currency': base_currency,
            'rates': filtered_rates,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# GUI Application
class CurrencyExchangeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Exchange Service")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="💱 Currency Exchange", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # From Currency Section
        from_frame = ttk.LabelFrame(main_frame, text="From", padding="10")
        from_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(from_frame, text="Currency:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.from_currency_var = tk.StringVar(value='GBP')
        from_currency_combo = ttk.Combobox(from_frame, textvariable=self.from_currency_var, 
                                          values=SUPPORTED_CURRENCIES, state='readonly', width=15)
        from_currency_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(from_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_var = tk.StringVar(value='100')
        amount_entry = ttk.Entry(from_frame, textvariable=self.amount_var, width=17)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # To Currency Section
        to_frame = ttk.LabelFrame(main_frame, text="To", padding="10")
        to_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(to_frame, text="Currency:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.to_currency_var = tk.StringVar(value='USD')
        to_currency_combo = ttk.Combobox(to_frame, textvariable=self.to_currency_var, 
                                        values=SUPPORTED_CURRENCIES, state='readonly', width=15)
        to_currency_combo.grid(row=0, column=1, padx=5)
        
        # Convert Button
        convert_btn = ttk.Button(main_frame, text="🔄 Convert", command=self.convert_currency)
        convert_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Result Frame
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.result_label = ttk.Label(result_frame, text="Enter amount and click Convert", 
                                     font=('Arial', 12), foreground='gray')
        self.result_label.grid(row=0, column=0, pady=10)
        
        # Exchange Rate Label
        self.rate_label = ttk.Label(result_frame, text="", font=('Arial', 10), foreground='blue')
        self.rate_label.grid(row=1, column=0)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready | API: Connected")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def convert_currency(self):
        """Perform currency conversion"""
        try:
            from_curr = self.from_currency_var.get()
            to_curr = self.to_currency_var.get()
            amount_str = self.amount_var.get()
            
            # Validation
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number")
                return
            
            # Update status
            self.status_var.set("Converting...")
            self.root.update()
            
            # Get exchange rates
            cache_key = get_cache_key()
            rates = get_exchange_rates(from_curr, cache_key)
            
            if rates is None:
                messagebox.showerror("API Error", "Failed to fetch exchange rates. Check your internet connection.")
                self.status_var.set("Ready | API: Error")
                return
            
            if to_curr not in rates:
                messagebox.showerror("Error", f"Exchange rate not available for {to_curr}")
                return
            
            # Calculate conversion
            exchange_rate = rates[to_curr]
            converted_amount = amount * exchange_rate
            
            # Display result
            from_symbol = CURRENCY_SYMBOLS.get(from_curr, '')
            to_symbol = CURRENCY_SYMBOLS.get(to_curr, '')
            
            result_text = f"{from_symbol}{amount:,.2f} {from_curr} = {to_symbol}{converted_amount:,.2f} {to_curr}"
            self.result_label.config(text=result_text, foreground='green', font=('Arial', 14, 'bold'))
            
            rate_text = f"Exchange Rate: 1 {from_curr} = {exchange_rate:.4f} {to_curr}"
            self.rate_label.config(text=rate_text)
            
            self.status_var.set(f"Ready | Last Update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Ready | API: Error")


def run_flask():
    """Run Flask server in a thread"""
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)


def main():
    """Main entry point"""
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Create and run GUI
    root = tk.Tk()
    app_gui = CurrencyExchangeGUI(root)
    
    print("="*60)
    print("Currency Exchange Service - Enhanced Version")
    print("="*60)
    print("✓ REST API running on http://localhost:5000")
    print("✓ Desktop GUI launched")
    print("✓ Both interfaces are active!")
    print("="*60)
    
    root.mainloop()


if __name__ == '__main__':
    main()