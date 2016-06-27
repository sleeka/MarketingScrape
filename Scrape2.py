from urllib.request import Request, urlopen
import html

from os import listdir
import requests, sys
from requests_file import FileAdapter
##from lxml import html
import csv, pandas

SITE = '' # removed

def rscrape():
        order = ['name','type','reviews','phone','address','url','description','profile']
        files = listdir('**removed**')
        for f in files[:1]:
                s = requests.Session()
                s.mount('file://', FileAdapter())

                resp = s.get('file:///C:/Users/**removed**/Documents/**removed**/'+f)
##                r = requests.get(SITE +f,
##                                 headers={'User-Agent':'Mozilla/5.0'})
                tree = html.fromstring(resp.content)

                rev = [r[:r.find('\n')] for r in tree.xpath(
                        '//div[@class="l-small-top-space l-small-bottom-space verified-reviews"]/a[@href]/text()')]
                # indexe of reviews >= 20
                indexes = []
                for r in range(len(rev)):
                        if int(rev[r]) > 19:
                                indexes.append(r)

                # dict of contractors
                contractor = {}
                                
                contractor['name'] = [tree.xpath('//span[@itemprop="name"]/text()')[i] for i in indexes]

                c_type = tree.xpath('//h1[@class="t-header-secondary"]/text()')[0]
                contractor['type'] = c_type[:c_type.find('Com')-1] if c_type[:2]=='Wi' else c_type[:c_type.find('Cont')-1]

                contractor['reviews'] = [rev[i] for i in indexes]

                contractor['phone'] = [tree.xpath(
                        '//span[@itemprop="telephone"]/text()')[i] for i in indexes]

                contractor['address'] = [tree.xpath(
                        '//span[@itemprop="streetAddress"]/text()'
                        )[i] +', '+ tree.xpath(
                                '//span[@itemprop="addressLocality"]/text()')[i] +', '+
                                         tree.xpath('//span[@itemprop="addressRegion"]/text()'
                                                 )[i] +' '+ tree.xpath(
                                                 '//span[@itemprop="postalCode"]/text()'
                                                 )[i] for i in indexes]


                for link in [tree.xpath(
                        '//div[@class="l-small-top-space l-small-bottom-space verified-reviews"]/a/@href'
                        )[i] for i in indexes]:
                        l2 = SITE + link[:link.find('#')]
                        print(l2)

                        req = requests.get(l2,
                                           headers={'User-Agent':'Mozilla/5.0'})
                        tree2 = html.fromstring(req.text)
                        print(tree2)
                        contractor['url'] = []
                        contractor['description'] = []
                        contractor['profile'] = []

                        try:
                                contractor['url'].append(tree2.xpath('//a[@rel="nofollow"]/text()'))
                        except:
                                contractor['url'].append('')
                        
                        # Add try block if this ever doesn't exist
                        desc = tree2.xpath('//p[@class="t-heavy"]/text()')
                        print(desc)
                        contractor['description'].append(desc[0])
                        contractor['profile'].append(desc[1])
                        
                print (contractor)

                

##                        if int(reviews[:reviews.find('\n')]) > 19:
##                                contractor['reviews'] = reviews[

# Attempts to write my own scraper are silly,
#       as python-requests.org details
# Use requests in rscrape()
def scrape():
        HA_URL = SITE
        order = ['name','type','reviews','phone','addy','url','serving','profile']
        files = listdir('**removed**')
        f3 = open('USAContractors.csv','a')
##        for o in order[:-1]:
##                # COLUMN DELIMETER IS PIPE
##                f3.write(o + '|')
##        # ROW DELIMETER IS NEW LINE
##        f3.write(order[-1] + '\n')
##        f4 = open('profile_links.txt','w')
        count = 2204
        maxcount = len(files)
        for f in files[2203:]:
                print(count, " of ", maxcount)
                count+=1
                f2 = open('**removed**/'+f,'r', encoding='utf-8')
                page = f2.read()
                if "Service Unavailable" in page[:100]:
                        continue
                page = page[page.find('>',page.find('t-header-secondary'))+1:]               
##                contractor = {}
##                for o in order:
##                        contractor[o] = []
                ComCon = 'Cont'
                if page[:2]=='Wi':
                        ComCon = 'Com'
                ctype = page[: page.find( ComCon )].strip()
                # Many companies service nearby cities
                # Disregard this searched city addy; log correct address later
##                contractor['city'] = page[:page.find(',')].split(' ')[-1]
##                contractor['state'] = page[page.find('(')+1 : page.find(')')]
                if page.rfind('pagination') == -1:
                        continue
                page = page[page.find('xmd-listing-company-name') :
                                        page.rfind('pagination')]
                page = page.split('#ratings-reviews')
                for con in range(1,len(page)):
                        rev = page[con][page[con].find('>')+1: page[con].find('Verif')].strip()
                        if int(rev) > 19:
                                contractor = {}
                                # type
                                contractor['type'] = ctype
                                
                                # reviews
                                contractor['reviews'] = rev

                                # name
                                name = page[con-1].find('itemprop=\"name\"')
                                contractor['name'] = html.unescape(page[con-1][page[con-1].find(
                                        '>', name)+1 : page[con-1].find('<', name)]).replace('\ufffd','')

                                # contractor link                          
                                link = (page[con-1][page[con-1].rfind('href=\"')+6 :])
                                if HA_URL not in link:
                                        link = HA_URL + link
                                # used to collect list of 5381 links
##                                f4.write(link + '\n')
##                                continue

                                # telephone
                                phone = page[con].find('>', page[con].find('itemprop=\"telephone'))+1
                                contractor['phone'] = page[con][phone : page[con].find('<', phone)]

                                # address
                                addy = page[con].find('>', page[con].find('itemprop=\"streetAddress'))+1
                                zipcode = page[con].find('>', page[con].find('itemprop=\"postalCode\"'))+1
                                cindex = page[con].find('addressLocality')
                                city = page[con][page[con].find('>', cindex)+1 : page[con].find('<', cindex)].strip()
                                sindex = page[con].find('addressRegion')
                                state = page[con][page[con].find('>', sindex)+1 : page[con].find('<', sindex)].strip()
                                contractor['addy'] = (page[con][addy : page[con].find(
                                        '<', addy)]+ ', ' +city+ ', ' +\
                                        state+ ', '+ page[con][zipcode : page[con].find('<', zipcode)]).replace('\ufffd','')

                                # serving
                                servindex = page[con].find('serving-text')
                                if servindex == -1:
                                        contractor['serving'] = ''
                                else:
                                        contractor['serving'] = page[con][page[con].find('g', servindex+10)+2 :
                                                                  page[con].find('<', servindex+10)].strip()

                                # contractor's profile page
                                try:
                                        req = Request(link, headers={'User-Agent':'Mozilla/5.0'})
##                                while req.status_code != requests.codes.ok:
##                                        time.wait(5)
##                                        print('holdor', link)
##                                        req = Request(link, headers={'User-Agent':'Mozilla/5.0'})
                                        page2 = urlopen(req).read().decode('utf-8')
                                except:
                                        f3.close()
                                        f2.close()
                                        print(sys.exc_info())
                                        print(contractor)
                                        print(f)
                                if "The page you are looking for is no longer available." in page2:
                                        contractor['profile'] = "The page you are looking for is no longer available."
                                        contractor['url'] = ''
                                        print (f, contractor, '\n\n')
                                        for o in order[:-1]:
                                                f3.write(contractor[o]+'|')
                                        f3.write(contractor[order[-1]]+'\n')
                                        continue

                                # profile
                                profile = page2.find('<p>', page2.find('itemprop="description')) +3
                                contractor['profile'] = page2[profile : page2.find('</p>', profile)].strip().replace(
                                        '\ufffd','').replace('\r','').replace('\n', ' ').replace(
                                                '\x92',"'").replace('\x93',"'").replace('\x94',"'").replace('\x97',"'")

                                # website
                                site = page2.find('rel=\"nofollow')
                                if site != -1:
                                    contractor['url'] = page2[page2.find(\
                                            '>', site)+1 : page2.find('</a>', site)].strip()
                                else:
                                        contractor['url'] = ''
                                print (f, contractor, '\n\n')
                                
                                for o in order[:-1]:
                                        f3.write(contractor[o]+'|')
                                f3.write(contractor[order[-1]]+'\n')
        f2.close()
##        f4.close()
##        pd = pandas.DataFrame({"key": contractor.keys(), "value": contractor.values()})
##        pd = pandas.DataFrame(contractor, columns=order)
##        pd.to_csv("USAContractors.csv")
        f3.close()                                

def finishDownloading():
        trans = {'25':'b01a', '50':'c09b', '75':'2ba2', '100':'2438', '125':'9951'}
        f = open ('../log.txt','r')
        for link in f.read().split('www.')[1::2]:
                link = link[:-7]
                #nonmember=true (repeats)
                if link[-1]=='e':
                        continue
                name = link[16:]
                if link[-1]!='l':
                        end = link[link.find('=')+1:]
                        name = name[:name.find('.html')] + trans[end] + '.html'
                print(link, name)
                req = Request('http://www.'+ link, headers={'User-Agent': 'Mozilla/5.0'})
                with open(name, 'wb') as f2:
                        f2.write(urlopen(req).read())
                        f2.close()
        f.close()
        
if __name__ == '__main__':
        #finishDownloading()
        #rscrape()
        scrape()
