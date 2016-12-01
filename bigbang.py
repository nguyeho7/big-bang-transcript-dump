from bs4 import BeautifulSoup
import bs4
import requests
import json
import time
from functools import reduce
from collections import Counter

def parse_script(input_text):
    result_list = []
    for line in input_text:
        if line.__class__ == bs4.element.Tag:
            txt = line.text
        else:
            txt = line
        if ":" in txt:
            args = txt.split(':')
            if len(args)>2:
                if '\n' in txt: 
                    result_list.extend(parse_script(txt.split('\n')))
                else:
                    colon_index = txt.find(':')
                    character = txt[:colon_index]
                    content = txt[colon_index:]
                    result_list.append({'character': character, 'content': content})

            elif(len(args)==2):
                result_list.append({'character': args[0], 'content': args[1]})
            else:
                result_list.append({'character': 'Scene', 'content': txt})
    return result_list

def load_bigbang():
    url = 'https://bigbangtrans.wordpress.com/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    result_dict = {}
    lines = 0
    links = soup.find_all('a', href=True)
    for link in links:
        next_url = link['href']
        print(next_url)
        if "series" in next_url:
            ep_name = next_url.split('series-')[1]
            print(ep_name)
            sub = requests.get(next_url)
            sub_parsed = BeautifulSoup(sub.text)
            scene_text = sub_parsed('div', {'class': 'entrytext'})[0].findAll('p')
            result_list = parse_script(scene_text)
            lines += len(result_list)
            result_dict.update({ep_name: result_list})
            time.sleep(0.4)
    print(lines)
    return result_dict

def get_shifting_windows(values, window_size):
    return (values[x:x+window_size] for x in range(len(values)-window_size+1))

def statistics(data_dict):
    total_sentences = reduce(lambda x, y: x+y,
                        map(len,
                            data_dict.values()))
    print("total sentences:", total_sentences)
    characters = set()
    for episode in data_dict.values():
        for line in episode:
            character = line['character']
            if "(" in character:
                character = character.split('(')[0].strip()
            characters.add(character)
    print(characters)
    print("total characters:",len(characters))
    print("")
    utterance_counter = Counter() # number of all utterances and responses between everyone
    response_counter = Counter() # number of all utterances towards a specific character
    for episode in data_dict.values():
        for utterance, response in get_shifting_windows(episode, 2):
            first = utterance['character']
            second = response['character']
            if first == 'Scene' or second == "Scene":
                continue
            utterance_counter[(first, second)] += 1
            response_counter[second] += 1
    print("most common utterance: response pairs")
    print(utterance_counter.most_common(15))
    print("")
    print("most common utterances towards a specific character")
    print(response_counter.most_common(15))

if __name__ == '__main__':
    result_dict = load_bigbang()
    json.dump(result_dict, open('bigbangtranscript.json', 'w'))
    statistics(result_dict)
