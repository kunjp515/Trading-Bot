from datetime import datetime
import numpy as np
import talib
import alpaca_trade_api as tradeapi


endpointURL = "https://paper-api.alpaca.markets"

#tradeapi.REST(key_id,secret_key,endpoint,version)
api = tradeapi.REST("API_KEY","SECRET_KEY",endpointURL,api_version='v2')

#trading setup
barTimeframe = "15Min" # 1Min, 5Min, 15Min, 1D
assetsToTrade = ["MSFT","AGIO","NVDA","DASH","BA","TSLA","SPY","SDS"]
numOfPositions = 8
positionsHeld = {}

# iterates through list of assets
iteratorPos = 0
assetListLen = len(assetsToTrade)


while iteratorPos < assetListLen:
        symbol = assetsToTrade[iteratorPos]
        
        returned_data = api.get_barset(symbol,barTimeframe,limit=100)
        
        timeList = []
        openList = []
        highList = []
        lowList = []
        closeList = []
        volumeList = []

        #updates dictionary with assets held and quantity of shares
        for pos in api.list_positions():
                positionsHeld.update({pos.symbol:pos.qty})

        # Reads, formats and stores the new bars
        for bar in list(returned_data.values())[0]:
                timeList.append(datetime.strptime(str(bar.t),'%Y-%m-%d %H:%M:%S-04:00'))
                openList.append(bar.o)
                highList.append(bar.h)
                lowList.append(bar.l)
                closeList.append(bar.c)
                volumeList.append(bar.v)

        # Processes all data into numpy arrays for use by talib
        timeList = np.array(timeList)
        openList = np.array(openList,dtype=np.float64)
        highList = np.array(highList,dtype=np.float64)
        lowList = np.array(lowList,dtype=np.float64)
        closeList = np.array(closeList,dtype=np.float64)
        volumeList = np.array(volumeList,dtype=np.float64)


        # Calculated trading indicators
        SMA20 = talib.SMA(closeList,20)[-1]
        SMA50 = talib.SMA(closeList,50)[-1]


        # Calculates the trading signals
        if SMA20 > SMA50:
                # Opens new position if one does not exist
                if not symbol in positionsHeld:
                        cashBalance = api.get_account().cash
                        targetPositionSize = ((float(cashBalance) / numOfPositions) / openList[-1]) - 1 # Calculates required position size
                        returned = api.submit_order(symbol,int(targetPositionSize),"buy","market","gtc") # Market order to open position
                        print(returned)
                
        else:
                # Closes position if SMA20 is below SMA50 and position is held
                if symbol in positionsHeld:
                        openPosition = api.get_position(symbol)
                        returned = api.submit_order(symbol,openPosition.qty,"sell","market","gtc") # Market order to fully close position
                        print(returned)
        
        iteratorPos += 1

print("--TRADING COMPLETE--")
