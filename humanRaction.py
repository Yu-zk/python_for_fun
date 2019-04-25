import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def numberMemory():
    url = "https://www.humanbenchmark.com/tests/number-memory"
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(1)
    # browser.find_element_by_link_text('START').click()
    input()
    while True:
        try:
            print(browser.page_source)
            w = browser.page_source.split('<div class="test-group">')[1].split('</div>')[0]
            # w = browser.page_source.split('<div class="big-number">')[1].split('</div>')[0]
            print(w)
            time.sleep(1)
        except:
            print()
        while browser.page_source.find('What was the number?')==-1:
            time.sleep(1)
        input_text = browser.find_element_by_xpath("//input[@type='text']")
        input_text.send_keys(w, Keys.ENTER)
        time.sleep(1)
        browser.find_element_by_link_text('NEXT').click()
    browser.quit()
    return


def verbalMemory():
    url = "https://www.humanbenchmark.com/tests/verbal-memory"
    l = []
    waittime = 0.001
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(1)
    input()
    # browser.find_element_by_css_selector('.hero-button.START')
    # browser.find_element_by_link_text('START').click()
    while True:
        time.sleep(waittime)
        w=browser.page_source.split('<div class="word">')[1].split('</div>')[0]
        print(w+' ', end='')
        if w in l:
            browser.find_element_by_link_text('SEEN').click()
            print('SEEN')
        else:
            browser.find_element_by_link_text('NEW').click()
            print('NEW')
            l.append(w)
    browser.quit()
    return


def main():
    a = input("1 for Number Memory\n2 for verbal Memory\n")
    while not(a=='1' or a=='2'):
        a=input("Invalid input\n1 for Number Memory\n2 for verbal Memory\n")
    if a=='1':
        numberMemory()
    elif a =='2':
        verbalMemory()
    else:
        print('laji')


main()
