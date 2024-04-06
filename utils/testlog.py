def testPrint(test, type, value):
    logTypes = ['debug', 'info', 'warn', 'err']
    outColor = ['\033[3;32m', '\033[37m', '\033[33m', '\033[31m']
    outText = ['[DEBUG]', '[INFO]', '[WARNING]', '[ERROR]']
    logType = logTypes.index(type)
    minType = logTypes.index('debug')
    if logType >= minType:
        print(f"{outColor[logType]}[{test}]{outText[logType]} : {value} \033[0m")