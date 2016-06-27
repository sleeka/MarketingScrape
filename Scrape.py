# Next time I'll use a library to scrape. Interesting process
# Very inefficient
from urllib.request import Request, urlopen

SITE = '' # removed

def getStatesList():
    req = Request(SITE,
                  headers={'User-Agent': 'Mozilla/6.0'})
    page = urlopen(req).read().decode('utf-8')
    page = page[page.find("Alabama")-27 : page.find("Wyoming")]
    
    states = list(s[:2] if s[1].isupper() else "Washington.DC"
                  for s in page.split('href=\"/c.'))
    return states

def getCityList(s):
    cities = []
    for ch in range(65,91):
        print (ch)
        req = Request(
                SITE +s+ '.html?searchByCityLetter='+
                chr(ch), headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read().decode('utf-8')
        page = page[page.find('Selecting a City') : page.find('xs-alpha-list')]
        if 'We\'re sorry' in page:
            continue
        page = page[page.find('href="/c.') +9:]
        for c in page.split('href="/c.'):
            cities.append(c[:c.find('.'+s)]) 
    return cities

def scrape(url, reviews, city, state, vert):
    req = Request(SITE +url,
                  headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read().decode('utf-8')

    con = []

    # name
    con.append(page[page.find('<title>')+7 : page.find(' |')])

    # verified reviews
    con.append(reviews)

    # telephone
    phone = page.find('itemprop="telephone')+21
    con.append(page[phone : phone +11])

    # address
    addy = page.find('itemprop="streetAddress')+25
    zipcode = page.find('itemprop="postalCode')+22
    con.append(page[addy : page.find('</span>', addy)] +', ' +city+ ', ' +state+
        ', '+ page[zipcode : zipcode +5])

    # profile
    profile = page.find('<p>', page.find('itemprop="description')) +3
    con.append(page[profile : page.find('</p>', profile)])

    # vertical
    con.append(vert)

    # website
    site = page.find('rel="nofollow') +15
    if site > 14:
        con.append(page[site : page.find('</a>', site)])

def search(cities, state):
    verticals = {('Roofing','12061'), ('Solar','14820'), ('Windows','12080'),
                 ('Air-Conditioning','12002'), ('Heating-Furnace-Systems','12040')}
    con = []
    for city in cities:
        for k, v in verticals:
            nextPage = ''
            while (True):
                req = Request(
                    SITE +k+ '.' +city+ '.' +
                    state+ '.-' +v+ '.html' +nextPage,
                    headers={'User-Agent': 'Mozilla/5.0'})
                page = urlopen(req).read().decode('utf-8')
                page = page[page.find('xmd-listing-company-name') :
                    page.find('x1-pagination')]
                
                contractors = page.split('#ratings-reviews">')
                for i in range(1,len(contractors)):
                    rev = contractors[i][:6].split(' ')
                    # 20 or more verified reviews;
                    # call this con
                    if int(rev[0]) > 19:
                        con.append(scrape(contractors[i-1]
                            [contractors.rfind('href="/')+7 :]),
                            rev[0], city, state, k)
                pagination = contractors[-1][contractors[-1].find(
                    'Showing 1-') +10 : contractors[-1].find('<')].split(' ')
                print(pagination)
                if pagination[0]=='':
                    print (page.rfind('pagination'))
                    print (contractors[-1])
                if int(pagination[0]) < int(pagination[2]):
                    nextPage = '?startingIndex='+pagination[0]
                else:
                    break                    
                                            
    f = open('Contractors.txt', 'a')
    for c in con:
        f.write(con + '|')
    f.close()
    print ('SUCCESS:\n\n' +len(con))
                               
if __name__ == "__main__":
    verticals = {('Roofing','12016'), ('Solar','14820'), ('Windows','12080'),
                 ('Air-Conditioning','12002'), ('Heating-Furnace-Systems','12040')}
    req = Request(
                    SITE,
                    headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()#.decode('utf-8')
    f = open('Page.txt','wb')
    f.write(page)
    f.close()
##    states = getStatesList()
##    f = open('States2.txt','w')
##    for s in states:
##        f.write(SITE +s+ '.html\n')
    
##    f = open('States.txt', 'a')
##    for s in states[states.index('HI'):]:
##        cities = []
##        cities = getCityList(s)
##        print(s,len(cities))
##                               
##    # I desipse this opening and closing nonsense
##    #   but I know I'll be banned fast
##        for c in cities:
##            for k,v  in verticals:
##                f.write(SITE +k+ '.' +c+ '.' +
##                    s+ '.-' +v+ '.html\n')
##
##            
    #f.close()
                           
    #search(cities, s)
    

# Postscript (intra-script): pep8 80 character line rule :O
