import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def get_xpath(elm):
    e = elm
    xpath = elm.tag_name
    while e.tag_name != 'html':
        e = e.find_element(By.XPATH, '..')
        neighbours = e.find_elements(By.XPATH, '../' + e.tag_name)
        level = e.tag_name
        if len(neighbours) > 1:
            level += '[' + str(neighbours.index(e) + 1) + ']'
        xpath = level + '/' + xpath
    return '/' + xpath


def parser(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        element_to_click = WebDriverWait(driver, 3).\
            until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Показать телефон')]")))
        xpath = get_xpath(element_to_click)
        button = WebDriverWait(driver, 3).until(ec.element_to_be_clickable((By.XPATH, xpath)))
        button.click()
    except:
        pass

    site_name = url.split('://')[1]
    chars_to_change = ['/', '?']
    for char in chars_to_change:
        site_name = site_name.replace(char, '_')

    with open(f'saved_pages/{site_name}.html', 'w', encoding="utf-8") as file:
        file.write(driver.page_source)

    phone_regex = re.compile(r'\D\+7 ?-? ?\(?\d{3}\)? ?-? ?\d{3} ?-? ?\d{2} ?-? ?\d{2}\D|'
                             r'\D8 ?-? ?\(?\d{3}\)? ?-? ?\d{3} ?-? ?\d{2} ?-? ?\d{2}\D|'
                             r'\D\(\d{4}\) ?\d{2} ?-? ?\d{2} ?-? ?\d{2}\D|'
                             r'\D\d{3} ?- ?\d{2} ?- ?\d{2}\D')

    phone_matches = phone_regex.findall(driver.page_source)

    with open('output.txt', 'a') as output:
        chars_to_remove = ['(', ')', ' ', '-']
        all_phone_numbers = set()
        for element in phone_matches:
            element = element[1:-1]
            for char in chars_to_remove:
                element = element.replace(char, "")
            element = element.replace('+7', '8')
            element = element if len(element) > 7 else '8925'+element
            all_phone_numbers.add(element)
        output.write(f"{site_name}: {', '.join(all_phone_numbers)}\n")


def main():
    with open('input.txt', encoding="utf-8") as file:
        url = file.readline().strip('\n')
        while url:
            parser(url)
            url = file.readline().strip('\n')


if __name__ == '__main__':
    main()
