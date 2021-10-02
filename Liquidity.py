from bs4 import BeautifulSoup
from datetime import datetime
import requests, colorama, time

colorama.init()


class PanckaeswapNewListing():


    pancakeswap = {}
    colours = {}
    header = {
        # 'Host'                      : 'm.youtube.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'close',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

    def __init__(self):
        '''
        Constructor function
        '''
        self.pancakeswap = {
            'version': 2,
            'factory_address': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',  # Panckaeswap Factory Address
            'route_address': '0x10ed43c718714eb63d5aa57b78b54704e256024e',  # Pancakeswap Router V2 Contract Address
            'wbnb': '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'  # WBNB Contract Address
        }

    def connect(self, url=None, header=None):
        '''
        Connect function is used to fetch HTML using GET request
        '''
        if url == None:
            return None
        else:
            if header == None:
                header = self.header
            else:
                header = header

            page = requests.get(url, headers=header)
            return page

    def getLiquidityInfo(self, creator_address=None):
        if creator_address != None:
            request = self.connect("https://bscscan.com/address/" + creator_address)
            if request.status_code == 200:
                soup = BeautifulSoup(request.text, 'lxml')
                getLiquidity = soup.find('a', attrs={
                    'title': 'PancakeSwap: Router v2\n(' + self.pancakeswap['route_address'] + ')'})

                if getLiquidity != None:
                    liquidityValue = getLiquidity.parent.parent.next_sibling.text
                    return liquidityValue
                else:
                    return None
            else:
                return None
        else:
            return None

    def getTokenCreator(self, contract_address=None):
        if contract_address != None:
            request = self.connect("https://bscscan.com/address/" + contract_address)
            if request.status_code == 200:
                soup = BeautifulSoup(request.text, 'lxml')
                getCreator = soup.find(attrs={'title': 'Creator Address'})

                if getCreator != None:
                    creatorTxn = soup.find(attrs={'title': 'Creator Txn Hash'}).text
                    creatorAddress = getCreator.text
                    return creatorAddress, creatorTxn
                else:
                    return None
            else:
                return None
        else:
            return None

    def getTokenInfo(self, contract_address=None):
        if contract_address != None:
            request = self.connect("https://bscscan.com/token/" + contract_address)
            if request.status_code == 200:
                soup = BeautifulSoup(request.text, 'lxml')
                getTokenName = soup.find('div', class_="media-body")
                getTokenSumarry = soup.find(id="ContentPlaceHolder1_divSummary")
                tokenName = getTokenName.find('span').text.replace(" ", "")
                tokenSupply = getTokenSumarry.find('input', id="ContentPlaceHolder1_hdnTotalSupply").get('value')
                tokenSymbol = getTokenSumarry.find('input', id="ContentPlaceHolder1_hdnSymbol").get('value')

                return {
                    'token_name': tokenName,
                    'token_symbol': tokenSymbol,
                    'token_supply': tokenSupply
                }
            else:
                return None
        else:
            return None

    def getNewPair(self,token):
        request = self.connect(
            "https://bscscan.com/address-events?m=normal&a=" + self.pancakeswap['factory_address'] + "&v=" +
            self.pancakeswap['factory_address'])
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'lxml')
            getLastPair = soup.find(id='demo1')
            getTokenPairs = getLastPair.find_all('a')

            # Swap token list to get fix token0 as a new token not a pair token (wbnb)
            if getTokenPairs[0].text == self.pancakeswap['wbnb']:
                getTokenPairs[0], getTokenPairs[1] = getTokenPairs[1], getTokenPairs[0]

            return {
                'token0': token,  # Token0 as a new token
                'token1': getTokenPairs[1].text,  # Token1 as a pair token in this case is WBNB
                'pair': getTokenPairs[2].text  # Pair Address
            }
        else:
            return None


    def run(self,tokenadd):
        lastToken = None
        getPair = self.getNewPair(tokenadd)
        if getPair != None:
            if getPair['token0'] != lastToken:
                lastToken = getPair['token0']
                getToken = self.getTokenInfo(getPair['token0'])
                if getToken != None:
                    getCreator = self.getTokenCreator(getPair['token0'])
                    if getCreator != None:
                        getLiquidity = self.getLiquidityInfo(getCreator[0])
                        return getLiquidity
