import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from loguru import logger
import requests
import pandas as pd


# year 年
#  quarter 季度
# month 月度
# week 周
# day 日
def get_xue_qiu_k_line(symbol, period):
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"

    params = {
        "symbol": symbol,
        "begin": "1742574377493",
        "period": period,
        "type": "before",
        "count": "-120084",
        "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://xueqiu.com",
        "priority": "u=1, i",
        "referer": "https://xueqiu.com/S/SZ300879?md5__1038=n4%2BxgDniDQeWqxYwq0y%2BbDyG%2BYDtODuD7q%2BqRYID",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "cookie": "cookiesu=401743509129481; device_id=e7bd664c2ad4091241066c3a2ddbd736; remember=1; xq_is_login=1; u=9627701445; xq_a_token=4d1dc50464f7995ed9da20125e94fc77df0605d4; xqat=4d1dc50464f7995ed9da20125e94fc77df0605d4; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjk2Mjc3MDE0NDUsImlzcyI6InVjIiwiZXhwIjoxNzQ2NjM0MzExLCJjdG0iOjE3NDQwNDIzMTE3OTIsImNpZCI6ImQ5ZDBuNEFadXAifQ.ehhu6ZGP8bXmIO4rB_UDPgCg7P996ExBcXkeuVRMTmswc_ZIRntQ04sv0nRoW7r6dBU10BIEFQmA3bvZO7kYuDKBVrCR86KBzDC5_3X6dTtHgb-Yr405r5ts-aQo0eYlDp4DMigJsfp6deH-058sKQlIIQajTjK4OI-0RZBNVPx6jhQcNHAJCpHNmUc613EnYTMOs9DUADOY63KIbf9VOz6fQyNd5bnyAkU0ubsoVMWu5_cFx14UUgq5BipMzG9zsjbWcXjqp2VsGQ42sJ9x-L_uqLaWdpcz5K8JqNTkvV6ADbsG3yOlzp4kdS-1WBVEYjj4vZv7UWe8eB6Aaf4Uyg; xq_r_token=cfb922056d8dd2e5212255f2fb0958cd6d98b416; Hm_lvt_1db88642e346389874251b5a1eded6e3=1744115609,1744116531,1744123698,1744128314; HMACCOUNT=1CFFE969351DFC92; is_overseas=0; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1744131160; ssxmod_itna=QqAx0DRGiQdbei7ditG8DI6KGRQrD2jDl4BttiGgDYq7=GFiDCOizO1CxBKA6Kd3Dj22AxWRxGXPmDA5Dnzx7YDt=SPxDB7YHi1KjnG+beSAj7e4qOaUehb3qQGnYFmEat0USSVYmkeDHxi8DB9DYG9FDenWDCeDQxirDD4DAQPDFxibDimI34DdTIOvstOwCDGrDlKDRx07CC3DWxDFTU0HKQgj48ExDGvxqk04rhP4DmRmC37LCl3Dn=Dv=QoD9p4DsOh9M4DCky6x+Roc=mQb=USfDCKDjoLIe/fQFbfv3IQ8e7vskhDjQ4dGvPGP3CGxeeViDRWQ1ei4Aqn7xdGPdQmqKmVjptt4DDcDo2Ky4xF0KHvM+ymIHZKhDrDxwOzFDbGYbYx7QGH9OUiTtBho5iq4+Pnri9Yie+ewo+DYPeD; ssxmod_itna2=QqAx0DRGiQdbei7ditG8DI6KGRQrD2jDl4BttiGgDYq7=GFiDCOizO1CxBKA6Kd3Dj22AxWKxDfCecxD5qDFrv4A=iDGX5is6Y7iAYQig8n7YGzGl9xrojBSddLV8xkjxkone8iq0Ejc4Mp9dBZRzPA9deDpPqmaGYSyOCPcDFDghi=DFWRBDNbo1/a9OqenaQKqsemSFI9SHF/AfvOhsQKP4=c8UGgBad0AE/2Owk9MOs/71ihBwzgQRHPZROZgINUiWdQZxbp1frOOL8c=AO6yjHaiGk+O7XUoF4UcHo+0HaKzTSG9yWDxwEiihkhxtkizH4ttfkd3xGrGSB3MrTqB=pOkhwdx+CYmb8l+0xxKbbYWsYfa88ajgN3l=Crtd8T0eijCG=AGk8+LnWqWt6O+wL3ZOoto5rr5xQksExto71TEISWtk+jE3P0WF7NW0DNS+7pD8pL8dEx2sGRb=riia3v=kopew0Du6UYY5l0=HjdFi5zEUn1DwBUdiDD"
    }
    try:
        response = requests.get(
            url=url,
            params=params,
            headers=headers
        )

        if response.status_code == 200:
            response_data = response.json()
            df = pd.DataFrame(
                data=response_data['data']['item'],
                columns=response_data['data']['column']
            )
            # 处理DataFrame列（秒级时间戳）
            df['str_day'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
            df["str_day"] = df["str_day"].dt.strftime("%Y-%m-%d")
            return df
        else:
            return pd.DataFrame()
    except BaseException as e:
        logger.error("同步股票年度数据出现异常:{},{}", symbol, e)


if __name__ == '__main__':
    test_df = get_xue_qiu_k_line('SZ000001', 'year')
    print(test_df)
