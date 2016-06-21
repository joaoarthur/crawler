# -*- coding: utf-8 -*-
from bs4 import  BeautifulSoup
import requests
import datetime, time
from PyQt4 import QtCore, QtGui, QtWebKit
import sys, signal
from pyvirtualdisplay import Display

class WebPage(QtWebKit.QWebPage):
	"""
		Classe para renderizar as paginas dinamicas importada do PyQT4
	"""
	def __init__(self):
		QtWebKit.QWebPage.__init__(self)
		self.mainFrame().loadFinished.connect(self.handleLoadFinished)

	def process(self, items, set_produtos):
		self._base_url="http://www.superprix.com.br/"
		self._items = iter(items)
		self._set_produtos = set_produtos
		self._visitados = set()
		self.fetchNext()

	def fetchNext(self):
		try:
			self._link = next(self._items)
			self._url= self._base_url + self._link
			self.mainFrame().load(QtCore.QUrl(self._url))
		except StopIteration:
			return False
		return True

	def handleLoadFinished(self):
		html = str(self.mainFrame().toHtml().toAscii())
		soup = BeautifulSoup(html,"html5lib")
		self._set_produtos(soup, self._link, self._visitados)
		if not self.fetchNext():
			print('# processing complete')
			QtGui.qApp.quit()



def visit_dinamic_url (urls, set_produtos):
	"""
		Funcao para visitar as paginas que precisam de carregamento dinamico
	"""	
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QtGui.QApplication(sys.argv)
	webpage = WebPage()
	webpage.process(urls,set_produtos_categ)
	sys.exit(app.exec_())
	 
	

def visit_static_url (url, set_produtos):
	"""
		Funcao para visitar as paginas que precisam de carregamento estatico
	"""
	base_url = "http://www.superprix.com.br/"
	full_url = base_url + url
	html = requests.get(full_url).content
	soup = BeautifulSoup(html,"html5lib")
	return set_produtos (soup, url)
	
	 

def set_produtos_individual (soup_element, url):
	"""
		Funcao para setar o produto individualmente a partir da pagina do produto.
		Essa funcao nao esta mais sendo usada, pois o prix nao possui uma boa recomendacao de novos produtos.
	"""
	sessao = ""
	links = set ()
	nome = soup_element.find('h1', itemprop='name').getText().strip()
	preco = soup_element.find('span', itemprop='price').getText().strip().split(" ")[1]
	breadcrumb = soup_element.find('div', {"class" : "breadcrumb"}).findAll('span', itemprop="name")
	for path in breadcrumb[1:]:
		sessao += path.getText().strip() + "/"
	
	try:
		rel_links = soup_element.findAll('div', { "class" : "also-purchased-products-grid product-grid" })[0].findAll('h2', { "class" : "product-title"})
	except IndexError:
		rel_links = ""
	else:
		for link in rel_links:
			links.add(link.find('a').attrs['href'].split("/")[1])	
			
	return {
        'produto': nome,
        'preco': preco,
		'url': url,
		'sessao' : sessao,
		'links': links,
    }



def busca_categoria (soup_element, url):
	"""
		Funcao para buscar todas as categorias. Feito isso ela chama a funcao que retorna todas as subcategorias de cada categoria.
		Com todas as subcategorias definidas, a funcao chama a visita de pagina dinamica, que sera responsavel por renderizar cada pagina de subcategoria.
	"""
	categorias = set ()
	sub_categorias = set ()
	
	categorias.add(url)
	
	div_categorias = soup_element.find('ul', { "class" : "list"}).findAll('li', { "class" : "inactive" })[1:]
	for categ in div_categorias:
		categorias.add(categ.find('a').attrs['href'].split("/")[1])
	
	#adiciona manualmente as subcategorias de bebidas alcolicas, pois nao era possivel pegar pelo DOM de forma unica as mesmas.
	sub_categorias.add('cervejas')
	sub_categorias.add('vinhos')
	sub_categorias.add('destilados')
	
	while categorias:
		link = categorias.pop()		
		sub_categorias = sub_categorias.union(visit_static_url(link, busca_sub_categoria))
	
	visit_dinamic_url(sub_categorias, set_produtos_categ)


def busca_sub_categoria (soup_element, url):
	"""
		Funcao para pegar todas as subcategorias de uma determinada categoria
	"""

	sub_categorias = set ()
	div_sub_categorias = soup_element.find('ul', { "class" : "list"}).find('li', { "class" : "active" }).findAll('a')[1:]
	for sub_categ in div_sub_categorias:
		sub_categorias.add(sub_categ.attrs['href'].split("/")[1])
		
	return sub_categorias

	
def set_produtos_categ (soup_element, url, visitados):
	"""
		funcao para pegar todos os produtos de uma sessao e imprimir no arquivo de saida
	"""
	
	#Guarda a sessao visitada
	sessao = url
	
	#abre arquivo de saida no modo "append" e com buffer = 1 (grava direto em disco sem precisar fechar)
	fh = open (file_dist,'a',1)
	
	#seleciona os produtos, pega as informaçoes de interesse e imprime no arquivo de saida
	div_produtos = soup_element.findAll('div', {"class" : "details"})
	for prod in div_produtos:
		aux = prod.find('a', { "class" : "ng-binding" })
		link = aux.attrs['href'].split("/")[1]
		if link not in visitados:
			visitados.add(link)
			#Apelei por nao conseguir tratar corretamente a codificacao de acentuacao do nome.
			aux_prod = aux.attrs['href'].split("/")[1].split("-")
			nome_aux = ''
			for nome in aux_prod:
				nome_aux += nome + " "
			#fim da apelacao
			produto = {
				'produto': nome_aux.strip(),
				'preco': prod.find('span', { "class" : "actual-price" }).getText().strip().split(" ")[1],
				'url': link,
				'sessao' : sessao,
				'links': "",
			}
			fh.write(to_string(produto))

	fh.close()		
	
	
	
	
def set_date ():	
	"""
		funcao para coletar a data do dia "sysdate"
	"""
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d')


def to_string (json_object):
	"""
		funcao para formatar produto no layout do arquivo de saida
	"""
	__nome_produto = json_object['produto'].encode('utf-8')
	__preco = json_object['preco'].encode('utf-8')
	__url = json_object['url'].encode('utf-8')
	__sessao = json_object['sessao'].encode('utf-8')
	__final = __nome_produto + ";" + __preco + ";" + __sessao + ";" + __url + "\n"
	
	return __final.encode('utf-8')
	
	
if __name__ == '__main__':

	#criando variaveis de controle
	produtos = []
	
	#setando sysdate
	data_atual = set_date()
	
	#cria arquivo de saida
	file_dist = 'crawler_prix_' + data_atual + '.csv'
	
	#Cria Display para renderizar pagina JS e chama funcao que visita paginas estaticas
	#Comecando pela "bem-estar" para ter um ponto de partida
	with Display(visible=0, size=(800, 600)):
		visit_static_url("bem-estar",busca_categoria)

