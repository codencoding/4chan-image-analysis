import pandas as pd
import numpy as np
import urllib, json, os, datetime, time, requests
from unidecode import unidecode
import unicodecsv as csv

def get_threads(data):
    threads = []
    for page in data:
        for thread in page["threads"]:
            threads.append(thread)
            
    return threads

def get_thread_posts(thread_no, board):
    time.sleep(1)
    response = requests.get("https://a.4cdn.org/" + board + "/thread/" + str(thread_no) + ".json")
    if response.ok:
        return eval(response.content)["posts"]
    else:
        return None
    
def get_complete_df(threads):
    posts = []
    thread_num = 0
    for thread in threads:
        for post in thread:
            post["thread_id"] = thread_num
        posts += thread
        thread_num += 1
        
    return pd.DataFrame(posts)

def download_images(df, board, save_dir):
    img_types = [".jpg", ".png"]
    image_df = df[df.ext.apply(lambda row:row in img_types)][["tim", "ext"]].dropna()
    images = image_df["tim"].apply(int).apply(str) + image_df["ext"]
    
    # Filter out already downloaded images
    downloaded_imgs = os.listdir(save_dir + board + '/')
    images = images[~images.apply(lambda img:img in downloaded_imgs)]
    
    if len(images) == 0:
        print("All images already downloaded")
        return
    elif len(images) > 3600:
        completion_time = round(len(images) / 3600, 3)
        print("Minimum time to completion: {} hours".format(completion_time))
    elif len(images) > 60:
        completion_time = round(len(images) / 60, 3)
        print("Minimum time to completion: {} minutes".format(completion_time))
    else:
        completion_time = round(len(images), 3)
        print("Minimum time to completion: {} seconds".format(completion_time))
    
    im_count = 0
    for image in images:
        # API rules ask for a 1 second delay between requests
        time.sleep(1)
        try:
            img = requests.get("https://i.4cdn.org/{}/{}".format(board, image))
            if img.ok:
                img = img.content
            else:
                print("Image 404: {}".format(image))
                continue
            with open(save_dir + board + '/' + image, "wb") as f:
                f.write(img)
        except:
            print("Error with image: {}".format(image))
            continue
            
        im_count += 1
        print("Saved {} image{}".format(im_count, "" if im_count == 1 else "s"), end='\r')
        
def scrape_new_data(board, save_dir):
    # Create a folder for the board
    path = save_dir + board
    if not os.path.exists(path):
        os.mkdir(path)

    # Get the 4chan board catalog JSON file and open it
    url = "https://a.4cdn.org/" + board + "/catalog.json"
    response = requests.get(url)
    data = eval(response.content)
    return data

def extract_board_posts(board, save_dir, data):
    # Create a folder for the board
    path = save_dir + board
    if not os.path.exists(path):
        os.mkdir(path)

    # Get the 4chan board catalog JSON file and open it
    url = "https://a.4cdn.org/" + board + "/catalog.json"
    response = requests.get(url)
    data = eval(response.content)
    
    threads_df = pd.DataFrame(get_threads(data))
    threads = []
    for thread_no in threads_df["no"]:
        threads.append(get_thread_posts(thread_no, board))
    df = get_complete_df(threads)
    return df

