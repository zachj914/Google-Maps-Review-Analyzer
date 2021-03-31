from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time


class Maps_Scraper:
    def __init__(self, driver_path='/usr/bin/chromedriver', headless=True):
        # Google Maps XPATHs
        self.REVIEW_XPATH = '//*[@class="section-review-content"]'
        self.SCROLLBAR_XPATH = '//*[@class="section-layout section-scrollbox scrollable-y scrollable-show"]'
        self.LOADING_XPATH = '//*[@class="section-loading noprint"]'
        self.EXPAND_XPATH = '//*[@class="section-expand-review blue-link"]'
        self.SORT_XPATH = '//*[@aria-label="Sort reviews"]'
        self.SORT_BUTTONS_XPATH = '//*[@role="menuitemradio"]'
        self.REVIEWER_NAME_XPATH = './/*[@class="section-review-title"]'
        self.REVIEW_STARS_XPATH = './/*[@class="section-review-stars"]'
        self.REVIEW_CONTENT_XPATH = './/*[@class="section-review-text"]'
        # Start WebDriver
        print("Starting Chrome")
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920x1080')
        self.driver = webdriver.Chrome(driver_path, options=chrome_options)
        self.reviews = []

    def load_page(self, url, page_timeout=10, scroll_timeout=100, poll_time=.1):
        # Open page
        print("Opening Page", url)
        self.driver.get(url)

        # Wait for reviews to load
        try:
            WebDriverWait(self.driver,
                          page_timeout if page_timeout else float('inf'))\
                          .until(lambda d: d.find_element_by_xpath(self.REVIEW_XPATH))
        except TimeoutException:
            print("Page loading timed out after", PAGE_TIMEOUT, "seconds.", end='')
            print("change the timeout duration in config")
            exit()

        # Sort by newest
        self.driver.find_element_by_xpath(self.SORT_XPATH).click()
        WebDriverWait(self.driver,
                      page_timeout if page_timeout else float('inf'))\
                      .until(lambda d: d.find_element_by_xpath(self.SORT_BUTTONS_XPATH))
        self.driver.find_elements_by_xpath(self.SORT_BUTTONS_XPATH)[1].click()

        # Scroll through reviews
        print("Scrolling Through Reviews")
        scroll_bar = self.driver.find_element_by_xpath(self.SCROLLBAR_XPATH)
        start_time = time.time()
        while True:
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                                  scroll_bar)
            if scroll_timeout and time.time() - start_time >= scroll_timeout:
                print("Review scrolling timed out after", SCROLL_TIMEOUT, end=' ')
                print("seconds. You can change the timeout duration in config")
                exit()
            try:
                self.driver.find_element_by_xpath(self.LOADING_XPATH)
                time.sleep(poll_time)
            except NoSuchElementException:
                break

        # Expand long reviews
        print("Expanding Long Reviews")
        for button in self.driver.find_elements_by_xpath(self.EXPAND_XPATH):
            button.click()

        # Read reviews
        review_count = len(self.reviews)
        self.reviews += self.driver.find_elements_by_xpath(self.REVIEW_XPATH)
        review_count = len(self.reviews) - review_count
        print("Found", review_count, "reviews")

    def log_reviews(self, outfile):
        print("Writing reviews to log")
        with open(outfile, "w") as f:
            for review in self.reviews:
                f.write(review.find_element_by_xpath(
                    self.REVIEWER_NAME_XPATH).text + "\n")

                f.write(review.find_element_by_xpath(
                    self.REVIEW_STARS_XPATH).get_attribute(
                        "aria-label")[1] + "\n")

                f.write(review.find_element_by_xpath(
                    self.REVIEW_CONTENT_XPATH).text.replace('\n', ' ') + "\n")

if __name__ == '__main__':
    scraper = Maps_Scraper(headless=False)
    scraper.load_page('https://www.google.com/maps/place/Pedal+Power/@41.5919174,-72.7558694,10z/data=!3m1!5s0x89e64a44acd20575:0xa34d998a6f820790!4m10!1m2!2m1!1spedal+power+ct!3m6!1s0x89e6f7cc95b67935:0x28d29c4ed04a07a0!8m2!3d41.561042!4d-72.650429!9m1!1b1')
    scraper.log_reviews("log.txt")

