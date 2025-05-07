import requests
from bs4 import BeautifulSoup

class VidioAuth:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Pragma': 'no-cache',
            'Accept': '*/*'
        }
        
    def get_authenticity_token(self):
        url = "https://www.vidio.com/users/login"
        response = self.session.get(url, headers=self.headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'name': 'authenticity_token'})
            if token_input:
                return token_input.get('value')
        return None
        
    def login(self, username, password):
        token = self.get_authenticity_token()
        if not token:
            return False, "Failed to get authenticity token"
            
        login_url = "https://www.vidio.com/users/login"
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.6',
            'cache-control': 'max-age=0',
            'content-length': '215',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.vidio.com',
            'priority': 'u=0, i',
            'referer': 'https://www.vidio.com/users/login',
            'sec-ch-ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        payload = {
            'authenticity_token': token,
            'user[login]': username,
            'user[password]': password,
            'user[remember_me]': '1',
            'commit': 'Sign In'
        }
        
        response = self.session.post(login_url, data=payload, headers=headers)
        
        # Check for successful login
        if response.status_code == 200:
            if "Sign Out" in response.text:
                return True, "Login successful"
            elif "Password min. 8 characters" in response.text or "Your email and password don't match." in response.text:
                return False, "Login failed - invalid credentials"
        return False, "Login failed"
        
    def get_transaction_history(self):
        url = "https://www.vidio.com/dashboard/transaction/histories"
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'priority': 'u=0, i',
            'referer': 'https://www.vidio.com/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        }
        
        response = self.session.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract Plan information
            plan_element = soup.find('h3', {'class': 'dashboard-transaction-history__detail-transaction-title'})
            plan = plan_element.text.strip() if plan_element else "Not found"
            
            # Extract Aktif information
            aktif_element = soup.find('span', {'class': 'dashboard-transaction-history__detail-transaction-description'})
            aktif = aktif_element.text.strip() if aktif_element else "Not found"
            
            return {
                'Plan': plan,
                'Aktif': aktif
            }
        return None