# NSBMD_Dumper

## 概要
NSBMD形式の3Dモデルを抽出するプログラムです．  
無圧縮，LZ77圧縮（0x10）に対応しています．  
NSBTX形式のテクスチャも同時に抽出します．

## 使用方法
Pythonプログラムとして実行してください．  
第一引数に抽出元のファイルを与えてください．  
`>python NSBMD_Dumper.py filename`

## 参考
- lowlines 氏によるNSBMD, NSBTXファイルの構造
  - http://llref.emutalk.net/docs/?file=xml/bmd0.xml  
  - http://llref.emutalk.net/docs/?file=xml/btx0.xml  

- LZ77圧縮の資料
  - http://florian.nouwt.com/wiki/index.php/LZ77_(Compression_Format)

- NDBMD, NSBTXファイルの閲覧
  - https://github.com/Gericom/EveryFileExplorer
