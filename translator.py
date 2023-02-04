import sys
import requests
from bs4 import BeautifulSoup

supported_langs = {"1": "Arabic", "2": "German", "3": "English", "4": "Spanish", "5": "French", "6": "Hebrew", "7": "Japanese",
                   "8": "Dutch", "9": "Polish", "10": "Portuguese", "11": "Romanian", "12": "Russian", "13": "Turkish"}
correct_input = [item.lower() for item in supported_langs.values()]
correct_input.extend(supported_langs.values())
correct_input.append("all")


def append_to_file(_word, _line):
    with open(f"{_word}.txt", "a") as f:
        f.write(_line + "\n")


def read_command_line():
    source, target, word = sys.argv[1].lower(), sys.argv[2].lower(), sys.argv[3].lower()
    # print(source, target, word)
    if source not in correct_input:
        print(f"Sorry, the program doesn't support {source}")
        sys.exit()
    elif target not in correct_input:
        print(f"Sorry, the program doesn't support {target}")
        sys.exit()
    return source, target, word


def make_url(_source, _target, _word):
    root = "https://context.reverso.net/translation"
    return f"{root}/{_source.lower()}-{_target.lower()}/{_word.lower()}", _word


def make_request(_url, _word):
    headers = {'User-Agent': 'Mozilla/5.0'}
    page = requests.get(_url, headers=headers)
    if page.status_code == 200:
        # print(page.status_code, "OK")
        # print()
        return page
    else:
        if str(page.status_code).startswith("4"):
            print(f"Sorry, unable to find {_word}")
            sys.exit()
        elif str(page.status_code).startswith("5"):
            print("Something wrong with your internet connection")
            sys.exit()


def make_soup(_page):
    _soup = BeautifulSoup(_page.content, "html.parser")
    _pretty_soup = BeautifulSoup.prettify(_soup)
    return _soup, _pretty_soup


def find_tags(_soup, _lang, _word):
    def _print():
        for t in translations[:5]:
            print(t)
            append_to_file(_word, t)
        print()
        append_to_file(_word, "")
    span_tags = _soup.find_all("span", {"class": "display-term"})
    div_tags = _soup.find_all("div", {"class": "example"})
    translations = [item.text for item in span_tags]
    examples_src = [item.find_next("div", {"class": "src ltr"}).text.strip() for item in div_tags if
                    item.text.strip() != ""]
    if _lang == "Arabic":
        examples_trg = [item.find_next("div", {"class": "trg rtl arabic"}).text.strip() for item in div_tags if item.text.strip() != ""]
    elif _lang == "Hebrew":
        examples_trg = [item.find_next("div", {"class": "trg rtl"}).text.strip() for item in div_tags if
                        item.text.strip() != ""]
    else:
        examples_trg = [item.find_next("div", {"class": "trg ltr"}).text.strip() for item in div_tags if
                        item.text.strip() != ""]
    print(f"{_lang.title()} Translations:")
    append_to_file(_word, f"{_lang.title()} Translations:")
    _print()
    print(f"{_lang.title()} Examples:")
    append_to_file(_word, f"{_lang.title()} Examples:")
    for src, trg in zip(examples_src[:5], examples_trg[:5]):
        print(src)
        append_to_file(_word, src)
        print(trg)
        append_to_file(_word, trg + "\n")
        print()


def main():
    # src, trg, word = take_input()
    src, trg, word = read_command_line()
    if trg == "all":
        for key in supported_langs:
            if supported_langs[key].lower() != src:
                url, word = make_url(src, supported_langs[key], word)
                page = make_request(url, word)
                soup, pretty_soup = make_soup(page)
                find_tags(soup, supported_langs[key], word)
    else:
        url, word = make_url(src, trg, word)
        page = make_request(url, word)
        soup, pretty_soup = make_soup(page)
        find_tags(soup, trg, word)


if __name__ == '__main__':
    main()
