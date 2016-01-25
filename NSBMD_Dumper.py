# coding:utf-8

"""
by exe
"""

import os
import io
import re
import sys
import binascii
import struct

# 文字列データから指定されたオフセットのバイナリ値を読み出す
def readBin(data, offset):
    bin = struct.unpack('c', data[offset])
    return bin[0]

# 指定した桁数に0埋め
def zeroPadd(string, num):
    return "{0:0>{N}}".format(string, N=num)

# 0x 0bなどを除いた部分を返す
def rmPre(num):
    return num[2:]

# 16進数を0bなしの2進数に変換
def hex2bin(h):
    d = int(h, 16)  #16進数を10進数に変換
    b = bin(d)      #10進数を2進数に変換
    b = rmPre(b)    #0bを除く
    return b

# ASCIIを2進数に変換
def ascii2bin(a):
    h = binascii.hexlify(a)
    b = hex2bin(h)
    b = zeroPadd(b, len(a) * 8) # 1文字8bit
    return b

# 引数が足りないとき
if len(sys.argv) < 2:
    print "Usage: >python NSBMD_Dumper.py file"
    quit()

file = sys.argv[1]  # 1つ目の引数をファイル名とする

# withを抜けると自動でファイルがクローズされる
with open(file, 'rb') as romFile:
    data = romFile.read()   # ファイルを文字列として読み込む

    fileName = os.path.basename(file)   # ファイルの名前をパスから切り出し
    path, ext = os.path.splitext(fileName)  # ベースネームと拡張子を取得
    if os.path.exists(path) != 1:
        os.mkdir(path)  # ベースネームと同じ名前のフォルダを作成
        os.mkdir(path + "\\nsbmd")  # モデル用フォルダ
        os.mkdir(path + "\\nsbtx")  # テクスチャ用フォルダ
    else:
        print "Directory already exists"

    find = re.finditer("BMD0|BTX0", data)    # 文字列BMD0,BTX0を検索
    for match in find:
        matchAddr = match.start()   # BMD0の開始位置
        print match.group()
        #print hex(matchAddr)

        output = "" # 出力データ格納用

        compForm = readBin(data, matchAddr - 5) # 圧縮形式を示すデータは5バイト前

        if compForm == str('\x10'): # LZ77 0x10
            print "LZ77(0x10) compression"
            uncompSize = struct.unpack('l', data[matchAddr - 4 : matchAddr])
            uncompSize = uncompSize[0]
            print "Uncompressed Size: " + str(uncompSize) + " Bytes"

            readPos = matchAddr - 1 # Start
            writePos = 0

            while len(output) < uncompSize:
                #print len(output)
                currentChar = readBin(data, readPos)
                #print binascii.hexlify(currentChar)
                blockHeader = ascii2bin(currentChar)    # ブロックヘッダを2進数で読み込み
                for i in range(8):  # 8ブロックで1セット
                    # 非圧縮ブロックなら
                    if blockHeader[i] == str(0):
                        readPos += 1
                        if readPos >= len(data):    # ここ適当
                            break
                        currentChar = readBin(data, readPos)
                        output += currentChar
                        writePos += 1
                    # 圧縮ブロックなら
                    else:
                        readPos += 2
                        blockData = data[readPos-1:readPos+1]   # 2バイトをブロック情報として読み込み
                        blockData = ascii2bin(blockData)    # ブロック情報を2進数文字列に変換
                        #print "Block Data: " + blockData
                        offs = int(blockData[4:16],2) + 1
                        #print "Backwards Offset: " + str(offs) + " bytes"
                        leng = int(blockData[0:4],2) + 3
                        #print "Copy Length: " + str(leng) + " bytes"
                        currentChar = output[writePos - offs : writePos - offs + leng]
                        if len(currentChar) < leng: # ここで引っかかった
                            #print "Block Data: " + blockData
                            #print "Backwards Offset: " + str(offs) + " bytes"
                            #print "Copy Length: " + str(leng) + " bytes"
                            # 存在する範囲を超えてコピーするときは直前のパターンを繰り返すと思われる
                            #currentChar = "{0:{s}<{N}}".format(currentChar, s=currentChar[0], N = leng)
                            currentChar = currentChar * leng # ここ適当
                            currentChar = currentChar[0:leng]
                            #print binascii.hexlify(currentChar)
                        #print currentChar
                        #print binascii.hexlify(currentChar)
                        output += currentChar
                        writePos += leng
                readPos += 1

                # 何か差異が生じた時はそのアドレス周辺まで生成して検証
                """
                if len(output) > int("0x6CC6",16):
                    break
                """


            output = output[0:uncompSize]   # 必要な部分だけ切り出し
            #print binascii.hexlify(output).upper()
            #print output
            #print len(output)

        elif compForm[0] == str('\x11'):
            print "LZ77(0x11) compression"
            uncompSize = struct.unpack('l', data[matchAddr -4 : matchAddr])
            uncompSize = uncompSize[0]
            print "Uncompressed Size: " + str(uncompSize) + " Bytes"

        # 非圧縮なら
        else:
            print "not compressed"
            fileSize = struct.unpack('l', data[matchAddr + 8 : matchAddr + 12])
            fileSize = fileSize[0]
            # ファイルサイズが0以下だったりLZ77であつかえるサイズ以上ならスキップ
            if fileSize < 0 or fileSize > int("FFFFFF",16):
                continue
            output = data[matchAddr:matchAddr + fileSize]

        """
        出力処理
        """
        # nsbmdファイルなら
        if match.group() == "BMD0":
            ext = "nsbmd"
            # セクション数によって名前の位置がずれる
            if output[14] == str('\x01'):
                outName = output[52:62].translate(None, str('\x00'))
            else:
                outName = output[56:66].translate(None, str('\x00'))

        # nsbtxファイルなら
        elif match.group() == "BTX0":
            ext = "nsbtx"
            # 名前が格納されているブロックの先頭アドレスを計算する
            # メインヘッダは共通で 80 Bytes
            blockSize = struct.unpack('h',output[86:88])    # 謎のブロックのサイズ
            blockSize = blockSize[0]
            infoSize = struct.unpack('h',output[80+blockSize+2:80+blockSize+4]) # 情報ブロックのサイズ
            infoSize = infoSize[0]
            outName = output[80 + blockSize + infoSize:80 + blockSize+ infoSize + 16].translate(None, str('\x00'))
        else:
            ext = "unknown"

        with open(path + "\\" + ext + "\\" + outName + "." + ext, "wb") as out:
            print outName + "." + ext + "\n"
            out.write(output)
            #print readPos

        #break   # 1モデルだけ出力
