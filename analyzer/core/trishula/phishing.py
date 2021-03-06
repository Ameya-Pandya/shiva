"""
This module contains implementation of phishing detectiton rules


"""


from bs4 import BeautifulSoup
from Levenshtein import distance
from string import split


import unicodedata
import re


# list of top level domains
TLD_LIST = ['abb','abbott','abogado','ac','academy','accenture','accountant','accountants','active','actor','ad','ads','adult','ae','aero','af','afl','ag',
'agency','ai','aig','airforce','al','allfinanz','alsace','am','amsterdam','an','android','ao','apartments','aq','aquarelle','ar','archi','army','arpa','as',
'asia','associates','at','attorney','au','auction','audio','auto','autos','aw','ax','axa','az','ba','band','bank','bar','barclaycard','barclays','bargains',
'bauhaus','bayern','bb','bbc','bd','be','beer','berlin','best','bf','bg','bh','bi','bid','bike','bingo','bio','biz','bj','black','blackfriday','bloomberg',
'blue','bm','bmw','bn','bnpparibas','bo','boats','bond','boo','boutique','br','bridgestone','broker','brother','brussels','bs','bt','budapest','build',
'builders','business','buzz','bv','bw','by','bz','bzh','ca','cab','cafe','cal','camera','camp','cancerresearch','canon','capetown','capital','caravan',
'cards','care','career','careers','cars','cartier','casa','cash','casino','cat','catering','cbn','cc','cd','center','ceo','cern','cf','cfa','cfd','cg','ch',
'channel','chat','cheap','chloe','christmas','chrome','church','ci','cisco','citic','city','ck','cl','claims','cleaning','click','clinic','clothing','club',
'cm','cn','co','coach','codes','coffee','college','cologne','com','community','company','computer','condos','construction','consulting','contractors','cooking',
'cool','coop','corsica','country','coupons','courses','cr','credit','creditcard','cricket','crs','cruises','cu','cuisinella','cv','cw','cx','cy','cymru','cyou',
'cz','dabur','dad','dance','date','dating','datsun','day','dclk','de','deals','degree','delivery','democrat','dental','dentist','desi','design','dev','diamonds',
'diet','digital','direct','directory','discount','dj','dk','dm','dnp','do','docs','dog','doha','domains','doosan','download','durban','dvag','dz','earth','eat',
'ec','edu','education','ee','eg','email','emerck','energy','engineer','engineering','enterprises','epson','equipment','er','erni','es','esq','estate','et','eu',
'eurovision','eus','events','everbank','exchange','expert','exposed','express','fail','faith','fan','fans','farm','fashion','feedback','fi','film','finance',
'financial','firmdale','fish','fishing','fit','fitness','fj','fk','flights','florist','flowers','flsmidth','fly','fm','fo','foo','football','forex','forsale',
'foundation','fr','frl','frogans','fund','furniture','futbol','fyi','ga','gal','gallery','garden','gb','gbiz','gd','gdn','ge','gent','gf','gg','ggee','gh',
'gi','gift','gifts','gives','gl','glass','gle','global','globo','gm','gmail','gmo','gmx','gn','gold','goldpoint','golf','goo','goog','google','gop','gov',
'gp','gq','gr','graphics','gratis','green','gripe','gs','gt','gu','guge','guide','guitars','guru','gw','gy','hamburg','hangout','haus','healthcare','help',
'here','hermes','hiphop','hitachi','hiv','hk','hm','hn','hockey','holdings','holiday','homes','honda','horse','host','hosting','house','how','hr','ht','hu',
'ibm','icbc','icu','id','ie','ifm','il','im','immo','immobilien','in','industries','infiniti','info','ing','ink','institute','insure','int','international',
'investments','io','iq','ir','irish','is','it','iwc','java','jcb','je','jetzt','jewelry','jll','jm','jo','jobs','joburg','jp','juegos','kaufen','kddi','ke',
'kg','kh','ki','kim','kitchen','kiwi','km','kn','koeln','komatsu','kp','kr','krd','kred','kw','ky','kyoto','kz','la','lacaixa','land','lat','latrobe','lawyer',
'lb','lc','lds','lease','leclerc','legal','lgbt','li','liaison','lidl','life','lighting','limited','limo','link','lk','loan','loans','lol','london','lotte',
'lotto','love','lr','ls','lt','ltda','lu','lupin','luxe','luxury','lv','ly','ma','madrid','maif','maison','management','mango','market','marketing','markets',
'marriott','mba','mc','md','me','media','meet','melbourne','meme','memorial','men','menu','mg','mh','miami','mil','mini','mk','ml','mm','mma','mn','mo','mobi',
'moda','moe','monash','money','mormon','mortgage','moscow','motorcycles','mov','movie','mp','mq','mr','ms','mt','mtn','mtpc','mu','museum','mv','mw','mx','my',
'mz','na','nadex','nagoya','name','navy','nc','ne','nec','net','network','neustar','new','news','nexus','nf','ng','ngo','nhk','ni','nico','ninja','nissan','nl',
'no','np','nr','nra','nrw','ntt','nu','nyc','nz','okinawa','om','one','ong','onl','online','ooo','oracle','org','organic','osaka','otsuka','ovh','pa','page',
'panerai','paris','partners','parts','party','pe','pf','pg','ph','pharmacy','philips','photo','photography','photos','physio','piaget','pics','pictet','pictures',
'pink','pizza','pk','pl','place','plumbing','plus','pm','pn','pohl','poker','porn','post','pr','praxi','press','pro','prod','productions','prof','properties',
'property','ps','pt','pub','pw','py','qa','qpon','quebec','racing','re','realtor','recipes','red','redstone','rehab','reise','reisen','reit','ren','rent','rentals',
'repair','report','republican','rest','restaurant','review','reviews','rich','rio','rip','ro','rocks','rodeo','rs','rsvp','ru','ruhr','run','rw','ryukyu','sa',
'saarland','sale','samsung','sap','sarl','saxo','sb','sc','sca','scb','schmidt','scholarships','school','schule','schwarz','science','scot','sd','se','seat',
'sener','services','sew','sex','sexy','sg','sh','shiksha','shoes','show','shriram','si','singles','site','sj','sk','sky','sl','sm','sn','so','soccer','social',
'software','sohu','solar','solutions','sony','soy','space','spiegel','spreadbetting','sr','st','study','style','su','sucks','supplies','supply','support','surf',
'surgery','suzuki','sv','swiss','sx','sy','sydney','systems','sz','taipei','tatar','tattoo','tax','taxi','tc','td','team','tech','technology','tel','temasek',
'tennis','tf','tg','th','thd','theater','tickets','tienda','tips','tires','tirol','tj','tk','tl','tm','tn','to','today','tokyo','tools','top','toray','toshiba',
'tours','town','toys','tr','trade','trading','training','travel','trust','tt','tui','tv','tw','tz','ua','ug','uk','university','uno','uol','us','uy','uz','va',
'vacations','vc','ve','vegas','ventures','versicherung','vet','vg','vi','viajes','video','villas','vision','vlaanderen','vn','vodka','vote','voting','voto',
'voyage','vu','wales','wang','watch','webcam','website','wed','wedding','weir','wf','whoswho','wien','wiki','williamhill','win','wme','work','works','world',
'ws','wtc','wtf','xerox','xin','xn','xxx','xyz','yachts','yandex','ye','yodobashi','yoga','yokohama','youtube','yt','za','zip','zm','zone','zuerich','zw'];

# patterns used for working with urls
URL_REGEX_PATTERN = re.compile(ur'(?i)(https?:\/\/)?([\da-z@\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?')
URL_IP_PATTERN = re.compile(ur'(?:\d{1,3}\.){3}\d{1,3}')
URL_DOMAIN_PATTERN = re.compile(ur'[a-z0-9.\-]+[.][a-z]{2,4}')


# list of common phishing subject regexes
PHISHING_SUBJECT_REGEX_LIST = []
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)account'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)update'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)security'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)secure'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)ebay'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)card'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)bank'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)verify'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)valid'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)visa'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)confirm'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)varovani'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)nalehav'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)dulez'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)platn'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)ukonceni'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)\bend'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)podezrel'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)over'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)naleh'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)nezbyt'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)webmail'))
PHISHING_SUBJECT_REGEX_LIST.append(re.compile('(?i)kone?c'))


# list of common phishing phrases
PHISHING_PHRASES_REGEX_LIST = []
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)your.{0,40}?account'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)please.{0,40}?confirm'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)dear.{0,40}?customer'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)verify.{0,40}?account'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)urgent'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)requir'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)prosim.{0,40}?over'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)vas.{0,40}?ucet'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)vas.{0,40}?schra'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)heslo'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)password'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)nezbyt'))
PHISHING_PHRASES_REGEX_LIST.append(re.compile('(?i)naleh'))

    

# list of common spam regexes
COMMON_SPAM_SUBJECT_REGEX_LIST = []
plain_regex = []
# returned mails
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)transcript'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)return'))
# science, scientific, conference
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)scien'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)conf\.'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)confe'))

COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)nauc'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)pouz'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)posil'))
# inviations
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)invit'))
# pcb is common spam 
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)pcb'))
COMMON_SPAM_SUBJECT_REGEX_LIST.append(re.compile('(?i)china'))



# helper functions
def extractdomain(url):
    """parse domain name from given url

    Keyword arguments:
    url - string
    """
    if not url:
        return ''
    
    m = re.match(URL_REGEX_PATTERN, url.strip())
    if m:
        m = re.search(URL_DOMAIN_PATTERN, url.strip())
        if m:
            return re.sub('^www\.', '', m.group())
    return ''

def extractip(url):
    """parse ip address given url

    Keyword arguments:
    url - string
    """
    if not url:
        return ''
    
    ips = re.findall(URL_IP_PATTERN, url)
    if len(ips) == 0:
        return ''
    ip = ips[0]
    
    domain = extractdomain(url)
    if not domain:
        return ip
    #check whether ip isn't part of query or params 
    return ip if url.find(ip) < url.find(domain) else '' 

def samedomain(url1, url2):
    """
    check whether two urls point to same domain
    (L1 domain and TLD mus be the same)
    """
    if not url1 or not url2:
        return False
    
    url1_splitted = url1.strip().split('.')
    url2_splitted = url2.strip().split('.')
    min_length = min(len(url1_splitted), len(url2_splitted))
    if min_length < 2 :
        return False
    url1_splitted.reverse()
    url2_splitted.reverse()
    
    if (url1_splitted[0] != url2_splitted[0]) | (url1_splitted[1] != url2_splitted[1]):
        return False
    return True

def extractalldomains(url):
    """
    extract all domains from given url
    """
    
    urls = list()
    if not url:
        return urls
    
    for match in re.findall(URL_DOMAIN_PATTERN, url):
        for tld in TLD_LIST:
            if match.endswith('.' + tld):
                urls.append(re.sub('www\d{0,3}\.', '', match))
    return urls

def getfinalurls(url_info={}):
    """
    return list of urls from url_tuple. Unshortened Url is alwas prefered
    """
    url_list = list()
    if not url_info:
        return url_list
    
    for current in url_info:
        url_list.append(current['raw_link'])
        if current['LongUrl']:
            url_list.append(current['LongUrl'])
    return url_list
        
def strip_accents(s):
    """ 
    normalize given string
    """
    if isinstance(s, unicode):
        return ''.join(c for c in unicodedata.normalize('NFD', s) 
                   if unicodedata.category(c) != 'Mn')
        

    return ''.join(c for c in unicodedata.normalize('NFD', s.decode('utf8','replace')) 
                   if unicodedata.category(c) != 'Mn')

def without_tld(s):
    """
    remove everything after last '.' of string
    """
    c = s.rfind('.') 
    return s if c < 0 else s[:c]


def check_url_phishing(mailFields):
    """
    check whether some of rules A1-A4 holds for given mailFields
    """
    return True if any((RuleA1().apply_rule(mailFields) > 0,
                       RuleA2().apply_rule(mailFields) > 0,
                       RuleA3().apply_rule(mailFields) > 0,
                       RuleA4().apply_rule(mailFields) > 0,)
                       ) else False











     
class MailClassificationRuleList(object):
    """
    Class represents list of MailClassificationRules to be
       applied on mail
    """    
    
    def __init__(self):
        self.rulelist = list()
     
    def add_rule(self, rule):
        """
        Add rule to list
        rule - instance of MailClassificationRules
        """
        if isinstance(rule, MailClassificationRule):
            self.rulelist.append(rule)
    
    def apply_rules(self, mailFields):
        """
        Apply all rules on given mailFields
        return - list of results
        """
        result = []
        for rule in self.rulelist:
            result.append(rule.apply_rule(mailFields))
        return result
    
    def get_rules(self):
        return self.rulelist
    
    def get_rule_names(self):
        """
        retrieve names of all rules
        """
        result = []
        for rule in self.rulelist:
            result.append(rule.get_rule_description())
        return result

    
    

class MailClassificationRule(object):
    """
    Generic classification rule
    
    all rules must implement etend this class
    """
    def __init__(self):
        # readable rule description
        self.description = "base_rule"
    
    def get_rule_description(self):
        """
        return human readable decription of rule 
        """
        return self.description
    
    def get_rule_code(self):
        return self.code
    
    def apply_rule(self, mailFields):
        """ 
        return 1 if email mathes rule, -1 otherwise
        """
        raise NotImplementedError("Implement this method")
    


# =============================================================
# Here starts definitions of phishing rules
# =============================================================

class RuleB1(MailClassificationRule):
    def __init__(self):
        self.code = 'B1'
        self.description = "At least one URL is shortened"
        
    def apply_rule(self, mailFields):
        if not 'links' in mailFields:
            return -1
        for url_info in mailFields['links']:
            if url_info['LongUrl']:
                return 1
        return -1
        
class RuleB2(MailClassificationRule):
    def __init__(self):
        self.code = 'B2'
        self.description = "Hyperlink with visible URL, pointing to different URL"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            href = extractdomain(a_tag.get('href'))
            text = extractdomain(a_tag.get_text())
            
            if not href or not text:
                continue
            
            if not samedomain(href, text):
                return 1 
        return -1
    
class RuleB3(MailClassificationRule):
    def __init__(self):
        self.code = 'B3'
        self.description = "Hyperlink with visible text pointing to IP based URL"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            text = a_tag.get_text()
            if not text:
                continue
            
            if extractip(a_tag.get('href')):
                return 1
              
        return -1
    
class RuleB4(MailClassificationRule):
    def __init__(self):
        self.code = 'B4'
        self.description = "Email body in HTML format"
        
    def apply_rule(self, mailFields):
        return 1 if mailFields['html'] else -1
    
class RuleB5(MailClassificationRule):
    def __init__(self):
        self.code = 'B5'
        self.description = "Too complicated URL"
    
    def apply_rule(self, mailFields):
        if 'links' in mailFields:
            for link_info in mailFields['links']:
                if 'raw_link' in link_info and not extractip(link_info['raw_link']):
                    if str(link_info['raw_link']).count('.') > 4:
                        return 1
        
        if not 'html' in mailFields:
            return -1
        
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            url = a_tag.get('href')
            if url and url.count('.') > 4:
                return 1
            
            url = a_tag.get_text()
            if url and url.count('.') > 4:
                return 1
        
        return -1
        
        

class RuleB6(MailClassificationRule):
    def __init__(self):
        self.code = 'B6'
        self.description = "Sender domain different from some URL in message body"
        
    def apply_rule(self, mailFields):
        if not 'from' in mailFields or not 'links' in mailFields:
            return -1

        sender = mailFields['from'];
        sender_splitted = sender.split('@',2)
        if len(sender_splitted) < 2:
            return -1
        
        m = re.search(URL_DOMAIN_PATTERN, sender_splitted[1])
        if not m:
            return -1
        
        sender_domain = m.group()
        for url in getfinalurls(mailFields['links']):
            if not samedomain(sender_domain, url):
                return 1
        return -1

class RuleB7(MailClassificationRule):
    def __init__(self):
        self.code = 'B7'
        self.description = "Image with external domain different from URLs in email body"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields or not 'links' in mailFields:
            return -1
        
        domain_list = filter(lambda url: url, (map(extractdomain, getfinalurls(mailFields['links']))))
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for img_tag in soup.find_all('img'):
            src_domain = extractdomain(img_tag.get('src'))
            if src_domain:
                for domain in domain_list:
                    if not samedomain(src_domain, domain):
                        return 1
        return -1

class RuleB8(MailClassificationRule):
    def __init__(self):
        self.code = 'B8'
        self.description = "Image source is IP address"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for img_tag in soup.find_all('img'):
            src_ip = extractip(img_tag.get('src'))
            if src_ip:
                return 1
        return -1
    
class RuleB9(MailClassificationRule):
    def __init__(self):
        self.code = 'B9'
        self.description = "More than one domain in URL"
        
    def apply_rule(self, mailFields):
        if 'html' in mailFields:
            soup = BeautifulSoup(mailFields['html'], 'html.parser')
            for a_tag in soup.find_all('a'):
                if len(extractalldomains(a_tag.get('href'))) > 1:
                    return 1 
        
        if 'links' in mailFields:
            for link in getfinalurls(mailFields['links']):
                if len(extractalldomains(link)) > 1:
                    return 1
               
        return -1
            
class RuleB10(MailClassificationRule):
    def __init__(self):
        self.code = 'B10'
        self.description = "More than three subdomains in URL"
        
    def apply_rule(self, mailFields):
        if 'html' in mailFields:
            soup = BeautifulSoup(mailFields['html'], 'html.parser')
            for a_tag in soup.find_all('a'):
                href = extractdomain(a_tag.get('href'))
                if href and not extractip(href) and len(split(extractdomain(href), '.')) > 4:
                    return 1
                
        if 'links' in mailFields:
            for link in getfinalurls(mailFields['links']):
                if not extractip(link) and len(split(extractdomain(link), '.')) > 4:
                    return 1
        
        return -1

class RuleB11(MailClassificationRule):
    def __init__(self):
        self.code = 'B11'
        self.description = "Hyperlink with image insted of visible text, image source is IP address"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            for img in a_tag.find_all('img'):
                if extractip(img.get('src')):
                    return 1
        return -1

class RuleB12(MailClassificationRule):
    def __init__(self):
        self.code = 'B12'
        self.description = "Visible text in hyperlink contains no information about destination"
        
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            href = extractdomain(a_tag.get('href'))
            text_link = extractdomain(a_tag.get_text())
            
            if not text_link:
                return 1
            if href:
                if text_link.lower() != href.lower():
                    return 1
                
        return -1



class RuleB13(MailClassificationRule):
    def __init__(self):
        self.code = 'B13'
        self.description = "URL contains username"
        
    def apply_rule(self, mailFields):
        if 'links' in mailFields:
            for link_info in mailFields['links']:
                if link_info['raw_link'] and '@' in link_info['raw_link'] and link_info['raw_link'].startswith('http'):
                    return 1
        
        if not 'html' in mailFields:
            return -1
        
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            url = a_tag.get('href')
            if not url or url.startswith('mailto'):
                continue
            if '@' in url:
                return 1
            
            url = a_tag.get_text()
            if url and '@' in url:
                return 1
        return -1
    
    
class RuleB14(MailClassificationRule):
    def __init__(self):
        self.code = 'B14'
        self.description = 'Presence of suspicious headers'
        
    def apply_rule(self, mailFields):
        if 'headers' not in mailFields:
            return -1
        
        content_type_regex = re.compile(ur'(?is)content.type.*?\)')
        boundary_regex  = re.compile('(?i)boundary.{1,40}qzsoft_directmail_seperator')
        
        
        
        for content in content_type_regex.findall(mailFields['headers']): 
            if boundary_regex.search(content):
                return 1
        
        clamav_virus_regex = re.compile('(?i)X-Virus-Status.{0,10}Yes')
        if clamav_virus_regex.search(mailFields['headers']):
            return 1
        
        return -1
    
class RuleB15(MailClassificationRule):
    def __init__(self):
        self.code = 'B15'
        self.description = 'Common phishing keywords in subject '
        
    def apply_rule(self, mailFields):
        if 'subject' not in mailFields or not mailFields['subject']:
            return -1
        
        subject = strip_accents(mailFields['subject'])
        for pattern in PHISHING_SUBJECT_REGEX_LIST:
            if pattern.search(subject):
                return 1
        return -1

class RuleB16(MailClassificationRule):
    def __init__(self):
        self.code = 'B16'
        self.description = 'Common phishing phrases in email body'
        
    def apply_rule(self, mailFields):
        if 'text' in mailFields and mailFields['text']:
            for current_regex in PHISHING_PHRASES_REGEX_LIST:
                if current_regex.search(mailFields['text']):
                    return 1
                
        if 'html' in mailFields and mailFields['html']:
            for current_regex in PHISHING_PHRASES_REGEX_LIST:
                if current_regex.search(mailFields['html']):
                    return 1

        return -1

class RuleB17(MailClassificationRule):
    def __init__(self):
        self.code = 'B17'
        self.description = 'Common spam keywords in subject'
         
    def apply_rule(self, mailFields):
        if 'subject' not in mailFields or not mailFields['subject']:
            return -1
        
        subject = strip_accents(mailFields['subject'])
        for pattern in COMMON_SPAM_SUBJECT_REGEX_LIST:
            if pattern.search(subject):
                return 1
        return -1
    
class RuleB18(MailClassificationRule):
    def __init__(self):
        self.code = 'B18'
        self.description = 'Suspicious amount of redirections'
         
    def apply_rule(self, mailFields):
        if 'links' not in mailFields:
            return -1
        
        for link_info in mailFields['links']:
            if 'RedirectCount' in link_info and link_info['RedirectCount'] > 6:
                return 1
        return -1        
    
class RuleB19(MailClassificationRule):
    def __init__(self):
        self.code = 'B19'
        self.description = 'Suspicious Alexa ranks in links'
         
    def apply_rule(self, mailFields):
        if 'links' not in mailFields:
            return -1
        
        rank_sum = 0
        rank_count = 0
        for link_info in mailFields['links']:
            if 'AlexaTrafficRank' in link_info and link_info['AlexaTrafficRank'] > 0:
                rank_sum += link_info['AlexaTrafficRank']
                rank_count += 1
                
        if rank_sum and rank_count > 0 and rank_sum / rank_count < 1000:
            return 1
            
        return -1
          
class RuleB20(MailClassificationRule):  
    def __init__(self):
        self.code = 'B20'
        self.description = 'Reply to header leads to different domain than sender'
            
    def apply_rule(self, mailFields):
        if 'headers' not in mailFields or not mailFields['headers']:
            return -1
        
        if 'from' not in mailFields or not mailFields['from']:
            return -1
        
        from_domain = mailFields['from'].partition('@')[2]
        if not from_domain:
            return -1 

        # get reply-to header
        reply_to_header_regex = re.compile('(?i)\(reply-to[^)]+')
        reply_to_headers = reply_to_header_regex.findall(mailFields['headers'])
        for current_reply_to in reply_to_headers:
            reply_to_domain = extractdomain(current_reply_to.partition('@')[2]) 
            if not reply_to_domain:
                continue
            if not samedomain(from_domain,reply_to_domain):
                return 1
        return -1

    

class RuleA1(MailClassificationRule):
    def __init__(self):
        self.code = 'A1'
        self.description = "At least one URL found on blacklist"

    def apply_rule(self,mailFields):    
        if 'links' not in mailFields:
            return -1
    
        if any(map(lambda a: a['GoogleSafeBrowsingAPI'] if 'GoogleSafeBrowsingAPI' in a else False, mailFields['links'])):
            return 1
        
        if any(map(lambda a: a['InPhishTank'] if 'InPhishTank' in a else False, mailFields['links'])):
            return 1
        return -1

    
class RuleA2(MailClassificationRule):
    def __init__(self):
        self.code = 'A2'
        self.description = "HTTPS in visible link, HTTP in real destination"
    
    def apply_rule(self, mailFields):
        if not 'html' in mailFields:
            return -1
        
        soup = BeautifulSoup(mailFields['html'], 'html.parser')
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            text_link = a_tag.get_text()
            
            if not href or not text_link:
                continue

            if re.search('http:\/\/', href) and re.search('https:\/\/',text_link):
                return 1
        
        return -1
    
    
# =============================================================
# rules using common phishing targets whitelist
# =============================================================

# This is the list of comon sites, that could be possibly phished
# Intended use of for second level domains
# Be carefull, adding something like 'php.cz' can really mess things up
# since 'php' is common string presented in URLs
COMMON_PHISH_SITES = ['muni.cz', 'paypal.com', 'visa.com', 'ebay.com']


def one_char_typosquatting(s_a='', s_b=''):
    """
    function searches for one character typosquatting for strings of length at least 4
    
    types of one char typosquatting:
        inplace one char:  
            paypal -> paypel
            paypal -> paypai
            paypal -> qaypal
        
        inflate one char: 
            paypal -> paypal2
            paypal -> payypal
            paypal -> ppaypal
        
        deflate one char:
            paypal -> payal
            paypal -> papal    
            
        switched neighbour chars:
            paypal -> papyal
            paypal -> payapl
    """
    if not s_a or not s_b or s_a == s_b:
        # nothing to compute
        return False
    
    if len(s_a) < 4 and len(s_b) < 4:
        return False
    
    # Levenshtein distance handle inplace, inflate and deflate one char
    if distance(strip_accents(s_a),strip_accents(s_b)) == 1:
        return True
    
    # try for find switched neighbours
    if not len(s_a) == len(s_b):
        return False
    
    
    for i in range(0,len(s_a) -1):
        t = s_a[i:i+2][::-1]
        switched_neighbours = ''.join((s_a[:i] if i > 0 else '' , t,s_a[i+2:],))
        
        if switched_neighbours == s_b:
            return True

    return False

            
class RuleA3(MailClassificationRule):
        
    def __init__(self):
        self.code = 'A3'
        self.description = 'Common phishing targets one character typosqutting'
    
    
    def apply_rule(self, mailFields):
        if 'links' not in mailFields:
            return -1
    
        for link_info in mailFields['links']:
            raw_link = link_info['raw_link']
        
            domain = extractdomain(raw_link)
            if not domain:
                continue
            
            domain = domain.lower()
            domain_no_tld = without_tld(domain)
            
            
            # check whether domain is on COMMON_PHISH_SITES list to prevent false possive match
            false_positive = False
            for common_phish_site in COMMON_PHISH_SITES:            
                if samedomain(domain, common_phish_site):
                    false_positive = True
                    
            if false_positive:
                continue
            
            # now we know domain is not on the COMMON_PHISH_SITES list
            # we try to find typosquating 
            # remove all nonalfanumerical characters
            bare_domain_no_tld = re.sub(r'[^a-z0-9]', '', domain_no_tld)
            
            for common_phish_site in COMMON_PHISH_SITES:
                
                # check for the  for common phishing site name in somewhere in domain
                # this matches things like paypal.biz paypal-secure,com paypal.somewhere.com
                
                bare_common_phish_site_no_tld = without_tld(common_phish_site)
                if one_char_typosquatting(bare_domain_no_tld, bare_common_phish_site_no_tld):
                    return 1
            
        return -1
        
        
class RuleA4(MailClassificationRule):
        
    def __init__(self):
        self.code = 'A4'
        self.description = 'Common phishing site reference in URL'
    
    
    def apply_rule(self, mailFields):
        if 'links' not in mailFields:
            return -1
    
        for link_info in mailFields['links']:
            raw_link = link_info['raw_link']
        
            domain = extractdomain(raw_link)
            if not domain:
                continue
            
            # should be safe, domain is part of raw_link
            rest_of_url = raw_link.split(domain,1)[1]
            
            domain = domain.lower()
            domain_no_tld = without_tld(domain)
            
            
            # check whether domain is on COMMON_PHISH_SITES list to prevent false possive match
            false_positive = False
            for common_phish_site in COMMON_PHISH_SITES:            
                if samedomain(domain, common_phish_site):
                    false_positive = True
                    
            if false_positive:
                continue
            
            # now we know domain is not on the COMMON_PHISH_SITES list
            # we try to find typosquating 
            # remove all nonalfanumerical characters
            bare_domain_no_tld = re.sub(r'[^a-z0-9]', '', domain_no_tld)
            
            for common_phish_site in COMMON_PHISH_SITES:
                
                # check for the substring of common phish site in domain
                bare_common_phish_site_no_tld = re.sub(r'[^a-z0-9]', '', without_tld(common_phish_site))
                
                if bare_common_phish_site_no_tld in bare_domain_no_tld:
                    return 1
                
                if bare_common_phish_site_no_tld in rest_of_url:
                    return 1
            
        return -1





     


# =============================================================
# Rules registrations
# =============================================================
# register desired rules into rule list
# rules will be applied on email in this order
# rules not added to rule list will be ignored

# contains list of rules that will be applied on emails   
# for statistical classification purposes
#
# Please note that each of rules A* should be strong enough to identify
# phishing attempt by the itself, but they are quite rare.
# It's better to use their result as direct verdict rather then statistical feature
rulelist = MailClassificationRuleList()

rulelist.add_rule(RuleB1())
rulelist.add_rule(RuleB2())
rulelist.add_rule(RuleB3())
rulelist.add_rule(RuleB4())
rulelist.add_rule(RuleB5())
rulelist.add_rule(RuleB6())
rulelist.add_rule(RuleB7())
rulelist.add_rule(RuleB8())
rulelist.add_rule(RuleB9())
rulelist.add_rule(RuleB10())
rulelist.add_rule(RuleB11())
rulelist.add_rule(RuleB12())
rulelist.add_rule(RuleB13())
rulelist.add_rule(RuleB14())
rulelist.add_rule(RuleB15())
rulelist.add_rule(RuleB16())
rulelist.add_rule(RuleB17())
rulelist.add_rule(RuleB18())
rulelist.add_rule(RuleB19())
rulelist.add_rule(RuleB20())

