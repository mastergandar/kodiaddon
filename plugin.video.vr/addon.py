from __future__ import print_function
import sys
try:
    from urllib.parse import parse_qs, urlencode
    from urllib.request import urlopen
except ImportError:
    # Python 2 (Kodi 18 and older)
    from urlparse import parse_qs
    from urllib import urlencode
    from urllib2 import urlopen
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs
import subprocess
#import resolveurl
import re
from bs4 import BeautifulSoup


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = parse_qs(sys.argv[2][1:])

_addon = xbmcaddon.Addon()
_icon = _addon.getAddonInfo('icon')



def build_url(query):
    return base_url + '?' + urlencode(query)

# def resolve_url(url):
#     duration=7500   #in milliseconds
#     message = "Cannot Play URL"
#     stream_url = resolveurl.HostedMediaFile(url=url).resolve()
#     # If urlresolver returns false then the video url was not resolved.
#     if not stream_url:
#         dialog = xbmcgui.Dialog()
#         dialog.notification("URL Resolver Error", message, xbmcgui.NOTIFICATION_INFO, duration)
#         return False
#     else:        
#         return stream_url    

def play_video(path):
    """
    Play a video by the provided path.
    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    vid_url = path
    stream_url = vid_url #resolve_url(vid_url)
    if stream_url:
        play_item.setPath(stream_url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
##############
def parseHTML(url=''):
    #connect to a URL
    #website = urlopen('http://m.perfectgirls.net/gal/497235/Astonishing_teacher_is_always_in_the_mood_to_fuck_her_students__if_no_one_is_watching_them')
    website = urlopen(url)

    #read html code
    html = website.read()

    #use re.findall to get all the links
    #links = re.findall('"((http)s?://.*?)"', html)
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select("source")
    vdolist =[];
    for item in links:
        #print item
        #print item
        path = item.get('src')
        if not path.startswith('http'):
            path = 'http:' + path

        vdolist.append(path)

    return vdolist        
###########
def getLinks(url,selector):
    website = urlopen(url)
    #read html code
    html = website.read()

    soup = BeautifulSoup(html, 'html.parser')
    links =[]
    for link in soup.select( selector):
        #print(link)
        #print(link.get('data-preview'))
        links.append({'href': link.get('href'), 'img':link.find('img').get('src')})
    #print(links)
    return links;

def getCatLinks(url,selector):
    website = urlopen(url)
    #read html code
    html = website.read()
    soup = BeautifulSoup(html, 'html.parser')
    links =[]
    for link in soup.select( selector):
        print(link)
        #print(link.find('img').get('src'))
        links.append({'href': domainurl + link.get('href'),'title':link.text})
    #print(links)
    return links;

def download_video(url):
    folder = xbmcgui.Dialog().browse(3, 'Download to', 'files')
    if not folder:
        return
    if not folder.endswith(('/', '\\')):
        folder += '/'
    fileName = url.split('?')[0].split('/')[-1] or 'video.mp4'
    dest = folder + fileName

    progress = xbmcgui.DialogProgress()
    progress.create('Download', fileName)
    response = urlopen(url)
    total = int(response.headers.get('Content-Length') or 0)
    done = 0
    out = xbmcvfs.File(dest, 'w')
    try:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(bytearray(chunk))
            done += len(chunk)
            if total:
                progress.update(int(done * 100 / total))
            if progress.iscanceled():
                break
    finally:
        out.close()
        progress.close()

    if progress.iscanceled():
        xbmcvfs.delete(dest)
    else:
        xbmcgui.Dialog().notification('Download', 'Saved ' + fileName, _icon)

def copy2Clip(txt):
    cmd = 'echo '+txt.strip()+ ' | clip'
    return subprocess.check_call(cmd, shell=True)

# addon kicks in

mode = args.get('mode', None)
domainurl = 'https://vrporn.com/';
print('mode=')
print(mode)
if mode is None or mode[0] == 'next':
    
    argsNext = args.get('nextval', None)
    #print argsNext    
    if argsNext is not None:
       nextval = int(argsNext[0])+1
       url = 'http://m.perfectgirls.net/'+str(nextval)
    else:
       nextval = 1
       url = domainurl
    print('nextval', nextval)

    print('category data',args.get('data'))
    catUrl = args.get('data', None)
    if catUrl is not None:
        url = catUrl[0]
        inde = url.rindex('/')+1
        nextUrl = url[:inde]+ str(nextval)
        print('nextUrl',nextUrl)
    else:
        nextUrl = None    

    print('url =', url)
    vdoObjects = getLinks(url, 'ul.slides li a')
    #print(vdoObjects)

    #category menu
    urlcategory = build_url({'mode' :'category'})
    licat = xbmcgui.ListItem('Categories')
    licat.setArt({'icon': 'DefaultVideo.png'})
    licat.setInfo( type="Video", infoLabels={ "Title": 'Categories' } )
    licat.setProperty('isFolder','true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlcategory, listitem=licat,isFolder=True)

    for page in vdoObjects:
        #url = build_url({'mode' :'page', 'data' : page.get('href')})
        #print('href=',page.get('href'))
        url = build_url({'mode' :'page', 'data' : page.get('href')})
        title = page.get('href').split('/')[-2]
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': page.get('img'), 'thumb': page.get('img')})
        li.setInfo( type="Video", infoLabels={ "Title": title } )
        li.setProperty('isFolder','true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li,isFolder=True)

    
    urlnext = build_url({'mode' :'next', 'nextval' : nextval, 'data':nextUrl})
    
    li = xbmcgui.ListItem('Next List')
    li.setArt({'icon': 'DefaultVideo.png'})
    li.setInfo( type="Video", infoLabels={ "Title": title } )
    li.setProperty('isFolder','true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlnext, listitem=li,isFolder=True)
    

    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'page':
    print('inside page')
    video_play_url = args['data'][0] #"http://m.perfectgirls.net/gal/497235/Astonishing_teacher_is_always_in_the_mood_to_fuck_her_students__if_no_one_is_watching_them"
    print('video_play_url=',video_play_url);
    vlist = parseHTML(video_play_url)
    print (vlist)
    for vdourl in vlist:
        url1 = build_url({'mode' :'play', 'playlink' : vdourl})
        fileName = vdourl.split('/')[-1]
        li1 = xbmcgui.ListItem(fileName)
        li1.setArt({'icon': 'DefaultVideo.png'})
        li1.setProperty('IsPlayable' , 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url1, listitem=li1)

        url2 = build_url({'mode' :'download', 'link' : vdourl})
        li2 = xbmcgui.ListItem('Download ')
        li2.setArt({'icon': 'DefaultVideo.png'})
        li2.setProperty('isFolder' , 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url2, listitem=li2)

        url3 = build_url({'mode' :'copy', 'link' : vdourl})
        li3 = xbmcgui.ListItem('Copy link ')
        li3.setArt({'icon': 'DefaultVideo.png'})
        li3.setProperty('isFolder' , 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url3, listitem=li3)

    


    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode[0] == 'category':
    print('category')
    catLinks = getCatLinks(domainurl+'/categories', 'a.category__item_link') 
    print(catLinks)
    
    for link in catLinks:
        urlcatlink = build_url({'mode' :'next', 'data' : link.get('href')+'/1','nextval':1})
        title = link.get('title')
        li = xbmcgui.ListItem(title)
        li.setArt({'icon': 'DefaultVideo.png'})
        li.setInfo( type="Video", infoLabels={ "Title": title } )
        li.setProperty('isFolder','true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=urlcatlink, listitem=li,isFolder=True)
    

    xbmcplugin.endOfDirectory(addon_handle)

   


elif mode[0] == 'play':
    final_link = args['playlink'][0]
    play_video(final_link)

elif mode[0] == 'download':
    link = args['link'][0]
    download_video(link)

elif mode[0] == 'copy':
    link = args['link'][0]
    copy2Clip(link)





