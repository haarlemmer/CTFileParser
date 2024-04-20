from utils.logging import testPrint
import testscripts.tests as tests
import os

# ----- Test Data -----
shareUrl = "https://url21.ctfile.com/d/37740821-60674467-922bf9"
sharePass = "8854"

expectedFolder = ['Folder', 'TestPatterns', [['Folder', 'Test1', [['File', 'dq9scv7WHzzHsxYRgzWwgmT5fbrFGs6p.txt'], ['File', '3fX769AEmT6n96RjDPWpJHWv5Ra5brZe.txt'], ['File', '4AXqNya2QHkBbHHY8eNVdUh2C56FVKJ2.txt']]], ['Folder', 'Test2', [['File', 'XWewZ4d5b3DDaMVsLEy7WZxQFnC96XdQ.txt']]], ['Folder', 'Test3', []], ['File', 'zVhRpmCeatLJVdEjCEDnWVCzzk6kvcqK.txt']]]

expectedFileContents = {
    '3fX769AEmT6n96RjDPWpJHWv5Ra5brZe.txt': 'wNukjdFrkmRmXW9csnZyEPEVpAunQgw5',
    '4AXqNya2QHkBbHHY8eNVdUh2C56FVKJ2.txt': 'Lf9WKaX48swUArtrNJPKgp4dAUWqS47r',
    'dq9scv7WHzzHsxYRgzWwgmT5fbrFGs6p.txt': 'q5UkfkjJTAYSRzwnMcrzuzjLdFjA4vwr',
    'XWewZ4d5b3DDaMVsLEy7WZxQFnC96XdQ.txt': '5x9Se5AF5HvmSDD8w4ApK9VPQuWqC22b',
    'zVhRpmCeatLJVdEjCEDnWVCzzk6kvcqK.txt': 'P9BRnug7g66j7ZSadwS6pMhwREUuC4yk',
}
try:
    os.mkdir('TestData')
except FileExistsError:
    pass

testPrint('TestMain', 'info', 'Starting ParseTest...')
fileList = tests.parseTest(shareUrl, sharePass, expectedFolder)
testPrint('TestMain', 'info', '')
testPrint('TestMain', 'info', 'ParseTest Complete!')

testPrint('TestMain', 'info', 'Starting DownloadTest...')
tests.downloadTest(fileList)
testPrint('TestMain', 'info', 'DownloadTest Complete!')

testPrint('TestMain', 'info', 'Starting ContentTest...')
tests.contentTest(expectedFileContents)
testPrint('TestMain', 'info', 'ContentTest Complete!')

testPrint('TestMain', 'info', 'Test Complete!')

os.system('rm -rf TestData/')