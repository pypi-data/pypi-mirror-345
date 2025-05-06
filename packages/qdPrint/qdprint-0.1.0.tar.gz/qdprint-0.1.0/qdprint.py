GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
END = '\033[0m'

GREEN_BOLD = '\033[1;92m'
BLUE_BOLD = '\033[1;94m'
YELLOW_BOLD = '\033[1;93m'
RED_BOLD = '\033[1;91m'


# 字体加粗，背景变红色背景
ERROR = '\033[1;41m'
# 字体加粗，背景变黄色背景
WARNING = '\033[1;43m'
# 字体加粗，背景变绿色背景
OK = '\033[1;42m'


def grePrint(msg: str, appd: str="")->None:
    """
    打印绿色字体
    :param msg: 要打印的消息（绿色字体）
    :param appd: 附加信息
    """
    print(GREEN + msg + END, appd)


def bluPrint(msg: str, appd: str="")->None:
    """
    打印蓝色字体
    :param msg: 要打印的消息（蓝色字体）
    :param appd: 附加信息
    """
    print(BLUE + msg + END, appd)


def yelPrint(msg: str, appd: str="")->None:
    """
    打印黄色字体
    :param msg: 要打印的消息（黄色字体）
    :param appd: 附加信息
    """
    print(YELLOW + msg + END, appd)

def redPrint(msg: str, appd: str="")->None:
    """
    打印红色字体
    :param msg: 要打印的消息（红色字体）"
    :param appd: 附加信息
    """
    print(RED + msg + END, appd)


def errPrint(msg: str, appd: str="")->None:
    """
    打印红色字体加粗背景
    :param msg: 要打印的消息（红色字体加粗背景）
    :param appd: 附加信息
    """
    print(ERROR + 'ERROR' + END, msg, '\n' + appd)


def warPrint(msg: str, appd: str="")->None:
    """
    打印黄色字体加粗背景
    :param msg: 要打印的消息（黄色字体加粗背景）
    :param appd: 附加信息
    """
    print(WARNING + 'WARNING' + END, msg, '\n' + appd)


def okPrint(msg: str, appd: str="")->None:
    """
    打印绿色字体加粗背景
    :param msg: 要打印的消息（绿色字体加粗背景）
    :param appd: 附加信息
    """
    print(OK + 'OK' + END, msg, '\n' + appd)


def redTagPrint(tag: str, msg: str, appd: str="")->None:
    """
    打印红色字体加粗背景
    :param tag: 标签
    :param msg: 要打印的消息（红色字体加粗背景）
    :param appd: 附加信息
    """
    print(ERROR + tag + END, msg, '\n' + appd)


def yelTagPrint(tag: str, msg: str, appd: str="")->None:
    """
    打印黄色字体加粗背景
    :param tag: 标签
    :param msg: 要打印的消息（黄色字体加粗背景）
    :param appd: 附加信息
    """
    print(WARNING + tag + END, msg, '\n' + appd)


def greTagPrint(tag: str, msg: str, appd: str="")->None:
    """
    打印绿色字体加粗背景
    :param tag: 标签
    :param msg: 要打印的消息（绿色字体加粗背景）
    :param appd: 附加信息
    """
    print(OK + tag + END, msg, '\n' + appd)


def greBPrint(msg: str, appd: str="")->None:
    """
    打印绿色字体加粗
    :param msg: 要打印的消息（绿色字体加粗）
    :param appd: 附加信息
    """
    print(GREEN_BOLD + msg + END, appd)


def bluBPrint(msg: str, appd: str="")->None:
    """
    打印蓝色字体加粗
    :param msg: 要打印的消息（蓝色字体加粗）
    :param appd: 附加信息
    """
    print(BLUE_BOLD + msg + END, appd)


def yelBPrint(msg: str, appd: str="")->None:
    """
    打印黄色字体加粗
    :param msg: 要打印的消息（黄色字体加粗）
    :param appd: 附加信息
    """
    print(YELLOW_BOLD + msg + END, appd)


def redBPrint(msg: str, appd: str="")->None:
    """
    打印红色字体加粗
    :param msg: 要打印的消息（红色字体加粗）
    :param appd: 附加信息
    """
    print(RED_BOLD + msg + END, appd)


def main():
    print("Hello from clprint!")
    grePrint("This is text!", "This is appended text!")
    bluPrint("This is blue text!", "This is appended blue text!")
    yelPrint("This is yellow text!", "This is appended yellow text!")
    redPrint("This is red text!", "This is appended red text!")
    greBPrint("This is bold green text!", "This is appended bold green text!")
    bluBPrint("This is bold blue text!", "This is appended bold blue text!")
    yelBPrint("This is bold yellow text!", "This is appended bold yellow text!") 
    redBPrint("This is bold red text!", "This is appended bold red text!")
    errPrint("This is an error message!", "This is appended error text!")
    warPrint("This is a warning message!", "This is appended warning text!")  
    okPrint("This is an ok message!", "This is appended ok text!")
    redTagPrint("RED", "This is an error message!", "This is appended error text!")
    yelTagPrint("YELLOW", "This is a yellow message!", "This is appended yellow text!")
    greTagPrint("GREEN", "This is a green message!", "This is appended green text!")


if __name__ == "__main__":
    main()
