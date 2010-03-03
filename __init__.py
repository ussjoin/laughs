from google.appengine.api import apiproxy_stub_map, urlfetch_stub

apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
apiproxy_stub_map.apiproxy.RegisterStub('urlfetch',urlfetch_stub.URLFetchServiceStub())

from google.appengine.api import urlfetch
import simplejson as json

class TahoeFile(object):
	def __init__(self, baseuri, rocap = '', rwcap = '', vcap = ''):
		self.baseuri = baseuri
		self.rocap = rocap
		self.rwcap = rwcap
		self.vcap = vcap
		self.info = ''
		
	def checkExistence(self):
		try:
			self.refreshInfo()
		except urllib2.URLError, e:
			return False
		return True
			
	def refreshInfo(self):
		uri = self.rwcap
		if (uri == ''):
			uri = self.rocap
		uri = self.baseuri+uri
		res = urlfetch.fetch(uri+"?t=json")
		body = res.content
		self.info = json.loads(body)
		self.info = self.info[1]
		self.rocap = self.info.get('ro_uri')
		self.rwcap = self.info.get('rw_uri')
		self.vcap = self.info.get('verify_uri')
	
	def getURI(self):
		return self.baseuri + self.rocap
	
	def getInfo(self):
		if (self.info == ''):
			self.refreshInfo()
		return self.info
		
	def getKids(self):
		info = self.getInfo()
		ret = {}
		if info.has_key('children'):
			for key in info['children']:
				kid = info['children'][key][1]
				child = TahoeFile(self.baseuri, kid.get('ro_uri'), kid.get('rw_uri'), kid.get('verify_uri'))
				ret[key] = child
		return ret
	
	def addchild(self, name, cap):
		if (self.rwcap != ''):
			uri = self.baseuri + self.rwcap
			if (uri[len(uri)-1] != '/'):
				uri += '/'
			uri += name
			res = urlfetch.fetch(uri + "?t=uri", method=urlfetch.PUT, payload=cap)
			if res.status_code == 200:
				return True
			else:
				return res.status_code
		else:
			return False
			
			
	def mkdir(self, name):
		if (self.rwcap != ''):
			uri = self.baseuri + self.rwcap
			res = urlfetch.fetch(uri + "?t=mkdir", method=urlfetch.POST)
			newrwcap = res.content
			self.addchild(name, newrwcap)
			return True
		else:
			return False
		
	def delete(self):
		if (self.rwcap != ''):
			uri = self.baseuri + self.rwcap
			res = urlfetch.fetch(uri, method=urlfetch.DELETE)
			if (res.status_code == 200):
				return True
			else:
				return res
		return False
		
	

