from ctparse.CTFile import CTFileShare
from utils.logging import testPrint
from utils.models import CTFile
import os, time, urllib.request

# ParseTest Start

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
    
# ParseTest End

# DownloadTest Start

def downloadTest(fileList):
    try:
        os.mkdir('TestData')
    except FileExistsError:
        pass
    links = getDownloadLinkForFolder(fileList)
    testPrint('DownloadTest', 'debug', f'Links: {links}')
    for fileName in list(links.keys()):
        testPrint('DownloadTest', 'info', f'Downloading {fileName} to TestData/{fileName}')
        urllib.request.urlretrieve(links[fileName], f'TestData/{fileName}')


def getDownloadLinkForFolder(fileList):
    testPrint('DownloadTest', 'debug', f'Get folder: {fileList}')
    links = {}
    for file in fileList[2]:
        if type(file) == CTFile:
            fileName = file.name
            testPrint('DownloadTest', 'info', f'Get download link: {fileName}')
            link = file.genDownloadLink()
            if link == None:   # 出问题了就消停会儿再试一次
                time.sleep(1)
                link = file.genDownloadLink()
            links[fileName] = link.fileDownloadLink
            testPrint('DownloadTest', 'info', f'Download Link: {links[fileName]}')
        elif type(file) == list:
            nxtLinks = getDownloadLinkForFolder(file)
            for key in list(nxtLinks.keys()):
                links[key] = nxtLinks[key]
        time.sleep(0.25)
    return links

# DownloadTest End

# ContentTest Start
def contentTest(expectedContents):
    for fileName in list(expectedContents.keys()):
        testPrint('ContentTest', 'info', f'Check file: {fileName}')
        f = open(f'TestData/{fileName}')
        content = f.read()
        if content[-1:] == '\n':
            content = content[:-1]    # 检测到结尾的换行符就去掉，避免干扰
        if content == expectedContents[fileName]:
            testPrint('ContentTest', 'info', f'Check PASS: {expectedContents[fileName]} -> {content}')
        else:
            testPrint('ContentTest', 'err', f'Check FAIL: {expectedContents[fileName]} -> {content}')
            raise ValueError
            
