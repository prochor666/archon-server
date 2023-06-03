from colorama import Fore, Back, Style, just_fix_windows_console


def mod(str, f='white', b='black'):
    just_fix_windows_console()
    f = f.upper()
    b = b.upper()

    return f"{fg(bg(str, b), f)}{Style.RESET_ALL}" 


def fg(str, c='white'):
    c = c.upper()

    match c:
        case 'BLACK':
            fg_color = Fore.BLACK
        case 'RED':
            fg_color = Fore.RED
        case 'GREEN':
            fg_color = Fore.GREEN
        case 'YELLOW':
            fg_color = Fore.YELLOW
        case 'BLUE':
            fg_color = Fore.BLUE
        case 'MAGENTA':
            fg_color = Fore.MAGENTA
        case 'CYAN':
            fg_color = Fore.CYAN
        case 'WHITE':
            fg_color = Fore.WHITE
        case 'LIGHTBLACK_EX':
            fg_color = Fore.LIGHTBLACK_EX
        case 'LIGHTRED_EX':
            fg_color = Fore.LIGHTRED_EX
        case 'LIGHTGREEN_EX':
            fg_color = Fore.LIGHTGREEN_EX
        case 'LIGHTYELLOW_EX':
            fg_color = Fore.LIGHTYELLOW_EX
        case 'LIGHTBLUE_EX':
            fg_color = Fore.LIGHTBLUE_EX
        case 'LIGHTMAGENTA_EX':
            fg_color = Fore.LIGHTMAGENTA_EX
        case 'LIGHTCYAN_EX':
            fg_color = Fore.LIGHTCYAN_EX
        case 'LIGHTWHITE_EX':
            fg_color = Fore.LIGHTWHITE_EX
        case _:
            fg_color = Fore.WHITE

    return f"{fg_color}{str}{Fore.RESET}" 


def bg(str, c='black'):
    c = c.upper()
    
    match c:
        case 'BLACK':
            bg_color = Back.BLACK
        case 'RED':
            bg_color = Back.RED
        case 'GREEN':
            bg_color = Back.GREEN
        case 'YELLOW':
            bg_color = Back.YELLOW
        case 'BLUE':
            bg_color = Back.BLUE
        case 'MAGENTA':
            bg_color = Back.MAGENTA
        case 'CYAN':
            bg_color = Back.CYAN
        case 'WHITE':
            bg_color = Back.WHITE
        case 'LIGHTBLACK_EX':
            bg_color = Fore.LIGHTBLACK_EX
        case 'LIGHTRED_EX':
            bg_color = Fore.LIGHTRED_EX
        case 'LIGHTGREEN_EX':
            bg_color = Fore.LIGHTGREEN_EX
        case 'LIGHTYELLOW_EX':
            bg_color = Fore.LIGHTYELLOW_EX
        case 'LIGHTBLUE_EX':
            bg_color = Fore.LIGHTBLUE_EX
        case 'LIGHTMAGENTA_EX':
            bg_color = Fore.LIGHTMAGENTA_EX
        case 'LIGHTCYAN_EX':
            bg_color = Fore.LIGHTCYAN_EX
        case 'LIGHTWHITE_EX':
            bg_color = Fore.LIGHTWHITE_EX
        case _:
            bg_color = Back.BLACK
            
    return f"{bg_color}{str}{Back.RESET}" 
