import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
import requests

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):

    def __init__(self, html):
        self.html = None
        self.app = QApplication(sys.argv)
        QWebPage.__init__(self)
        self.loadFinished.connect(self._loadFinished)
        self.mainFrame().setHtml(html)
        self.app.exec_()

    def _loadFinished(self, result):
        self.html = self.mainFrame().toHtml()
        self.app.quit()

url = 'https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/'  

source_html = requests.get(url).text
	
with Display(visible=0, size=(800, 600)):
    rendered_html = Render(source_html).html
 
# get the BeautifulSoup
soup = BeautifulSoup(str(rendered_html.toAscii), 'html.parser')

print('title is %r' % soup.select_one('title').text)
#print result.toAscii()
#This step is important.Converting QString to Ascii for lxml to process



