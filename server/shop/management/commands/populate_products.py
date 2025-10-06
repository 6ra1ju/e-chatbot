from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Populate sample products data'

    def handle(self, *args, **options):
        sample_products = [
            {
                "name": "Bánh Bao Hội An",
                "price": 150000,
                "original_price": 180000,
                "discount": 17,
                "rating": 4.5,
                "sold_count": 1250,
                "image": "client/src/assets/banh_bao_hoi_an.png",
                "labels": ["Nổi bật", "Đánh giá cao"]
            },
            {
                "name": "Bánh Bèo Chén",
                "price": 45000,
                "original_price": 50000,
                "discount": 10,
                "rating": 4.2,
                "sold_count": 3200,
                "image": "client/src/assets/banh_beo_chen.png",
                "labels": ["Giá tốt", "Phổ biến"]
            },
            {
                "name": "Bánh Đa Hến Xào",
                "price": 55000,
                "original_price": 60000,
                "discount": 8,
                "rating": 4.3,
                "sold_count": 2100,
                "image": "client/src/assets/banh_dap_hen_xao.png",
                "labels": ["Đặc sản", "Nổi tiếng"]
            },
            {
                "name": "Bánh Khọt Tôm Tươi",
                "price": 280000,
                "original_price": 350000,
                "discount": 20,
                "rating": 4.6,
                "sold_count": 890,
                "image": "client/src/assets/banh_khot_tom_tuoi.png",
                "labels": ["Cao cấp", "Hải sản"]
            },
            {
                "name": "Bánh Lọc Trần",
                "price": 120000,
                "original_price": 150000,
                "discount": 20,
                "rating": 4.4,
                "sold_count": 1560,
                "image": "client/src/assets/banh_loc_tran.png",
                "labels": ["Đặc sản", "Truyền thống"]
            },
            {
                "name": "Bánh Xèo Miền Nam",
                "price": 450000,
                "original_price": 500000,
                "discount": 10,
                "rating": 4.7,
                "sold_count": 650,
                "image": "client/src/assets/banh_xeo_mien_nam.png",
                "labels": ["Buffet", "Cao cấp"]
            },
            {
                "name": "Bún Bò Huế Giò Heo",
                "price": 180000,
                "original_price": 200000,
                "discount": 10,
                "rating": 4.1,
                "sold_count": 980,
                "image": "client/src/assets/bun_bo_hue_gio_heo.png",
                "labels": ["Lẩu","Đậm đà"]
            },
            {
                "name": "Bún Hến Xào",
                "price": 320000,
                "original_price": 380000,
                "discount": 16,
                "rating": 4.5,
                "sold_count": 720,
                "image": "client/src/assets/bun_hen_xao.png",
                "labels": ["Đặc sản", "Miền quê"]
            },
            {
                "name": "Bún Riêu Cua",
                "price": 120000,
                "original_price": 150000,
                "discount": 20,
                "rating": 4.0,
                "sold_count": 2100,
                "image": "client/src/assets/bun_rieu_cua.png",
                "labels": ["Lẩu", "Buffet"]
            },
            {
                "name": "Cá Nướng Giấy Bạc",
                "price": 180000,
                "original_price": 220000,
                "discount": 18,
                "rating": 4.3,
                "sold_count": 1100,
                "image": "client/src/assets/ca_nuong_giay_bac.png",
                "labels": ["Không gian đẹp", "Truyền thống"]
            },
            {
                "name": "Canh Chua Cá Bớp",
                "price": 380000,
                "original_price": 450000,
                "discount": 16,
                "rating": 4.6,
                "sold_count": 580,
                "image": "client/src/assets/canh_chua_ca_bop.png",
                "labels": ["Steak", "Cao cấp"]
            },
            {
                "name": "Hoành Thánh Chiên",
                "price": 65000,
                "original_price": 75000,
                "discount": 13,
                "rating": 4.2,
                "sold_count": 1800,
                "image": "client/src/assets/hoanh_thanh_chien.png",
                "labels": ["Đặc sản", "Bình dân"]
            }
        ]

        # Check if products already exist
        if Product.objects.count() == 0:
            self.stdout.write("Creating sample products...")
            for product_data in sample_products:
                product = Product.objects.create(
                    name=product_data["name"],
                    price=product_data["price"],
                    original_price=product_data.get("original_price"),
                    discount=product_data.get("discount"),
                    rating=product_data.get("rating"),
                    sold_count=product_data.get("sold_count"),
                    image=product_data.get("image")
                )
                product.set_labels_list(product_data.get("labels"))
                product.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {len(sample_products)} products')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Database already contains {Product.objects.count()} products. Skipping sample data creation.')
            ) 

#python3 manage.py reset_products