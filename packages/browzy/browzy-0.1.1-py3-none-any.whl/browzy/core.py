import webbrowser
from googlesearch import search
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from colorama import init, Fore, Style
import re
from pyfiglet import Figlet

# Inisialisasi colorama
init()

def display_logo():
    # Buat ASCII art logo dengan font 'slant'
    f = Figlet(font='slant')
    logo = f.renderText('BROWZY')
    
    # Hitung lebar terminal dan logo untuk centering
    terminal_width = 80  # Default width
    logo_lines = logo.split('\n')
    max_length = max(len(line) for line in logo_lines)
    padding = (terminal_width - max_length) // 2
    
    # Print logo dengan warna ungu dan centered
    for line in logo_lines:
        if line.strip():  # Skip empty lines
            print(' ' * padding + f"{Fore.MAGENTA}{line}{Style.RESET_ALL}")
    
    # Print slogan centered dengan warna biru
    slogan = "Explore the world, simply"
    slogan_padding = (terminal_width - len(slogan)) // 2
    print('\n' + ' ' * slogan_padding + f"{Fore.BLUE}{slogan}{Style.RESET_ALL}\n")

def get_page_info(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else urlparse(url).netloc
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
        else:
            first_p = soup.find('p')
            if first_p:
                desc = first_p.text.strip()
        
        return {
            'title': title[:100],
            'description': desc[:200] + '...' if desc else 'Tidak ada deskripsi',
            'url': url
        }
    except:
        return {
            'title': urlparse(url).netloc,
            'description': 'Tidak dapat mengambil deskripsi',
            'url': url
        }

def get_readable_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
            
        for tag in soup.find_all():
            if tag.name == 'a' and tag.has_attr('href'):
                href = tag['href']
                tag.attrs = {}
                tag['href'] = href
            else:
                tag.attrs = {}
        
        content = []
        
        if soup.title:
            content.append(f"\n{Fore.CYAN}=== {soup.title.string} ==={Style.RESET_ALL}\n")
        
        main_content = soup.find(['article', 'main', 'div'], class_=re.compile(r'content|article|post'))
        if not main_content:
            main_content = soup
            
        for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'a', 'ul', 'ol']):
            if elem.name.startswith('h'):
                content.append(f"\n{Fore.GREEN}{elem.text.strip()}{Style.RESET_ALL}")
            elif elem.name == 'p':
                content.append(f"\n{elem.text.strip()}")
            elif elem.name == 'a':
                content.append(f"{Fore.BLUE}[{elem.text.strip()}]({elem.get('href', '')}){Style.RESET_ALL}")
            elif elem.name in ['ul', 'ol']:
                for li in elem.find_all('li'):
                    content.append(f"\n  • {li.text.strip()}")
        
        return "\n".join(content)
        
    except Exception as e:
        return f"{Fore.RED}Error membaca konten: {str(e)}{Style.RESET_ALL}"

def search_google(query):
    try:
        search_results = []
        for url in search(query, num_results=10, lang="id", sleep_interval=2):
            page_info = get_page_info(url)
            search_results.append(page_info)
            
        return search_results
        
    except Exception as e:
        print(f"Error detail: {str(e)}")
        return []

def main():
    display_logo()
    print(f"{Fore.YELLOW}Command yang tersedia:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}s(kata kunci) - untuk mencari{Style.RESET_ALL}")
    print(f"{Fore.WHITE}o(nomor) atau o nomor - untuk membuka web di browser{Style.RESET_ALL}")
    print(f"{Fore.WHITE}ow(nomor) - untuk membaca konten web di terminal{Style.RESET_ALL}")
    print(f"{Fore.WHITE}keluar - untuk keluar program{Style.RESET_ALL}")
    
    results = []  # Menyimpan hasil pencarian terakhir
    
    while True:
        command = input(f"\n{Fore.YELLOW}Masukkan command: {Style.RESET_ALL}").strip()
        
        if command.lower() == 'keluar':
            break
            
        # Command pencarian
        if command.startswith('s(') and command.endswith(')'):
            query = command[2:-1]  # Mengambil kata kunci dalam kurung
            print(f"\n{Fore.YELLOW}Mencari '{query}'... mohon tunggu...{Style.RESET_ALL}")
            results = search_google(query)
            
            if results:
                print(f"\n{Fore.CYAN}Hasil Pencarian:{Style.RESET_ALL}")
                print(f"{Fore.BLUE}-" * 70 + f"{Style.RESET_ALL}")
                
                for i, result in enumerate(results, 1):
                    print(f"\n{Fore.GREEN}{i}. {result['title']}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}{result['description']}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}   URL: {result['url']}{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}-" * 70 + f"{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Tidak ada hasil ditemukan atau terjadi error.{Style.RESET_ALL}")
                
        # Command baca konten web di terminal
        elif command.startswith('ow(') and command.endswith(')'):
            try:
                num = int(command[3:-1])
                if not results:
                    print(f"{Fore.RED}Belum ada hasil pencarian! Gunakan s(kata kunci) terlebih dahulu{Style.RESET_ALL}")
                elif 1 <= num <= len(results):
                    print(f"\n{Fore.YELLOW}Membaca konten dari {results[num-1]['title']}...{Style.RESET_ALL}")
                    content = get_readable_content(results[num-1]['url'])
                    print(content)
                    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Nomor tidak valid! Masukkan nomor 1-{len(results)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Format tidak valid! Gunakan ow(nomor){Style.RESET_ALL}")
                
        # Command buka web di browser
        elif command.startswith('o(') or (command.startswith('o ') and len(command) > 2):
            try:
                num = int(command.replace('o(', '').replace(')', '').strip())
                if not results:
                    print(f"{Fore.RED}Belum ada hasil pencarian! Gunakan s(kata kunci) terlebih dahulu{Style.RESET_ALL}")
                elif 1 <= num <= len(results):
                    webbrowser.open(results[num-1]['url'])
                    print(f"{Fore.GREEN}Membuka browser untuk hasil nomor {num}...{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Nomor tidak valid! Masukkan nomor 1-{len(results)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Format tidak valid! Gunakan o(nomor) atau o nomor{Style.RESET_ALL}")
                
        else:
            print(f"{Fore.RED}Command tidak valid!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Gunakan:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}s(kata kunci) - untuk mencari{Style.RESET_ALL}")
            print(f"{Fore.WHITE}o(nomor) atau o nomor - untuk membuka web di browser{Style.RESET_ALL}")
            print(f"{Fore.WHITE}ow(nomor) - untuk membaca konten web di terminal{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
