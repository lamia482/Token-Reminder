import os, sys, time
import datetime
import re
import json
import numpy as np
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level = logging.INFO)
import smtplib
from email.message import EmailMessage


class MinerNotaficator:
  '''
  '''
  def __init__(self, url = None, email_address = None, delay_time = None):
    '''
    '''
    self._pid = os.getpid()
    self._msg = ''
    self._today_date = None
    self._today_filename = None
    self._today_file = None
    self._today_values = []
    self._all_values = {}
    self.set_url(url)
    self.set_email_address(email_address)
    self.set_delay_time(delay_time)
    return

  def today_date(self):
    '''
    '''
    return self._today_date
    
  def set_today(self):
    '''
    '''
    self._today_values = []
    self._today_date = str(datetime.date.today())
    self._today_filename = os.path.join('log', self._today_date + '.log')
    self._today_file = open(self._today_filename, 'w')
    return
    
  def shut_yesterday(self):
    '''
    '''
    if self._today_file is not None:
      self._today_file.close()
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
    
  def pull(self, tokens):
    '''
    '''
    info = {}
    for token in tokens:
      value = reminder.fetch(token)
      info[token] = value
    return info
    
  def remind(self, values, notes):
    '''
    '''
    values = np.array([i for i in values])
    notes = np.array(notes)
    status = np.sum(values >= notes)
    if status > 0:
      reminder.send_email(reminder.message())
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
      content = content + i + ' = ' + str(info[i]) + ', '
    self._today_values.append(value)
    ttime = ttime.split('.')[0]
    self._msg = str(ttime) + ' >> ' +  content[0:len(content)-2] + ' $USD\n'
    logging.info(self._msg)
    self._today_file.write(self._msg)
    return
  
  def save_to_all(self, date):
    '''
    '''
    self._all_values[date] = self._today_values
    return
    
  def send_email(self, content = None, email_address = None):
    '''
    '''
    if self._today_date is None:
      return
    content = '' if content is None else content
    email_address = self._email_address if email_address is None else email_address
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = 'mining notification - ' + self._today_date
    msg['From'] = 'account@example.com' # 'laMia.mining.notification@auto'
    msg['To'] = email_address
    
    s = smtplib.SMTP()
    s.connect('smtp.qq.com', 587)
    s.starttls()
    s.login(msg['From'], 'pwd@example.com')
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
  os.system('clear && mkdir -p log')
  website = 'https://www.coingecko.com/en/price_charts/{}/usd'
  reminder = MinerNotaficator(website, '1216352472@qq.com', 5)
  while reminder.keep_alive() is True:
    if reminder.is_next_day() is True:
      reminder.save_to_all(reminder.today_date())
      reminder.send_email(reminder.message())
      reminder.shut_yesterday()
      reminder.set_today()
    
    token = ['huobi-token', 'ripple', 'ethereum', 'zcash']
    vnote = [2.650, 0.950, 870, 410]
    info = reminder.pull(token)
    reminder.save_to_today(str(datetime.datetime.now()), info)
    reminder.remind(info.values(), vnote)
    
    reminder.delay(300)
  