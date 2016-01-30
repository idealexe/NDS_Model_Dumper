# coding:utf-8

import sys
import os
import struct

# 引数が足りないとき
if len(sys.argv) < 3:
    print "Usage: >python BMD+BTX.py file.nsbmd file.nsbtx"
    quit()

bmdFileName = sys.argv[1]  # 1つ目の引数をBMDファイル名とする
btxFileName = sys.argv[2]  # 2つ目の引数をBTXファイル名とする

fileName = os.path.basename(bmdFileName)   # ファイルの名前をパスから切り出し
path, ext = os.path.splitext(fileName)  # ベースネームと拡張子を取得
outDataName = path + "bonded" + ext

with open(bmdFileName, 'rb') as bmdFile:
    with open(btxFileName, 'rb') as btxFile:
        bmdData = bmdFile.read()
        btxData = btxFile.read()

        bmdFileSize = struct.unpack('l', bmdData[0x8 : 0x8 + 4])
        bmdFileSize = bmdFileSize[0]
        bmdSectionSize = bmdFileSize + 4

        btxFileSize = struct.unpack('l', btxData[0x8 : 0x8 +4])
        btxFileSize = btxFileSize[0]
        btxSectionSize = btxFileSize - 0x14

        outFileSize = bmdSectionSize + btxSectionSize

        # pythonは作成後の文字列を書き換えることはできないので切り出す
        bmdData = bmdData[0:0x0 + 8] + struct.pack('l', outFileSize) + '1000020018000000'.decode('hex') + struct.pack('l',bmdSectionSize) + bmdData[0x14:bmdFileSize]
        btxData = btxData[0x14 : btxFileSize]

        outData = bmdData + btxData
        
        with open(outDataName, "wb") as out:
            out.write(outData)
