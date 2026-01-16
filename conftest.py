import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from helpers import Generators,User
import allure
import copy
from urls import Endpoints

# фикстура запускает браузеры Chrome, Firefox и закрывает их завершению теста
@pytest.fixture(params=["chrome", "firefox"])
def driver(request):
    try:
        if request.param == "chrome":
            driver = webdriver.Chrome()
        elif request.param == "firefox":
            driver = webdriver.Firefox()
    except WebDriverException as e:
        pytest.fail(f"Не удалось запустить браузер {request.param}. Ошибка: {e}")
    yield driver
    driver.quit()


@pytest.fixture(scope='function')
def random_user():
    payload = Generators.generate_payload()
    email = payload["email"]
    password = payload["password"]
    with allure.step("Создание пользователя через API"):
        response = User.register_user(payload)
        access_token = response.json().get("access_token")
    yield email, password
    with allure.step("Удаление пользователя через API"):
        login_payload = copy.deepcopy(payload)
        del login_payload["name"]
        with allure.step('Проверка перед удалением, что пользователь существует'):
            response_login = requests.post(url=Endpoints.LOGIN_USER, json=login_payload)
            if response_login.status_code == 200:
                header = {'Authorization': access_token}
                with allure.step('Запрос удаление пользователя'):
                    requests.delete(Endpoints.DELETE_USER, headers=header)

