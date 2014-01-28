#!C:\Python27\python
# -*- coding: UTF-8 -*-

import cgi
import cgitb
import sys
import xml.parsers
import xmlformatter.formatter

# TODO error handling long document eg. Workshop-Postgresql.xml
# appends chunk in opera!!! fireox never observed

# enable debugging
cgitb.enable()

MAX_DOC_SIZE = 5000000
PROJECT_HOME = "http://www.pamoller.com/XmlFormatter.html"

class CgiHandler():
	params = []
	error = []
			
	def __init__(self):
		try:
			self.params = cgi.parse()
			self.validate()
		except:
			self.error.append("Input invalid")
		else:
			self.response()

	def __str__():
		raise NotImplementedError()

	@property
	def header(self):
		return "Content-type: text/html\n\n"

	def validate(self):
		raise NotImplementedError()

	def response(self):
		raise NotImplementedError()
		
	def param_value(self, key, default="", pos=0):
		if key in self.params.keys() and self.params[key] is not None:
			if isinstance(self.params[key], list):
				return self.params[key][pos]
			return self.params[key]
		return default

class CgiXmlformat(CgiHandler):
	doc=""
	preserve=[]
	indent=2
	mode = ""
	def validate(self):
		self.mode = self.param_value('mode')
		self.indent = int(self.param_value('indent', 2))
		self.preserve = self.param_value('preserve').replace(",", " ").split()
		if 0 < len(self.param_value('file')) < MAX_DOC_SIZE:
			self.doc = self.param_value("file")
		elif 0 <= len(self.param_value('doc')) < MAX_DOC_SIZE:
			self.doc = self.param_value("doc")
		else:
			self.error.append('max document size (%s) exceeded' %MAX_DOC_SIZE)

	def response(self):
		try:
			self.formatter = xmlformatter.formatter.Formatter(encoding_output="UTF-8", indent=self.indent, preserving=self.preserve)
			self.doc = self.formatter.format_string(self.doc)
		except xml.parsers.expat.ExpatError as (error):
			self.error.append("XML Error: %s" %error)
		except:
			self.error.append("Input Error")

	def __str__(self):
		str = self.header
		str += '<!DOCTYPE html>'
		str += '<html>'
		str += '  <head>'
		str += '  <meta charset="UTF-8">'
		str += '    <title>Python XmlFormatter</title>'
		str += '    <style>'
		str += '      body {background-color:#3b3b3b; font-family:Arial, sans}'
		str += '      h1 { margin:0; padding:0; line-height:1;}'
		str += '      #page {padding:1% 2%; border-radius:0.4em; background-color:#eef; margin:3%;}'
		str += '      div { margin-top:1em;} '
		str += '      textarea { width:98%; height:15em; padding:0.2em	}'
		str += '      p { background-color: #eef; padding:0.3em; }'
		str += '      nav ul {padding:0; list-style:none;margin:0;}'
		str += '      nav ul li {border-radius:0.4em; display:inline; padding:0.2em; padding-right:0.5em; background-color:#3b3b3b; padding-bottom:1.5em; margin-right:0.2em;}'
		str += '      nav a { color:#fff; font-weight:bold; text-decoration:none;}'
		str += '      .input {background-color:#3b3b3b; margin:0; padding:1em 0.4em;}'
		str += '      input[type=file] {width:30%}'
		str += '    </style>'
		str += '  </head>'
		str += '  <body>'
		str += '    <div id="page">'
		str += '      <h1>Python - XmlFormatter Online</h1>'
		if (self.error):
			str += '      <p style="color:red;font-weight:bold">%s</p>' %", ".join(self.error)
		else:
			str += '      <p>Format or compress XML-documents using <a href="%s">Python XmlFormatter</a>. </p>'  %PROJECT_HOME
		str += '	  <nav><ul><li><a href="?mode=direct_input">Direct Input</a></li><li><a href="?mode=file_input">Upload</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</li><li><a href="?mode=about">About</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</li></ul></nav>'
		str += '      <form action="xmlformat.cgi" enctype="multipart/form-data" method="post">'
		if self.mode == 'file_input':
			str += '        <div class="input"><input type="file" id="file" name="file" value=""/></div>'
		elif self.mode == 'about':
			str += '        <div class="input"><p style="height:15em"><a href="%s">XmlFormatter</a> is an Open Source Python (2) class, who provides formatting of XML documents. This formatter differs from others by handling whitespaces by a distinct set of formatting rules (see below) - thinking element content as objects and mixed content as a written text. But formatting is suspended for elements marked as preserve.<br/><br/>Use Indent slider for indenting elements content and input a list of comma or blank separated list of elements to be whitespace preserved for.</p></div>' %PROJECT_HOME
		else:
			str += '        <div class="input"><textarea id="doc" name="doc">%s</textarea></div>' %cgi.escape(self.doc)
		str += '        <div>'
		str += '          <input type="submit" value="Format"/>'
		str += '          Indent <input type="range" name="indent" max="10" min="0" step="1" value="%s"/>  ' %self.indent
		str += '          Preserve <input type="text" name="preserve" value="%s"/>' %" ".join(self.preserve)
		str += '        </div>'
		str += '      </form>'
		str += '    </div>'
		str += '  </body>'
		str += '</html>'

		return str

print CgiXmlformat()