from boto3 import resource
from decimal import Decimal


def dynamodb_put_item_disk():
    try:
        dynamodb = resource('dynamodb')
        _table_name = ["st_disk", "st_memory", "st_cpu_stats"]
        _table_input = [
            {
                "id": 1,
                "free": Decimal("20.09"),
                "total": Decimal("24.06"),
                "used": Decimal("2.74")
            },
            {
                "id": 1,
                "active": "326254592",
                "available": "455225344",
                "buffers": "47992832",
                "cached": "472260608",
                "free": "118136832",
                "inactive": "248201216",
                "percent": Decimal("47.0"),
                "shared": "33239040",
                "slab": "125714432",
                "total": "858411008",
                "used": "220020736"
            },
            {
                "id": 1,
                "ctx_switches": "58668751",
                "interrupts": "32587530",
                "soft_interrupts": "28369329",
                "syscalls": "0"
            }
        ]

        for _tbl, _col in zip(_table_name, _table_input):
            table = dynamodb.Table(_tbl)
            table.put_item(Item=_col)
        return "success"
    except Exception as err:
        raise err
