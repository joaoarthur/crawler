import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from pyvirtualdisplay import Display

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit()  

url = 'http://pycoders.com/archive/'  
	
with Display(visible=0, size=(800, 600)):
    r = Render(url)
 
result = r.frame.toHtml()
print result.toAscii()
#This step is important.Converting QString to Ascii for lxml to process



