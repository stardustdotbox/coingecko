#!/usr/bin/env python3
"""
CoinGecko APIを使用して暗号通貨の価格取得と通貨換算を行うツール
"""

import sys
import requests
import re
from typing import Optional, Tuple


# 暗号通貨名からCoinGecko IDへのマッピング
COIN_MAPPING = {
    'ETH': 'ethereum',
    'BTC': 'bitcoin',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'AVAX': 'avalanche-2',
    'LINK': 'chainlink',
    'UNI': 'uniswap',
    'ATOM': 'cosmos',
    'ETC': 'ethereum-classic',
    'LTC': 'litecoin',
    'BCH': 'bitcoin-cash',
    'XLM': 'stellar',
    'ALGO': 'algorand',
}


def get_coin_id(coin_name: str) -> Optional[str]:
    """暗号通貨名からCoinGecko IDを取得"""
    coin_name_upper = coin_name.upper()
    return COIN_MAPPING.get(coin_name_upper, coin_name.lower())


def get_price(coin_id: str) -> Tuple[Optional[float], Optional[float]]:
    """指定した暗号通貨のUSDCとJPY価格を取得"""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': coin_id,
        'vs_currencies': 'usd,jpy'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if coin_id not in data:
            return None, None
        
        coin_data = data[coin_id]
        usd_price = coin_data.get('usd')
        jpy_price = coin_data.get('jpy')
        
        return usd_price, jpy_price
    except requests.exceptions.RequestException as e:
        print(f"エラー: APIリクエストに失敗しました - {e}", file=sys.stderr)
        return None, None
    except KeyError:
        return None, None


def format_price(price: float, currency: str) -> str:
    """価格を適切なフォーマットで表示"""
    if currency == 'USDC':
        # USDCは小数点以下2桁まで
        return f"{price:,.2f}USDC"
    elif currency == 'JPY':
        # JPYは小数点以下2桁まで（カンマ区切り）
        return f"{price:,.2f}JPY"
    else:
        return f"{price:,.2f}{currency}"


def format_crypto_amount(amount: float, coin_name: str) -> str:
    """暗号通貨の数量を適切なフォーマットで表示"""
    # 小数点以下8桁まで表示（必要に応じて調整）
    if amount < 0.0001:
        return f"{amount:.8f}{coin_name}"
    elif amount < 1:
        return f"{amount:.6f}{coin_name}"
    else:
        return f"{amount:.2f}{coin_name}"


def parse_amount_and_currency(arg: str) -> Tuple[Optional[float], Optional[str]]:
    """引数から金額と通貨を解析（例: "100JPY" -> (100.0, "JPY")）"""
    # 数値と通貨名を分離
    match = re.match(r'^([\d,]+\.?\d*)([A-Z]+)$', arg.upper())
    if match:
        amount_str = match.group(1).replace(',', '')
        currency = match.group(2)
        try:
            amount = float(amount_str)
            return amount, currency
        except ValueError:
            return None, None
    return None, None


def show_price(coin_name: str):
    """暗号通貨の価格を表示"""
    coin_id = get_coin_id(coin_name)
    if not coin_id:
        print(f"エラー: '{coin_name}' はサポートされていない暗号通貨です", file=sys.stderr)
        sys.exit(1)
    
    usd_price, jpy_price = get_price(coin_id)
    
    if usd_price is None or jpy_price is None:
        print(f"エラー: '{coin_name}' の価格情報を取得できませんでした", file=sys.stderr)
        sys.exit(1)
    
    # USDC価格として表示（USDCはUSDとほぼ同じ価値）
    print(format_price(usd_price, 'USDC'))
    print(format_price(jpy_price, 'JPY'))


def convert_currency(amount: float, from_currency: str, to_coin: str):
    """通貨を暗号通貨に換算"""
    # JPYから暗号通貨への換算
    if from_currency == 'JPY':
        coin_id = get_coin_id(to_coin)
        if not coin_id:
            print(f"エラー: '{to_coin}' はサポートされていない暗号通貨です", file=sys.stderr)
            sys.exit(1)
        
        _, jpy_price = get_price(coin_id)
        if jpy_price is None:
            print(f"エラー: '{to_coin}' の価格情報を取得できませんでした", file=sys.stderr)
            sys.exit(1)
        
        # JPY金額を暗号通貨に換算
        crypto_amount = amount / jpy_price
        print(format_crypto_amount(crypto_amount, to_coin))
    
    # USDから暗号通貨への換算
    elif from_currency == 'USD':
        coin_id = get_coin_id(to_coin)
        if not coin_id:
            print(f"エラー: '{to_coin}' はサポートされていない暗号通貨です", file=sys.stderr)
            sys.exit(1)
        
        usd_price, _ = get_price(coin_id)
        if usd_price is None:
            print(f"エラー: '{to_coin}' の価格情報を取得できませんでした", file=sys.stderr)
            sys.exit(1)
        
        # USD金額を暗号通貨に換算
        crypto_amount = amount / usd_price
        print(format_crypto_amount(crypto_amount, to_coin))
    
    # 暗号通貨から暗号通貨への換算
    elif from_currency.upper() in COIN_MAPPING or from_currency.lower() in COIN_MAPPING.values():
        from_coin_id = get_coin_id(from_currency)
        to_coin_id = get_coin_id(to_coin)
        
        if not from_coin_id or not to_coin_id:
            print(f"エラー: サポートされていない暗号通貨です", file=sys.stderr)
            sys.exit(1)
        
        from_usd_price, _ = get_price(from_coin_id)
        to_usd_price, _ = get_price(to_coin_id)
        
        if from_usd_price is None or to_usd_price is None:
            print(f"エラー: 価格情報を取得できませんでした", file=sys.stderr)
            sys.exit(1)
        
        # 暗号通貨から暗号通貨への換算
        crypto_amount = (amount * from_usd_price) / to_usd_price
        print(format_crypto_amount(crypto_amount, to_coin))
    
    else:
        print(f"エラー: '{from_currency}' はサポートされていない通貨です", file=sys.stderr)
        sys.exit(1)


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:", file=sys.stderr)
        print("  価格表示: python coingecko.py <暗号通貨名>", file=sys.stderr)
        print("  通貨換算: python coingecko.py <金額><通貨> <暗号通貨名>", file=sys.stderr)
        print("", file=sys.stderr)
        print("例:", file=sys.stderr)
        print("  python coingecko.py ETH", file=sys.stderr)
        print("  python coingecko.py 100JPY ETH", file=sys.stderr)
        print("  python coingecko.py 100JPY USDC", file=sys.stderr)
        sys.exit(1)
    
    # 引数が1つの場合: 価格表示
    if len(sys.argv) == 2:
        coin_name = sys.argv[1]
        show_price(coin_name)
    
    # 引数が2つの場合: 通貨換算
    elif len(sys.argv) == 3:
        amount_arg = sys.argv[1]
        to_coin = sys.argv[2]
        
        amount, from_currency = parse_amount_and_currency(amount_arg)
        if amount is None or from_currency is None:
            print(f"エラー: 無効な金額形式です: '{amount_arg}'", file=sys.stderr)
            print("正しい形式: <数値><通貨> (例: 100JPY, 50USD)", file=sys.stderr)
            sys.exit(1)
        
        convert_currency(amount, from_currency, to_coin)
    
    else:
        print("エラー: 引数が多すぎます", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

