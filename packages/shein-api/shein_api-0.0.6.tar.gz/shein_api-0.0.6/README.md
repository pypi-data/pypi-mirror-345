```shell
# 安装
pip install shein_api
```

```python
from shein_api import SheinClient
from shein_api.base.helpers import ShopType
from shein_api.base.crypto import decrypt

SHEIN_APP_ID = ''
SHEIN_APP_SECRET = ''
tempToken = ''

client = SheinClient(SHEIN_APP_ID, SHEIN_APP_SECRET, ShopType.SELF_OPERATION)
openKeyId, secretKey = client.auth.get_by_token(tempToken)
decrypt_result = decrypt(openKeyId, secretKey)

orders = client.order.order_list(2, '2024-12-12 15:38:29', '2024-12-13 15:38:29', 1, 30)
return_order = client.return_order.sign_return_order('return_order_no', ['goods_id_list', 'sfaadsa'])
```