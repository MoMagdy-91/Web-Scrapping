import sys
import os
import requests
import time
import socket
from pathlib import Path
from bs4 import BeautifulSoup
from htmldocx import HtmlToDocx

def createPages(cat,Targetlink):
    dirTypes=['Experts','Indicators','Scripts','Libraries']
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    if not os.path.exists('Pages'):
        os.makedirs('Pages')
    if not os.path.exists('{}/Pages/{}'.format(dir_path,cat)):
        createDir('{}/Pages'.format(dir_path),cat)
    #Path('/Pages/{}'.format(cat)).mkdir(parents=True, exist_ok=True) 
    for t in range(len(dirTypes)):
        parentPath='{}/Pages/{}'.format(dir_path,cat)
        path = createDir(parentPath,dirTypes[t])
        lnk=Targetlink+'/'+dirTypes[t].lower()
        getContent(lnk,path)

def checkPathLenght(path):
    info = (path[:200]) if len(path) > 200 else path
    return info
    
def createDir(parentPath,dirName):
    os.chdir(parentPath)
    if (os.path.isdir(parentPath+'/'+ dirName.strip()))==False:
        os.mkdir(dirName.strip())
    currentPath = parentPath+'/'+ dirName
    currentPath = checkPathLenght(currentPath)
    return currentPath

def download_url(url, save_path):
    req  = requests.get(url, stream=True)
    filename = url.split('/')[-1]
    with open(save_path+'/'+filename,'wb') as output_file:
        for chunk in req.iter_content(chunk_size=1025):
            if chunk:
                output_file.write(chunk)

def internet_on(host="8.8.8.8", port=53, timeout=5):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print('Sorry internet not connected .. Please Wait')
        return False

def createPageData(PageTitle,PageLink,PageContent,CurPath,fileUrl,mqFiles):
    os.chdir(CurPath)
    dirName=PageTitle
    dirName = checkPathLenght(CurPath+'/'+dirName).split('/')[-1]
    id=PageLink.split('/')[-1]
    print(dirName+' '+id)
    if(os.path.isdir(CurPath+'/'+dirName)):
        dirName=dirName+'-'+id
        if not(os.path.isdir(CurPath+'/'+dirName)):
            os.mkdir(dirName)
    else:
        os.mkdir(dirName)
    try:
        #check internet connection
        while(True):
            if(internet_on()):
                if fileUrl != '':
                    download_url(fileUrl, CurPath+'/'+dirName)
                #for mqFile in mqFiles:
                if mqFiles != '':
                    download_url(mqFiles, CurPath+'/'+dirName)
                HtmlContent = "<a href='{}'>{}</a></br><h1>{}</h1></br>".format(PageLink,PageLink,PageTitle)+str(PageContent)
                htmlFile=CurPath+'/'+dirName+'/'+PageTitle+'.html'
                docxFile=CurPath+'/'+dirName+'/'+PageTitle
                if not(os.path.exists(htmlFile)):
                    with open(htmlFile,"w", encoding='utf8')as file:
                        file.write(HtmlContent)
                        new_parser = HtmlToDocx()
                        new_parser.parse_html_file(htmlFile, docxFile)
                break
            else:
                time.sleep(5)
                continue
    except Exception as e:
        print('Failed to create the file: '+ str(e))

def getContent(lnk,Cpath):
    page_num = 1
    titles =[]
    links =[]
    bad_chars = [';',':','!','*','"','&','|','?','!','.']
    while True:
        try:
            result = requests.get("{}//page{}".format(lnk,page_num))
            src = result.content
            soup = BeautifulSoup(src,"lxml")
            pages = soup.find("span",{"class":"paginatorEx"}).find_all('a')
            pages_limit = int(pages[-1].text)
            if page_num > pages_limit:
                break
            topics = soup.find_all("div",{"class":"code-tile"})
            for i in range(len(topics)):
                title = topics[i].find("a").attrs['title']
                title = ''.join((filter(lambda i: i not in bad_chars, title)))
                titles.append(str(title))
                links.append('https://www.mql5.com'+topics[i].find("a").attrs['href'])
            page_num += 1
        except:
            print("error")
            break
    for link in links:
        result = requests.get(link)
        src = result.content
        soup = BeautifulSoup(src,"lxml")
        content = soup.find("div",{"id":"publication_content"})
        if (soup.find("span",{"id":"codebaseDownloadZip"}).find("a")):
            fileUrl = 'https://www.mql5.com'+soup.find("span",{"id":"codebaseDownloadZip"}).find("a").attrs['href']
        else:
            fileUrl =''
        if (soup.find("div",{"id":"codeAttachments"}).find("a")):
            mqFiles = 'https://www.mql5.com'+soup.find("div",{"id":"codeAttachments"}).find("a").attrs['href']
        else:
            mqFiles = ''
        title = titles[links.index(link)].replace('/','-')
        time.sleep(5)
        createPageData(title,link,content,Cpath,fileUrl,mqFiles)

def main():
    catagory={"mt4":"MetaTrader 4","mt5":"MetaTrader 5"}
    for i in catagory:
        superLink="https://www.mql5.com/en/code/{}".format(i)
        createPages(catagory[i],superLink)

if __name__ == "__main__":
	main()
