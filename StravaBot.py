#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Robert Sanders

import time, random
from selenium import webdriver
from bs4 import BeautifulSoup

LOAD_TIME_SEC = 3

# Configure constants here
EMAIL = ''
PASSWORD = ''
LOGIN_SERVICE = 'Google'
DRIVER = 'Firefox'

ENABLE_KUDOS_ON_MAIN_PAGE = True
NUMBER_OF_MAIN_PAGE_PAGES = 4

ENABLE_KUDOS_ON_CLUBS = True
#               Train Race Beer
CLUB_URLS = ["https://www.strava.com/clubs/47423/recent_activity"]
NUMBER_OF_CLUB_PAGES = 2

ENABLE_KUDOS_ON_ATHLETES = True
#               Gary Robbins
ATHLETE_URLS = ["https://www.strava.com/pros/1481479"]

NUMBER_OF_TIMES_TO_ITERATE = 1  # -1 = infinite


KUDOS_COUNT = 0
FAILED_COUNT = 0


def Launch():
    """
    Launch the Medium bot and ask the user what browser they want to use.
    """

    LIKE_COUNT = 0
    FAILED_COUNT = 0

    if 'chrome' not in DRIVER.lower() and 'firefox' not in DRIVER.lower() and 'phantomjs' not in DRIVER.lower():

        # Browser choice
        print 'Choose your browser:'
        print '[1] Chrome'
        print '[2] Firefox/Iceweasel'
        print '[3] PhantomJS'

        while True:
            try:
                browserChoice = int(raw_input('Choice? '))
            except ValueError:
                print 'Invalid choice.',
            else:
                if browserChoice not in [1,2,3]:
                    print 'Invalid choice.',
                else:
                    break

        StartBrowser(browserChoice)

    elif 'chrome' in DRIVER.lower():
        StartBrowser(1)

    elif 'firefox' in DRIVER.lower():
        StartBrowser(2)

    elif 'phantomjs' in DRIVER.lower():
        StartBrowser(3)


def StartBrowser(browserChoice):
    """
    Based on the option selected by the user start the selenium browser.
    browserChoice: browser option selected by the user.
    """

    if browserChoice == 1:
        print '\nLaunching Chrome'
        browser = webdriver.Chrome()
    elif browserChoice == 2:
        print '\nLaunching Firefox/Iceweasel'
        browser = webdriver.Firefox()
    elif browserChoice == 3:
        print '\nLaunching PhantomJS'
        browser = webdriver.PhantomJS()

    if SignInToService(browser):
        print 'Success!\n'
        StravaBot(browser)

    else:
        soup = BeautifulSoup(browser.page_source, "lxml")
        if soup.find('div', {'class':'alert error'}):
            print 'Error! Please verify your username and password.'
        elif browser.title == '403: Forbidden':
            print 'Medium is momentarily unavailable. Please wait a moment, then try again.'
        else:
            print 'Please make sure your config is set up correctly.'

    browser.quit()


def SignInToService(browser):
    """
    Using the selenium browser passed and the config file login to Medium to
    begin the botting.
    browser: the selenium browser used to login to Medium.
    """

    serviceToSignWith = LOGIN_SERVICE.lower()
    signInCompleted = False
    print 'Signing in...'

    # Sign in
    browser.get('https://www.strava.com/')

    if serviceToSignWith == "google":
        signInCompleted = SignInToGoogle(browser)

    return signInCompleted


def SignInToGoogle(browser):
    """
    Sign into Medium using a Google account.
    browser: selenium driver used to interact with the page.
    return: true if successfully logged in : false if login failed.
    """

    signInCompleted = False

    try:
        browser.find_element_by_xpath('//a[contains(text(),"Sign up with Google")]').click()
        time.sleep(LOAD_TIME_SEC)
        browser.find_element_by_id('identifierId').send_keys(EMAIL)
        browser.find_element_by_id('identifierNext').click()
        time.sleep(LOAD_TIME_SEC)
        browser.find_element_by_name('password').send_keys(PASSWORD)
        browser.find_element_by_id('passwordNext').click()
        time.sleep(LOAD_TIME_SEC)
        signInCompleted = True
    except Exception, e:
        print "Exception while setting username and password: " + str(e)

    return signInCompleted


def StravaBot(browser):
    """
    Start botting Strava
    browser: selenium browser used to interact with the page
    """

    iteration = 0
    # Infinite loop
    while True:

        if ENABLE_KUDOS_ON_MAIN_PAGE:
            print "\nNavigating to Strava Dashboard..."
            NavigateToPageAndGiveKudos(browser, "https://www.strava.com/dashboard", NUMBER_OF_MAIN_PAGE_PAGES)
        if ENABLE_KUDOS_ON_CLUBS:
            for club_url in CLUB_URLS:
                print "\nNavigating to Club " + club_url + "..."
                NavigateToPageAndGiveKudos(browser, club_url, NUMBER_OF_CLUB_PAGES)
        if ENABLE_KUDOS_ON_ATHLETES:
            for athlete_url in ATHLETE_URLS:
                print "\nNavigating to Club " + athlete_url + "..."
                NavigateToPageAndGiveKudos(browser, athlete_url, 0)

        print("\n")

        iteration += 1
        print "iteration: " + str(iteration) + ", NUMBER_OF_TIMES_TO_ITERATE: " + str(NUMBER_OF_TIMES_TO_ITERATE)
        if NUMBER_OF_TIMES_TO_ITERATE != -1:
            if iteration == NUMBER_OF_TIMES_TO_ITERATE:
                print "\nBreaking loop and finishing..."
                break

        print '\nPause for 1 hour to wait for new articles to be posted\n'
        time.sleep(3600+(random.randrange(0, 10))*60)

    print "\nSummary:"
    print "Number of Activities Kudo'd: " + str(KUDOS_COUNT)
    print "Number of Activities Failed to Kudo: " + str(FAILED_COUNT)


def NavigateToPageAndGiveKudos(browser, url, number_of_pages):
    global KUDOS_COUNT
    global FAILED_COUNT

    browser.get(url)
    time.sleep(LOAD_TIME_SEC)
    for i in range(0, number_of_pages):
        ScrollToBottomAndWaitForLoad(browser)

    # kudos_buttons = browser.find_elements_by_class_name("js-add-kudo")
    kudos_buttons = browser.find_elements_by_xpath("//button[contains(@class, 'btn-kudo') and contains(@class, 'js-add-kudo')]")

    for kudos_button in kudos_buttons:

        try:
            kudos_button.click()
            print "Successfully Gave Kudos"
            KUDOS_COUNT += 1
        except Exception, e:
            FAILED_COUNT += 1
            print 'Exception thrown in NavigateToPageAndGiveKudos(): ' + str(e)


def ScrollToBottomAndWaitForLoad(browser):
    """
    Scroll to the bottom of the page and wait for the page to perform it's lazy loading.
    browser: selenium webdriver used to interact with the browser.
    """

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)


def ScrollHalfWayAndWaitForLoad(browser):
    """
    Scroll to the bottom of the page and wait for the page to perform it's lazy loading.
    browser: selenium webdriver used to interact with the browser.
    """

    browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(3)


if __name__ == '__main__':
    Launch()
