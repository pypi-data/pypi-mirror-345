from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import chromedriver_autoinstaller
from functools import wraps

def install_chromedriver():
  chromedriver_autoinstaller.install()  # 자동으로 맞는 버전 설치 & 사용


def chromedriver(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        install_chromedriver()
        return func(*args, **kwargs)

    return wrapper

@chromedriver
def buy_lotto_ticket(id, password, ticket_count=5):
    """ Buy the lotto tickets """
    # 웹드라이버 초기화
    driver = webdriver.Chrome()

    try:
        browse_lotto_buy_page(driver, id, password)

        # lotto ticket button click
        driver.find_element(By.XPATH, '//*[@id="num2"]').click()
        time.sleep(1)

        # lotto ticket count select
        select_element = driver.find_element(By.XPATH, '//*[@id="amoundApply"]')
        select = Select(select_element)
        select.select_by_index(ticket_count - 1)

        driver.find_element(By.XPATH, '//*[@id="btnSelectNum"]').click()
        driver.find_element(By.XPATH, '//*[@id="btnBuy"]').click()
        driver.find_element(By.XPATH, '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]').click()
        time.sleep(5)

        print(f"{id}, 5장의 로또를 성공적으로 구매했습니다.")

    except Exception as e:
        print(f"{id}, 로또 구매 실패했습니다 :", e)

    finally:
        # 웹드라이버 종료
        driver.quit()


@chromedriver
def check_lotto_balance(id, password):
    """ Check the lotto balance """
    # 웹드라이버 초기화
    driver = webdriver.Chrome()
    try:
        browse_lotto_main_page(driver, id, password)

        element = driver.find_element(By.XPATH, '/html/body/div[1]/header/div[2]/div[2]/form/div/ul[1]/li[2]/a[1]/strong')
        balance_text = element.text.strip()
        balance = int(balance_text.replace("원", "").replace(",", ""))

        print(f"{id}, 현재 로또 잔액은 {balance_text} 입니다")
        print(f"{id}, 현재 로또 잔액은 {balance}원 입니다.")

    except Exception as e:
        print(f"{id}, 로또 잔액 확인 실패했습니다 :", e)

    finally:
        # 웹드라이버 종료
        driver.quit()


@chromedriver
def check_lotto_result(id, password):
    """ Check the lotto result """
    # 웹드라이버 초기화
    driver = webdriver.Chrome()

    try:
        browse_lotto_result_page(driver, id, password)

        driver.find_element(By.XPATH, '//*[@id="frm"]/table/tbody/tr[3]/td/span[2]/a[3]').click()
        driver.find_element(By.XPATH, '//*[@id="submit_btn"]').click()
        time.sleep(5)

        iframe = driver.find_element(By.XPATH, '//*[@id="lottoBuyList"]')
        driver.switch_to.frame(iframe)
        time.sleep(1)

        result_elements = driver.find_elements(By.XPATH, '/html/body/table/tbody/tr/td[6]')
        results = [result_element.text.strip() for result_element in result_elements]
        for result in results:
            if "당첨" in result:
                print(f"{id}, 당첨 결과가 있습니다.")
                return

        print(f"{id}, 당첨 결과가 없습니다.")
    except Exception as e:
        print(f"{id}, 로또 결과 확인 실패했습니다 :", e)
    finally:
        # 웹드라이버 종료
        driver.quit()


def browse_lotto_main_page(driver, id, password):
    """ Browse the lotto main page """
    login_lotto(driver, id, password)

    driver.get('https://www.dhlottery.co.kr/common.do?method=main')
    time.sleep(5)


def browse_lotto_result_page(driver, id, password):
    """ Browse the lotto result page """
    login_lotto(driver, id, password)

    driver.get('https://www.dhlottery.co.kr/myPage.do?method=lottoBuyListView')
    time.sleep(5)


def browse_lotto_buy_page(driver, id, password):
    """ Browse the lotto buy page """
    login_lotto(driver, id, password)

    # 로또 구매 페이지로 이동
    driver.get('https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40')
    time.sleep(5)

    # iframe으로 전환
    iframe = driver.find_element(By.XPATH, '//*[@id="ifrm_tab"]')
    driver.switch_to.frame(iframe)
    time.sleep(1)


def login_lotto(driver, id, password):
    """ Login to the lotto website """

    # 동행복권 로그인 페이지 접속
    driver.get('https://www.dhlottery.co.kr/user.do?method=login&returnUrl=')
    time.sleep(2)  # 페이지 로딩 대기

    # 아이디 입력
    driver.find_element(By.ID, 'userId').send_keys(id)

    # 비밀번호 입력
    driver.find_element(By.NAME, 'password').send_keys(password)

    # 로그인 버튼 클릭
    driver.find_element(By.XPATH, '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a').click()
    time.sleep(5)  # 로그인 완료 대기

