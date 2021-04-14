from pprint import pprint
from urllib import parse
import mimetypes
import requests
import datetime
import argparse
import logging
import os


def read(f):
    '''用来读取文件的'''
    try:
        # 上传的图片类型
        f_type = mimetypes.guess_type(f)[0]
        # 以时间戳为命名规则
        time = datetime.datetime.now().strftime('%F-%H-%M-%S-%f')
        f_name = "image-" + time + os.path.splitext(f)[1]
        files = [('key', (None, key)),
        ("source", (f_name, open(f, "rb"), f_type))]
        return files
    except PermissionError as e:
        print("Upload fail(上传失败): 没有权限读取")
        logging.exception(e)  # 在typora里看的更直观
        exit(0)
    except FileNotFoundError as e:
        print("Upload fail(上传失败): 文件不存在")
        logging.exception(e)
        exit(0)


def link(link):
    '''通过图片链接地址上传'''
    upurl = f"{url}/?key={key}&source={link}&format=json"
    return upurl


def upload(url, key, image_size, images):
    image_list = []
    for image in images:
        # 如果设置了“插入url图片时自动转义”的话，会自动吧路径url编码，所以这里解码
        image = parse.unquote(image)
        if image[:4] == "http":
            r = requests.get(link(image))
        else:
            r = requests.post(url, files=read(image)).json()

        try:
            r['status_code']
        except TypeError:
            r = r.json() # 在一次 json

        if r['status_code'] == 200:
            if image_size in r["image"]:
                image_url = r["image"][image_size]["url"]
            else:
                image_url = r["image"]["image"]["url"]
            image_list.append(image_url)
        else:
            print("Upload fail(上传失败):")
            pprint(r)
            exit()
    print("Upload Success(上传成功):")
    for image_url in image_list:
        print(image_url)


if __name__ == "__main__":
    description='在typora上传图片设置该脚本文件，实现粘贴图片自动上传到图床'
    epilog="python typora_chevereto.py -u url -k key -f images"
    parser = argparse.ArgumentParser(prog='图床上传', description=description, epilog=epilog)
    parser.add_argument('-f', nargs='+', required=True, help='图片的url或路径', metavar=("images", ''))
    parser.add_argument('-s', help='图片的大小，默认中等，取值 0-2（0最大）', metavar="images size", default='0', type=int)
    parser.add_argument('-k', help='http[s]://ip/dashboard/settings/api 获取key', metavar="chevereto api KEY")
    parser.add_argument('-u', help='chevereto的url，最后不要加/，http://IP/api/1/upload', metavar="chevereto api url")

    args = parser.parse_args()

    # 可以修改文件加入url和key，这样命令就不用加参数了
    key = "6056a0b8f7c4b1080d18c575e5078c32"
    url = f"https://image.zhr.red/api/1/upload"

    if args.k:
        key = args.k

    if args.u:
        url = args.u

    # api的最后不要有斜杠 /
    if url[-1:] == "/":
        url = url[:-1]

    # 图片的大小
    image_size = ['image', 'medium', 'thumb']
    image_size = image_size[args.s]

    upload(url, key, image_size, args.f)
