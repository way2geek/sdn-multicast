import json
import httplib


class FlowEntry():

	def __init__ (self, dpid, priority=1):
		self._dpid = dpid
		self._priority = priority
		self._matches = {}
		self._actions = []

	def addMatch (self, field, value):
		self._matches[field] = value

	def addAction (self, action, **params):
		action = {'type': action}
		for key in params:
			action[key] = params[key]
		self._actions.append(action)

	def install (self):
		body = self._make_request_body()
		res = self._send_request("POST", "/stats/flowentry/add", body)

	def delete (self):
		body = self._make_request_body()
		res = self._send_request("POST", "/stats/flowentry/delete", body)

	def _make_request_body (self):
		obj = {}
		obj['dpid'] = self._dpid
		obj['priority'] = self._priority
		obj['match'] = self._matches
		obj['actions'] = self._actions
		return json.dumps(obj)

	def _send_request (self, method, url, body):
		conn = httplib.HTTPConnection("127.0.0.1", 8080)
		conn.request(method, url, body)
		res = conn.getresponse()
		return res


class GroupEntry():

	def __init__ (self, dpid, grpid, grptype):
		self._dpid = dpid
		self._grpid = grpid
		self._type = grptype
		self._buckets = []

	def addBucket (self, weight=0):
		self._buckets.append({'weight': weight, 'actions': []})

	def addAction (self, bucket, action, **params):
		if not bucket < len(self._buckets):
			print "** Bucket %d does not exist **" % bucket
			return
		action = {'type': action}
		for key in params:
			action[key] = params[key]
		self._buckets[bucket]['actions'].append(action)

	def install (self):
		body = self._make_request_body()
		res = self._send_request("POST", "/stats/groupentry/add", body)

	def delete (self):
		body = self._make_request_body()
		res = self._send_request("POST", "/stats/groupentry/delete", body)

	def _make_request_body (self):
		obj = {}
		obj['dpid'] = self._dpid
		obj['group_id'] = self._grpid
		obj['type'] = self._type
		obj['buckets'] = self._buckets
		return json.dumps(obj)

	def _send_request (self, method, url, body):
		conn = httplib.HTTPConnection("127.0.0.1", 8080)
		conn.request(method, url, body)
		res = conn.getresponse()
		return res
