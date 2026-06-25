import scrapy
import json
from datetime import datetime

class CellphonesSpider(scrapy.Spider):
    name = "cellphones"
    allowed_domains = ["cellphones.com.vn"]
    
    # Khai thac API GraphQL noi bo cua CellphoneS
    # Lap tu trang 1 den 45 de gom du so luong ban ghi lon vuot moc barem >= 1500 dong
    start_urls = []
    for page in range(1, 46):
        url = f"https://api.cellphones.com.vn/v2/graphql/query?query=query{{products(filter:{{category_id:\"3\"}},page:{page},size:50){{items{{_id,name,brand,stock_info{{stock_available}},attributes{{code,value}},price_info{{price,original_price}}}}}}}}"
        start_urls.append(url)
        

    def parse(self, response):
        try:
            data = json.loads(response.text)
            
            # Lay du lieu tung buoc mot de de hieu, thay vi noi chuoi .get() dai
            data_dict = data.get('data', {})
            products_dict = data_dict.get('products', {})
            products = products_dict.get('items', [])
            
            for prod in products:
                name = prod.get('name', '')
                brand = prod.get('brand', '')
                prod_id = prod.get('_id', '')
                
                # Trich xuat thong tin gia ban va gia goc
                price_info = prod.get('price_info', {})
                sale_price = price_info.get('price', 0)
                
                # Kiem tra gia goc, neu khong co hoac bang 0 thi lay bang gia ban
                original_price = price_info.get('original_price', 0)
                if original_price == None or original_price == 0:
                    original_price = sale_price
                
                # Trich xuat trang thai kho hang (Phuc vu Dashboard truc quan cua TV4)
                stock_info = prod.get('stock_info', {})
                stock_available = stock_info.get('stock_available', 0)
                
                # Kiem tra xem co hang hay khong
                if stock_available > 0:
                    stock_status = "Con hang"
                else:
                    stock_status = "Het hang"
                
                # Khoi tao mac dinh cau hinh phan cung
                ram = "N/A"
                rom = "N/A"
                model_series = "N/A"
                
                # Vong lap boc tach mang thuoc tinh ky thuat cua API
                attrs = prod.get('attributes', [])
                for attr in attrs:
                    code = attr.get('code')
                    val = attr.get('value', 'N/A')
                    
                    if code == 'phone_ram':
                        ram = val
                    elif code == 'phone_internal_storage':
                        rom = val
                    elif code == 'phone_model_series':
                        model_series = val
                
                # Chuan hoa dong may tam thoi phuc vu bai toan Product Diversity cua TV3
                if model_series == "N/A":
                    if name != "":
                        # Cat ten thanh cac tu rieng le, sau do ghep 3 tu dau tien lai voi nhau
                        words = name.split()
                        first_three_words = words[:3]
                        model_series = " ".join(first_three_words)
                
                # Xu ly product_id cho ro rang
                if prod_id != "":
                    final_product_id = f"CPS_{prod_id}"
                else:
                    final_product_id = "N/A"
                
                # Xuat ra dung cau truc 12 cot du lieu toi uu da thong nhat phuc vu ca nhom
                yield {
                    'product_id': final_product_id,
                    'product_name': name,
                    'brand': brand,
                    'model_series': model_series,
                    'ram_capacity': ram,
                    'rom_capacity': rom,
                    'original_price': original_price,
                    'sale_price': sale_price,
                    'stock_status': stock_status,
                    'product_status': 'May moi chinh hang',
                    'source_site': 'CellphoneS',
                    'crawl_date': datetime.now().strftime('%Y-%m-%d')
                }
        except Exception as e:
            self.logger.error(f"Loi phan tich du lieu tai trang: {e}")
