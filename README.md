# coingecko

## Python 3.12.8の構築

```
┌──(stardust✨stardust)-[~/coingecko]
└─$ sudo apt-get update && sudo apt-get install -y libsqlite3-dev liblzma-dev libbz2-dev libreadline-dev libssl-dev zlib1g-dev libffi-dev
┌──(stardust✨stardust)-[~/coingecko]
└─$ pyenv install 3.12.8
pyenv: /home/stardust/.anyenv/envs/pyenv/versions/3.12.8 already exists
continue with installation? (y/N) y
Downloading Python-3.12.8.tar.xz...
-> https://www.python.org/ftp/python/3.12.8/Python-3.12.8.tar.xz
Installing Python-3.12.8...
Installed Python-3.12.8 to /home/stardust/.anyenv/envs/pyenv/versions/3.12.8
┌──(stardust✨stardust)-[~/coingecko]
└─$ pyenv local 3.12.8

┌──(stardust✨stardust)-[~/coingecko]
└─$ exec $SHEL -l

┌──(stardust✨stardust)-[~/coingecko]
└─$ python -V
Python 3.12.8

┌──(stardust✨stardust)-[~/coingecko]
└─$ python -m venv venv

┌──(stardust✨stardust)-[~/coingecko]
└─$ source venv/bin/activate

┌──(venv)(stardust✨stardust)-[~/coingecko]
└─$ python -V
Python 3.12.8
```

## 機能要件

coingecko.pyはPython 3.12.8で動作するcoingecko APIを使用して暗号通貨関連の便利な機能を提供するツールです。

## 使用例

### ETHの価格をする

```
python coingecko.py ETH 
1000,USDC
5000,00JPY
```

### 1ETHのドルと円の通貨換算を行いたい

```
python coingecko.py 100JPY ETH
0.001ETH
```

```
python coingecko.py 100JPY USDC
50USDC
```

## ライブラリのインストール

```
┌──(venv)(stardust✨stardust)-[~/coingecko]
└─$ pip install -r requirements.txt
```

## Usage

```
┌──(venv)(stardust✨stardust)-[~/coingecko]
└─$ python coingecko.py 
使用方法:
  価格表示: python coingecko.py <暗号通貨名>
  通貨換算: python coingecko.py <金額><通貨> <暗号通貨名>

例:
  python coingecko.py ETH
  python coingecko.py 100JPY ETH
  python coingecko.py 100JPY USDC
```

 * 通貨情報の表示

```
┌──(venv)(stardust✨stardust)-[~/coingecko]
└─$ python coingecko.py loot
=== Lootcoin (LOOT) Price Data ===
0.015954USD
2.5JPY

=== Lootcoin (LOOT) Market Data ===
Market Cap (USD): $27,191.14
Market Cap (JPY): ¥4,266,585.88
Fully Diluted Valuation (USD): $27,256
Fully Diluted Valuation (JPY): ¥4,276,828
24 Hour Trading Vol (USD): $3,019.55
24 Hour Trading Vol (JPY): ¥473,660.4

=== Lootcoin (LOOT) Supply ===
Circulating Supply: 1,722,385.39 LOOT
Total Supply: 1,726,519.9 LOOT
Max Supply: 21,000,000 LOOT
```

 * 通貨換算

```
┌──(venv)(stardust✨stardust)-[~/coingecko]
└─$ python coingecko.py 1BTC JPYC
11501403.11JPYC
```

