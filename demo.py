from ctparse.CTFile import CTFileShare

def printFolder(fileDir, folderDepth, subDir=False):
    """
    文件夹信息显示
    """
    if subDir:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  |' * (folderDepth - 2)}  Dir: {fileDir[1]}"))
    else:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  ' * (folderDepth - 1)}Dir: {fileDir[1]}"))
    for fileDownloadLink in fileDir[2]:
        if isinstance(fileDownloadLink, list):
            printFolder(fileDownloadLink, folderDepth + 1, subDir=True)
        else:
            print((f"|{'  |' * folderDepth} {fileDownloadLink['name']}"
                   f"\t{fileDownloadLink['downloadLink']}"))


if __name__ == '__main__':
    link = input("CTFile Share Link: ")
    passwd = input("Password: ")
    ct = CTFileShare(link, passwd)
    getShare = ct.getShare()
    downloadLink = ct.getFileList()
    print("---- Raw ----\n")
    print("-- getShare() Raw Return --")
    print(getShare)
    print("-- getShare() Raw Return --\n")
    print("-- genDownloadLink() Raw Return --")
    print(downloadLink)
    print("-- genDownloadLink() Raw Return --\n")
    print("---- Raw ----\n")

    print("--Download Link--")
    if isinstance(downloadLink, list):
        printFolder(downloadLink, 1)
    else:
        print("File Name\tDownload Link")
        print(f"{downloadLink[1]}\t{downloadLink[2]}")
    print("--Download Link--")
