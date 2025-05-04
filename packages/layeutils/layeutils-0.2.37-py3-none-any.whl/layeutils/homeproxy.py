import logging
import os


def using_home_server_proxy(type: str = 'http', proxy_url: str = None):
    """使用代理服务器

    Args:
        type (str, optional): 可选: http or socks5. Defaults to 'socks5'.
        proxy_url (str, optional): 指定代理服务器地址. Defaults to None.
    """
    logging.info('seting proxy...')
    if not proxy_url:
        match type:
            case 'socks5':
                proxy = 'socks5://192.168.1.81:7890'
            case 'http':
                proxy = 'http://192.168.1.81:7890'
    else:
        proxy = proxy_url

    os.environ['http_proxy'] = proxy
    os.environ['https_proxy'] = proxy
