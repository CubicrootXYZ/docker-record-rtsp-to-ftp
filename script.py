#!/usr/bin/env python
#
# This file is licensed under the terms of the GPL, Version 3
#
# Copyright 2018 Tamas Kinsztler <https://github.com/humpedli>

__author__ = 'Tamas Kinsztler'
__copyright__ = 'Copyright (C) Tamas Kinsztler'
__license__ = 'GPLv3'
__version__ = '1.0'

import subprocess
import sys
import json
from datetime import datetime
from sys import argv
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import ftputil 

# HTTP server class
class MyServer(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_HEAD(self):
		self._set_headers()

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = json.loads(self.rfile.read(content_length))
		try:
			if post_data['name'] and post_data['duration'] and post_data['stream_url'] and post_data['host'] and post_data['user'] and post_data['password']:
				t = threading.Thread(target=record_and_upload, args=[post_data])
				t.setDaemon(False)
				t.start()
				self._set_headers()
				self.wfile.write(bytes('{"done": true}', 'utf-8'))
				
		except Exception as e:
			print(e)
			self._set_headers()
			self.wfile.write(bytes('{"done": false}', 'utf-8'))

# Record and upload data
def record_and_upload(post_data):
	file_name = datetime.today().strftime('%Y%m%d_%H%M%S') + '_' + post_data['name'] + '.mp4'
	print('Start recording: {}'.format(file_name))
	connection_string = f"ftp://{post_data['user']}:{post_data['password']}@{post_data['host']}"
	process = subprocess.Popen(('ffmpeg -rtsp_transport tcp -y -i {} -t {} -vcodec libx264 -crf 20 -acodec copy /tmp/{} && curl --upload-file /tmp/{} {}{} && rm /tmp/{} > /dev/null'.format(post_data['stream_url'], post_data['duration'], file_name, file_name,connection_string, '/' + file_name, file_name)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = process.communicate()
	errcode = process.returncode
	print('Recorded and uploaded file: {}'.format(file_name))
	clean_ftp(post_data)

def clean_ftp(post_data):
	print("Deleting files > 14 days")
	host = ftputil.FTPHost(post_data['host'], post_data['user'], post_data['password'])
	now = time.time()
	names = host.listdir(host.curdir)
	for name in names:
		if host.path.getmtime(name) < (now - (14 * 86400)):
			if host.path.isfile(name):
				host.remove(name)


	print ('Closing FTP connection')
	host.close()

# Main Loop
def main_loop(port=11122):
	print('Started http server on port: {}'.format(port))
	HTTPServer(('', port), MyServer).serve_forever()

# Start main loop
try:
	if len(argv) == 2:
		main_loop(port=int(argv[1]))
	else:
		main_loop()
except KeyboardInterrupt:
	print('Interrupted by keypress')
	sys.exit(0)

