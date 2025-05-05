from .file import read_file, get_data_path
import threading

dynamic_idx = 0
dynamic_lock = threading.Lock()

file_path = get_data_path(file_name='dynamic_http_proxy.txt')
dynamic_proxies = read_file(file_path=file_path)


def get_dynamic_http_proxy():
    global dynamic_idx
    global dynamic_lock
    dynamic_lock.acquire()
    proxy = dynamic_proxies[dynamic_idx % len(dynamic_proxies)]
    dynamic_idx += 1
    dynamic_lock.release()
    return get_http_proxy(proxy)


file_path = get_data_path(file_name='static_http_proxy.txt')
static_proxies = read_file(file_path=file_path)

static_idx = 0
static_lock = threading.Lock()


def get_static_http_proxy(idx: int = None):
    global static_proxies
    if idx is not None:
        idx = idx % len(static_proxies)
        return {'http': static_proxies[idx], 'https': static_proxies[idx]}
    else:
        global static_lock, static_idx
        static_lock.acquire()
        proxy = static_proxies[static_idx % len(static_proxies)]
        static_idx += 1
        static_lock.release()
        return get_http_proxy(proxy)


def get_http_proxy(proxy: str):
    return {'http': proxy, 'https': proxy}


if __name__ == '__main__':
    print(get_static_http_proxy())
    print(get_static_http_proxy(0))
    print(get_static_http_proxy())
    print(get_static_http_proxy(1))
    print(get_static_http_proxy(100))

    print(get_dynamic_http_proxy())
