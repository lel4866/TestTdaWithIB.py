import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import asyncio
import datetime
import json
import time
import datetime

import tda
from tda import auth, client, orders, utils
from tda.streaming import StreamClient
from tda.orders.options import OptionSymbol
from tda.orders.common import OrderType
from tda.orders.generic import OrderBuilder

from testib import TestIB

api_key = 'RUM4KIDS@AMER.OAUTHAP'  # also known as consumer key: url-encoded: RUM4KIDS%40AMER.OAUTHAP
data_account_number = 490586653  # account for lel4866b - to get real-time data
order_account_number = 493991357  # account for lel4866c - to place orders and get account positions
token_path_lel4866b = 'C:/Users/lel48/PycharmProjects/TestTdaWithIB.py/lel4866b.txt'  # for quotes
token_path_lel4866c = 'C:/Users/lel48/PycharmProjects/TestTdaWithIB.py/lel4866c.txt'  # for orders

field_list = [StreamClient.LevelOneOptionFields.UNDERLYING, StreamClient.LevelOneOptionFields.BID_PRICE,
              StreamClient.LevelOneOptionFields.ASK_PRICE, StreamClient.LevelOneOptionFields.DELTA]

# This only needs to be done once
def get_auth_token(token_path: str) -> bool:
    if not os.path.exists(token_path):
        print("Attempting to get authorization token.")
        redirect_url = 'https://127.0.0.1'
        # pops up Chrome browser window
        driver = webdriver.Chrome(executable_path='C:/Users/lel48/chromedriver_win32/chromedriver.exe')
        tda.auth.client_from_login_flow(driver, api_key, redirect_url, token_path)
        filename = os.path.split(token_path)[1]
        print(f"Authorization token for {filename} accessed successfully.\n")
        return True
    if not os.path.isfile(token_path):
        print(f"Token path is not a file: {token_path}")
        return False
    return True


def get_option_chain(client: tda.client.Client, symbol: str) -> bool:
    response = client.get_option_chain(symbol, contract_type=tda.client.Client.Options.ContractType.PUT, strike_count=8,
                                       include_quotes='TRUE', strategy=tda.client.Client.Options.Strategy.SINGLE,
                                       interval=None, strike=None,
                                       strike_range=tda.client.Client.Options.StrikeRange.ALL,
                                       from_date=None, to_date=None, volatility=None, underlying_price=None,
                                       interest_rate=None,
                                       days_to_expiration=None, exp_month=None,
                                       option_type=tda.client.Client.Options.Type.STANDARD)
    yy = json.loads(response.text)
    status = yy['status']  # should be 'SUCCESS'
    is_index = yy['isIndex']  # should be True
    underlying = yy['underlying']
    ubid = underlying['bid']
    uask = underlying['ask']
    ulast = underlying['last']
    delayed = underlying['delayed']  # better be False
    yy_list = list(yy)

    # a dict of string keys which are dates and DTE: '2021-09-24:0, 2021-09-27:3..., and values which are a dict of keys which are strikes (like '4440.0' and values that are a dict
    puts = yy['putExpDateMap']
    puts_list = list(puts)
    puts_len = len(puts_list)  # dates:DTE for the option chain

    date0 = puts_list[0]
    puts_for_date0 = puts[date0]
    keys = list(puts_for_date0)  # strikes for the given expiration date
    keys_len = len(keys)
    key0 = keys[0]  # first strike in list
    strikeList = puts_for_date0[key0]
    slen = len(strikeList)
    strikes = strikeList[0]
    s1 = strikes['putCall']
    s2 = strikes['symbol']
    s3 = strikes['description']
    s4 = strikes['exchangeName']
    s5 = strikes['bid']
    s6 = strikes['ask']
    s7 = strikes['last']
    s8 = strikes['mark']
    s9 = strikes['bidSize']
    s10 = strikes['askSize']
    s11 = strikes['bidAskSize']  # sting like '244x16'
    s12 = strikes['lastSize']
    s13 = strikes['highPrice']
    s14 = strikes['lowPrice']
    s15 = strikes['openPrice']
    s16 = strikes['closePrice']
    s17 = strikes['totalVolume']
    s18 = strikes['tradeDate']
    s19 = strikes['tradeTimeInLong']  # unix time stamp
    # datetime.fromtimestamp()
    s19a = datetime.fromtimestamp(s19 / 1000.0)
    s20 = strikes['quoteTimeInLong']
    s20a = datetime.fromtimestamp(s20 / 1000.0)
    s21 = strikes['netChange']
    s22 = strikes['volatility']
    s23 = strikes['delta']
    s23a = strikes['gamma']
    s24 = strikes['vega']
    s25 = strikes['rho']
    s26 = strikes['openInterest']
    s27 = strikes['timeValue']
    s28 = strikes['theoreticalOptionValue']
    s29 = strikes['theoreticalVolatility']
    s30 = strikes['optionDeliverablesList']  # seems to be None
    s31 = strikes['strikePrice']
    s32 = strikes['expirationDate']  # int
    s32a = datetime.fromtimestamp(s32 / 1000.0)
    s33 = strikes['daysToExpiration']
    s34 = strikes['expirationType']  # 'S'
    s35 = strikes['lastTradingDay']  # int
    s35a = datetime.fromtimestamp(s35 / 1000.0)
    s36 = strikes['multiplier']  # 100.0
    s37 = strikes['settlementType']  # 'P'
    s38 = strikes['deliverableNote']  # ""
    s39 = strikes['isIndexOption']  # None
    s40 = strikes['percentChange']
    s41 = strikes['markChange']
    s42 = strikes['markPercentChange']
    s43 = strikes['intrinsicValue']
    s44 = strikes['inTheMoney']  # bool
    s45 = strikes['mini']  # bool
    s46 = strikes['nonStandard']  # bool
    s47 = strikes['pennyPilot']  # bool

    return True


def get_streaming_quotes(account: str, client) -> None:
    # process command line arguments which specify symbols
    equities_list = []
    futures_list = []
    options_list = []
    opt_list = sys.argv[1:]
    for symbol in opt_list:
        if symbol[0] == '/':
            futures_list.append(symbol)
        elif symbol.find('-') >= 0:
            # it's an option symbol SPX-02-19-2022-P-4400
            fields = symbol.split('-')
            opt_symbol = fields[0]
            opt_month = int(fields[1])
            opt_day = int(fields[2])
            opt_year = int(fields[3])
            opt_date = datetime.date(opt_year, opt_month, opt_day)
            opt_type = fields[4]
            opt_strike = fields[5]
            opt_sym_struct = OptionSymbol(opt_symbol, opt_date, opt_strike, opt_type)
            opt_string = opt_sym_struct.build()  # a string - example: 'SPXW_110220P2100'
            options_list.append(opt_string)
        else:
            equities_list.append(symbol)

    stream_client = StreamClient(client, account_id=account)
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(read_stream(stream_client, equities_list, futures_list, options_list))
    # *** never gets here! ***
    print("*** end of event_loop() ***\n")


async def read_stream(stream_client, ok_to_trade_event, equities_quote_list, futures_quote_list, options_quote_list):
    # this stuff gets executed once (remember, await waits for completion)
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    # always add handlers before subscribing
    if len(equities_quote_list) > 0:
        stream_client.add_level_one_equity_handler(lambda msg: quote_handler(msg, ok_to_trade_event))
    if len(futures_quote_list) > 0:
        stream_client.add_level_one_futures_handler(lambda msg: quote_handler(msg, ok_to_trade_event))
    if len(options_quote_list) > 0:
        stream_client.add_level_one_option_handler(lambda msg: quote_handler(msg, ok_to_trade_event))

    # now, subscribe
    if len(equities_quote_list) > 0:
        await stream_client.level_one_equity_subs(equities_quote_list)
    if len(futures_quote_list) > 0:
        await stream_client.level_one_futures_subs(futures_quote_list)
    if len(options_quote_list) > 0:
        await stream_client.level_one_option_subs(options_quote_list, fields=field_list)

    # add handler then subscribe to account activity
    stream_client.add_account_activity_handler(account_activity)
    await stream_client.account_activity_sub()

    # stream_client.add_timesale_equity_handler(lambda msg: printGoog(msg))
    # await stream_client.timesale_equity_subs(['SPY'])
    # await stream_client.nasdaq_book_subs(['SPY'])

    # here's where each event from tda gets processed
    print("*** wait for stream_client event in read_stream() ***\n")
    #while True:
    for i in range(0,4):
        # print("*** before handle_message")
        await stream_client.handle_message()
        # print("*** after handle_message\n")

    print("*** end of read_stream() ***\n")


def quote_handler(msg, ok_to_trade_event):
    yy = msg['content']
    for quote in yy:
        # if 'LAST_PRICE' in quote:
        # print(quote['key'], " ", quote['LAST_PRICE'])
        print(quote)


def get_streaming_quotes(account: str, client) -> None:
    # process command line arguments which specify symbols
    equities_quote_list = []
    futures_quote_list = []
    options_quote_list = []
    opt_list = sys.argv[1:]
    for symbol in opt_list:
        if symbol[0] == '/':
            futures_quote_list.append(symbol)
        elif symbol.find('-') >= 0:
            # it's an option symbol
            fields = symbol.split('-')
            opt_month = int(fields[1])
            opt_day = int(fields[2])
            opt_year = int(fields[3])
            opt_date = datetime.date(opt_year, opt_month, opt_day)
            opt_sym_struct = OptionSymbol(fields[0], opt_date, fields[5], fields[4])
            opt_string = opt_sym_struct.build()   # a string - example: 'SPXW_110220P2100'
            options_quote_list.append(opt_string)
        else:
            equities_quote_list.append(symbol)

    stream_client = StreamClient(client, account_id=account)
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(read_stream(stream_client, equities_quote_list, futures_quote_list, options_quote_list))
    # *** never gets here! ***
    print("*** end of event_loop() ***\n")


def place_option_order(data_client: tda.client.Client, account: str, order: list):
    # legs is a list of options
    # each option is a dict with keys: symbol, quantity, expiration_date, type, strike;
    # values are all strings (including strike), except for quantity, which is signed int, and expiration_date which is
    # a datetime.date
    # places order, saves opt_string in orders dict (under key 'opt_string')

    # wait until we get 2 requests over 10 seconds with same bid/ask
    bid_ask_list = [] # will have 1 item per leg
    for leg in order:
        bid, ask = get_option_price(data_client, leg)
        bid_ask_list.append((bid, ask))
    time.sleep(10)

    prices_changed = False
    while True:
        for i, leg in enumerate(order):
            bid_ask = get_option_price(data_client, leg)
            if bid_ask != bid_ask_list[i]:
                prices_changed = True
                bid_ask_list[i] = bid_ask

        if not prices_changed:
            break
        prices_changed = False

    ok_to_trade_event.set()


def get_option_price(data_client: tda.client.Client, option) -> (float, float):
    symbol = option['symbol']
    expiration_date = option['expiration_date']
    type = option['type']
    strike = option['strike']
    opt_sym_struct = OptionSymbol(symbol, expiration_date, type, strike)
    opt_string = opt_sym_struct.build()  # SPX_101521P4400: 10/15/2021 SPX Put at strike of 4400
    response = data_client.get_quote(opt_string)
    response_dict = json.loads(response.text)
    opt_dict = response_dict[opt_string]
    bid = opt_dict['bidPrice']
    ask = opt_dict['askPrice']
    return (bid, ask)


def place_stock_order(account: str) -> bool:
    do_order = False
    pct = False
    total_buy_amount = 50000.0
    buyQuantityDict = {"XLY": 102, "XRT": 138, "SPYG": 158, "TLT": 44, "SPY": 19, "GLD": 5, "DBC": 59, "TIP": 7}

    # this is where we really start...c is a client
    c_4866b = auth.client_from_token_file(token_path_lel4866b, api_key)  # for quotes
    c_4866c = auth.client_from_token_file(token_path_lel4866c, api_key)  # for orders
    for k, v in buyQuantityDict.items():
        resp = c_4866b.get_quote(k)
        respdict = json.loads(resp.text)
        symDict = respdict[k]
        symPrice = symDict["askPrice"]
        # symPrice = buyPriceDict[k]
        print(f"{k} askPrice={symPrice}")
        quantity = 0
        builder_object = None
        if pct:
            quantity = total_buy_amount * .01 * v / symPrice
            quantity = round(quantity, 0)
        else:
            quantity = v
        # quantity = 1
        if do_order:
            if quantity > 0:
                # builder_object = tda.orders.equities.equity_buy_limit(k, quantity, symPrice)
                builder_object = tda.orders.equities.equity_buy_market(k, quantity)
            elif quantity < 0:
                # builder_object = tda.orders.equities.equity_sell_limit(k, -quantity, symPrice)
                builder_object = tda.orders.equities.equity_sell_market(k, -quantity)
            order_spec = builder_object.build()
            res = c_4866c.place_order(account, order_spec)
            if not res.ok:
                print(res.text)
            else:
                # order_id = utils.Utils(client, account).extract_rder_id(res)
                # assert order_id is not None
                order_id = 1
                print(f"Order placed for {quantity} shares of {k}. order id = {order_id}\n")
        else:
            print(f"Order placed for {quantity} shares of {k}\n")

        # break;
    return

    opt_sym1 = OptionSymbol('SPX', datetime.date(year=2021, month=2, day=19), 'P', '1900')
    symbol1 = opt_sym1.build()  # 'SPXW_110220P2100'
    opt_sym2 = OptionSymbol('SPX', datetime.date(year=2021, month=2, day=19), 'P', '2000')
    symbol2 = opt_sym2.build()  # 'SPXW_110220P2100'
    symbol3 = "AGG"

    resp = c_4866b.get_quote(symbol3)

    # symbol = ".SPXW201102P2100&C" doesn't work
    # place order to buy single put
    # quantity = 3
    # limit_price = 1.05
    # builder_object = tda.orders.options.option_buy_to_close_limit(symbol2, quantity, limit_price)
    # builder_object.set_requested_destination(tda.orders.common.Destination.CBOE)
    # order_spec = builder_object.build()

    # place order for a PCS
    quantity = 1
    limit_price = 0.75  # debit or credit is determined by function call
    # smaller strike first: for pcs, long put is first, short put is second
    builder_object = tda.orders.options.bull_put_vertical_open(symbol1, symbol2, quantity, 0.75)
    builder_object.set_requested_destination(tda.orders.common.Destination.CBOE)
    order_spec = builder_object.build()

    # futures_builder_object = orders.equities.equity_buy_limit(symbol3, 1, 100.00)
    # order_spec = futures_builder_object.build()

    call_do_order = False

    stream_client = StreamClient(c_4866c, account_id=account)
    # fields = [stream_client.LevelOneOptionFields.ASK_PRICE]

    event_loop = asyncio.get_event_loop()

    async def read_stream(do_order):
        # this stuff gets executed once
        await stream_client.login()
        await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

        # always add handlers before subscribing
        stream_client.add_account_activity_handler(lambda msg: account_activity(msg))
        stream_client.add_level_one_option_handler(lambda msg: printOption(msg))
        # stream_client.add_timesale_options_handler(lambda msg: printGoog(msg))
        # stream_client.add_timesale_equity_handler(lambda msg: printGoog(msg))

        # await stream_client.nasdaq_book_subs(['SPY'])
        # await stream_client.timesale_equity_subs(['SPY'])
        await stream_client.account_activity_sub()
        await stream_client.level_one_option_subs([symbol1, symbol2])  # fields doesn't work
        # await stream_client.timesale_options_subs(['.SPX201120C2700&C'])

        # here's where each event from tda gets processed
        print("*** wait for stream_client event in read_stream() ***\n")
        while True:
            # I put do order here so we won't miss any events cause by placing order
            # also, processing the events may cause us to modiy/place additional orders
            if do_order:
                print(f"placing order for put credit spread\n")
                rc, order_id = actually_do_order(account, c_4866c, order_spec)
                # now check to make sure order happened
                event_loop.call_later(5.0, check_order_entry, "xxx1111yyy")
                do_order = False

            # print("*** before handle_message")
            await stream_client.handle_message()
            # print("*** after handle_message\n")

        print("*** end of read_stream() ***\n")

    # asyncio.get_event_loop().run_until_complete(read_stream(call_do_order))
    event_loop.run_until_complete(read_stream(call_do_order))
    # asyncio.run(read_stream(call_do_order))
    # *** never gets here! ***
    print("*** end of get_event_loop() ***\n")


def check_order_entry(order_id):
    print(f"check_order_entry called. order_id={order_id}")
    asyncio.get_event_loop().call_later(2.0, check_order_entry, order_id)


# async def timeout_callback():
#     await asyncio.sleep(0.1)
#     print('echo!')


def actually_do_order(account, c, order_spec):
    res = c.place_order(account, order_spec)
    if not res.ok:
        print(res.text)
        return False, 0
    order_id = utils.Utils(client, account).extract_order_id(res)
    assert order_id is not None
    print(f"Order placed. order id = {order_id}\n")
    return True, order_id


def printOption(msg):
    print("*** option handler message: ***")
    return
    yy = msg['content']
    zz = yy[0]
    if 'DESCRIPTION' in zz:
        ww = zz['DESCRIPTION']
        if ww == 'Symbol not found':
            print(f"Symbol not found: {zz['key']}")
            return
    print(json.dumps(msg, indent=4))
    print("\n")
    xxx = 1


def account_activity(msg):
    print("*** account_activity message: ***")
    if type(msg) is not dict:
        print("*** Error: msg is not a dict ***")
        return

    if 'service' not in msg:
        print("*** Error: service not in msg ***")
        return
    service = msg['service']

    if service != "ACCT_ACTIVITY":
        print(f"*** Error: unknown service = '{service}'")
        return

    if 'content' not in msg:
        print("*** Error: content not in msg")
        return
    content = msg['content']

    # print(json.dumps(msg, indent=4))
    # print("\n")


def printGoog(msg):
    print(json.dumps(msg, indent=4))
    print("\n")
    yy = msg['content']
    zz = yy[0]
    ww = zz['DESCRIPTION']
    xxx = 1


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()


def select_sttbwb_plus_bsh_options(data_client: tda.client.Client) -> list[dict]:
    # an stt bwb consists of 4 option strikes. A 25-15-5 delta broken wing butterfly at about 160DTE and2 long puts at
    # at about 90DTE

    option_list = [
        {'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'},
        {'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'},
        {'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'},
        {'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'}
    ]

    # get_option_chain(data_client, '$SPX.X')

    return option_list


def place_stt_order(options_list: list[dict]):
    assert len(options_list) > 0

    #order = [{'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'}]
    #place_option_order(data_client, data_account_number, order)
    # opt_sym_struct = OptionSymbol(order[0]['symbol'], order[0]['expiration_date'], order[0]['type'], order[0]['strike'])
    # opt_string = opt_sym_struct.build()  # SPX_101521P4400: 10/15/2021 SPX Put at strike of 4400
    # response = data_client.get_quote(opt_string)
    # response_dict = json.loads(response.text)
    # opt_dict = response_dict[opt_string]
    # mark = opt_dict['mark']
    # bid = opt_dict['bidPrice']
    # ask = opt_dict['askPrice']

    stream_client = StreamClient(data_client, account_id=data_account_number)
    event_loop = asyncio.get_event_loop()

    # start getting quotes on option legs
    quote_task = event_loop.create_task(read_option_stream(stream_client, options_list))

    # place trade
    # wait for option quotes to be valid
    place_trade(options_list)

    # check trade
    #event_loop.call_soon(check_trade(options_list))

    # wait for trade to complete
    event_loop.run_forever()

    zz = 1


async def read_option_stream(stream_client, option_list):
    assert len(options_list) > 0

    # this stuff gets executed once (remember, await waits for completion)
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    stream_client.add_level_one_option_handler(quote_handler)
    await stream_client.level_one_option_subs(options_list) #, fields=field_list)

    while trade_check_count >= 0:
        print("*** handle_message called")
        await stream_client.handle_message()
        # print("*** after handle_message\n")

    # logout of stream client
    print("*** end of read_stream() ***\n")


def place_trade(options_list):
    global trade_check_count

    trade_check_count = 0
    return


async def amain():
    await asyncio.sleep(10)
    print('hello')


def do_option_order():
    # select strikes for bwb (25-15-5 delta at 160 DTE, 2LP's at 90DTE)

    data_client = auth.client_from_token_file(token_path_lel4866b, api_key)  # for quotes
    options_list = select_sttbwb_plus_bsh_options(data_client)

    ok_to_trade_event = asyncio.Event()
    asyncio.ensure_future(do_trade(ok_to_trade_event))

    get_stt_quotes(data_client, ok_to_trade_event, options_list)
    # place_stt_order(options_list)


def get_stt_quotes(data_client, ok_to_trade_event, option_list: list[dict]):
    # first convert passed in option dictionaries yo tda-api option strings
    # {'symbol': 'SPX', 'expiration_date': datetime.date(2022, 3, 18), 'type': 'P', 'strike': '4400'},
    optstr_list = []  # list of strings that read_stream takes
    for option_dict in option_list:
        opt_sym_struct = OptionSymbol(option_dict['symbol'], option_dict['expiration_date'], option_dict['type'],
                                      option_dict['strike'])
        opt_string = opt_sym_struct.build()  # a string - example: 'SPXW_110220P2100'
        optstr_list.append(opt_string)

    # now create a tda-api StreamClient that will get quotes for those options
    stream_client = StreamClient(data_client, account_id=data_account_number)
    asyncio.get_event_loop().run_until_complete(read_stream(stream_client, ok_to_trade_event, [], [], optstr_list))
    # *** never gets here! ***
    print("*** end of event_loop() ***\n")


async def get_quotes(event):
    #asyncio.ensure_future(do_trade())

    count = 0
    while not kill:
        await asyncio.sleep(1)
        if count == 2:
            print("event set")
            event.set()
        print("First Worker Executed")
        count = count + 1
    print("First Worker ended")


async def do_trade(event):
    global kill

    await event.wait()  # wait until it is ok to trade
    print("ok to trade")

    for i in range(1,3):
        print("Second Worker Executed")
        await asyncio.sleep(3)

    print("Second Worker ended")
    kill = True


# command line arguments: space delimited list of symbols
# options are colon separated sets of minus separated values:
#    symbol-expirationMonth-expirationDay-expirationYear-strike-P|C
#
# output is 1 line per symbol (symbol is same as input)
#     symbol bid ask last
#     options may not have last
if __name__ == '__main__':
    # use lel4866b for data, IB for trades
    rc = get_auth_token(token_path_lel4866b)
    if not rc:
        exit(-1)

    #asyncio.run(amain())
    if False:
        kill = False
        loop = asyncio.get_event_loop()  # loop is global!!
        ok_to_trade_event = asyncio.Event()
        asyncio.ensure_future(do_trade(ok_to_trade_event))
        loop.run_until_complete(get_quotes(ok_to_trade_event))
        print("Closing Loop")
        loop.stop()
        loop.close()
        exit(0)

    place_stock_orders = False
    place_option_orders = True
    run_ib = False

    if place_option_orders:
        do_option_order()
        exit(0)

    if place_stock_orders:
        rc = get_auth_token(token_path_lel4866c)
        if not rc:
            exit(-1)
        place_stock_order(order_account_number)
        exit(0)

    if run_ib:
        app = TestIB()
        app.nextOrderId = 0
        exit(0)
