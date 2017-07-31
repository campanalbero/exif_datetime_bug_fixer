#!/usr/bin/python3
import datetime
import glob
import re
import sys

''' overwrite jpg-exif on current directory '''


def utf2datetime(unnormalized):

    ''' 2017:07:21 24:10:20\0 to datetime'''

    dt = re.split('[: \0]', unnormalized)
    base = datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]))
    delta = datetime.timedelta(hours=int(dt[3]), minutes=int(dt[4]), seconds=int(dt[5]))
    twenty_four = datetime.timedelta(hours=24)
    # bugfix for Nexus 5
    if delta > twenty_four:
        return base + delta - twenty_four
    else:
        return base + delta


#tag 2byte
#type 2byte
#count 4byte
#offset 4byte
def find(val, mark):
    # SOI(2bytes) + APP1(2bytes) + LENGTH(2bytes) + 'Exif'(4bytes) + ????(2bytes)
    FIX_OFFSET = 12
    pos = val.index(mark)
    offset = int.from_bytes(val[pos+8:pos+12], 'big') + FIX_OFFSET
    # TODO type * count
    count = int.from_bytes(val[pos+4:pos+8], 'big')
    return (val[offset:offset+count], offset)


def load_header(path):
    try:
        jpg = open(path, 'rb')
        # get header length
        jpg.seek(4)
        header_length = int.from_bytes(jpg.read(2), 'big') + 4
        # load header
        jpg.seek(0)
        header = jpg.read(header_length)
        return header
    finally:
        jpg.close()


def update(path):
    # DateTimeOriginal, DateTimeDigitized, DateTime
    marks = [bytes([0x90, 0x03]), bytes([0x90, 0x04]), bytes([0x01, 0x32])]
    header = load_header(path)
    try:
        output = open(path, 'r+b')
        for mk in marks:
            val, pos = find(header, mk)
            dt = utf2datetime(val.decode('utf-8'))
            raw = bytes(dt.strftime('%Y:%m:%d %H:%M:%S'), 'utf-8')
            output.seek(pos)
            output.write(raw)
    finally:
        output.close()


list= glob.glob("./*.jpg")
for item in list:
    update(item)

