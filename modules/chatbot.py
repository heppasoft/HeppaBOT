import re
import json
import EdgeGPT
import typing as t


__all__ = ["chatbot_ask"]

cookies_edge = json.loads("""
[
    {
        "domain": ".bing.com",
        "expirationDate": 1716039763.313246,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHUSR",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "DOB=20230403&T=1681479761000"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1683166984.759093,
        "hostOnly": false,
        "httpOnly": true,
        "name": "SUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "A"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1717696739.503423,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHHPGUSR",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "SRCHLANG=tr&DM=1&THEME=1&PV=15.0.0&BRW=W&BRH=M&CW=1479&CH=792&SCW=1462&SCH=3576&DPR=1.3&UTC=180&EXLTT=9&HV=1683136740&PRVCW=1479&PRVCH=792"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1717694050.980433,
        "hostOnly": false,
        "httpOnly": false,
        "name": "ANON",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "A=C68FAA8B2607D936748C3572FFFFFFFF"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1713015767,
        "hostOnly": false,
        "httpOnly": false,
        "name": "BCP",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AD=1&AL=1&SM=1"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "_SS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "SID=3A946C232FD265750CD37F252EB9644E&R=3&RB=3&GB=0&RG=0&RP=3"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "ipv6",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "hit=1683139591793&t=4"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "dsc",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "order=News"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1684343650.980404,
        "hostOnly": false,
        "httpOnly": false,
        "name": "_U",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1iUnB1W2Y12r0x4D_MKEPp1EJZ9cr-5SX1eZ3RCYuIL7S7H182FmZfRMz_tqZMY5tl3BC7ixmYpOdeWza8BNwMiaopDoOIoNQR0e-X9p37oLd2IK86SAyZ3NXgN62SMWYs56se9Fq8kOn98QPHom94k5AGTX-TnbfTGE2A9IlgP-QazserjFjTQNb2VEGSYJG0QMTbFdg1nrKOJLVRwDfJcnKX6ko8PT99IXtmUOp8F8"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1715107900.964903,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHD",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AF=NOFORM"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1714243900.96489,
        "hostOnly": false,
        "httpOnly": true,
        "name": "_EDGE_V",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "1"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1716039764.018499,
        "hostOnly": false,
        "httpOnly": false,
        "name": "BFBUSR",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "BAWAS=1&BAWFS=1"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1714759139.184664,
        "hostOnly": false,
        "httpOnly": false,
        "name": "_RwBf",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "ilt=0&ihpd=0&ispd=0&rc=3&rb=3&gb=0&rg=0&pc=3&mtu=0&mte=0&rbb=0&g=0&cid=&clo=0&v=5&l=2023-05-03T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=BINGCOPILOTWAITLIST&c=MR000T&t=3530&s=2023-04-03T19:02:50.9793406+00:00&ts=2023-05-03T17:58:58.1857166+00:00&rwred=0&wls=2&lka=0&lkt=0&TH=&mta=0&e=VyDCpzxPYFlxlTl6BRnNQWS11NJuXMVvaSFdzoLQkkfyDkzZ4XEM4wTddMBpjgiLEQhSnRwfiEVYcWYJ6Vi_hA&A="
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": true,
        "name": "_EDGE_S",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": true,
        "storeId": null,
        "value": "SID=3A946C232FD265750CD37F252EB9644E&ui=tr-tr"
    },
    {
        "domain": "www.bing.com",
        "expirationDate": 1716832748.466917,
        "hostOnly": true,
        "httpOnly": true,
        "name": "MUIDB",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "14D89A7A6EE76D2F37EC88926F7E6CF2"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1715107900.964896,
        "hostOnly": false,
        "httpOnly": true,
        "name": "USRLOC",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "HS=1"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1713015768,
        "hostOnly": false,
        "httpOnly": false,
        "name": "_clck",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "53cl57|1|far|0"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1716039764.018524,
        "hostOnly": false,
        "httpOnly": true,
        "name": "BFB",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AhDlB5Rnvnjs8rW55Zyo20pJpO3cc2Mngnm4_lgtcoO4sBm8JD_msq3QKflwhNN6v6ICdj_CGmJPlgas3NHMfo0hi_sh7kbBe1bjBAHPRRDpR6FNDbnnR9l8ZLwmPIS6JrwideIQbenOTFDtlEP6HUTgvwIR_kUNtqR-CRfhP64YFQ"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1716823987.124659,
        "hostOnly": false,
        "httpOnly": false,
        "name": "MUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "14D89A7A6EE76D2F37EC88926F7E6CF2"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1689255764.018553,
        "hostOnly": false,
        "httpOnly": true,
        "name": "OID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AhAERc8T2T2ChqUXad67M8-G6tBrwbOyN33Xw1YItT4lcU-9UBP2xFMDcE0cSm6KS1M1k4Rbf6iHmaxR8zIRd6z4"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1689255764.018569,
        "hostOnly": false,
        "httpOnly": true,
        "name": "OIDI",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AhCdddcXazZ6sWXu5UbQZm4pId7NuGQ3RnflQmfg_LMfAQ"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1715107900.964915,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "V=2&GUID=2D2B09685E68406EBF4D855E7154B096&dmnchg=1"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "WLS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "C=024bcaf653855fbb&N=%c4%b0sa"
    }
]""")

cookies_chrome = json.loads("""
[
    {
        "domain": ".bing.com",
        "expirationDate": 1717701341.944416,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHUSR",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "DOB=20230414&T=1683141340000&TPC=1683126743000"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1683169941.423669,
        "hostOnly": false,
        "httpOnly": true,
        "name": "SUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "M"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1717701346.010296,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHHPGUSR",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "SRCHLANG=tr&PV=15.0.0&BRW=XW&BRH=M&CW=1536&CH=760&SCW=1519&SCH=3478&DPR=1.3&UTC=180&DM=1&HV=1683141343&WTS=63818738140&PRVCW=1536&PRVCH=760&EXLTT=3"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1713015747,
        "hostOnly": false,
        "httpOnly": false,
        "name": "BCP",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AD=1&AL=1&SM=1"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "_SS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "SID=21A5B618046263713D9FA4EB05FB62B5&R=18&RB=0&GB=0&RG=200&RP=15"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "ipv6",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "hit=1683144945821&t=4"
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": false,
        "name": "dsc",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": true,
        "storeId": null,
        "value": "order=News"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1716039738.499339,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHD",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "AF=NOFORM"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1715175738.297822,
        "hostOnly": false,
        "httpOnly": true,
        "name": "_EDGE_V",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "1"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1714763742.096807,
        "hostOnly": false,
        "httpOnly": false,
        "name": "_RwBf",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "ilt=6&ihpd=0&ispd=6&rc=18&rb=0&gb=0&rg=200&pc=15&mtu=0&rbb=0&g=0&cid=&clo=0&v=6&l=2023-05-03T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2023-05-03T19:15:41.1206457+00:00&rwred=0&wls=&lka=0&lkt=0&TH="
    },
    {
        "domain": ".bing.com",
        "hostOnly": false,
        "httpOnly": true,
        "name": "_EDGE_S",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": true,
        "storeId": null,
        "value": "F=1&SID=21A5B618046263713D9FA4EB05FB62B5"
    },
    {
        "domain": "www.bing.com",
        "expirationDate": 1716837344.959956,
        "hostOnly": true,
        "httpOnly": true,
        "name": "MUIDB",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "2CDF14DD78CA68183809062E79536950"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1717686814.995364,
        "hostOnly": false,
        "httpOnly": true,
        "name": "USRLOC",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "HS=1"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1715175738.29777,
        "hostOnly": false,
        "httpOnly": false,
        "name": "MUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "2CDF14DD78CA68183809062E79536950"
    },
    {
        "domain": ".bing.com",
        "expirationDate": 1716039738.499361,
        "hostOnly": false,
        "httpOnly": false,
        "name": "SRCHUID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "V=2&GUID=DF05195038E343D69F1350098263CF44&dmnchg=1"
    }
]""")

EdgeGPT.HEADERS["accept-language"] = "tr,en-US;q=0.9,en;q=0.8"
EdgeGPT.HEADERS_INIT_CONVER["accept-language"] = "tr,en-US;q=0.9,en;q=0.8"

async def chatbot_ask(prompt: str, conversation_style: EdgeGPT.CONVERSATION_STYLE_TYPE = None) -> t.Union[str, None]:
    bot = EdgeGPT.Chatbot(cookies=cookies_chrome)
    resp = await bot.ask(prompt=prompt, conversation_style=conversation_style)
    bot_return = None
    for msg in resp["item"]["messages"]:
        if msg["author"] == "bot":
            bot_return = msg["text"]
    bot_return = re.sub('\[\^\d+\^\]', '', bot_return)
    await bot.close()
    return bot_return