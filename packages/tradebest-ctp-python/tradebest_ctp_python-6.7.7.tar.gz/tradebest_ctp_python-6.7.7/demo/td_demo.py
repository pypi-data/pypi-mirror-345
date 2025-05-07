
"""
Trading API Demo
"""

import sys
import time
import os
import threading
from tradebest_ctp import tdapi


class TdImpl(tdapi.CThostFtdcTraderSpi):
    def __init__(self, host, broker, user, password, appid, authcode):
        super().__init__()

        self.broker = broker
        self.user = user
        self.password = password
        self.appid = appid
        self.authcode = authcode

        self.TradingDay = ""
        self.FrontID = 0
        self.SessionID = 0
        self.OrderRef = 0

        self.api = tdapi.CThostFtdcTraderApi.CreateFtdcTraderApi()
        self.api.RegisterSpi(self)
        self.api.RegisterFront(host)
        self.api.SubscribePrivateTopic(tdapi.THOST_TERT_QUICK)
        self.api.SubscribePublicTopic(tdapi.THOST_TERT_QUICK)

    def Run(self):
        self.api.Init()

    def OnFrontConnected(self):
        print("OnFrontConnected")

        req = tdapi.CThostFtdcReqAuthenticateField()
        req.BrokerID = self.broker
        req.UserID = self.user
        req.AppID = self.appid
        req.AuthCode = self.authcode
        self.api.ReqAuthenticate(req, 0)

    def OnFrontDisconnected(self, nReason: int):
        print(f"OnFrontDisconnected.[nReason={nReason}]")

    def OnRspAuthenticate(
            self,
            pRspAuthenticateField: tdapi.CThostFtdcRspAuthenticateField,
            pRspInfo: tdapi.CThostFtdcRspInfoField,
            nRequestID: int,
            bIsLast: bool,
    ):
        """客户端认证响应"""
        if pRspInfo and pRspInfo.ErrorID != 0:
            print("认证失败：{}".format(pRspInfo.ErrorMsg))
            exit(-1)
        print("Authenticate succeed.")

        req = tdapi.CThostFtdcReqUserLoginField()
        req.BrokerID = self.broker
        req.UserID = self.user
        req.Password = self.password
        req.UserProductInfo = "demo"
        self.api.ReqUserLogin(req, 0)

    def OnRspUserLogin(
            self,
            pRspUserLogin: tdapi.CThostFtdcRspUserLoginField,
            pRspInfo: tdapi.CThostFtdcRspInfoField,
            nRequestID: int,
            bIsLast: bool,
    ):
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print(f"Login failed. {pRspInfo.ErrorMsg}")
            exit(-1)
        print(f"Login succeed. TradingDay: {pRspUserLogin.TradingDay}, MaxOrderRef: {pRspUserLogin.MaxOrderRef}, SystemName: {pRspUserLogin.SystemName}")
        self.TradingDay = pRspUserLogin.TradingDay
        self.FrontID = pRspUserLogin.FrontID
        self.SessionID = pRspUserLogin.SessionID
        self.OrderRef = 1

        self.QryAccount()

    def OnRtnOrder(self, pOrder):
        print(f"OnRtnOrder:"
              f"UserID={pOrder.UserID} "
              f"BrokerID={pOrder.BrokerID} "
              f"InvestorID={pOrder.InvestorID} "
              f"ExchangeID={pOrder.ExchangeID} "
              f"InstrumentID={pOrder.InstrumentID} "
              f"Direction={pOrder.Direction} "
              f"CombOffsetFlag={pOrder.CombOffsetFlag} "
              f"CombHedgeFlag={pOrder.CombHedgeFlag} "
              f"OrderPriceType={pOrder.OrderPriceType} "
              f"LimitPrice={pOrder.LimitPrice} "
              f"VolumeTotalOriginal={pOrder.VolumeTotalOriginal} "
              f"OrderSysID={pOrder.OrderSysID} "
              f"OrderStatus={pOrder.OrderStatus} "
              f"StatusMsg={pOrder.StatusMsg} "
              )

    def OnRtnTrade(self, pTrade):
        print(f"OnRtnTrade:"
              f"BrokerID={pTrade.BrokerID} "
              f"InvestorID={pTrade.InvestorID} "
              f"ExchangeID={pTrade.ExchangeID} "
              f"InstrumentID={pTrade.InstrumentID} "
              f"Direction={pTrade.Direction} "
              f"OffsetFlag={pTrade.OffsetFlag} "
              f"HedgeFlag={pTrade.HedgeFlag} "
              f"Price={pTrade.Price}  "
              f"Volume={pTrade.Volume} "
              f"OrderSysID={pTrade.OrderSysID} "
              f"OrderRef={pTrade.OrderRef} "
              f'TradeID={pTrade.TradeID} '
              f'TradeDate={pTrade.TradeDate} '
              f'TradeTime={pTrade.TradeTime} '
              )

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print(f"查询账户资金失败: {pRspInfo.ErrorMsg}")
            return
        
        if pTradingAccount is not None:
            print(f"账户资金: 可用资金={pTradingAccount.Available}, "
                  f"当前保证金={pTradingAccount.CurrMargin}, "
                  f"平仓盈亏={pTradingAccount.CloseProfit}, "
                  f"持仓盈亏={pTradingAccount.PositionProfit}")
        
        self.QryPosition()

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print(f"查询持仓失败: {pRspInfo.ErrorMsg}")
            return
        
        if pInvestorPosition is not None:
            print(f"持仓: 合约={pInvestorPosition.InstrumentID}, "
                  f"方向={'多' if pInvestorPosition.PosiDirection == '2' else '空'}, "
                  f"总持仓={pInvestorPosition.Position}, "
                  f"今日持仓={pInvestorPosition.TodayPosition}, "
                  f"昨日持仓={pInvestorPosition.YdPosition}, "
                  f"持仓成本={pInvestorPosition.PositionCost}, "
                  f"持仓盈亏={pInvestorPosition.PositionProfit}")

    def QryAccount(self):
        req = tdapi.CThostFtdcQryTradingAccountField()
        req.BrokerID = self.broker
        req.InvestorID = self.user
        self.api.ReqQryTradingAccount(req, 0)

    def QryPosition(self):
        req = tdapi.CThostFtdcQryInvestorPositionField()
        req.BrokerID = self.broker
        req.InvestorID = self.user
        self.api.ReqQryInvestorPosition(req, 0)

    def OrderInsert(self, instrument_id, direction, offset_flag, price, volume):
        """
        报单
        
        Args:
            instrument_id: 合约代码
            direction: 买卖方向 '0'买 '1'卖
            offset_flag: 开平标志 '0'开仓 '1'平仓 '3'平今 '4'平昨
            price: 价格
            volume: 数量
        
        Returns:
            报单引用
        """
        self.OrderRef += 1
        order_ref = f"{self.OrderRef:012d}"
        
        req = tdapi.CThostFtdcInputOrderField()
        req.BrokerID = self.broker
        req.InvestorID = self.user
        req.InstrumentID = instrument_id
        req.OrderRef = order_ref
        req.UserID = self.user
        req.OrderPriceType = tdapi.THOST_FTDC_OPT_LimitPrice
        req.Direction = direction
        req.CombOffsetFlag = offset_flag
        req.CombHedgeFlag = tdapi.THOST_FTDC_HF_Speculation
        req.LimitPrice = price
        req.VolumeTotalOriginal = volume
        req.TimeCondition = tdapi.THOST_FTDC_TC_GFD
        req.VolumeCondition = tdapi.THOST_FTDC_VC_AV
        req.MinVolume = 1
        req.ContingentCondition = tdapi.THOST_FTDC_CC_Immediately
        req.ForceCloseReason = tdapi.THOST_FTDC_FCC_NotForceClose
        req.IsAutoSuspend = 0
        req.UserForceClose = 0
        
        self.api.ReqOrderInsert(req, 0)
        return order_ref


if __name__ == '__main__':
    td = TdImpl(
        "tcp://180.168.146.187:10101",  # 交易前置地址
        "9999",                         # 经纪公司代码
        "123456",                       # 投资者代码
        "password",                     # 密码
        "simnow_client_test",           # AppID
        "0000000000000000"              # 授权码
    )
    td.Run()
    
    input("Press enter key to exit.")
