import ClientKit
import requests
import os


def login(username, password):
    login_url = "https://onlineservices.adriandevprojects.com/v1/auth/login/"

    credentials = {
        "username": username,
        "password": password
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    logincheck = ClientKit.checklogin()
    if logincheck is False:
        response = requests.post(login_url, data=credentials, headers=headers)
        if response.status_code == 200:
            with open("userdata.txt", "w+") as accfile:
                accfile.write(response.text)
                return True
        else:
            return f"Login failed: {response.text}"
    else:
        return "User already logged in"


def register(username, password, instant_login=bool):
    register_url = "https://onlineservices.adriandevprojects.com/v1/auth/register/"

    register_credentials = {
        "username": username,
        "password": password,
        "confirm_password": password
    }

    register_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(register_url, data=register_credentials, headers=register_headers)

    if response.status_code == 201:
        if instant_login:
            return login(username, password)
        else:
            return True
    else:
        return f"Registration failed: {response.text}"


def logout():
    state = ClientKit.checklogin()
    if state is True:
        os.remove("userdata.txt")
        return True
    else:
        return False
