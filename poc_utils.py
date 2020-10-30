#--------さわるな危険--------

from pixivpy3 import PixivAPI
from pixivpy3 import AppPixivAPI
import json
import os
from time import sleep
import matplotlib.pyplot as plt
from google.colab.patches import cv2_imshow
import cv2
import math

def login(id, password):
  api = PixivAPI()
  api.login(id, password)
  return api

def binary_search(apilogin, range_num):
  api = apilogin
  aapi = AppPixivAPI()

  head = 1
  tail = range_num
  while head <= tail:
    errorcount = 0
    target = (head + tail) // 2
    for i in range(2):
      json_result = api.search_works(searchtag, page=target+i, mode='tag')
      try:
        illust_len = len(json_result.response)
      except TypeError as e:
        errorcount = errorcount + 1
      sleep(0.2)
    if errorcount == 1:
      return target
    elif errorcount == 0:
      head = target + 1
    else:
      tail = target - 1

def clearLabel(_ax):
  _ax.tick_params(labelbottom="off",bottom="off")
  _ax.tick_params(labelleft="off",left="off")
  _ax.set_xticklabels([]) 
  _ax.axis('off')
  return _ax

def binary_check(searchtag, apilogin, range_num):
  api = apilogin
  aapi = AppPixivAPI()

  json_result = api.search_works(searchtag, page=range_num, mode='tag')
  try:
    illust_len = len(json_result.response)
  except TypeError as e:
    binary_num = binary_search(apilogin,range_num)
    if binary_num < range_num:
      range_num = binary_num
  return range_num

def search_and_save(searchtag, apilogin, min_score, range_num, dirname, R18mode):
  api = apilogin
  aapi = AppPixivAPI()
  saving_dir_path = os.path.join("/content/", dirname)
  if not os.path.exists(saving_dir_path):
    os.mkdir(saving_dir_path)

  illsut_hitsum = 0
  illsut_sum = 0
  for page in range(1, range_num + 1):
    json_result = api.search_works(searchtag, page=page, mode='tag')
    illust_len = len(json_result.response)

    illsut_sum = illsut_sum + illust_len
    illust_hit = 0

    progress = int(page / range_num * 20)
    progressbar = "["
    for i in range(progress):
      progressbar = progressbar + "*"
    for i in range(20-progress):
      progressbar = progressbar + "-"
    progressbar = progressbar + "]"
    print('\r' + "page: " + str(page) + " / " + str(range_num) + " " + str(progressbar), end = '')

    for i in range(0, illust_len):
      illust = json_result.response[i]
      score = illust.stats.score

      if score <= min_score:
        continue
      else:
        flag = 0
        for j in range(0,len(illust.tags)):
          if illust.tags[j] == "R-18":
            flag = 1
        if flag == 1 and R18mode == "off":
          continue 
        if flag == 0 and R18mode == "on":
          continue
        illust_hit = illust_hit + 1
        aapi.download(illust.image_urls.px_480mw, path=saving_dir_path)
        sleep(1)
    illsut_hitsum = illsut_hitsum + illust_hit
  print('\n' + "完了! " + str(illsut_hitsum) + " / " + str(illsut_sum) + "件を取得しました！")

def gifdelete(dirname):
  path = "/content/" + dirname

  files = os.listdir(path)
  files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]

  kakuchoushi = [" "] * (len(files_file))

  for i in range(len(files_file)):
    kakuchoushi[i] = files_file[i][-4:]
    if kakuchoushi[i] == ".gif":
      os.remove(files_file[i])

def preview(dirname):
  dirname = insertbar(dirname)
  gifdelete(dirname)
  path = "/content/" + dirname

  files = os.listdir(path)
  files_file = [f for f in files if os.path.isfile(os.path.join(path, f))]

  illust_num = [" "] * (len(files_file))
  illust_name = [" "] * (len(files_file))
  for i in range(len(files_file)):
    illust_num[i]  = ""
    illust_name[i] = files_file[i][:-4]
    
    for j in range(len(files_file[i])):
      if files_file[i][j] == "_":
        break
      else:
        illust_num[i] = illust_num[i] + files_file[i][j]

  for i in range(10000):
    imgurl = ""
    fig = plt.figure(dpi=350)
    if 5*i > len(files_file)-1:
      break
    for j in range(5):
      imagenow = j +5*i
      if imagenow > len(files_file)-1:
        continue
      imgurl = imgurl + "    " + "https://www.pixiv.net/artworks/" + illust_num[imagenow]
      imgpath = dirname + "/" + files_file[imagenow]
      img = cv2.imread(imgpath)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
      height = img.shape[0]
      width = img.shape[1]
      clearLabel(fig.add_subplot(1,5,j+1))
      plt.imshow(img)
    print(imgurl)
    plt.show()  

def insertbar(dirname):
  listname = list(dirname)
  for i in range(len(listname)):
    if listname[i] == " ":
      listname[i] = '_'
  dirname = ""
  dirname = "".join(listname)
  return dirname

def generate(searchtag, R18mode):
  range_num = 666
  dirname = searchtag
  apilogin  = login("bixiv12345", "pixiv12345")  #login("ユーザーネーム","パスワード")の順で入力
  if R18mode != "off":
    if R18mode == "on":
      dirname = dirname + "(R)"
    else:
      dirname = dirname + "(A)"

  dirname = insertbar(dirname)
  binary_num = binary_check(searchtag,apilogin,range_num)
  min_score = max(int((math.log(binary_num,10)**4)*700), 2000)
  print(searchtag + " タグの画像を探索しています…(1ページにつき30枚、最大666ページ)")
  search_and_save(searchtag, apilogin, min_score, binary_num, dirname, R18mode)
  print()
  preview(dirname)
