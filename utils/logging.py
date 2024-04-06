# ----- Log Config -----

# Configures any ontputs except outputs from tests
EnableLogOutput_logPrint = True
LogLevel_logPrint = 'debug'

# Configures outputs from tests
LogLevel_testPrint = 'debug'


def logPrint(type, value):
    if not EnableLogOutput_logPrint:
        return
    logTypes = ['debug', 'info', 'warn', 'err']
    outText = ['\033[3;32m[DEBUG]', '\033[37m[INFO]', '\033[33m[WARNING]', '\033[31mERROR']
    logType = logTypes.index(type)
    minType = logTypes.index(LogLevel_logPrint)
    if logType >= minType:
        print(f"{outText[logType]} {value} \033[0m")

def testPrint(test, type, value):
    logTypes = ['debug', 'info', 'warn', 'err']
    outColor = ['\033[3;32m', '\033[37m', '\033[33m', '\033[31m']
    outText = ['[DEBUG]', '[INFO]', '[WARNING]', '[ERROR]']
    logType = logTypes.index(type)
    minType = logTypes.index(LogLevel_testPrint)
    if logType >= minType:
        print(f"{outColor[logType]}[{test}]{outText[logType]} : {value} \033[0m")