import sys
import random
from datetime import datetime
import os
import time
import uuid
import subprocess
import sys
from subprocess import PIPE
import httplib
from urllib import urlencode
from urllib2 import urlopen, Request, HTTPRedirectHandler
import urllib2
import urllib
from cookielib import *
from urlparse import urlparse

#serverhost = 'test.commcarehq.org'
#serverhost = 'localhost'
serverhost = 'localhost:8000'

curl_command = 'curl' #make sure curl is in your path

# you can turn curl on and off here.  The alternative is standard python posts
# but curl seems to be required for django to correctly handle multipart forms
use_curl = False

#filename = r'C:\Source\hq\commcare-hq\apps\backups\tests\data\backup.xml'
#filename = r"C:\Documents and Settings\Cory Zue\Desktop\reg.xml"
#filename = r'C:\Source\hq\commcare-hq\tests\deployment\multipart\multipart-3.txt'
#filename = r'/media/Otoro/projects/AquaTest/data/attachments/aqua2.xml'
filename = r'/media/Otoro/codes/temp-xforms/h2stest.xml' 
#filename = r'D:\Work\AquaTest\repo\AquatestClone\data\attachments\h2s.xml'
#filename = os.path.join(os.getcwd(), 'test-data', 'multipart-1.post')

domain_name = "itido"
content_type = "text/xml"
#content_type = "multipart/form-data; boundary=newdivider"

string_url = 'http://%s/receiver/submit/%s' % (serverhost, domain_name)
up = urlparse(string_url)

dict = {}
dict['User-Agent'] = 'CCHQ-submitfromfile-python-v0.1'
try:
    file = open(filename, "rb")
    data = file.read()
    print "data: %s" % data
    randint = random.random()
    # randomize some block in the file so it's not handled as a duplicate.
    data = data.replace("LWRYWILK0ZCFO61Y7XIXGMDP5", str(randint))
    dict["content-type"] = content_type
    dict["content-length"] = len(data)
    if use_curl:
        p = subprocess.Popen([curl_command,'--header','Content-type:%s' % content_type, '--header', '"Content-length:%s' % len(data), 
                          '--data-binary', '@%s' % filename, '--request', 'POST', string_url],
                          stdout=PIPE,stderr=PIPE,shell=False)
        errors = p.stderr.read()
        results = p.stdout.read()
        print "curl gets back:\n%s\nAnd errors:\n%s" % (results, errors)
    else:
        conn = httplib.HTTPConnection(up.netloc)
        conn.request('POST', up.path, data, dict)
        resp = conn.getresponse()
        results = resp.read()
        print "httplib gets back\n%s" % results
except Exception, e:
    print"problem submitting form: %s" % filename 
    print e
    
