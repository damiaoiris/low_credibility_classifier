import domain_utils as du
import os


def parse_ps_plus_1(url: str, keep_subdomain: bool = True) -> str:
    """ 
    Parse the "public suffix + 1" of a url, 
        e.g. "https://www.publico.pt/2021/09/07/sociedade/noticia/chile-aprova-vacina-sinovac-criancas-seis-anos-1976551" -> "publico.pt"
        see: https://publicsuffix.org/
    """
    psp1 = du.get_ps_plus_1(url)
    if keep_subdomain is False:
        # split by dot using psp1 and keep the last two elements (hostname and top level domain)
        psp1 = ".".join(psp1.split(".")[-2:])
    return psp1


def clear_terminal():
    # Clear terminal based on the operating system
    if os.name == 'posix':  # For Unix/Linux/Mac systems
        _ = os.system('clear')
    elif os.name == 'nt':  # For Windows systems
        _ = os.system('cls')

