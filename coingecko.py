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
    'XMR': 'monero',
    'HYPE': 'hyperliquid',
    'RISE': 'sunrise',
    'ASTR': 'astar',
    'XYM': 'symbol',
    'LOOT': 'lootcoin',
    'JPYC': 'jpyc',
}


def get_coin_id(coin_name: str) -> Optional[str]:
    """暗号通貨名からCoinGecko IDを取得"""
    coin_name_upper = coin_name.upper()
    return COIN_MAPPING.get(coin_name_upper, coin_name.lower())


def get_price(coin_id: str) -> Tuple[Optional[float], Optional[float]]:
    """指定した暗号通貨のUSDとJPY価格を取得"""
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


def get_market_data(coin_id: str) -> Optional[dict]:
    """指定した暗号通貨の市場データを取得"""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': coin_id,
        'vs_currencies': 'usd,jpy',
        'include_market_cap': 'true',
        'include_24hr_vol': 'true',
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if coin_id not in data:
            return None
        
        coin_data = data[coin_id]
        
        # 追加の市場データを取得
        url_detail = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params_detail = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        try:
            response_detail = requests.get(url_detail, params=params_detail, timeout=10)
            response_detail.raise_for_status()
            detail_data = response_detail.json()
            market_data = detail_data.get('market_data', {})
            
            return {
                'name': detail_data.get('name', ''),
                'symbol': detail_data.get('symbol', '').upper(),
                'usd_price': coin_data.get('usd'),
                'jpy_price': coin_data.get('jpy'),
                'market_cap_usd': coin_data.get('usd_market_cap'),
                'market_cap_jpy': coin_data.get('jpy_market_cap'),
                'fully_diluted_valuation_usd': market_data.get('fully_diluted_valuation', {}).get('usd'),
                'fully_diluted_valuation_jpy': market_data.get('fully_diluted_valuation', {}).get('jpy'),
                'total_volume_24h_usd': coin_data.get('usd_24h_vol'),
                'total_volume_24h_jpy': coin_data.get('jpy_24h_vol'),
                'circulating_supply': market_data.get('circulating_supply'),
                'total_supply': market_data.get('total_supply'),
                'max_supply': market_data.get('max_supply'),
            }
        except requests.exceptions.RequestException:
            # 詳細APIが失敗した場合、基本データのみ返す
            return {
                'name': '',
                'symbol': coin_id.upper(),
                'usd_price': coin_data.get('usd'),
                'jpy_price': coin_data.get('jpy'),
                'market_cap_usd': coin_data.get('usd_market_cap'),
                'market_cap_jpy': coin_data.get('jpy_market_cap'),
                'total_volume_24h_usd': coin_data.get('usd_24h_vol'),
                'total_volume_24h_jpy': coin_data.get('jpy_24h_vol'),
            }
    except requests.exceptions.RequestException as e:
        print(f"エラー: APIリクエストに失敗しました - {e}", file=sys.stderr)
        return None
    except KeyError:
        return None


def format_price(price: float, currency: str) -> str:
    """価格を適切なフォーマットで表示"""
    if currency == 'USD':
        # USD価格は小数点以下6桁まで表示
        if price < 0.01:
            return f"{price:.8f}".rstrip('0').rstrip('.') + currency
        elif price < 1:
            return f"{price:.6f}".rstrip('0').rstrip('.') + currency
        elif price < 1000:
            return f"{price:.4f}".rstrip('0').rstrip('.') + currency
        else:
            return f"{price:.2f}".rstrip('0').rstrip('.') + currency
    elif currency == 'JPY':
        # JPY価格は小数点以下2桁まで表示
        if price < 1:
            return f"{price:.4f}".rstrip('0').rstrip('.') + currency
        else:
            return f"{price:.2f}".rstrip('0').rstrip('.') + currency
    else:
        # その他の通貨は小数点以下6桁まで
        if price < 0.01:
            return f"{price:.8f}".rstrip('0').rstrip('.') + currency
        elif price < 1:
            return f"{price:.6f}".rstrip('0').rstrip('.') + currency
        else:
            return f"{price:.2f}".rstrip('0').rstrip('.') + currency


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


def format_large_number(value: Optional[float]) -> str:
    """大きな数値を適切なフォーマットで表示"""
    if value is None:
        return "N/A"
    
    # 時価総額や取引量などの大きな数値は小数点以下2桁まで表示
    if value >= 1000000:
        # 100万以上の場合は小数点以下2桁
        return f"{value:,.2f}".rstrip('0').rstrip('.')
    elif value >= 1000:
        # 1000以上の場合は小数点以下2桁
        return f"{value:,.2f}".rstrip('0').rstrip('.')
    else:
        # 1000未満の場合は小数点以下4桁
        return f"{value:,.4f}".rstrip('0').rstrip('.')


def format_supply(value: Optional[float]) -> str:
    """供給量を適切なフォーマットで表示"""
    if value is None:
        return "N/A"
    
    # 供給量は整数として表示（小数点以下は不要）
    if value == int(value):
        return f"{int(value):,}"
    else:
        # 小数点がある場合は小数点以下2桁まで
        return f"{value:,.2f}".rstrip('0').rstrip('.')


def show_price(coin_name: str):
    """暗号通貨の価格と市場データを表示"""
    coin_id = get_coin_id(coin_name)
    if not coin_id:
        print(f"エラー: '{coin_name}' はサポートされていない暗号通貨です", file=sys.stderr)
        sys.exit(1)
    
    # 市場データを取得
    market_data = get_market_data(coin_id)
    
    if market_data is None or market_data.get('usd_price') is None or market_data.get('jpy_price') is None:
        print(f"エラー: '{coin_name}' の価格情報を取得できませんでした", file=sys.stderr)
        sys.exit(1)
    
    # APIから取得した通貨名とシンボルを使用
    display_name = market_data.get('name', '')
    display_symbol = market_data.get('symbol', coin_name.upper())
    
    # 通貨名と価格表示
    if display_name:
        print(f"=== {display_name} ({display_symbol}) Price Data ===")
    else:
        print(f"=== {display_symbol} Price Data ===")
    print(format_price(market_data['usd_price'], 'USD'))
    print(format_price(market_data['jpy_price'], 'JPY'))
    
    # 市場データ表示
    print()
    if display_name:
        print(f"=== {display_name} ({display_symbol}) Market Data ===")
    else:
        print(f"=== {display_symbol} Market Data ===")
    
    # Market Cap
    if market_data.get('market_cap_usd'):
        print(f"Market Cap (USD): ${format_large_number(market_data['market_cap_usd'])}")
    if market_data.get('market_cap_jpy'):
        print(f"Market Cap (JPY): ¥{format_large_number(market_data['market_cap_jpy'])}")
    
    # Fully Diluted Valuation
    if market_data.get('fully_diluted_valuation_usd'):
        print(f"Fully Diluted Valuation (USD): ${format_large_number(market_data['fully_diluted_valuation_usd'])}")
    if market_data.get('fully_diluted_valuation_jpy'):
        print(f"Fully Diluted Valuation (JPY): ¥{format_large_number(market_data['fully_diluted_valuation_jpy'])}")
    
    # 24 Hour Trading Volume
    if market_data.get('total_volume_24h_usd'):
        print(f"24 Hour Trading Vol (USD): ${format_large_number(market_data['total_volume_24h_usd'])}")
    if market_data.get('total_volume_24h_jpy'):
        print(f"24 Hour Trading Vol (JPY): ¥{format_large_number(market_data['total_volume_24h_jpy'])}")
    
    # Supply
    print()
    if display_name:
        print(f"=== {display_name} ({display_symbol}) Supply ===")
    else:
        print(f"=== {display_symbol} Supply ===")
    if market_data.get('circulating_supply') is not None:
        print(f"Circulating Supply: {format_supply(market_data['circulating_supply'])} {display_symbol}")
    if market_data.get('total_supply') is not None:
        print(f"Total Supply: {format_supply(market_data['total_supply'])} {display_symbol}")
    if market_data.get('max_supply') is not None:
        print(f"Max Supply: {format_supply(market_data['max_supply'])} {display_symbol}")


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

