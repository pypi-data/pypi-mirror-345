# encoding:utf-8
# distutils: language=c++
"""
(Copyright) 2018, Winton Wang <365504029@qq.com>

ctpwrapper is free software: you can redistribute it and/or modify
it under the terms of the GNU LGPLv3 as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ctpwrapper.  If not, see <http://www.gnu.org/licenses/>.

"""
from cpython cimport PyObject
from libc.string cimport const_char

from .ThostFtdcUserApiStruct cimport *

cdef extern from "ThostFtdcTraderApi.h":
    cdef cppclass CTraderApi "CThostFtdcTraderApi":

        @staticmethod
        const_char *GetApiVersion()

        # 删除接口对象本身
        #@remark 不再使用本接口对象时,调用该函数删除接口对象
        void Release() except + nogil

        #初始化
        #@remark 初始化运行环境,只有调用后,接口才开始工作
        void Init() except + nogil

        #等待接口线程结束运行
        #@return 线程退出代码
        int Join() except + nogil

        #获取当前交易日
        #@retrun 获取到的交易日
        #@remark 只有登录成功后,才能得到正确的交易日
        const_char *GetTradingDay() except + nogil

        # 获取已连接的前置的信息
        # @param pFrontInfo：输入输出参数，用于存储获取到的前置信息，不能为空
        # @remark 连接成功后，可获取正确的前置地址信息
        # @remark 登录成功后，可获取正确的前置流控信息
        void GetFrontInfo(CThostFtdcFrontInfoField *pFrontInfo) except + nogil

        #注册前置机网络地址
        #@param pszFrontAddress：前置机网络地址。
        #@remark 网络地址的格式为：“protocol://ipaddress:port”，如：”tcp://127.0.0.1:17001”。
        #@remark “tcp”代表传输协议，“127.0.0.1”代表服务器地址。”17001”代表服务器端口号。
        void RegisterFront(char *pszFrontAddress) except + nogil

        #注册名字服务器网络地址
        #@param pszNsAddress：名字服务器网络地址。
        #@remark 网络地址的格式为：“protocol://ipaddress:port”，如：”tcp://127.0.0.1:12001”。
        #@remark “tcp”代表传输协议，“127.0.0.1”代表服务器地址。”12001”代表服务器端口号。
        #@remark RegisterNameServer优先于RegisterFront
        void RegisterNameServer(char *pszNsAddress) except + nogil

        #注册名字服务器用户信息
        #@param pFensUserInfo：用户信息。
        void RegisterFensUserInfo(CThostFtdcFensUserInfoField *pFensUserInfo) except + nogil

        #注册回调接口
        #@param pSpi 派生自回调接口类的实例
        void RegisterSpi(CTraderSpi *pSpi) except + nogil

        #订阅私有流。
        #@param nResumeType 私有流重传方式
        #        THOST_TERT_RESTART:从本交易日开始重传
        #        THOST_TERT_RESUME:从上次收到的续传
        #        THOST_TERT_QUICK:只传送登录后私有流的内容
        #@remark 该方法要在Init方法前调用。若不调用则不会收到私有流的数据。
        void SubscribePrivateTopic(THOST_TE_RESUME_TYPE nResumeType) except + nogil

        #订阅公共流。
        #@param nResumeType 公共流重传方式
        #        THOST_TERT_RESTART:从本交易日开始重传
        #        THOST_TERT_RESUME:从上次收到的续传
        #        THOST_TERT_QUICK:只传送登录后公共流的内容
        #@remark 该方法要在Init方法前调用。若不调用则不会收到公共流的数据。
        void SubscribePublicTopic(THOST_TE_RESUME_TYPE nResumeType) except + nogil

        #客户端认证请求
        int ReqAuthenticate(CThostFtdcReqAuthenticateField *pReqAuthenticateField, int nRequestID) except + nogil

        #注册用户终端信息，用于中继服务器多连接模式
        #需要在终端认证成功后，用户登录前调用该接口
        int RegisterUserSystemInfo(CThostFtdcUserSystemInfoField *pUserSystemInfo) except + nogil

        #上报用户终端信息，用于中继服务器操作员登录模式
        # 操作员登录后，可以多次调用该接口上报客户信息
        int SubmitUserSystemInfo(CThostFtdcUserSystemInfoField *pUserSystemInfo) except + nogil

        #用户登录请求
        int ReqUserLogin(CThostFtdcReqUserLoginField *pReqUserLoginField, int nRequestID) except + nogil

        #登出请求
        int ReqUserLogout(CThostFtdcUserLogoutField *pUserLogout, int nRequestID) except + nogil

        #用户口令更新请求
        int ReqUserPasswordUpdate(CThostFtdcUserPasswordUpdateField *pUserPasswordUpdate, int nRequestID) except + nogil

        #资金账户口令更新请求
        int ReqTradingAccountPasswordUpdate(CThostFtdcTradingAccountPasswordUpdateField *pTradingAccountPasswordUpdate, int nRequestID) except + nogil

        # 查询用户当前支持的认证模式
        int ReqUserAuthMethod(CThostFtdcReqUserAuthMethodField *pReqUserAuthMethod, int nRequestID) except + nogil

        # 用户发出获取图形验证码请求
        int ReqGenUserCaptcha(CThostFtdcReqGenUserCaptchaField *pReqGenUserCaptcha, int nRequestID) except + nogil

        # 用户发出获取短信验证码请求
        int ReqGenUserText(CThostFtdcReqGenUserTextField *pReqGenUserText, int nRequestID) except + nogil

        # 用户发出带有图片验证码的登陆请求
        int ReqUserLoginWithCaptcha(CThostFtdcReqUserLoginWithCaptchaField *pReqUserLoginWithCaptcha, int nRequestID) except + nogil

        # 用户发出带有短信验证码的登陆请求
        int ReqUserLoginWithText(CThostFtdcReqUserLoginWithTextField *pReqUserLoginWithText, int nRequestID) except + nogil

        # 用户发出带有动态口令的登陆请求
        int ReqUserLoginWithOTP(CThostFtdcReqUserLoginWithOTPField *pReqUserLoginWithOTP, int nRequestID) except + nogil

        #报单录入请求
        int ReqOrderInsert(CThostFtdcInputOrderField *pInputOrder, int nRequestID) except + nogil

        #预埋单录入请求
        int ReqParkedOrderInsert(CThostFtdcParkedOrderField *pParkedOrder, int nRequestID) except + nogil

        #预埋撤单录入请求
        int ReqParkedOrderAction(CThostFtdcParkedOrderActionField *pParkedOrderAction, int nRequestID) except + nogil

        #报单操作请求
        int ReqOrderAction(CThostFtdcInputOrderActionField *pInputOrderAction, int nRequestID) except + nogil

        #查询最大报单数量请求

        int ReqQryMaxOrderVolume(CThostFtdcQryMaxOrderVolumeField *pQryMaxOrderVolume, int nRequestID) except + nogil

        #投资者结算结果确认
        int ReqSettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField *pSettlementInfoConfirm, int nRequestID) except + nogil

        #请求删除预埋单
        int ReqRemoveParkedOrder(CThostFtdcRemoveParkedOrderField *pRemoveParkedOrder, int nRequestID) except + nogil

        #请求删除预埋撤单
        int ReqRemoveParkedOrderAction(CThostFtdcRemoveParkedOrderActionField *pRemoveParkedOrderAction, int nRequestID) except + nogil

        #执行宣告录入请求
        int ReqExecOrderInsert(CThostFtdcInputExecOrderField *pInputExecOrder, int nRequestID) except + nogil

        #执行宣告操作请求
        int ReqExecOrderAction(CThostFtdcInputExecOrderActionField *pInputExecOrderAction, int nRequestID) except + nogil

        #询价录入请求
        int ReqForQuoteInsert(CThostFtdcInputForQuoteField *pInputForQuote, int nRequestID) except + nogil

        #报价录入请求
        int ReqQuoteInsert(CThostFtdcInputQuoteField *pInputQuote, int nRequestID) except + nogil

        #报价操作请求
        int ReqQuoteAction(CThostFtdcInputQuoteActionField *pInputQuoteAction, int nRequestID) except + nogil

        #批量报单操作请求
        int ReqBatchOrderAction(CThostFtdcInputBatchOrderActionField *pInputBatchOrderAction, int nRequestID) except + nogil

        #期权自对冲录入请求
        int ReqOptionSelfCloseInsert(CThostFtdcInputOptionSelfCloseField *pInputOptionSelfClose, int nRequestID) except + nogil

        #期权自对冲操作请求
        int ReqOptionSelfCloseAction(CThostFtdcInputOptionSelfCloseActionField *pInputOptionSelfCloseAction, int nRequestID) except + nogil

        #申请组合录入请求
        int ReqCombActionInsert(CThostFtdcInputCombActionField *pInputCombAction, int nRequestID) except + nogil

        #请求查询报单
        int ReqQryOrder(CThostFtdcQryOrderField *pQryOrder, int nRequestID) except + nogil

        #请求查询成交
        int ReqQryTrade(CThostFtdcQryTradeField *pQryTrade, int nRequestID) except + nogil

        #请求查询投资者持仓
        int ReqQryInvestorPosition(CThostFtdcQryInvestorPositionField *pQryInvestorPosition, int nRequestID) except + nogil

        #请求查询资金账户
        int ReqQryTradingAccount(CThostFtdcQryTradingAccountField *pQryTradingAccount, int nRequestID) except + nogil

        #请求查询投资者
        int ReqQryInvestor(CThostFtdcQryInvestorField *pQryInvestor, int nRequestID) except + nogil

        #请求查询交易编码
        int ReqQryTradingCode(CThostFtdcQryTradingCodeField *pQryTradingCode, int nRequestID) except + nogil

        #请求查询合约保证金率
        int ReqQryInstrumentMarginRate(CThostFtdcQryInstrumentMarginRateField *pQryInstrumentMarginRate, int nRequestID) except + nogil

        #请求查询合约手续费率
        int ReqQryInstrumentCommissionRate(CThostFtdcQryInstrumentCommissionRateField *pQryInstrumentCommissionRate, int nRequestID) except + nogil

        #请求查询交易所
        int ReqQryExchange(CThostFtdcQryExchangeField *pQryExchange, int nRequestID) except + nogil

        #请求查询产品
        int ReqQryProduct(CThostFtdcQryProductField *pQryProduct, int nRequestID) except + nogil

        #请求查询合约
        int ReqQryInstrument(CThostFtdcQryInstrumentField *pQryInstrument, int nRequestID) except + nogil

        #请求查询行情
        int ReqQryDepthMarketData(CThostFtdcQryDepthMarketDataField *pQryDepthMarketData, int nRequestID) except + nogil

        # 请求查询交易员报盘机
        int ReqQryTraderOffer(CThostFtdcQryTraderOfferField *pQryTraderOffer, int nRequestID) except + nogil

        #请求查询投资者结算结果
        int ReqQrySettlementInfo(CThostFtdcQrySettlementInfoField *pQrySettlementInfo, int nRequestID) except + nogil

        #请求查询转帐银行
        int ReqQryTransferBank(CThostFtdcQryTransferBankField *pQryTransferBank, int nRequestID) except + nogil

        #请求查询投资者持仓明细
        int ReqQryInvestorPositionDetail(CThostFtdcQryInvestorPositionDetailField *pQryInvestorPositionDetail, int nRequestID) except + nogil

        #请求查询客户通知
        int ReqQryNotice(CThostFtdcQryNoticeField *pQryNotice, int nRequestID) except + nogil

        #请求查询结算信息确认
        int ReqQrySettlementInfoConfirm(CThostFtdcQrySettlementInfoConfirmField *pQrySettlementInfoConfirm, int nRequestID) except + nogil

        #请求查询投资者持仓明细
        int ReqQryInvestorPositionCombineDetail(CThostFtdcQryInvestorPositionCombineDetailField *pQryInvestorPositionCombineDetail, int nRequestID) except + nogil

        #请求查询保证金监管系统经纪公司资金账户密钥
        int ReqQryCFMMCTradingAccountKey(CThostFtdcQryCFMMCTradingAccountKeyField *pQryCFMMCTradingAccountKey, int nRequestID) except + nogil

        #请求查询仓单折抵信息
        int ReqQryEWarrantOffset(CThostFtdcQryEWarrantOffsetField *pQryEWarrantOffset, int nRequestID) except + nogil

        #请求查询投资者品种/跨品种保证金
        int ReqQryInvestorProductGroupMargin(CThostFtdcQryInvestorProductGroupMarginField *pQryInvestorProductGroupMargin, int nRequestID) except + nogil

        #请求查询交易所保证金率
        int ReqQryExchangeMarginRate(CThostFtdcQryExchangeMarginRateField *pQryExchangeMarginRate, int nRequestID) except + nogil

        #请求查询交易所调整保证金率
        int ReqQryExchangeMarginRateAdjust(CThostFtdcQryExchangeMarginRateAdjustField *pQryExchangeMarginRateAdjust, int nRequestID) except + nogil

        #请求查询汇率
        int ReqQryExchangeRate(CThostFtdcQryExchangeRateField *pQryExchangeRate, int nRequestID) except + nogil

        #请求查询二级代理操作员银期权限
        int ReqQrySecAgentACIDMap(CThostFtdcQrySecAgentACIDMapField *pQrySecAgentACIDMap, int nRequestID) except + nogil

        #请求查询产品报价汇率
        int ReqQryProductExchRate(CThostFtdcQryProductExchRateField *pQryProductExchRate, int nRequestID) except + nogil

        #请求查询产品组
        int ReqQryProductGroup(CThostFtdcQryProductGroupField *pQryProductGroup, int nRequestID) except + nogil

        #请求查询做市商合约手续费率
        int ReqQryMMInstrumentCommissionRate(CThostFtdcQryMMInstrumentCommissionRateField *pQryMMInstrumentCommissionRate, int nRequestID) except + nogil

        #请求查询做市商期权合约手续费
        int ReqQryMMOptionInstrCommRate(CThostFtdcQryMMOptionInstrCommRateField *pQryMMOptionInstrCommRate, int nRequestID) except + nogil

        #请求查询报单手续费
        int ReqQryInstrumentOrderCommRate(CThostFtdcQryInstrumentOrderCommRateField *pQryInstrumentOrderCommRate, int nRequestID) except + nogil

        #请求查询资金账户
        int ReqQrySecAgentTradingAccount(CThostFtdcQryTradingAccountField *pQryTradingAccount, int nRequestID) except + nogil

        #请求查询二级代理商资金校验模式
        int ReqQrySecAgentCheckMode(CThostFtdcQrySecAgentCheckModeField *pQrySecAgentCheckMode, int nRequestID) except + nogil

        #请求查询二级代理商信息
        int ReqQrySecAgentTradeInfo(CThostFtdcQrySecAgentTradeInfoField *pQrySecAgentTradeInfo, int nRequestID) except + nogil

        #请求查询期权交易成本
        int ReqQryOptionInstrTradeCost(CThostFtdcQryOptionInstrTradeCostField *pQryOptionInstrTradeCost, int nRequestID) except + nogil

        #请求查询期权合约手续费
        int ReqQryOptionInstrCommRate(CThostFtdcQryOptionInstrCommRateField *pQryOptionInstrCommRate, int nRequestID) except + nogil

        #请求查询执行宣告
        int ReqQryExecOrder(CThostFtdcQryExecOrderField *pQryExecOrder, int nRequestID) except + nogil

        #请求查询询价
        int ReqQryForQuote(CThostFtdcQryForQuoteField *pQryForQuote, int nRequestID) except + nogil

        #请求查询报价
        int ReqQryQuote(CThostFtdcQryQuoteField *pQryQuote, int nRequestID) except + nogil

        #请求查询期权自对冲
        int ReqQryOptionSelfClose(CThostFtdcQryOptionSelfCloseField *pQryOptionSelfClose, int nRequestID) except + nogil

        #请求查询投资单元
        int ReqQryInvestUnit(CThostFtdcQryInvestUnitField *pQryInvestUnit, int nRequestID) except + nogil

        #请求查询组合合约安全系数
        int ReqQryCombInstrumentGuard(CThostFtdcQryCombInstrumentGuardField *pQryCombInstrumentGuard, int nRequestID) except + nogil

        #请求查询申请组合
        int ReqQryCombAction(CThostFtdcQryCombActionField *pQryCombAction, int nRequestID) except + nogil

        #请求查询转帐流水
        int ReqQryTransferSerial(CThostFtdcQryTransferSerialField *pQryTransferSerial, int nRequestID) except + nogil

        #请求查询银期签约关系
        int ReqQryAccountregister(CThostFtdcQryAccountregisterField *pQryAccountregister, int nRequestID) except + nogil

        #请求查询签约银行
        int ReqQryContractBank(CThostFtdcQryContractBankField *pQryContractBank, int nRequestID) except + nogil

        #请求查询预埋单
        int ReqQryParkedOrder(CThostFtdcQryParkedOrderField *pQryParkedOrder, int nRequestID) except + nogil

        #请求查询预埋撤单
        int ReqQryParkedOrderAction(CThostFtdcQryParkedOrderActionField *pQryParkedOrderAction, int nRequestID) except + nogil

        #请求查询交易通知
        int ReqQryTradingNotice(CThostFtdcQryTradingNoticeField *pQryTradingNotice, int nRequestID) except + nogil

        #请求查询经纪公司交易参数
        int ReqQryBrokerTradingParams(CThostFtdcQryBrokerTradingParamsField *pQryBrokerTradingParams, int nRequestID) except + nogil

        #请求查询经纪公司交易算法
        int ReqQryBrokerTradingAlgos(CThostFtdcQryBrokerTradingAlgosField *pQryBrokerTradingAlgos, int nRequestID) except + nogil

        #请求查询监控中心用户令牌
        int ReqQueryCFMMCTradingAccountToken(CThostFtdcQueryCFMMCTradingAccountTokenField *pQueryCFMMCTradingAccountToken, int nRequestID) except + nogil

        #期货发起银行资金转期货请求
        int ReqFromBankToFutureByFuture(CThostFtdcReqTransferField *pReqTransfer, int nRequestID) except + nogil

        #期货发起期货资金转银行请求
        int ReqFromFutureToBankByFuture(CThostFtdcReqTransferField *pReqTransfer, int nRequestID) except + nogil

        #期货发起查询银行余额请求
        int ReqQueryBankAccountMoneyByFuture(CThostFtdcReqQueryAccountField *pReqQueryAccount, int nRequestID) except + nogil

        # 请求查询分类合约
        int ReqQryClassifiedInstrument(CThostFtdcQryClassifiedInstrumentField *pQryClassifiedInstrument, int nRequestID) except + nogil

        # 请求组合优惠比例
        int ReqQryCombPromotionParam(CThostFtdcQryCombPromotionParamField *pQryCombPromotionParam, int nRequestID) except + nogil

        # 投资者风险结算持仓查询
        int ReqQryRiskSettleInvstPosition(CThostFtdcQryRiskSettleInvstPositionField *pQryRiskSettleInvstPosition, int nRequestID) except + nogil

        # 风险结算产品查询
        int ReqQryRiskSettleProductStatus(CThostFtdcQryRiskSettleProductStatusField *pQryRiskSettleProductStatus, int nRequestID) except + nogil

        # SPBM期货合约参数查询
        int ReqQrySPBMFutureParameter(CThostFtdcQrySPBMFutureParameterField *pQrySPBMFutureParameter, int nRequestID) except + nogil

        # SPBM期权合约参数查询
        int ReqQrySPBMOptionParameter(CThostFtdcQrySPBMOptionParameterField *pQrySPBMOptionParameter, int nRequestID) except + nogil

        # SPBM品种内对锁仓折扣参数查询
        int ReqQrySPBMIntraParameter(CThostFtdcQrySPBMIntraParameterField *pQrySPBMIntraParameter, int nRequestID) except + nogil

        # SPBM跨品种抵扣参数查询
        int ReqQrySPBMInterParameter(CThostFtdcQrySPBMInterParameterField *pQrySPBMInterParameter, int nRequestID) except + nogil

        # SPBM组合保证金套餐查询
        int ReqQrySPBMPortfDefinition(CThostFtdcQrySPBMPortfDefinitionField *pQrySPBMPortfDefinition, int nRequestID) except + nogil

        # 投资者SPBM套餐选择查询
        int ReqQrySPBMInvestorPortfDef(CThostFtdcQrySPBMInvestorPortfDefField *pQrySPBMInvestorPortfDef, int nRequestID) except + nogil

        # 投资者新型组合保证金系数查询
        int ReqQryInvestorPortfMarginRatio(CThostFtdcQryInvestorPortfMarginRatioField *pQryInvestorPortfMarginRatio, int nRequestID) except + nogil

        # 投资者产品SPBM明细查询
        int ReqQryInvestorProdSPBMDetail(CThostFtdcQryInvestorProdSPBMDetailField *pQryInvestorProdSPBMDetail, int nRequestID) except + nogil

        # 投资者商品组SPMM记录查询
        int ReqQryInvestorCommoditySPMMMargin(CThostFtdcQryInvestorCommoditySPMMMarginField *pQryInvestorCommoditySPMMMargin, int nRequestID) except + nogil

        # 投资者商品群SPMM记录查询
        int ReqQryInvestorCommodityGroupSPMMMargin(CThostFtdcQryInvestorCommodityGroupSPMMMarginField *pQryInvestorCommodityGroupSPMMMargin, int nRequestID) except + nogil

        # SPMM合约参数查询
        int ReqQrySPMMInstParam(CThostFtdcQrySPMMInstParamField *pQrySPMMInstParam, int nRequestID) except + nogil

        # SPMM产品参数查询
        int ReqQrySPMMProductParam(CThostFtdcQrySPMMProductParamField *pQrySPMMProductParam, int nRequestID) except + nogil

        # SPBM附加跨品种抵扣参数查询
        int ReqQrySPBMAddOnInterParameter(CThostFtdcQrySPBMAddOnInterParameterField *pQrySPBMAddOnInterParameter, int nRequestID) except + nogil

        # RCAMS产品组合信息查询
        int ReqQryRCAMSCombProductInfo(CThostFtdcQryRCAMSCombProductInfoField *pQryRCAMSCombProductInfo, int nRequestID) except + nogil

        # RCAMS同合约风险对冲参数查询
        int ReqQryRCAMSInstrParameter(CThostFtdcQryRCAMSInstrParameterField *pQryRCAMSInstrParameter, int nRequestID) except + nogil

        # RCAMS品种内风险对冲参数查询
        int ReqQryRCAMSIntraParameter(CThostFtdcQryRCAMSIntraParameterField *pQryRCAMSIntraParameter, int nRequestID) except + nogil

        # RCAMS跨品种风险折抵参数查询
        int ReqQryRCAMSInterParameter(CThostFtdcQryRCAMSInterParameterField *pQryRCAMSInterParameter, int nRequestID) except + nogil

        # RCAMS空头期权风险调整参数查询
        int ReqQryRCAMSShortOptAdjustParam(CThostFtdcQryRCAMSShortOptAdjustParamField *pQryRCAMSShortOptAdjustParam, int nRequestID) except + nogil

        # RCAMS策略组合持仓查询
        int ReqQryRCAMSInvestorCombPosition(CThostFtdcQryRCAMSInvestorCombPositionField *pQryRCAMSInvestorCombPosition, int nRequestID) except + nogil

        # 投资者品种RCAMS保证金查询
        int ReqQryInvestorProdRCAMSMargin(CThostFtdcQryInvestorProdRCAMSMarginField *pQryInvestorProdRCAMSMargin, int nRequestID) except + nogil

        # RULE合约保证金参数查询
        int ReqQryRULEInstrParameter(CThostFtdcQryRULEInstrParameterField *pQryRULEInstrParameter, int nRequestID) except + nogil

        # RULE品种内对锁仓折扣参数查询
        int ReqQryRULEIntraParameter(CThostFtdcQryRULEIntraParameterField *pQryRULEIntraParameter, int nRequestID) except + nogil

        # RULE跨品种抵扣参数查询
        int ReqQryRULEInterParameter(CThostFtdcQryRULEInterParameterField *pQryRULEInterParameter, int nRequestID) except + nogil

        # 投资者产品RULE保证金查询
        int ReqQryInvestorProdRULEMargin(CThostFtdcQryInvestorProdRULEMarginField *pQryInvestorProdRULEMargin, int nRequestID) except + nogil

        # 投资者新型组合保证金开关查询
        int ReqQryInvestorPortfSetting(CThostFtdcQryInvestorPortfSettingField *pQryInvestorPortfSetting, int nRequestID) except + nogil

        # 投资者申报费阶梯收取记录查询
        int ReqQryInvestorInfoCommRec(CThostFtdcQryInvestorInfoCommRecField *pQryInvestorInfoCommRec, int nRequestID) except + nogil

        # 组合腿信息查询
        int ReqQryCombLeg(CThostFtdcQryCombLegField *pQryCombLeg, int nRequestID) except + nogil

        # 对冲设置请求
        int ReqOffsetSetting(CThostFtdcInputOffsetSettingField *pInputOffsetSetting, int nRequestID) except + nogil

        # 对冲设置撤销请求
        int ReqCancelOffsetSetting(CThostFtdcInputOffsetSettingField *pInputOffsetSetting, int nRequestID) except + nogil

        # 投资者对冲设置查询
        int ReqQryOffsetSetting(CThostFtdcQryOffsetSettingField *pQryOffsetSetting, int nRequestID) except + nogil


cdef extern from "ThostFtdcTraderApi.h" namespace "CThostFtdcTraderApi":
    CTraderApi *CreateFtdcTraderApi(const_char *pszFlowPath) except + nogil

cdef extern from "CTraderAPI.h":
    cdef cppclass CTraderSpi:
        CTraderSpi(PyObject *obj) except +
