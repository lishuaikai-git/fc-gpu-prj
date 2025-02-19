# -*- coding: utf-8 -*-
# python2 and python3

from __future__ import print_function
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import logging
import os
import time
import urllib.request
import subprocess

class Resquest(BaseHTTPRequestHandler):
    def download(self, url, path):
        print("enter download:", url)
        f = urllib.request.urlopen(url)
        with open(path, "wb") as local_file:
            local_file.write(f.read())

    def upload(self, url, path):
        print("enter upload:", url)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': os.stat(path).st_size,
        }
        req = urllib.request.Request(url, open(path, 'rb'), headers=headers, method='PUT')
        urllib.request.urlopen(req)

    def trans(self, input_path, output_path, enable_gpu):
        print("enter trans input:", input_path, " output:", output_path, " enable_gpu:", enable_gpu)

        cmd = ['ffmpeg', '-y', '-i', input_path, "-c:a", "copy", "-c:v", "h264", "-b:v", "5M", output_path]
        if enable_gpu:
            cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", input_path, "-c:v", "h264_nvenc", "-b:v", "5M", output_path]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as exc:
            print('\nreturncode:{}'.format(exc.returncode))
            print('\ncmd:{}'.format(exc.cmd))
            print('\noutput:{}'.format(exc.output))
            print('\nstderr:{}'.format(exc.stderr))
            print('\nstdout:{}'.format(exc.stdout))

    def trans_wrapper(self, enable_gpu):
        src_url = "https://your.domain/input.mp4"  # 需替换为您个人阿里云账号下的OSS，且您有可读写的权限。
        dst_url = "https://your.domain/output.flv" # 需替换为您个人阿里云账号下的OSS，且您有可读写的权限。
        src_path = "/tmp/input_c.flv"
        dst_path = "/tmp/output_c.mp4"

        if enable_gpu:
            src_url = "https://your.domain/input.mp4"  # 需替换为您个人账号下的OSS，且您有可读写的权限。
            dst_url = "https://your.domain/output.flv" # 需替换为您个人账号下的OSS，且您有可读写的权限。
            src_path = "/tmp/input_g.flv"
            dst_path = "/tmp/output_g.mp4"

        local_time = time.time()
        self.download(src_url, src_path)
        download_time = time.time() - local_time

        local_time = time.time()
        self.trans(src_path, dst_path, enable_gpu)
        trans_time = time.time() - local_time

        local_time = time.time()
        self.upload(dst_url, dst_path)
        upload_time = time.time() - local_time

        data = {'result':'ok', 'download_time':download_time, 'trans_time':trans_time, 'upload_time':upload_time}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def pong(self):
        data = {"function":"trans_gpu"}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def dispatch(self):
        mode = self.headers.get('TRANS-MODE')

        if mode == "ping":
            self.pong()
        elif mode == "gpu":
            self.trans_wrapper(True)
        elif mode == "cpu":
            self.trans_wrapper(False)
        else:
            self.pong()

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch()

if __name__ == '__main__':
    host = ('0.0.0.0', 9000)
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()