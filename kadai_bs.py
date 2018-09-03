import requests
from time import sleep
from bs4 import BeautifulSoup
import re
import shelve


def device_decision():
    #  ゲームの機種ごとのURLをkeyを機種名valueにして返す
    devices = {}
    url = 'https://www.famitsu.com/schedule/'
    url_res = requests.get(url)
    url_content = url_res.content
    url_soup = BeautifulSoup(url_content, 'html.parser')
    device = url_soup.select('li[data-platform]')
    for i in device:
        devices[i.getText().strip('\n')] = 'https://www.famitsu.com{}'.format(i.a['href'])
    return devices


def user_select_device(devices):
    # ユーザにデバイス選択時に入力を簡略化
    device_names = list(devices.keys())
    print('デバイスを選んでください')
    for k, i in enumerate(device_names):
        print('{}:{} '.format(k, i), end="")
    print('')
    user_select = int(input())
    select_device = device_names[user_select]
    return select_device


def selection_device(devices_list, select_device):
    select = devices_list[select_device]
    print(select)
    return select


def loop_url(url):
    # ユーザが選択したデバイスの全urlを取得する関数
    url_list = [url]
    master_url = 'https://www.famitsu.com'
    count = 0
    while count < 1:
        print('現在{}ページ目のURLを取得しています。'.format(len(url_list)))
        url_res = requests.get("".join(url_list[-1]))
        url_content = url_res.content
        url_soup = BeautifulSoup(url_content, 'html.parser')
        url_groups = url_soup.find(class_='end')
        if url_groups is None:
            break
        url_a = url_groups.find('a')
        if url_a is None:
            break
        url_list.append(master_url+url_a['href'])
        sleep(0.5)
    return url_list


def isExistNextUrl(url):
    #  次のページがあるかどうかを調べる
    #  あればURLなければNoneを返す
    master_url = 'https://www.famitsu.com'
    source = requests.get(url).content
    soup = BeautifulSoup(source)
    end_elem = soup.find(class_='end')
    if end_elem is None:
        return
    next_url = end_elem.find('a')
    if next_url is None:
        return
    next_url = master_url + next_url['href']
    return next_url


def takeGameDatas(url):
    #  1ページ分のゲームの情報を辞書化して返す
    game_datas = {}
    source = requests.get(url).content
    soup = BeautifulSoup(source)
    groups = soup.find_all(class_='itemBlockWrap')
    for group in groups:
        date = group.find(class_='heading03 blueBorder').getText().replace('\n', '')
        game_data = {}
        for game in group.find_all('li'):
            price_elem = game.find(class_='price')
            if price_elem is not None:
                price = price_elem.getText().replace('\n', '')
            else:
                price = 'None'
            itemName = list(filter(lambda x: len(x) != 0, game.find(class_='itemName').getText().split('\n')))
            device = itemName[0]
            name = itemName[1]
            game_data[name] = {'name': name, 'device': device, 'price': price}
        game_datas[date] = game_data
    return game_datas


def check_game_data(game_datas):
    game_data = len(game_datas)
    if game_data == 0:
        sleep(0.5)
        print('ゲームデータが存在しません。')
        print('他のデバイスを選択してください。')
    return game_datas


def takeAllGameData(url):
    datas = []
    while url is not None:
        datas.append(takeGameDatas(url))
        url = isExistNextUrl(url)
        print('page{} 取得中...\n'.format(len(datas)))
    return datas


def shapingData(datas):
    shaped_datas = []
    for data in datas:
        name = data['name']
        device = data['device']
        price = data['price']
        text = '''
{:-^30}
name   :{}
device :{}
price  :{}
'''.format(name, device, price)
        shaped_datas.append(text)
    print(shaped_datas)
    return shaped_datas


def main_prints(name, device, price):
    # デバイス名、ゲーム名、価格を整形しプリントする関数
    print('-'*50)
    print("デバイス名：{}".format(name))
    print("ゲーム名：{}".format(device))
    print(price)


def last_function():
    device_list = device_decision()
    user_select = user_select_device(device_list)
    url = selection_device(device_list, user_select)
    for url_list in loop_url(url):
        game_data = check_game_data(takeGameDatas(url_list).items())
        for i, v in game_data:
            print('\n')
            print('発売予定日は{}'.format(i))
            for d, k in v.items():
                main_prints(k['name'], k['device'], k['price'])


if __name__ == '__main__':
    last_function()
