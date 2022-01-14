import os, sys
import binascii

# 更改当前工作目录
path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)

KEYS = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]


def char2lattice_asc16(text, rect_list):
    if ord(text) > 127:
        print("ASCII 不支持的字符：" + text)
        return
    utf8 = text.encode("utf8")
    # 将二进制编码数据转化为十六进制数据
    hex_str = binascii.b2a_hex(utf8)
    # 将数据按unicode转化为字符串
    result = str(hex_str, encoding="utf-8")
    offset = eval("0x" + result[:2] + "* 0x10")
    font_rect = None

    # 读取ASC16文件
    with open("ASC16", "rb") as f:
        # 找到目标的偏移位置
        f.seek(offset)
        # 从该字模数据中读取16字节数据
        font_rect = f.read(16)

    # font_rect的长度是16，此处相当于for k in range(16)
    for k in range(len(font_rect)):
        # 每行数据
        row_list = rect_list[k]
        binStr = bin(font_rect[k])[2:].zfill(8)
        for i in range(8):
            row_list.append(int(binStr[i]))

    # 导出16*25数据
    with open("./lcd_data", "w+", encoding="utf-8") as file:
        try:
            output = []
            for row in rect_list:
                for i in range(10):
                    output.append(0)
                for col in row:
                    if col:
                        output.append(1)
                    else:
                        output.append(0)
                for i in range(7):
                    output.append(0)
            for i in output:
                file.write(str(i) + "\n")
        except:
            file.close()


def char2lattice_hzk16(text, rect_list):
    # 获取中文的gb2312编码，一个汉字是由2个字节编码组成
    try:
        gb2312 = text.encode("gb2312")
    except UnicodeEncodeError:
        print("GB2312 不支持的字符：" + text)
        return
    # 将二进制编码数据转化为十六进制数据
    hex_str = binascii.b2a_hex(gb2312)
    # 将数据按unicode转化为字符串
    result = str(hex_str, encoding="utf-8")

    # 前两位对应汉字的第一个字节：区码，每一区记录94个字符
    area = eval("0x" + result[:2]) - 0xA0
    # 后两位对应汉字的第二个字节：位码，是汉字在其区的位置
    index = eval("0x" + result[2:]) - 0xA0
    # 汉字在HZK16中的绝对偏移位置，最后乘32是因为字库中的每个汉字字模都需要32字节
    offset = (94 * (area - 1) + (index - 1)) * 32

    font_rect = None

    # 读取HZK16汉字库文件
    with open("HZK16", "rb") as f:
        # 找到目标汉字的偏移位置
        f.seek(offset)
        # 从该字模数据中读取32字节数据
        font_rect = f.read(32)

    # font_rect的长度是32，此处相当于for k in range(16)
    for k in range(len(font_rect) // 2):
        # 每行数据
        row_list = rect_list[k]
        for j in range(2):
            for i in range(8):
                asc = font_rect[k * 2 + j]
                # 此处&为Python中的按位与运算符
                flag = asc & KEYS[i]
                # 数据规则获取字模中数据添加到16行每行中16个位置处每个位置
                row_list.append(flag)

    # 导出16*25数据
    with open("./lcd_data", "w+", encoding="utf-8") as file:
        try:
            output = []
            for row in rect_list:
                for i in range(6):
                    output.append(0)
                for col in row:
                    if col:
                        output.append(1)
                    else:
                        output.append(0)
                for i in range(3):
                    output.append(0)
            for i in output:
                file.write(str(i) + "\n")
        except:
            file.close()


# 根据获取到的点阵信息，打印到控制台
def printLattice(rect_list, line, background):
    for row in rect_list:
        for i in row:
            if i:
                # 前景字符（即用来表示汉字笔画的输出字符）
                print(line, end=" ")
            else:

                # 背景字符（即用来表示背景的输出字符）
                print(background, end=" ")
        print()


def main(inpt):
    if inpt == "":
        inpt = input("写你所想：")
    lineSign = "■"
    # lineSign = "0"
    backgroundSign = "○"
    # backgroundSign = "."
    # 初始化16行的点阵位置
    rect_list = [] * 16
    for i in range(16):
        rect_list.append([] * 16)
    for ch in inpt:
        if "\u4e00" <= ch <= "\u9fff":
            char2lattice_hzk16(ch, rect_list)
        else:
            char2lattice_asc16(ch, rect_list)

    printLattice(rect_list, lineSign, backgroundSign)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("写你所想：" + sys.argv[1])
        main(sys.argv[1])
    else:
        main("")
    os.system("pause")
