import os, sys, time
import datetime
import re
import json
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
import numpy as np
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level = logging.INFO)
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class MinerNotaficator:
  '''
  '''
  def __init__(self, url = None, email_address = None, delay_time = None, tokens = None):
    '''
    '''
    self._pid = os.getpid()
    self._msg = ''
    self._today_date = None
    self._today_filename = None
    self._today_file = None
    self._today_values = []
    self._all_values = {}
    self._init_max_vnotes = np.array([2.650, 0.950, 870, 410])
    self._init_min_vnotes = np.array([2.000, 0.850, 820, 360])
    self._max_vnotes = self._init_max_vnotes
    self._min_vnotes = self._init_min_vnotes
    
    self.set_url(url)
    self.set_email_address(email_address)
    self.set_delay_time(delay_time)
    self.set_tokens(tokens)
    self.set_color()
    return

  def today_date(self):
    '''
    '''
    return self._today_date
    
  def open_file(self):
    '''
    '''
    self._today_file = open(self._today_filename, mode = 'a', encoding = 'utf-8')
    return
    
  def write_file(self, msg):
    '''
    '''
    self.open_file()
    self._today_file.write(msg)
    self.close_file()
    return
    
  def close_file(self):
    '''
    '''
    self._today_file.close()
    return
    
  def set_color(self):
    '''
    '''
    self._color = []
    self._color.append((255,   0,   0))
    self._color.append((  0, 255,   0))
    self._color.append((  0,   0, 255))
    self._color.append((  0, 255, 255))
    
  def set_today(self):
    '''
    '''
    self._today_values = []
    self._today_date = str(datetime.date.today())
    self._today_filename = os.path.join('log', self._today_date + '.log')
    self._today_chart_prefix = os.path.join('chart', self._today_date)
    return
    
  def shut_yesterday(self):
    '''
    '''
    if self._today_file is not None:
      self.close_file()
    return
    
  def is_next_day(self):
    '''
    '''
    if str(datetime.date.today()) != self._today_date:
      return True
    return False
    
  def set_url(self, url = None):
    '''
    '''
    self._url = url
    return
    
  def set_email_address(self, email_address = None):
    '''
    '''
    self._email_address = email_address
    return
    
  def set_delay_time(self, delay_time = None):
    '''
    '''
    self._delay_time = delay_time
    return
    
  def set_tokens(self, tokens):
    '''
    '''
    self._tokens = tokens
    return
    
  def keep_alive(self):
    '''
    '''
    return True
    
  def fetch(self, token):
    '''
    '''
    url = self._url.format(token)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    self.delay()
    data = urlopen(req).read().decode('utf-8')
    reg_expr = r'<span class="currency-exchangable"(.*?)data-price-btc=(.*?)>(.*?)</span>'
    content = re.findall(reg_expr, data, re.S|re.M)
    content = content[0][2].split('$')[1].replace(',', '')
    value = float(content)
    return value
    
  def pull(self):
    '''
    '''
    info = {}
    for token in self._tokens:
      value = reminder.fetch(token)
      info[token] = value
    return info
    
  def remind(self, values):
    '''
    '''
    values = np.array([i for i in values])
    
    max_status = (values >= self._max_vnotes).astype(np.float)
    if np.sum(max_status) > 0:
      reminder.draw_save_chart()
      reminder.send_email(reminder.message() + '\nhas climbed over max\n')
      self._max_vnotes = self._max_vnotes * (1 + max_status * 0.01)
      self._min_vnotes = self._init_min_vnotes
      
    min_status = (values <= self._min_vnotes).astype(np.float)
    if np.sum(min_status) > 0:
      reminder.draw_save_chart()
      reminder.send_email(reminder.message() + '\nhas dropped to min\n')
      self._min_vnotes = self._min_vnotes * (1 - min_status * 0.01)
      self._max_vnotes = self._init_max_vnotes
    
    return
    
  def message(self):
    '''
    '''
    return self._msg
    
  def save_to_today(self, ttime, info):
    '''
    '''
    value = []
    content = ''
    for i in info:
      value.append(info[i])
      content = content + i + ' = ' + '{:.4f}'.format(info[i]) + ', '
    self._today_values.append(value)
    ttime = ttime.split('.')[0]
    self._msg = str(ttime) + ' >> ' +  content + '$USD'
    logging.info(self._msg)
    self.write_file(self._msg + '\n')
    return
  
  def _extract(self, line, token):
    '''
    '''
    price = float(re.findall(token + ' = (.*?),', line, re.S|re.M)[0])
    return price
  
  def draw_save_chart(self):
    '''
    '''
    if self._today_filename is None:
      return
    prices = {}
    for token in self._tokens:
      prices[token] = []
    with open(self._today_filename, 'r') as fp:
      while True:
        line = fp.readline()
        if line is '':
          break
        for token in self._tokens:
          price = self._extract(line, token)
          prices[token].append(price)
      for token in self._tokens:
        plt.clf()
        plt.plot(prices[token])
        plt.savefig(self._today_chart_prefix + '.' + token + '.jpg')
    return
  
  def save_to_all(self, date):
    '''
    '''
    self.draw_save_chart()
    self._all_values[date] = self._today_values
    return
    
  def send_email(self, content = None, email_address = None):
    '''
    '''
    if self._today_date is None:
      return
    content = '' if content is None else content
    content = 'Hi laMia, belows are the prices of tokens today, details seen in the attached\n' + content
    email_address = self._email_address if email_address is None else email_address
    
    msg = MIMEMultipart()
    msg['Subject'] = 'mining notification - ' + self._today_date
    msg['From'] = 'address_here' # 'laMia.mining.notification@auto'
    msg['To'] = email_address
    
    # full text
    puretext = MIMEText(content)
    msg.attach(puretext)
    # log file attached
    with open(self._today_filename, 'rb') as txt_attach:
      txt_attach = MIMEApplication(txt_attach.read())
      txt_attach.add_header('Content-Disposition', 'attachment', filename = self._today_filename)
      msg.attach(txt_attach)
    # tendency chart upon log file
    for token in self._tokens:
      chart_file = self._today_chart_prefix + '.' + token + '.jpg'
      try:
        with open(chart_file, 'rb') as image_attach:
          image_attach = MIMEApplication(image_attach.read())
          image_attach.add_header('Content-Disposition', 'attachment', filename = chart_file)
          msg.attach(image_attach)
      except FileNotFoundError as ex:
        continue
    
    s = smtplib.SMTP()
    s.connect('smtp.qq.com', 587)
    s.starttls()
    s.login(msg['From'], 'password_here')
    s.send_message(msg)
    s.quit()
    logging.info('send email to {} succeed'.format(email_address))
    return
  
  def delay(self, delay_time = None):
    '''
    '''
    delay_time = self._delay_time if delay_time is None else delay_time
    time.sleep(delay_time)
    return
    

if __name__ == '__main__':
  os.system('clear && mkdir -p log && mkdir -p chart')
  website = 'https://www.coingecko.com/en/price_charts/{}/usd'
  reminder = MinerNotaficator(website, 'address_here', 5)
  while reminder.keep_alive() is True:
    
    if reminder.is_next_day() is True:
      reminder.draw_save_chart()
      reminder.send_email(reminder.message())
      reminder.shut_yesterday()
      reminder.set_today()
    
    token = ['huobi-token', 'ripple', 'ethereum', 'zcash']
    reminder.set_tokens(token)
    info = reminder.pull()
    reminder.save_to_today(str(datetime.datetime.now()), info)
    reminder.remind(info.values())
    
    reminder.delay(60)
  
