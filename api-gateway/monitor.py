import requests
import threading
import time


def monitor(micro):
    while True:
        try:
            url_micro_seguridad = f'http://{micro}/ping'
            response = requests.get(url_micro_seguridad)
            print(f'{micro} {response.text}')
        except requests.exceptions.RequestException as e:
            print(f'{micro} no disponible')
        time.sleep(5)


def health_check(micros):
    for micro in micros:
        thread = threading.Thread(target=monitor, args=(micro,))
        thread.daemon = True
        thread.start()
