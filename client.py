
import argparse
import requests
import sys
from datetime import datetime

# Base URL - update this after deployment
BASE_URL = 'http://localhost:5000'  # Change to your AWS URL after deployment


def convert_currency(from_curr, to_curr, amount):
    """Convert currency using the API"""
    try:
        response = requests.get(
            f'{BASE_URL}/api/v1/convert',
            params={
                'from_currency': from_curr,
                'to_currency': to_curr,
                'amount': amount
            },
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("\n" + "="*50)
        print("CURRENCY CONVERSION")
        print("="*50)
        print(f"From: {data['from']['amount']} {data['from']['currency']}")
        print(f"To:   {data['to']['amount']} {data['to']['currency']}")
        print(f"Rate: 1 {data['from']['currency']} = {data['exchange_rate']} {data['to']['currency']}")
        print(f"Time: {data['timestamp']}")
        print("="*50 + "\n")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError: Failed to connect to service")
        print(f"Details: {e}\n")
        sys.exit(1)
    except KeyError as e:
        print(f"\nError: Unexpected response format")
        print(f"Details: {e}\n")
        sys.exit(1)


def get_rates(base_curr):
    """Get all exchange rates for a base currency"""
    try:
        response = requests.get(
            f'{BASE_URL}/api/v1/rates',
            params={'base_currency': base_curr},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        print("\n" + "="*50)
        print(f"EXCHANGE RATES - Base: {data['base_currency']}")
        print("="*50)
        
        for currency, rate in sorted(data['rates'].items()):
            print(f"1 {data['base_currency']} = {rate:>12.6f} {currency}")
        
        print(f"\nTimestamp: {data['timestamp']}")
        print("="*50 + "\n")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError: Failed to connect to service")
        print(f"Details: {e}\n")
        sys.exit(1)
    except KeyError as e:
        print(f"\nError: Unexpected response format")
        print(f"Details: {e}\n")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Currency Exchange Service CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s convert --from GBP --to USD --amount 100
  %(prog)s rates --base EUR
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert currency')
    convert_parser.add_argument('--from', dest='from_currency', required=True,
                               help='Source currency code (e.g., GBP)')
    convert_parser.add_argument('--to', dest='to_currency', required=True,
                               help='Target currency code (e.g., USD)')
    convert_parser.add_argument('--amount', type=float, required=True,
                               help='Amount to convert')
    
    # Rates command
    rates_parser = subparsers.add_parser('rates', help='Get exchange rates')
    rates_parser.add_argument('--base', dest='base_currency', required=True,
                             help='Base currency code (e.g., GBP)')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        convert_currency(
            args.from_currency,
            args.to_currency,
            args.amount
        )
    elif args.command == 'rates':
        get_rates(args.base_currency)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
