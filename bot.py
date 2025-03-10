from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, string, random, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Capfizz:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "mainnet.capfizz.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Capfizz - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, cookie):
        if cookie not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[cookie] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[cookie]

    def rotate_proxy_for_account(self, cookie):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[cookie] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_hash(self, length=20):
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=length))
    
    def mask_cap_session(self, cookie: str):
        pattern = r"cap-session=([\w\.-]+)"
        match = re.search(pattern, cookie)
        
        if match:
            full_value = match.group(1)
            if len(full_value) > 6:
                masked_value = full_value[:3] + '*' * 3 + full_value[-3:]
            else:
                masked_value = full_value

            return masked_value
        else:
            return "cap-session Not Found"

    def print_message(self, cookie, idx, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{self.mask_cap_session(cookie)}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Connection:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                proxy_choice = int(input("Choose [1/2/3] -> ").strip())

                if proxy_choice in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if proxy_choice == 1 else 
                        "Run With Private Proxy" if proxy_choice == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        nodes_count = 0
        if proxy_choice in [1, 2]:
            while True:
                try:
                    nodes_count = int(input("How Many Nodes Do You Want to Run For Each Account? -> ").strip())
                    if nodes_count > 0:
                        break
                    else:
                        print(f"{Fore.RED+Style.BRIGHT}Please enter a positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED+Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        return proxy_choice, nodes_count
    
    async def check_auth(self, cookie: str, idx: int, proxy=None):
        url = "https://mainnet.capfizz.com/api/user/extension/check-auth"
        headers = {
            **self.headers,
            "Cookie": cookie
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.text()
                    return json.loads(result)
        except (Exception, ClientResponseError) as e:
            return self.print_message(cookie, idx, proxy, Fore.RED, "Check Auth Failed")
    
    async def uptime_static(self, cookie: str, idx: int, proxy=None, retries=5):
        url = "https://mainnet.capfizz.com/api/user/extension/uptime-static"
        headers = {
            **self.headers,
            "Cookie": cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(cookie, idx, proxy, Fore.RED, "GET Uptime Failed")
    
    async def send_ping(self, cookie: str, idx: int, proxy=None, retries=5):
        url = "https://mainnet.capfizz.com/api/ping"
        headers = {
            **self.headers,
            "Cookie": cookie
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.text()
                        return json.loads(result)
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(cookie, idx, proxy, Fore.RED, "Send PING Failed")
    
    async def perform_mining(self, cookie: str, idx: int, proxy=None, retries=5):
        url = "https://mainnet.capfizz.com/api/node/mining"
        data = json.dumps({"data":{"hash":self.generate_hash()}})
        headers = {
            **self.headers,
            "Authorization": "Bearer none",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": cookie,
            "Origin": "chrome-extension://agollninopbkafedoijcnbdopajjjmfa",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(cookie, idx, proxy, Fore.RED, "Perform Mining Failed")
        
    async def process_check_auth(self, cookie: str, idx: int, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(cookie[idx]) if use_proxy else None
        is_valid = None
        while is_valid is None:
            is_valid = await self.check_auth(cookie, idx, proxy)
            if not is_valid:
                await asyncio.sleep(5)
                continue
            
            if is_valid and is_valid.get("message") == "success":
                self.print_message(cookie, idx, proxy, Fore.GREEN, "Check Auth Success")
                return True
            else:
                self.print_message(cookie, idx, proxy, Fore.RED, "Check Auth Failed")
                await asyncio.sleep(5)
                continue

    async def process_uptime_static(self, cookie: str, idx: int, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(cookie[idx]) if use_proxy else None
            today_uptime = "N/A"
            session_uptime = "N/A"
            total_uptime = "N/A"

            uptime = await self.uptime_static(cookie, idx, proxy)
            if uptime:
                today_uptime = uptime.get("todayUptime", 0)
                session_uptime = uptime.get("sessionUptime", 0)
                total_uptime = uptime.get("totalUptime", 0)
                self.print_message(cookie, idx, proxy, Fore.WHITE, 
                    f"{Fore.BLUE + Style.BRIGHT}Uptime: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Today {today_uptime} Minutes{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Session {session_uptime} Minutes{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Total {total_uptime} Minutes{Style.RESET_ALL}"
                )
                
            await asyncio.sleep(15 * 60)

    async def process_send_ping(self, cookie: str, idx: int, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(cookie[idx]) if use_proxy else None
            ping = await self.send_ping(cookie, idx, proxy)
            if ping and ping.get("message") == "success":
                self.print_message(cookie, idx, proxy, Fore.GREEN, "PING Success")
            else:
                self.print_message(cookie, idx, proxy, Fore.RED, "PING Failed")
                
            await asyncio.sleep(1 * 60)

    async def process_perform_mining(self, cookie: str, idx: int, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(cookie[idx]) if use_proxy else None
            mining = await self.perform_mining(cookie, idx, proxy)
            if mining and mining.get("message") == "Mining job added to queue":
                job_id = mining.get("jobId")
                self.print_message(cookie, idx, proxy, Fore.GREEN, "Perform Mining Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Job Id: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{job_id}{Style.RESET_ALL}"
                )
            else:
                self.print_message(cookie, idx, proxy, Fore.RED, "Perform Mining Failed")
                
            await asyncio.sleep(5 * 60)
        
    async def process_accounts(self, cookie: str, use_proxy: bool, nodes_count: int):
        tasks = []
        idx = 1
        if use_proxy:
            for i in range(nodes_count):
                is_valid = asyncio.create_task(self.process_check_auth(cookie, idx, use_proxy))
                if is_valid:
                    tasks.append(asyncio.create_task(self.process_uptime_static(cookie, idx, use_proxy)))
                    tasks.append(asyncio.create_task(self.process_send_ping(cookie, idx, use_proxy)))
                    tasks.append(asyncio.create_task(self.process_perform_mining(cookie, idx, use_proxy)))
                idx += 1
        else:
            is_valid = await self.process_check_auth(cookie, idx, use_proxy)
            if is_valid:
                tasks.append(asyncio.create_task(self.process_uptime_static(cookie, idx, use_proxy)))
                tasks.append(asyncio.create_task(self.process_send_ping(cookie, idx, use_proxy)))
                tasks.append(asyncio.create_task(self.process_perform_mining(cookie, idx, use_proxy)))

        await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            with open('cookies.txt', 'r') as file:
                cookies = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice, nodes_count = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(cookies)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for cookie in cookies:
                    if cookie:
                        tasks.append(asyncio.create_task(self.process_accounts(cookie, use_proxy, nodes_count)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'cookies.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Capfizz()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Capfizz - BOT{Style.RESET_ALL}                                       "                              
        )