import json
import threading
import time
import random
import datetime

def backgroundthreading():
    while True:
        backgroundmarket()
        autotrade()
        time.sleep(10)
    
def backgroundmarket():
    market = marketread()
    if not market:
        currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        market = {
            "AAPL": {"prices": [100.00], "volumes": [10000], "history": [{"time":currenttime, "price":100.00, "volume":10000}]},
            "TSLA": {"prices": [200.00], "volumes": [20000], "history": [{"time":currenttime, "price":200.00, "volume":20000}]},
            "GOOG": {"prices": [500.00], "volumes": [50000], "history": [{"time":currenttime, "price":500.00, "volume":50000}]}
        }
        marketwrite(market)
        time.sleep(10)
    for ticker in market:
        price = market[ticker]["prices"][-1]
        fluctuation = random.uniform(-0.05, 0.05)
        tempprice = price * (1 + fluctuation)
        while tempprice < 0:
            fluctuation = random.uniform(-0.05, 0.05)
            tempprice = price * (1 + fluctuation)
        currentprice = round(tempprice, 2)
        currentvolume = random.randint(10000, 500000)
        
        currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        market[ticker]["prices"].append(currentprice)
        market[ticker]["volumes"].append(currentvolume)
        market[ticker]["history"].append({
            "time": currenttime,
            "price": currentprice,
            "volume": currentvolume
        })
        
        if len(market[ticker]["prices"]) > 30:
            market[ticker]["prices"].pop(0)
            market[ticker]["volumes"].pop(0)
            market[ticker]["history"].pop(0)
    marketwrite(market)
        
def autotrade():
    userinfo = userread()
    market = marketread()
    transactioninfo = transactionread()
    currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for user in userinfo:
        if userinfo[user]["auto"]:
            if userinfo[user]["strategy"] == 'RandomStrategy':
                for ticker in ["AAPL", "TSLA", "GOOG"]:
                    purchaseflag = random.randint(1, 2)
                    if purchaseflag == 1:
                        continue
                    else:
                        purchasequantity = random.randint(1, 5)
                        currentprice = market[ticker]["prices"][-1]
                        cost = currentprice * purchasequantity
                        if userinfo[user]["balance"] < cost:
                            continue
                        userinfo[user]["balance"] -= cost
                        if not userinfo[user]["portfolio"]:
                            userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
                        userinfo[user]["portfolio"][ticker].append({
                            "price": currentprice,
                            "volume": purchasequantity
                        })
                        userwrite(userinfo)
                        if not transactioninfo:
                            transactioninfo[user] = []
                        else:
                            if user not in transactioninfo:
                                transactioninfo[user] = []
                        transaction = f"{currenttime} - BUY {purchasequantity} {ticker} @${currentprice}"
                        transactioninfo[user].append(transaction)
                        transactionwrite(transactioninfo)
            elif userinfo[user]["strategy"] == 'MovingAverageStrategy':
                for ticker in ["AAPL", "TSLA", "GOOG"]:
                    shortterm = []
                    longterm = []
                    if len(market[ticker]["prices"]) < 7:
                        continue
                    for i in range(6, -1, -1):
                        price = market[ticker]["prices"][-i-1]
                        if i < 3:
                            shortterm.append(price)
                        longterm.append(price)
                    shortavg = round(sum(shortterm)/len(shortterm),2)
                    longavg = round(sum(longterm)/len(longterm),2)
                    currentprice = market[ticker]["prices"][-1]
                    if not userinfo[user]["portfolio"]:
                        userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
                    # print(f"ticker: {ticker} shortavg :{shortavg} longavg :{longavg}")
                    if shortavg > longavg:
                        cost = currentprice
                        if userinfo[user]["balance"] < cost:
                            continue
                        userinfo[user]["balance"] -= cost
                        userinfo[user]["portfolio"][ticker].append({
                            "price": currentprice,
                            "volume": 1
                        })
                        userwrite(userinfo)
                        if not transactioninfo:
                            transactioninfo[user] = []
                        else:
                            if user not in transactioninfo:
                                transactioninfo[user] = []
                        transaction = f"{currenttime} - BUY {1} {ticker} @${currentprice}"
                        transactioninfo[user].append(transaction)
                        transactionwrite(transactioninfo)
                    elif shortavg < longavg:
                        proceeds = currentprice
                        availabletotalquantity = 0
                        for item in userinfo[user]["portfolio"][ticker]:
                            availabletotalquantity += item["volume"]
                        if availabletotalquantity < 1:
                            continue
                        userinfo[user]["balance"] += proceeds    
                        userinfo[user]["portfolio"][ticker].append({
                            "price": currentprice,
                            "volume": -1
                        })
                        userwrite(userinfo)                        
                        if not transactioninfo:
                            transactioninfo[user] = []
                        else:
                            if user not in transactioninfo:
                                transactioninfo[user] = []
                        transaction = f"{currenttime} - SELL {1} {ticker} @${currentprice}"
                        transactioninfo[user].append(transaction)
                        transactionwrite(transactioninfo)
            elif userinfo[user]["strategy"] == 'MomentumStrategy':
                for ticker in ["AAPL", "TSLA", "GOOG"]:
                    if len(market[ticker]["prices"]) < 7:
                        continue
                    currentprice = market[ticker]["prices"][-1]
                    minuteagoprice = market[ticker]["prices"][-7]
                    if not userinfo[user]["portfolio"]:
                        userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
                    # print(f"ticker: {ticker} currentprice :{currentprice} minuteagoprice :{minuteagoprice}")
                    if currentprice > minuteagoprice:
                        cost = currentprice
                        if userinfo[user]["balance"] < cost:
                            continue
                        userinfo[user]["balance"] -= cost
                        userinfo[user]["portfolio"][ticker].append({
                            "price": currentprice,
                            "volume": 1
                        })
                        userwrite(userinfo)
                        if not transactioninfo:
                            transactioninfo[user] = []
                        else:
                            if user not in transactioninfo:
                                transactioninfo[user] = []
                        transaction = f"{currenttime} - BUY {1} {ticker} @${currentprice}"
                        transactioninfo[user].append(transaction)
                        transactionwrite(transactioninfo)
                    elif currentprice < minuteagoprice:
                        proceeds = currentprice
                        availabletotalquantity = 0
                        for item in userinfo[user]["portfolio"][ticker]:
                            availabletotalquantity += item["volume"]
                        if availabletotalquantity < 1:
                            continue
                        userinfo[user]["balance"] += proceeds     
                        userinfo[user]["portfolio"][ticker].append({
                            "price": currentprice,
                            "volume": -1
                        })
                        userwrite(userinfo)                        
                        if not transactioninfo:
                            transactioninfo[user] = []
                        else:
                            if user not in transactioninfo:
                                transactioninfo[user] = []                                
                        transaction = f"{currenttime} - SELL {1} {ticker} @${currentprice}"
                        transactioninfo[user].append(transaction)
                        transactionwrite(transactioninfo)
        else:
            continue
        
def marketread():
    try:
        with open("market.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def marketwrite(market):
    with open("market.json", 'w') as file:
        json.dump(market, file, indent = 4)

def userread():
    try:
        with open("users.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def userwrite(user):
    with open("users.json", 'w') as file:
        json.dump(user, file, indent = 4)

def transactionread():
    try:
        with open("transactions.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def transactionwrite(transaction):
    with open("transactions.json", 'w') as file:
        json.dump(transaction, file, indent = 4)

def register():
    userinfo = userread()

    while True:
        username = input("Username: ")
        if username in userinfo:
            print("Username already exists. Please choose another.")
        else:
            break
    
    while True:
        password = input("Password: ")
        error = []
        if len(password) < 8:
            error.append("- Password must be at least 8 characters.")
            
        uppercaseexist = False
        for c in password:
            if c.isupper():
                uppercaseexist = True
                break
        if not uppercaseexist:
            error.append("- Password must include at least one uppercase letter.")
            
        specialstring = "!@#$%^&*()"
        specialcharexist = False
        for c in password:
            if c in specialstring: 
                specialcharexist = True
                break
        if not specialcharexist:
            error.append("- Password must include at least one special character (!@#$%^&*()).")
            
        if error:
            for e in error:
                print(e)
        else:
            break

    while True:
        print("Select strategy:")
        print(" 1) RandomStrategy")
        print(" 2) MovingAverageStrategy")
        print(" 3) MomentumStrategy")
        choice = input("Choose (1/2/3): ")

        if choice == '1':
            strategy = 'RandomStrategy'
            break
        elif choice == '2':
            strategy = 'MovingAverageStrategy'
            break
        elif choice == '3':
            strategy = 'MomentumStrategy'
            break
        else:
            print("Invalid selection. Try again.")

    userinfo[username] = {
        "password": password,
        "strategy": strategy,
        "balance": 10000.0,
        "auto": False,
        "portfolio": {}
    }

    userwrite(userinfo)
    print(f"User '{username}' registered successfully.\n")

def login():
    userinfo = userread()
    username = input("Username: ")
    password = input("Password: ")
    if (username not in userinfo) or (password != userinfo[username]["password"]):
        print("Invalid username or password.\n")
        return ""
    else:
        print(f"Welcom, {username}!\n")
        return username

def stock(user):
    while True:
        print("===== Select Option =====")
        print("1. view\n2. buy TICKER QTY\n3. sell TICKER QTY\n4. portfolio\n5. history\n6. auto on/off\n7. logout")
        choice = input(f"{user}> ")

        if choice == '1':
            view()
        elif choice == '2':
            buyticker(user)
        elif choice == '3':
            sellticker(user)
        elif choice == '4':
            portfolio(user)
        elif choice == '5':
            history(user)
        elif choice == '6':
            autoonoff(user)
        elif choice == '7':
            return
        else:
            print("Invalid Option. Try again.")

def view():
    market = marketread()
    last5price = {}
    last5volume = {}
    for ticker in market:
        last5price[ticker] = []
        last5volume[ticker] = []
        for i in range(min(4, len(market[ticker]["prices"])-1), -1, -1):
            price = market[ticker]["prices"][-i-1]
            volume = market[ticker]["volumes"][-i-1]
            last5price[ticker].append(price)
            last5volume[ticker].append(volume)
    for ticker in market:
        currentprice = market[ticker]["prices"][-1]
        currentvolume = market[ticker]["volumes"][-1]
        print(f"\n[{ticker}] ${currentprice} Vol:{currentvolume}")
        print(f"Last {len(last5price[ticker])} prices: {last5price[ticker]}")
        print(f"Last {len(last5volume[ticker])} volumes: {last5volume[ticker]}")
    print("\n")
    
def buyticker(user):
    userinfo = userread()
    market = marketread()
    transactioninfo = transactionread()
    count = 0
    print("\n===== Buy Menu =====\n")
    print(f"Available Cash: ${round(userinfo[user]["balance"],2)}")
    print(f"Your Holdings: ")
    
    if not userinfo[user]["portfolio"]:
        userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
    for ticker in ["AAPL", "TSLA", "GOOG"]:
        if userinfo[user]["portfolio"][ticker]:
            portfolio = userinfo[user]["portfolio"][ticker]
            stocklist = []
            totalquantity = 0
            totalprice = 0
            for item in portfolio:
                if item["volume"] > 0:
                    stocklist.append({"price": item["price"], "volume":item["volume"]})
                else:
                    soldquantity = item["volume"]*(-1)
                    while soldquantity > 0 and stocklist:
                        if stocklist[0]["volume"] > soldquantity:
                            stocklist[0]["volume"] -= soldquantity
                            soldquantity = 0
                        else:
                            soldquantity -= stocklist[0]["volume"]
                            stocklist.pop(0)
            for item in stocklist:
                totalquantity += item["volume"]
                totalprice += (item["volume"] * item["price"])
            if totalquantity == 0:
                count += 1
                continue
            avgprice = round(totalprice/totalquantity,2)
            print(f" {ticker}: {totalquantity} shares @ avg ${avgprice}")
        else:
            count += 1
            continue
        
    if count == 3:
        print("  (No stocks owned)")

    buywantticker = input("Enter ticker (AAPL, TSLA, GOOG) or 'back' to return: ")
    while buywantticker not in ["AAPL", "TSLA", "GOOG"]:
        if buywantticker == 'back':
            return
        print("Invalid Ticker")
        buywantticker = input("Enter ticker (AAPL, TSLA, GOOG) or 'back' to return: ")
        
        
    buywantquantity = int(input("Enter quantity to buy: "))
    while buywantquantity <= 0:
        print("Invalid Quantity")
        buywantquantity = int(input("Enter quantity to buy: "))
        
    currentprice = market[buywantticker]["prices"][-1]
    cost = currentprice * buywantquantity
    
    if userinfo[user]["balance"] < cost:
        print("Insufficient balance.")
        return
    
    userinfo[user]["balance"] -= cost
        
    userinfo[user]["portfolio"][buywantticker].append({
        "price": currentprice,
        "volume": buywantquantity
    })
    
    print(f"Bought {buywantquantity} {buywantticker} @ ${currentprice}\n")
    
    userwrite(userinfo)
    
    currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not transactioninfo:
        transactioninfo[user] = []
    else:
        if user not in transactioninfo:
            transactioninfo[user] = []
    transaction = f"{currenttime} - BUY {buywantquantity} {buywantticker} @${currentprice}"
    transactioninfo[user].append(transaction)
    
    transactionwrite(transactioninfo)

def sellticker(user):
    userinfo = userread()
    market = marketread()
    transactioninfo = transactionread()
    count = 0
    availabletotalquantity = 0
    print("\n===== Sell Menu =====\n")
    print(f"\nAvailable Cash: ${round(userinfo[user]["balance"],2)}")
    print(f"Your Holdings: ")
    
    if not userinfo[user]["portfolio"]:
        userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
        
    for ticker in ["AAPL", "TSLA", "GOOG"]:
        if userinfo[user]["portfolio"][ticker]:
            portfolio = userinfo[user]["portfolio"][ticker]
            stocklist = []
            totalquantity = 0
            totalprice = 0
            for item in portfolio:
                if item["volume"] > 0:
                    stocklist.append({"price": item["price"], "volume":item["volume"]})
                else:
                    soldquantity = item["volume"]*(-1)
                    while soldquantity > 0 and stocklist:
                        if stocklist[0]["volume"] > soldquantity:
                            stocklist[0]["volume"] -= soldquantity
                            soldquantity = 0
                        else:
                            soldquantity -= stocklist[0]["volume"]
                            stocklist.pop(0)
            for item in stocklist:
                totalquantity += item["volume"]
                totalprice += (item["volume"] * item["price"])
            if totalquantity == 0:
                count += 1
                continue
            avgprice = round(totalprice/totalquantity,2)
            print(f" {ticker}: {totalquantity} shares @ avg ${avgprice}")
        else:
            count += 1
            continue
        
    if count == 3:
        print("  (No stocks owned)")
        
    sellwantticker = input("Enter ticker (AAPL, TSLA, GOOG) or 'back' to return: ")
    if sellwantticker == 'back':
        return
    totalquantityflag = 0
    for item in userinfo[user]["portfolio"][sellwantticker]:
       availabletotalquantity += item["volume"]
    if availabletotalquantity == 0:
        totalquantityflag = 1
    else:
        totalquantityflag = 0
    
    while sellwantticker not in ["AAPL", "TSLA", "GOOG"] or (sellwantticker in ["AAPL", "TSLA", "GOOG"] and totalquantityflag == 1):
        availabletotalquantity = 0
        if sellwantticker == 'back':
            return
        elif sellwantticker not in ["AAPL", "TSLA", "GOOG"]:
            print("Invalid Ticker")
            sellwantticker = input("Enter ticker (AAPL, TSLA, GOOG) or 'back' to return: ")
            continue
        else:
            for item in userinfo[user]["portfolio"][sellwantticker]:
                availabletotalquantity += item["volume"]
            if availabletotalquantity == 0:
                totalquantityflag = 1
                print("The holdings of this ticker are 0")
                sellwantticker = input("Enter ticker (AAPL, TSLA, GOOG) or 'back' to return: ")
            else:
                totalquantityflag = 0
    
    sellwantquantity = int(input("Enter quantity to sell: "))
    availabletotalquantity = 0
    for item in userinfo[user]["portfolio"][sellwantticker]:
        availabletotalquantity += item["volume"]

    while sellwantquantity <= 0 or availabletotalquantity < sellwantquantity:
        print("Invalid Quantity")
        sellwantquantity = int(input("Enter quantity to sell: "))
        
    currentprice = market[sellwantticker]["prices"][-1]
    proceeds = currentprice * sellwantquantity
        
    userinfo[user]["balance"] += proceeds
    
    userinfo[user]["portfolio"][sellwantticker].append({
        "price": currentprice,
        "volume": (-1)*sellwantquantity
    })
    
    print(f"Sold {sellwantquantity} {sellwantticker} @ ${currentprice}\n")
    
    userwrite(userinfo)
    
    currenttime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not transactioninfo:
        transactioninfo[user] = []
    else:
        if user not in transactioninfo:
            transactioninfo[user] = []
    transaction = f"{currenttime} - SELL {sellwantquantity} {sellwantticker} @${currentprice}"
    transactioninfo[user].append(transaction)
    
    transactionwrite(transactioninfo)

def portfolio(user):
    userinfo = userread()
    market = marketread()
    totalaccountvalue = 0
    if not userinfo[user]["portfolio"]:
        userinfo[user]["portfolio"] = {"AAPL":[], "TSLA": [] , "GOOG":[]}
        
    print(f"\nCash: ${round(userinfo[user]["balance"],2)}")
    totalaccountvalue += userinfo[user]['balance']
    
    for ticker in ["AAPL", "TSLA", "GOOG"]:
        if userinfo[user]["portfolio"][ticker]:
            portfolio = userinfo[user]["portfolio"][ticker]
            stocklist = []
            totalquantity = 0
            totalprice = 0
            for item in portfolio:
                if item["volume"] > 0:
                    stocklist.append({"price": item["price"], "volume":item["volume"]})
                else:
                    soldquantity = item["volume"]*(-1)
                    while soldquantity > 0 and stocklist:
                        if stocklist[0]["volume"] > soldquantity:
                            stocklist[0]["volume"] -= soldquantity
                            soldquantity = 0
                        else:
                            soldquantity -= stocklist[0]["volume"]
                            stocklist.pop(0)
            for item in stocklist:
                totalquantity += item["volume"]
                totalprice += (item["volume"] * item["price"])
            if totalquantity == 0:
                continue
            avgprice = round(totalprice/totalquantity,2)
            currenttotalprice = round(totalquantity * market[ticker]["prices"][-1],2)
            totalaccountvalue += currenttotalprice
            percentage = round((100 * (market[ticker]["prices"][-1] - avgprice))/avgprice, 2)
            if (market[ticker]["prices"][-1] - avgprice) >= 0:
                print(f"{ticker}: {totalquantity} @avg${avgprice} -> ${currenttotalprice} (+{percentage}%)")
            else:
                print(f"{ticker}: {totalquantity} @avg${avgprice} -> ${currenttotalprice} ({percentage}%)")
        else:
            continue
        
    print(f"Total: ${round(totalaccountvalue, 2)}\n")

def autoonoff(user):
    userinfo = userread()
    if userinfo[user]["auto"]:
        print("Auto-trade unenabled.")
        userinfo[user]["auto"] = False
    else:
        print("Auto-trade enabled.")
        userinfo[user]["auto"] = True
    userwrite(userinfo)
    
def history(user):
    transactioninfo = transactionread()
    userinfo = userread()
    print("\n--- Transactions ---")
    if len(userinfo[user]["portfolio"]) == 0:
        print()
        return
    for i in range(len(transactioninfo[user])-1, -1, -1):
        if i == 0:
           print(f"{transactioninfo[user][i]}\n")
           continue
        print(transactioninfo[user][i])


def main():
    threading.Thread(target=backgroundthreading, daemon=True).start()
    
    while True:
        print("=== Stock Trading Simulation ===")
        print("1) Register  2) Login  3) Exit")
        choice = input("Select: ")

        if choice == '1':
            register()
        elif choice == '2':
            user = login()
            if user:
                stock(user)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Try again.")

if __name__ == "__main__":
    main()