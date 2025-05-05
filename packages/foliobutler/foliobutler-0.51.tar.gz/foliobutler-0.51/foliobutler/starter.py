import os
import time
import click
from click_params import EMAIL
import logging
from datetime import datetime
from foliobutler.fb_api import get_token, get_folios  # type: ignore
from foliobutler.fb_api import post_json
from dotenv import dotenv_values
from ib_insync import IB, Forex, util, Stock, Order


def send_email(to_email, config, text, debug=False):
    import smtplib
    # print(config)
    TO_EMAIL = to_email
    MY_EMAIL = config['SEND_EMAIL']
    MY_PASSWORD = config['SEND_EMAILPASS']
    with smtplib.SMTP(config['SMTP']) as connection:
        if debug:
            print("SENDING... {}".format(text))
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=[TO_EMAIL],
            msg=f"From: {MY_EMAIL}\r\nSubject: FolioButler Check Orders\r\n\r\n{text}"
        )


def create_config(env=None):
    if env is None:
        env = env_location()
    if not os.path.exists(os.path.dirname(env)):
        os.mkdir(os.path.dirname(env))
    if 'HOST' in os.environ:
        host = os.environ['HOST']
    else:
        host = input("Enter the host [https://foliobutler.com]:") or\
            "https://foliobutler.com"

    if 'EMAIL' in os.environ:
        email = os.environ['EMAIL']
    else:
        email = input("Enter your Foliobutler Email: ")

    if 'SEND_EMAIL' in os.environ:
        send_email = os.environ['SEND_EMAIL']
    else:
        send_email = input("Enter your Sender Email: ")

    if 'SEND_EMAILPASS' in os.environ:
        send_emailpass = os.environ['SEND_EMAILPASS']
    else:
        send_emailpass = input("Enter your Sender Email Password: ")

    if 'SMTP' in os.environ:
        smtp = os.environ['SMTP']
    else:
        smtp = input("Enter your Sender SMTP Server:")

    if 'API_KEY' in os.environ:
        api = os.environ['API_KEY']
    else:
        api = input("Enter your Foliobutler Api-Key: ")

    if 'ib_port' in os.environ:
        ib_port = os.environ['ib_port']
    else:
        ib_port = click.prompt('Please enter the TWS Port:', default='7497')

    f = open(env, "w+")
    f.write("HOST={}\n".format(host))
    f.write("EMAIL={}\n".format(email))
    f.write("SEND_EMAIL={}\n".format(send_email))
    f.write("SEND_EMAILPASS={}\n".format(send_emailpass))
    f.write("SMTP={}\n".format(smtp))
    f.write("API_KEY={}\n".format(api))
    f.write("ib_port='{}'\n".format(ib_port))
    f.close()


def add_account(dest_path):
    source_path = os.path.dirname(__file__)
    if 'port' in os.environ:
        port = os.environ['port']
    else:
        port = click.prompt('Please enter the port for the account:',
                            default=4001)
    if 'user' in os.environ:
        IbLoginId = os.environ['user']
    else:
        IbLoginId = click.prompt('Please enter IB Username')
    if 'pass' in os.environ:
        IbPassword = os.environ['pass']
    else:
        IbPassword = click.prompt('Please enter IB Password')

    source = os.path.join(source_path, 'ibc_default_ini')
    destination = os.path.join(dest_path, str(port)+'.ini')
    from shutil import copyfile
    import dotenv
    copyfile(source, destination)
    dotenv.set_key(destination, "IbLoginId", IbLoginId)
    dotenv.set_key(destination, "IbPassword", IbPassword)
    dotenv.set_key(destination, "OverrideTwsApiPort",
                   str(port), quote_mode="never")
    print("Please protect the Folder ", dest_path)


def connected_ib(config, api_ip, api_port, clientId):
    ib = IB()

    def customErrorHandler(reqId, errorCode, errorString, contract):
        if errorCode in [2104, 2106, 2107, 2158]:
            return
        print(f"Fehlermeldung: {errorCode} - {errorString}")

    ib.errorEvent += customErrorHandler

    for x in range(5):
        try:
            ib.connect(api_ip, api_port, clientId=clientId+x)
            if ib:
                return ib
        except Exception:
            # clientId = clientId + 1
            print("Connecting {}:{} clientID = {}".format(
                api_ip, api_port, clientId+x))
            # ib.connect(api_ip, api_port, clientId=clientId)
    return ib


def debug_meldungen_fb(account, api_ip, api_port, fb_positions, fb_orders):
    logging.debug("---- SYNC ---- : {} {} {}".format(
        account, api_ip, api_port))
    if len(fb_positions) > 0:
        logging.debug("---- Foliobutler current positions:")
    for ticker, _data in fb_positions.items():
        logging.debug("{} x {}".format(_data['amount'], ticker))
    # logging.debug("FB Positions: {}".format(fb_positions))
    if len(fb_orders) > 0:
        logging.debug("---- Foliobutler current orders:")
    for ticker, _data in fb_orders.items():
        logging.debug(ticker, _data)
    # logging.debug("FB Orders: %s ", str(fb_orders))


def debug_meldungen_tws(openTrades, portfolio):
    if len(portfolio) > 0:
        logging.debug("---- TWS current positions:")
    for data in portfolio:
        logging.debug("{} x {}".format(data.position, data.contract.symbol))

    # logging.debug("IB OpenTrades: %s ", openTrades)
    if len(openTrades) > 0:
        logging.debug("---- TWS current OpenTrades:")
    for data in openTrades:
        quantity = data.order.totalQuantity
        if data.order.action != 'BUY':
            quantity = -quantity
        logging.debug("{} x {}".format(quantity,
                                       data.contract.symbol))
    # Trade(contract=Stock(
    #   conId=418893644,
    #   symbol='USO',
    #   right='?',
    #   exchange='SMART',
    #   currency='USD',
    #   localSymbol='USO',
    #   tradingClass='USO'),
    # order=Order(
    #   orderId=8748,
    #   clientId=1,
    #   permId=1397787043,
    #   action='BUY',
    #   totalQuantity=220.0,
    #   orderType='MKT',
    #   lmtPrice=0.0,
    #   auxPrice=0.0,
    #   tif='OPG',
    #   ocaType=3,
    #   displaySize=2147483647,
    #   openClose='',
    #   volatilityType=0,
    #   deltaNeutralOrderType='None',
    #   referencePriceType=0,
    #   account='U2174937',
    #   clearingIntent='IB',
    #   adjustedOrderType='None',
    #   cashQty=0.0,
    #   dontUseAutoPriceForHedge=True),
    # orderStatus=OrderStatus(
    #   orderId=8748,
    #   status='PreSubmitted',
    #   filled=0.0,
    #   remaining=220.0,
    #   avgFillPrice=0.0,
    #   permId=1397787043,
    #   parentId=0,
    #   lastFillPrice=0.0,
    #   clientId=1,
    #   whyHeld='',
    #   mktCapPrice=0.0),
    # fills=[],
    # log=[
    # TradeLogEntry(
    #   time=datetime.datetime(2023, 5, 14, 8,
    #     47, 2, 173702, tzinfo=datetime.timezone.utc),
    #   status='PreSubmitted',
    #   message='',
    #   errorCode=0)],
    #   advancedError='')
    print("__________________________________________")


def check_order(symbol, fb_ist, fb_soll, ib_ist, ib_soll, order, quiet):
    if fb_soll == (fb_ist + fb_soll) - (ib_ist + ib_soll):
        return order
    if fb_soll + fb_ist == 0 and fb_soll != ib_soll:
        logging.info(">>{} {} {} {} {} => {}".format(symbol, fb_ist, fb_soll,
                                                     ib_ist, ib_soll, -ib_ist))
        order.totalamount = abs(ib_ist)
        return order
    if fb_ist + fb_soll == 0 and ib_ist + ib_soll > 0 and not quiet:
        answer = input("soll {} verkauft werden (nicht in foliobutler)?\
[(I)gnore, (M)arket, (L)imit, (D)epot]".format(symbol))
        if answer.upper() == "I":
            import json
            print(os.path.dirname(g_env))
            x = '{"organization" :"GeeksForGeeks","country":"India"}'
            y = {"pin": 110096}
            z = json.loads(x)
            z.update(y)
            print(json.dumps(z))

        return None
    if fb_soll == 0 and ib_soll == 0:
        percent_change = ((fb_ist/ib_ist)*100-100) if ib_ist != 0\
            else 100
        if abs(fb_ist - ib_ist) < max(fb_ist, ib_ist)*0.05:
            print("ignore {:d} {:.2f}%".format(
                int(abs(fb_ist - ib_ist)),
                percent_change))
        else:
            print("TODO {} {:d} -> {:d} ({:.2f}%)".format(
                symbol, int(ib_ist), int(fb_ist),
                percent_change
            ))
    elif ib_soll == 0 and (fb_ist + fb_soll) == 0:
        order.action = 'SELL'
        order.totalQuantity = abs(ib_ist)
        return order
    else:
        logging.info("TODO2: {} {:d} {:d} {:d} {:d} => "
                     .format(
                        symbol, int(fb_ist), int(fb_soll),
                        int(ib_ist), int(ib_soll)))
        # print(todo, fb_soll, abs(todo-fb_soll))
        # print(max(abs(todo), abs(fb_soll)))
        # print("amount:", todo)
        # for t in openTrades:
        #    # print(symbol)
        #    if t.contract.symbol == symbol:
        #        if t.contract.symbol == "USO":
        #            print("jojoamount:", todo)
# logging.debug(trade)
    return None
    pass


def sync(account, config, api_ip, api_port,
         fb_positions, fb_orders, clientId, quiet, debug, email):
    debug_meldungen_fb(account, api_ip, api_port, fb_positions, fb_orders)
    ib = connected_ib(config, api_ip, api_port, clientId)

    accountlist = ib.managedAccounts()
    if account not in accountlist:
        ib.disconnect()
        print(account + " not found.")
        return account + " not found."
    ib.reqAllOpenOrders()

    openTrades = ib.openTrades()
    portfolio = ib.positions(account=account)
    # print(portfolio)
    debug_meldungen_tws(openTrades, portfolio)
    current_ib_stocks = [x.contract.symbol + "_" + x.contract.secType + "_"
                         + x.contract.currency
                         for x in portfolio if x.contract.currency == 'USD']
    current_ib_orders = [x.contract.symbol + "_" + x.contract.secType + "_"
                         + x.contract.currency
                         for x in openTrades if x.order.account == account]
    current_fb_stocks = [x for x in fb_positions.keys() if x.count("_") == 2]
    # current_fb_orders = [x for x in fb_orders]
    current_fb_orders = [x for x in fb_orders.keys() if x.count("_") == 2]

    allset = set(current_ib_stocks + current_ib_orders +
                 current_fb_stocks + current_fb_orders)
    email_message = []
    for stock in allset:
        symbol = stock.split("_")[0]
        type = stock.split("_")[1]
        currency = stock.split("_")[2]

        # fb_ist = fb_positions[stock]['amount']
        #          if stock in fb_positions else 0
        fb_ist = 0
        for p in fb_positions:
            if p.count("_") == 3:
                if stock == p[:p.rfind("_")]:
                    fb_ist = fb_ist + fb_positions[p]['amount']
            else:
                if stock == p:
                    fb_ist = fb_ist + fb_positions[stock]['amount']

        # fb_soll = fb_orders[stock]['amount'] if stock in fb_orders else 0
        fb_soll = 0
        for p in fb_orders:
            if p.count("_") == 3:
                if stock == p[:p.rfind("_")]:
                    fb_soll = fb_soll + fb_orders[p]['amount']
            else:
                if stock == p:
                    fb_soll = fb_soll + fb_orders[stock]['amount']

        ib_ist = 0
        ib_soll = 0

        for ib_stock in openTrades:
            if ib_stock.contract.symbol == symbol and\
               ib_stock.contract.currency == currency and\
               ib_stock.contract.secType == type and\
               ib_stock.order.account == account:
                if ib_stock.orderStatus.status in ['PreSubmitted',
                                                   'Submitted']:
                    if ib_stock.order.action == 'SELL':
                        ib_soll = ib_soll - ib_stock.order.totalQuantity
                    else:
                        ib_soll = ib_soll + ib_stock.order.totalQuantity

                elif ib_stock.orderStatus.status in ['PendingCancel']:
                    pass
                else:
                    raise Exception("Unknown status: " +
                                    ib_stock.orderStatus.status)
        for ib_stock in portfolio:
            if ib_stock.contract.symbol == symbol and\
               ib_stock.contract.currency == currency and\
               ib_stock.contract.secType == type:
                ib_ist = ib_ist + ib_stock.position

        todo = (fb_ist + fb_soll) - (ib_ist + ib_soll)
        if todo != 0:
            logging.info("{} {} {} {} {} => {}".format(stock, fb_ist, fb_soll,
                                                       ib_ist, ib_soll, todo))
            email_message.append("{} {} {} {} {} => {}".format(stock, fb_ist,
                                 fb_soll, ib_ist, ib_soll, todo))

        if todo != 0:
            # if todo != fb_soll:
            #    continue
            contract = Stock(symbol, 'SMART', currency)
            contracts = ib.qualifyContracts(contract)
            logging.debug(contracts)
            # logging.info("{} * {}".format(abs(todo), symbol))
            ordertype = fb_orders[stock]['ordertype']\
                if stock in fb_orders else 'MKT'
            timeinforce = fb_orders[stock]['timeinforce']\
                if stock in fb_orders else 'OPG'
            limit_price = fb_orders[stock]['limit_price']\
                if stock in fb_orders else None
            order = Order(orderType=ordertype,
                          action='BUY' if todo > 0 else 'SELL',
                          totalQuantity=abs(todo),
                          tif=timeinforce,
                          lmtPrice=limit_price,
                          account=account)
            order = check_order(symbol, fb_ist, fb_soll,
                                ib_ist, ib_soll, order, quiet)
            if order is not None:
                ib.placeOrder(contract, order)
    ib.disconnect()
    return email_message


def old_in_sync_test(config, api_ip, api_port):
    logging.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    ib = connected_ib(config, api_ip, api_port)

    contract = Forex('EURUSD')
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='120 S',
        barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=True)

    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    df.to_csv(os.path.join(config['ibcIniPath'], 'my_csv.csv'), mode='a',
              header=False)


def env_path():
    return os.path.join(os.path.expanduser("~"), 'Documents', 'foliobutler')


def env_location():
    return os.path.join(env_path(), '.env')


def starter(env, action, ip, port, quiet, debug, email):
    clientId = 10
    if action.lower() == 'init':
        return create_config(env)

    if not os.path.exists(os.path.dirname(env)):
        logging.error("Enviroment Path not exists: " + os.path.dirname(env))
        if click.confirm('Do you want to create the folder?', default=True):
            os.mkdir(os.path.dirname(env))
    if not os.path.exists(env):
        email = input("Enter your Foliobutler Email: ")
        api = input("Enter your Foliobutler Api-Key: ")
        f = open(env, "a")
        f.write("EMAIL={}\nAPI_KEY={}\n".format(email, api))
        f.close()

    config = dotenv_values(env)

    if action.lower() == 'upload':
        return upload_positions(env, ip, port, clientId, debug)

    if action.lower() == 'add_account':
        return add_account(config['ibcIniPath'])
    # else:
    # print(action.lower())

    token = get_token(config['HOST'], config['EMAIL'], config['API_KEY'])
    folios = get_folios(config['HOST'], token)
    emailtxt = ""
    for folioname in list(folios):
        f = folios[folioname]
        if f['ib_sync']:
            emailtxt = emailtxt + folioname + "\n"
            # print(ip or f['ib_ip'])
            message = sync(f['ib_account'],
                           config, ip or f['ib_ip'],
                           port or f['ib_port'],
                           f['positions'],
                           f['orders'],
                           clientId,
                           quiet, debug, email)
            for m in message:
                emailtxt = emailtxt + m + "\n"
            emailtxt = emailtxt + "\n"
            time.sleep(1)
            clientId = clientId + 1
    # print(emailtxt)
    if email is not None:
        send_email(email, config, emailtxt, True)


@click.command()
@click.option('--env', default=env_location(),
              help='Location of Enviroment-file. Default {}'
              .format(env_location()))
@click.option('--action', default='sync',
              help='init, add_account, sync, upload')
@click.option('--ip', default=None, help='IP')
@click.option('--port', default=None, help='Port')
@click.option('--quiet/--not-quiet', default=False, help='no questions asked')
@click.option('--debug/--no-debug', default=False)
@click.option('-e', '--email', type=EMAIL, default=None, help='send to')
def click_starter(env, action, ip, port, quiet, debug, email):
    global g_env
    g_env = env
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("ib_insync.wrapper").disabled = True
    logging.getLogger("ib_insync.client").disabled = True
    logging.getLogger("ib_insync.ib").disabled = True
    logging.getLogger("urllib3.connectionpool").disabled = True
    starter(env, action, ip, port, quiet, debug, email)


def upload_positions(env, ip, port, clientId, debug):
    config = dotenv_values(env)
    token = get_token(config['HOST'], config['EMAIL'], config['API_KEY'])
    folios = get_folios(config['HOST'], token)
    for folioname in list(folios):
        f = folios[folioname]
        if f['ib_sync']:
            print("Upload: ", folioname)
            account = f['ib_account']
            api_ip = ip or f['ib_ip']
            api_port = port or f['ib_port']

            ib = connected_ib(config, api_ip, api_port, clientId)
            accountlist = ib.managedAccounts()
            if account not in accountlist:
                ib.disconnect()
                print("-Abbruch- nicht gefunden")
                continue

            accountsummary = ib.accountSummary(account)

            ib.reqAllOpenOrders()
            openTrades = ib.openTrades()
            if debug:
                for data in openTrades:
                    if data.order.account == account:
                        quantity = data.order.totalQuantity
                        if data.order.action != 'BUY':
                            quantity = -quantity
                            print("ORD: {:5d} * {:4s}".format(
                                int(quantity),
                                data.contract.symbol))

            portfolio = ib.positions(account=account)
            if debug:
                for pos in portfolio:
                    print("POS: {:5d} * {:4s} @ {:.2f}".format(
                            int(pos.position),
                            pos.contract.symbol,
                            pos.avgCost))
                print("")

            dictPortfolio = {}
            dictPortfolio['account'] = account
            dictPortfolio['accountsummary'] = accountsummary
            dictPortfolio['order'] = []
            dictPortfolio['portfolio'] = []
            for o in openTrades:
                if o.order.account == account:
                    dictPortfolio['order'].append((
                        o.contract.conId,
                        o.contract.symbol,
                        o.contract.right,
                        o.contract.exchange,
                        o.contract.currency,
                        o.contract.localSymbol,
                        o.contract.tradingClass,

                        o.order.permId,
                        o.order.action,
                        o.order.totalQuantity,
                        o.order.orderType,
                        o.order.lmtPrice,
                        o.order.auxPrice,
                        o.order.tif,
                        o.order.ocaType,
                        o.order.displaySize,
                        o.order.rule80A,
                        o.order.openClose,
                        o.order.volatilityType,
                        o.order.deltaNeutralOrderType,
                        o.order.referencePriceType,
                        o.order.account,
                        o.order.clearingIntent,
                        o.order.adjustedOrderType,
                        o.order.cashQty,
                        o.order.dontUseAutoPriceForHedge,

                        o.orderStatus.orderId,
                        o.orderStatus.status,
                        o.orderStatus.filled,
                        o.orderStatus.remaining,
                        o.orderStatus.avgFillPrice,
                        o.orderStatus.permId,
                        o.orderStatus.parentId,
                        o.orderStatus.lastFillPrice,
                        o.orderStatus.clientId,
                        o.orderStatus.whyHeld,
                        o.orderStatus.mktCapPrice
                    ))

            for p in portfolio:
                dictPortfolio['portfolio'].append((
                    p.contract.symbol,
                    p.contract.conId,
                    p.contract.exchange,
                    p.contract.currency,
                    p.contract.localSymbol,
                    p.contract.tradingClass,
                    p.avgCost,
                    p.position))
            # print("°°")
            # print(dictPortfolio)
            # ib.disconnect()
            # continue
            # debug_meldungen_tws(openTrades, portfolio)
            resp = post_json(config['HOST']+"/api/v1/folio/",
                             dictPortfolio,
                             token)
            # print(resp)
            if resp[0].status_code != 200:
                print("Error code {}:{}".format(resp[0].status_code,
                      resp[0].text))
            ib.disconnect()


if __name__ == "__main__":
    global g_env
    g_env = env_location()
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("ib_insync.wrapper").disabled = True
    logging.getLogger("ib_insync.client").disabled = True
    logging.getLogger("ib_insync.ib").disabled = True
    logging.getLogger("urllib3.connectionpool").disabled = True
    # starter(g_env, "sync", None, 7497, True, True, "sven.otremba@hotmail.com")
    starter(g_env, "sync", None, 7497, True, True, "sven.otremba@hotmail.com")
    import sys
    sys.exit(0)

    # os.system('cls')
    # logging.basicConfig(filename='example.log', level=logging.INFO)
    # logging.getLogger().addHandler(logging.StreamHandler())
    print("JO")
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("ib_insync.wrapper").disabled = True
    logging.getLogger("ib_insync.client").disabled = True
    logging.getLogger("ib_insync.ib").disabled = True
    logging.getLogger("urllib3.connectionpool").disabled = True
    # starter(env_location(), 'sync', None, 7497)
    # exit()
    global env
    env = env_location()
    if not os.path.exists(os.path.dirname(env)):
        logging.error("Enviroment Path not exists: {}"
                      .format(os.path.dirname(env)))
        if click.confirm('Do you want to create the folder?', default=True):
            os.mkdir(os.path.dirname(env))
    if not os.path.exists(env):
        email = input("Enter your Foliobutler Email: ")
        api = input("Enter your Foliobutler Api-Key: ")
        f = open(env, "a")
        f.write("EMAIL={}\nAPI_KEY={}\n".format(email, api))
        f.close()
    ip = None
    port = 7497
    clientId = 1
    config = dotenv_values(env)

    host = config['HOST']
    print(host)
    print(config)
    # host = "https://fbm.svencloud.de"
    token = get_token(host, config['EMAIL'], config['API_KEY'])
    print(token)
    folios = get_folios(host, token)
    clientId = 1
    print(folios)
    exit()
    # for folioname in list(folios):
    f = folios["Ab_Juli2024"]
    for x in f['positions']:
        print(x)
    exit()

    # upload_positions(env)
    # exit()

    # read tws positions and orders:
    f = folios['Ab_Juli2024']
    account = f['ib_account']
    api_ip = ip or f['ib_ip']
    api_port = port or f['ib_port']
    fb_positions = f['positions']
    fb_orders = f['orders']
    debug_meldungen_fb(account, api_ip, api_port, fb_positions, fb_orders)
    ib = connected_ib(config, api_ip, api_port, clientId)
    accountlist = ib.managedAccounts()
    if account not in accountlist:
        ib.disconnect()
        exit(1)
    ib.reqAllOpenOrders()

    openTrades = ib.openTrades()
    # current_ib_orders = [x.contract.symbol + "_" + x.contract.secType + "_"
    # + x.contract.currency
    # for x in openTrades if x.order.account == account]
    print(openTrades)
    print(len(openTrades))
    for data in openTrades:
        quantity = data.order.totalQuantity
        if data.order.action != 'BUY':
            quantity = -quantity
            print("{} x {}".format(quantity,
                                   data.contract.symbol))


    # print(openTrades)
    portfolio = ib.positions(account=account)
    dictPortfolio = {}
    for p in portfolio:
        if p.account not in dictPortfolio:
            dictPortfolio[p.account] = []
        dictPortfolio[p.account].append((
            p.contract.symbol,
            p.contract.conId,
            p.contract.exchange,
            p.contract.currency,
            p.contract.localSymbol,
            p.contract.tradingClass,
            p.avgCost,
            p.position))

    debug_meldungen_tws(openTrades, portfolio)

    resp = post_json(config['HOST']+"/api/v1/folio/",
                     dictPortfolio,
                     token)
    print(resp)
    exit(0)
    for folioname in list(folios):
        f = folios[folioname]
        if f['ib_sync']:
            # print(folios[folioname]['orders'])
            sync(f['ib_account'],
                 config, ip or f['ib_ip'],
                 port or f['ib_port'],
                 f['positions'],
                 f['orders'],
                 clientId)
            time.sleep(1)
