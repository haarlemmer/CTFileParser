from ctparse.CTFile import CTFileShare
from utils.logging import testPrint
from utils.models import CTFile


def parseTest(link, passwd, expectedFolder):
    ct = CTFileShare(link, passwd)
    getShare = ct.getShare()
    fileList = ct.getFileList()
    testPrint('ParseTest', 'debug', f'fileList: {fileList}')
    inFolder = proccessRetFolder(fileList)
    chkFolder(inFolder,expectedFolder)
    return fileList


def chkFolder(inFolder, expectedFolder):
    if expectedFolder[1] == inFolder[1]:
        testPrint('ParseTest', 'info', f'Folder match: {expectedFolder[1]} -> {inFolder[1]}')
        for item in expectedFolder[2]:
            if item[0] == 'Folder':
                testPrint('ParseTest', 'debug', '')
                testPrint('ParseTest', 'debug', f'Proccess next folder: {item}')
                nxtIndex = inFolder[2].index(item)
                testPrint('ParseTest', 'debug', f'Next folder index on inFolder: {nxtIndex}')
                chkFolder(inFolder[2][nxtIndex], item)
            elif item[0] == 'File':
                fileIn = inFolder[2][inFolder[2].index(item)]
                testPrint('ParseTest', 'debug', f'File match: {item} -> {fileIn}')
    else:
        testPrint('ParseTest', 'err', f'Folder missmatch: {expectedFolder[1]}')
        raise ValueError

def proccessRetFolder(retFolder):
    items = []
    for retItem in retFolder[2]:
        if type(retItem) == CTFile: 
            items.append(['File', retItem['name']])
        elif type(retItem) == list:
            if retItem[0] == 'Folder':
                items.append(proccessRetFolder(retItem))
    return ['Folder', retFolder[1], items]
    

