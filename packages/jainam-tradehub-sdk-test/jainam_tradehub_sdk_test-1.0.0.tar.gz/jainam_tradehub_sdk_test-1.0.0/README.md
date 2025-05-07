## Jainam API - The Official Python SDK for Smart Trading  

The jainam Python SDK provides a streamlined interface for secure and efficient communication with the jainam API. It offers extensive features to manage trading operations, monitor market data, and handle account management seamlessly.  

* __Author: [CodiFi](https://github.com/Periyasamy-Dev/TRADEHUB_PySDK.git)__
* **Current Version: 1.0.0**


### Installation

To install the jainam SDK using pip, run the following command: 

```
pip install jainam-tradehub-sdk-test
```

Ensure that Python 3.8 or higher is installed on your system

```
python --version
```

#### Update pip 
To force update pip to the latest version, you can run the following command:
```
pip uninstall jainam-tradehub-sdk-test -y
pip install --no-cache-dir jainam-tradehub-sdk-test
```

---

### REST Documentation

For detailed information on the underlying REST API, refer to the official jainam API documentation:  
[jainam API Documentation](https://protrade.jainam.in/apidocs/)

---

### Getting Started with API

The jainam SDK has primary classes: `TradeHub`.  
- **TradeHub Class**: This class handles direct interactions with the jainam API, including managing sessions, placing orders, and retrieving market data.

#### Session Management
The `get_session_id` method is used to retrieve a session ID from the Jainam server. The session ID remains valid until you log out of your trading account. It is recommended to generate the session ID once during login and store it securely for subsequent use. 

#### 1. Import the Library
Import the required class from the SDK:
```python
from TradeMaster.TradeSync import *
```

#### 2. Create a Trading Object
Initialize a Trading object using your user_id, auth_code, and secret_key
```python
trade = TradeHub(user_id="YOUR_USER_ID", auth_code="YOUR_AUTH_CODE", secret_key="YOUR_SECRET_KEY")
```

#### 3. Get Session
To get the session ID, use the get_session_id() method.

You can call it directly, or optionally provide a check_sum or an existing session_id if you already have them.
```python
# Get session ID (default way)
print(trade.get_session_id())

# Optionally, pass a checksum if you have one
print(trade.get_session_id(check_sum="your_checksum_here"))

# Optionally, pass an existing session ID
print(trade.get_session_id(session_id="your_existing_session_id"))
```

#### 4. Download the contract master
Master contracts simplify the process of locating instruments by their symbol names and placing orders. These contracts are stored locally as CSV files, organized by token number and symbol name.
By default, master contracts for all enabled exchanges in your profile are downloaded.
To download contracts for specific enabled exchanges (e.g., ['NSE', 'BSE', 'NFO', 'BFO', 'CDS', 'BCD', 'NCO', 'BCO', 'MCX', 'INDICES', 'NCDEX']), replace "EXCHANGE" with the desired exchange names in the command below:
```python
trade.get_contract_master(exchange="EXCHANGE")
```

#### 5. Retrieve Available Instruments for Trading
Instruments can be fetched based on their symbol, token, or Futures & Options (FNO) from the downloaded contract master as shown below:
```python
# Fetching instrument by symbol (TCS) or trading symbol (TCS-EQ) for all exchange
print(trade.get_instrument(exchange=Exchange.NSE, symbol='TCS'))

# Fetching instrument by token for all exchange
print(trade.get_instrument(exchange=Exchange.NSE, token='11915'))

# Fetching Futures & Options instrument
print(trade.get_instrument_for_fno(exchange=Exchange.NFO, symbol='HAL', expiry_date='2025-04-24', strike='5000',
                                               is_fut=False, is_CE=True))
```

---

### Predefined Categories

The following predefined categories are used for placing or modifying orders and retrieving data. You can use these categories or, if you already know their corresponding values, you can pass them directly.

1. **TransactionType**: Specifies the type of transaction.

   * `TransactionType.Buy`: **BUY**
   * `TransactionType.Sell`: **SELL**


2. **OrderComplexity**: Specifies the type of order.

   * `OrderComplexity.Regular`: **Regular**
   * `OrderComplexity.AMO`: **AMO** (After Market Order)
   * `OrderComplexity.Cover`: **CO** (Cover Order)
   * `OrderComplexity.Bracket`: **BO** (Bracket Order)


3. **ProductType**: Defines the product category.
   
   * `ProductType.Normal`: **NORMAL** (Normal order)
   * `ProductType.Intraday`: **INTRADAY** (Margin Intraday Square-off)
   * `ProductType.Delivery`: **DELIVERY** (Cash and Carry)
   * `ProductType.BNPL`: **BNPL** (Buy Now Pay Later)
   * `ProductType.MTF`: **MTF** (Margin Trading Facility)
   * `ProductType.GTT`: **GTT** (Good Till Triggered)


4. **OrderType**: Specifies the pricing mechanism.
    
    * `OrderType.Limit`: **LIMIT** (Limit Order)
    * `OrderType.Market`: **MARKET** (Market Order)
    * `OrderType.StopLose`: **SL** (Stop Loss Limit Order)
    * `OrderType.StopLossMarket`: **SLM** (Stop Loss Market Order)


5. **PositionType**: Defines how the position is managed.

    * `PositionType.posDAY`: **DAY** (Intraday position)
    * `PositionType.posNET`: **NET** (Carry forward position)
    * `PositionType.posIOC`: **IOC** (Immediate or Cancel)


6. **Exchange**: Defines the Exchange category.

   * `Exchange.NSE`: **NSE** National Stock Exchange
   * `Exchange.BSE`: **BSE** Bombay Stock Exchange
   * `Exchange.NFO`: **NFO** NSE Futures & Options
   * `Exchange.BFO`: **BFO** BSE Futures & Options
   * `Exchange.CDS`: **CDS** Currency Derivatives Segment (NSE)
   * `Exchange.BCD`: **BCD** BSE Currency Derivatives
   * `Exchange.NCO`: **NCO** NSE Commodities
   * `Exchange.BCO`: **BCO** BSE Commodities
   * `Exchange.MCX`: **MCX** Multi Commodity Exchange
   * `Exchange.INDICES`: **INDICES** Index data (NSE/BSE indices)
   * `Exchange.NCDEX`: **NCDEX** National Commodity & Derivatives Exchange
---

### Order & Trade Management

#### Place Order
To place an order, use the trade.placeOrder() method. You can provide the instrument details in one of three optional ways:
   - Option 1: Using instrumentId, exchange (When you already know the token (instrumentId) and exchange, pass both directly.)
   - Option 2: Using get_instrument (When you only know the symbol, this function will fetch the instrument; no need to pass the exchange separately.)
   - Option 3: Using get_instrument_for_fno (for Futures & Options, when you know the symbol details; no need to pass the exchange separately.)

Option 1:
```python
placeOrder = trade.placeOrder(instrumentId='532822', 
                              exchange=Exchange.BSE,
                              transactionType=TransactionType.Buy,
                              quantity='2',
                              orderComplexity=OrderComplexity.Regular,
                              product=ProductType.BNPL,
                              orderType=OrderType.Market,
                              price='',
                              slTriggerPrice="",
                              slLegPrice="",
                              targetLegPrice="",
                              validity=PositionType.posDAY,
                              trailingSlAmount="",
                              disclosedQuantity="",
                              marketProtectionPercent="",
                              apiOrderSource="",
                              algoId="",
                              orderTag="")

print("User placeOrder :", placeOrder)
```

Option 2:
```python
placeOrder = trade.placeOrder(instrument=trade.get_instrument(exchange=Exchange.BSE, symbol='IDEA'), 
                              transactionType=TransactionType.Buy,
                              quantity='2',
                              orderComplexity=OrderComplexity.Regular,
                              product=ProductType.BNPL,
                              orderType=OrderType.Limit,
                              price='10',
                              slTriggerPrice="",
                              slLegPrice="",
                              targetLegPrice="",
                              validity=PositionType.posDAY,
                              trailingSlAmount="",
                              disclosedQuantity="",
                              marketProtectionPercent="",
                              apiOrderSource="",
                              algoId="",
                              orderTag="")

print("User placeOrder :", placeOrder)
```

Option 3:
```python
placeOrder = trade.placeOrder(instrument=trade.get_instrument_for_fno(exchange=Exchange.BSE, symbol='IDEA', expiry_date="2025-04-29", strike="82500", is_fut=False, is_CE=True), 
                              transactionType=TransactionType.Buy,
                              quantity='2',
                              orderComplexity=OrderComplexity.Regular,
                              product=ProductType.BNPL,
                              orderType=OrderType.StopLoss,
                              price='10',
                              slTriggerPrice="8.5",
                              slLegPrice="0",
                              targetLegPrice="0",
                              validity=PositionType.posDAY,
                              trailingSlAmount="",
                              disclosedQuantity="",
                              marketProtectionPercent="",
                              apiOrderSource="",
                              algoId="",
                              orderTag="")

print("User placeOrder :", placeOrder)
```

#### Modify Order

```python
modifyOrder = trade.modifyOrder(orderNo="250424000007880",
                                price="20",
                                slTriggerPrice="19",
                                slLegPrice="",
                                targetLegPrice="",
                                quantity="20",
                                orderType=OrderType.Limit,
                                trailingSLAmount="",
                                validity=PositionType.posDAY,
                                disclosedQuantity="",
                                marketProtectionPrecent="",
                                deviceId="grhskjdvbDVHBVH" # Optional
                                )

print("User Modify_Order :", modifyOrder)
```

#### Cancel Order
To cancel a previously placed order, use the cancelOrder() method by providing the orderNo (Order Number).
```python
# Example: Cancel an order by Order Number
print(trade.cancelOrder(orderNo='25033100000020'))
```

#### Single Order Margin
   - Option 1: Using instrumentId, exchange (When you already know the token (instrumentId) and exchange, pass both directly.)
   - Option 2: Using get_instrument (When you only know the symbol, this function will fetch the instrument; no need to pass the exchange separately.)
   - Option 3: Using get_instrument_for_fno (for Futures & Options, when you know the symbol details; no need to pass the exchange separately.)

Option 1:
```python
singleOrderMargin = trade.singleOrderMargin(instrumentId="21951",
                                      exchange=Exchange.NSE,
                                      transactionType=TransactionType.Buy, 
                                      quantity='1', 
                                      orderComplexity=OrderComplexity.Regular,
                                      product=ProductType.Intraday, 
                                      orderType=OrderType.Market,
                                      price="",
                                      slTriggerPrice="",
                                      slLegPrice="")

print("User Single Order Margin :", singleOrderMargin)
```

Option 2:
```python
singleOrderMargin = trade.singleOrderMargin(instrument=trade.get_instrument(exchange=Exchange.NSE, symbol="HFCL"), 
                                      transactionType=TransactionType.Buy, 
                                      quantity='1', 
                                      orderComplexity=OrderComplexity.Regular,
                                      product=ProductType.Intraday, 
                                      orderType=OrderType.Limit,
                                      price="82.99",
                                      slTriggerPrice="",
                                      slLegPrice="")

print("User Single Order Margin :", singleOrderMargin)
```

Option 3:
```python
singleOrderMargin = trade.singleOrderMargin(instrument=trade.get_instrument_for_fno(exchange=Exchange.BSE, symbol='IDEA', expiry_date="2025-04-29", strike="82500", is_fut=False, is_CE=True), 
                                      transactionType=TransactionType.Buy, 
                                      quantity='1', 
                                      orderComplexity=OrderComplexity.Regular,
                                      product=ProductType.Intraday, 
                                      orderType=OrderType.StopLoss,
                                      price="10",
                                      slTriggerPrice="8.7",
                                      slLegPrice="0")

print("User Single Order Margin :", singleOrderMargin)
```

#### Order & Trade History Retrieval

#### Retrieve order book

```python
print(trade.get_orderbook())
```

#### Retrieve trade book

```python
print(trade.get_Tradebook())
```

#### Retrieve order history
To get the full history of a particular order (e.g., status changes, partial fills), use the get_orderHistory() method by passing the specific order number.
```python
print(trade.get_orderHistory(orderNo="25033100000020"))
```

### User & Portfolio Management

#### Retrieve profile
```python
print(trade.get_profile())
```

#### Retrieve funds
```python
print(trade.get_funds())
```
#### Retrieve positions
```python
print(trade.get_positions())
```

#### Retrieve holdings
```python
print(trade.get_holdings())
```

---

### General instruction

### Order Validation Logic

#### Order Type As (Limit or SL)
- `price` must be greater than zero.

#### Order Type As (SL or SLM)
- `slTriggerPrice` must be greater than zero.

#### Order Type As (SL) and Order Complexity As (BO, CO)
- `slLegPrice` must be greater than zero.

#### Order Complexity As (BO)
- `targetLegPrice` must be greater than zero.

---

### Read this before creating an issue
Before creating an issue in this library, please follow the following steps.

1. Search the problem you are facing is already asked by someone else. There might be some issues already there, either solved/unsolved related to your problem. Go to [issues](https://github.com/jerokpradeep/pya3/issues)
2. If you feel your problem is not asked by anyone or no issues are related to your problem, then create a new issue.
3. Describe your problem in detail while creating the issue. If you don't have time to detail/describe the problem you are facing, assume that I also won't be having time to respond to your problem.
4. Post a sample code of the problem you are facing. If I copy paste the code directly from issue, I should be able to reproduce the problem you are facing.
5. Before posting the sample code, test your sample code yourself once. Only sample code should be tested, no other addition should be there while you are testing.
6. Have some print() function calls to display the values of some variables related to your problem.
7. Post the results of print() functions also in the issue.
8. Use the insert code feature of github to inset code and print outputs, so that the code is displayed neat. ![image](https://user-images.githubusercontent.com/38440742/85207234-4dc96f80-b2f5-11ea-990c-df013dd69cf2.png)
9. If you have multiple lines of code, use triple grave accent ( ``` ) to insert multiple lines of code. [Example:](https://docs.github.com/en/github/writing-on-github/creating-and-highlighting-code-blocks) ![image](https://user-images.githubusercontent.com/38440742/89105781-343a3e00-d3f2-11ea-9f86-92dda88aa5bf.png)

---