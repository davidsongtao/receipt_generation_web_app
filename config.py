import os

# 常量定义（保持不变）
TEMPLATE_DIR = 'templates'
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# 电器选项
ELECTRICAL_APPLIANCES = [
    "fridge", "microwave", "oven", "dish washer", "washing machine", "dryer", "air conditioner", "kitchen hood"
]

# 房间选项
ROOMS = ["bedroom", "kitchen", "bathroom"]

# 其他服务选项
OTHER_SERVICES = [
    "window glasses", "walls", "mattress",
    "balcony", "laundry room", "sofa",
    "extra kitchen", "extra bathroom", "extra clean of floor board",
    "extra clean of carpet"
]

# AWA服务选项
AWA_SERVICES = [
    "garbage removal", "furniture wipe off",
    "mold removal", "pet hair removal"
]

# 基础服务选项
BASIC_SERVICES = [
    " the clean of floor board,",
    " steam cleaning of carpet, the clean of"
]


CUSTOM_HEADER = {
    'notes': '备注',
    'work_time': '工作时间',
    'address': '工作地址',
    'project': '项目',
    'dispatcher': '派单阿姨',
    'confirmed': '已确认',
    'registered': '登记',
    'dispatched': '派单',
    'dispatch_price': '派遣价格',
    'final_price': '成交价',
    'receipt_or_invoice': '收据/发票',
    'sent_or_not': '已发送'
}
