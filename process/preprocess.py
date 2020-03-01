#coding:utf-8
import sys
import codecs
from pyltp import SentenceSplitter
import os
import random

from langconv import *

def simple2tradition(line):
    # 将简体转换成繁体
    line = Converter('zh-hant').convert(line)
    line = line.encode('utf-8')
    return line


def tradition2simple(line):
    # 将繁体转换成简体
    line = Converter('zh-hans').convert(line)
    line = line.encode('utf-8')
    return line
zn_punc = "！？｡＂＃＄％＆＇。（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
max_sentence_length = 5
bad_keywords = set()
source_dir = sys.argv[1]
start_index = int(sys.argv[2])
target_path = source_dir + "/../clue_pretrain_data/"
if not os.path.exists(target_path):
  os.mkdir(target_path)
if not os.path.exists(target_path + "train"):
  os.mkdir(target_path + "train")
if not os.path.exists(target_path + "dev"):
  os.mkdir(target_path + "dev")
if not os.path.exists(target_path + "test"):
  os.mkdir(target_path + "test")
file_prefix_train= target_path + "/train/clue_pretrain_"
file_prefix_dev= target_path + "/dev/clue_pretrain_"
file_prefix_test= target_path + "/test/clue_pretrain_"

with codecs.open("bad_keywords.txt", "r", "utf-8", errors="ignore") as input:
  for line in input:
    bad_keywords.add(line.strip())
import re
zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

def contain_zh(word):
    '''
    判断传入字符串是否包含中文
    :param word: 待判断字符串
    :return: True:包含中文  False:不包含中文
    '''
    global zh_pattern
    match = zh_pattern.search(word)

    return match
import string
def is_punc(uchar):
    if uchar  in string.punctuation:
        return True
    else:
        return False
"""判断一个unicode是否是汉字"""
def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False
"""判断一个unicode是否是数字"""
def is_number(uchar):
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False
"""判断是否是一个中文标点"""
def is_zh_punc(uchar):
    if uchar in zn_punc:
        return True
    else:
        return False
"""判断一个unicode是否是英文字母"""
def is_alphabet(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False
"""判断是否是（汉字，数字和中文/英文字符之外的）其他字符"""
def is_other(uchar):
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar) or is_zh_punc(uchar) or is_space(uchar) or is_punc(uchar)) :
        return True
    else:
        return False

def is_space(uchar):
    if uchar == " ":
        return True
    else:
        return False

def filter_others_char(sent):
    new_sent = ""
    for s in sent:
        if is_other(s):
            continue
        new_sent += s
    return new_sent

def contain_bad_keywords(sentence):
    for item in bad_keywords:
      if item in sentence:
          return True
    return False

def filter_first_punc(buf):
  #print("buf:",buf)
  while True:
    if not buf:
      return buf
    #print(buf)
    if is_punc(buf[0]) or is_zh_punc(buf[0]):
      buf =  buf[1:]
    else:
      return buf

def many_same_sent_num(sent_res):
    if sent_res and sent_res[0]:
        first_sent = sent_res[0]
    else:
        return sent_res
    num = 0
    short_num = 0
    for sent in sent_res:
        if len(sent) < 15:
            short_num += 1
        if same_char_num(first_sent, sent) >= 2:
            num += 1

    if num > 5 or short_num > 5:
        return True
    else:
        return False

def same_char_num(s1, s2):
    return len(set(list(s1)) & set(list(s2)))
def split_by_space(sent):
    sent = sent.replace("&#0;", "")
    sents = sent.split(" ")
    sent_set = set()
    sent_res = []
    if len(sents) < 10:
        s = filter_first_punc(filter_others_char(sent))
        if len(s) > max_sentence_length :
            sent_res.append(filter_first_punc(filter_others_char(sent)))
    else :
        for s in sents:
            #print("s:",s)
            s = filter_first_punc(filter_others_char(s))
            #print(s)
            if s in sent_set or len(s) <= max_sentence_length or s.isdigit() or not contain_zh(s):
                continue
            if sent_res and same_char_num(s, sent_res[-1]) >= 0.5 * len(s):
                continue
            sent_res.append(s)
            sent_set.add(s)
    if many_same_sent_num(sent_res):
        sent_res = []
    return sent_res



def to_str(bytes_or_str):
  if isinstance(bytes_or_str, bytes):
    value = bytes_or_str.decode('utf-8')
  else:
    value = bytes_or_str
  return value

def filter(sents):
    result = []
    result_set = set()
    for sent in sents:
        #print("sent:",sent)
        s = split_by_space(sent)
        for item in s:
            if item and item not in result_set :
               # print("item:", item, "result_set:",result_set)
                result.append(item)
                result_set.add(item)
    return "\n".join(result)

def Split(filename, size, start_index):
  fp = codecs.open(filename, 'r', "utf-8", errors="ignore")
  i = start_index
  n = 0
  index = "0000000" + str(i)
  temp_train = codecs.open(file_prefix_train + index[-7:] + ".txt",'w', "utf-8")
  temp_dev = codecs.open(file_prefix_dev + index[-7:] + ".txt",'w', "utf-8")
  temp_test = codecs.open(file_prefix_test + index[-7:] + ".txt",'w', "utf-8")
  temp_prev_train = []
  temp_prev_dev = []
  temp_prev_test = []
  new_file = True
  for buf in fp:
    buf = filter_first_punc(buf.strip())
    if contain_bad_keywords(buf) or buf.count("/") > 10 :
      continue
    if n == size:
      n = 0
      i += 1
      index = "000000" + str(i)
      temp_train = codecs.open(file_prefix_train + index[-7:] + ".txt",'w', "utf-8")
      temp_dev = codecs.open(file_prefix_dev + index[-7:] + ".txt",'w', "utf-8")
      temp_test = codecs.open(file_prefix_test + index[-7:] + ".txt",'w', "utf-8")
      new_file = True
    buf = tradition2simple(buf)
    #buf = "".join(buf.split())
    #print("buf:", buf)
    sents = SentenceSplitter.split(buf)
    try:
      buf = filter(sents)
      #print(buf)
      if not buf or len(buf) < 128 :
          continue
    except UnicodeDecodeError:
      print("UnicodeDecodeError")
      continue
    if not buf:
      if buf not in temp_prev_dev and temp_prev_dev:
        temp_dev.write(buf + "\n")
        temp_prev_dev.append(buf)
        temp_prev_dev = temp_prev_dev[-3:]
      if buf not in temp_prev_test and temp_prev_test:
        temp_test.write(buf + "\n")
        temp_prev_test.append(buf)
        temp_prev_test = temp_prev_test[-3:]
      if buf not in temp_prev_train and temp_prev_train:
        temp_train.write(buf + "\n")
        temp_prev_train.append(buf)
        temp_prev_train = temp_prev_train[-3:]
      continue
    buf = buf + "\n"
    rd = random.random()
    if rd < 0.005:
      if buf in temp_prev_dev:
        continue
      if not temp_prev_dev and not buf:
        continue
      temp_dev.write(buf + "\n")
      temp_prev_dev.append(buf)
      temp_prev_dev = temp_prev_dev[-3:]
    elif rd > 0.995:
      if buf in temp_prev_test:
        continue
      if not temp_prev_test and not buf:
        continue
      temp_test.write(buf + "\n")
      temp_prev_test.append(buf)
      temp_prev_test = temp_prev_test[-3:]
    else:
      #print("buf:", buf, "temp_prev_train:", temp_prev_train)
      if buf in temp_prev_train:
        continue
      if not temp_prev_train and not buf:
        continue
      # if len(buf)<mini_length and len(buf)>1: continue # add by xul 太短的文本（并且）不是空行，怎不需要写入了
      temp_train.write(buf + "\n")
      temp_prev_train.append(buf)
      temp_prev_train = temp_prev_train[-3:]
    if buf:
      n += 1
  print("Finish: " + filename + ", end index:" + str(i))
  temp_dev.close()
  temp_test.close()
  temp_train.close()
  fp.close()
  if not os.path.exists(file_prefix_train + index[-7:] + ".txt") or not os.path.getsize(file_prefix_train + index[-7:] + ".txt"):
    new_file = False
  if os.path.exists(file_prefix_dev + index[-7:] + ".txt") and not os.path.getsize(file_prefix_dev + index[-7:] + ".txt"):
    os.remove(file_prefix_dev + index[-7:] + ".txt")
  if os.path.exists(file_prefix_test + index[-7:] + ".txt") and not os.path.getsize(file_prefix_test + index[-7:] + ".txt"):
    os.remove(file_prefix_test + index[-7:] + ".txt")
  if new_file:
    return i + 1
  else:
    return i

def find_files(root_dir):
  all_files = []
  for root, dirs, files in os.walk(root_dir, topdown=False):
    for name in files:
        all_files.append(os.path.join(root, name))
  return all_files

if __name__ == "__main__":

    files = find_files(source_dir)
    size = 2
    print("files num:", len(files))
    for file in files:
        start_index = Split(file, 3500 * size, start_index)
    print("End index: ", start_index - 1)

'''
    string1 = u'收割季节 麦浪和月光 洗着快镰刀'
    string2 = u'LWT-1系列�N管�C用于在包�b物外表面粘�N吸管、勺、叉等食具，LWT-1系列�N管�C�c�慧股份生�a的LWT-2系列粘�N�C相比，�m然速度�^慢，国产在线自天天人人_,2018最新福利天堂视频_,天天燥夜夜b在线视频_但是同�泳哂行阅芊�定，易于�S�o的特�c，而且�r格更便宜，具有很好的性�r比。'
    #string1 = 'Sky0天地Earth1* '
    #string1 = " "
    sents = SentenceSplitter.split(string2)

    print("\n".join([split_by_space(s) for s in sents]))
    
    for item in string2:
        #print (is_chinese(item))
        #print (is_number(item))
        #print (is_alphabet(item))
        print (is_other(item))
        #print (is_zh_alphabet(item))
        #print(is_space(item))

'''

