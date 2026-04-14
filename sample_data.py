"""
Tạo dữ liệu mẫu danh mục cho vay — 30 khách hàng
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import io

def generate_sample_data():
    """Tạo DataFrame 30 khách hàng mẫu"""
    random.seed(42)
    np.random.seed(42)
    
    nganh_list = ['Bất động sản', 'Sản xuất', 'Thương mại', 'Nông nghiệp', 
                  'Xây dựng', 'Vận tải', 'Dịch vụ', 'Công nghệ']
    
    khu_vuc_list = ['TP.HCM', 'Hà Nội', 'Đà Nẵng', 'Bình Dương', 'Đồng Nai', 'Cần Thơ']
    
    loai_tsdb_list = ['Bất động sản', 'Máy móc thiết bị', 'Hàng tồn kho', 
                       'Tiền gửi', 'Chứng khoán', 'Phương tiện vận tải']
    
    ten_cty = [
        'Công ty CP Hoàng Anh', 'Công ty TNHH Minh Phát', 'Công ty CP Đại Việt',
        'Công ty TNHH Thành Công', 'Công ty CP An Khang', 'Công ty TNHH Phú Thịnh',
        'Công ty CP Tân Phú', 'Công ty TNHH Hòa Bình', 'Công ty CP Nam Á',
        'Công ty TNHH Bình Minh', 'Công ty CP Đông Dương', 'Công ty TNHH Quốc Việt',
        'Công ty CP Thiên Long', 'Công ty TNHH Kim Cương', 'Công ty CP Sao Mai',
        'Công ty TNHH Hưng Thịnh', 'Công ty CP Việt Tiến', 'Công ty TNHH Đại Phát',
        'Công ty CP Phương Nam', 'Công ty TNHH Trường Phát', 'Công ty CP Hải Đăng',
        'Công ty TNHH Gia Phát', 'Công ty CP Long Thành', 'Công ty TNHH Tân Á',
        'Công ty CP Việt Hưng', 'Công ty TNHH Thái Sơn', 'Công ty CP Đức Phát',
        'Công ty TNHH An Phát', 'Công ty CP Minh Quang', 'Công ty TNHH Phúc Lộc'
    ]
    
    data = []
    
    # Phân bổ nhóm nợ: 60% nhóm 1, 15% nhóm 2, 10% nhóm 3, 10% nhóm 4, 5% nhóm 5
    nhom_no_dist = [1]*18 + [2]*5 + [3]*3 + [4]*3 + [5]*1
    random.shuffle(nhom_no_dist)
    
    for i in range(30):
        nhom = nhom_no_dist[i]
        
        # Dư nợ: 5-200 tỷ
        du_no = round(random.uniform(5, 200), 1)
        
        # TSĐB phụ thuộc nhóm nợ (nhóm xấu → TSĐB thấp hơn)
        if nhom == 1:
            tsdb_ratio = random.uniform(1.2, 2.5)
        elif nhom == 2:
            tsdb_ratio = random.uniform(0.8, 1.5)
        elif nhom == 3:
            tsdb_ratio = random.uniform(0.5, 1.0)
        elif nhom == 4:
            tsdb_ratio = random.uniform(0.3, 0.7)
        else:
            tsdb_ratio = random.uniform(0.1, 0.4)
        
        tsdb = round(du_no * tsdb_ratio, 1)
        
        # Ngày quá hạn theo nhóm nợ
        if nhom == 1: ngay_qua_han = random.randint(0, 9)
        elif nhom == 2: ngay_qua_han = random.randint(10, 90)
        elif nhom == 3: ngay_qua_han = random.randint(91, 180)
        elif nhom == 4: ngay_qua_han = random.randint(181, 360)
        else: ngay_qua_han = random.randint(361, 720)
        
        # Ngày giải ngân + đáo hạn
        ngay_giai_ngan = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 700))
        ky_han_thang = random.choice([12, 24, 36, 48, 60])
        ngay_dao_han = ngay_giai_ngan + timedelta(days=ky_han_thang * 30)
        
        # Chỉ số tài chính (nhóm xấu → chỉ số yếu hơn)
        base_score = max(0, 100 - nhom * 18 + random.randint(-10, 10))
        
        de_ratio = round(random.uniform(0.5, 1.0) if nhom <= 2 else random.uniform(1.5, 4.0), 2)
        current_ratio = round(random.uniform(1.5, 3.0) if nhom <= 2 else random.uniform(0.5, 1.2), 2)
        roe = round(random.uniform(0.08, 0.25) if nhom <= 2 else random.uniform(-0.1, 0.05), 3)
        nam_hoat_dong = random.randint(1, 25)
        lich_su_tra_no = max(0, nam_hoat_dong - random.randint(0, 5))
        
        nganh = random.choice(nganh_list)
        # Tập trung BĐS nhiều hơn để có concentration risk
        if i < 10:
            nganh = random.choice(['Bất động sản', 'Bất động sản', 'Xây dựng'])
        
        data.append({
            'Mã KH': f'KH{i+1:03d}',
            'Tên KH': ten_cty[i],
            'Ngành': nganh,
            'Khu vực': random.choice(khu_vuc_list),
            'Dư nợ (tỷ)': du_no,
            'TSĐB (tỷ)': tsdb,
            'Loại TSĐB': random.choice(loai_tsdb_list),
            'Ngày giải ngân': ngay_giai_ngan.strftime('%d/%m/%Y'),
            'Ngày đáo hạn': ngay_dao_han.strftime('%d/%m/%Y'),
            'Số ngày quá hạn': ngay_qua_han,
            'Lãi suất (%)': round(random.uniform(7.5, 13.0), 1),
            'D/E': de_ratio,
            'Current Ratio': current_ratio,
            'ROE (%)': round(roe * 100, 1),
            'Năm hoạt động': nam_hoat_dong,
            'Lịch sử trả nợ (năm)': lich_su_tra_no
        })
    
    return pd.DataFrame(data)


def get_excel_template():
    """Tạo file Excel template để user download"""
    df = generate_sample_data().head(3)  # 3 dòng mẫu
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Danh mục cho vay', index=False)
    
    return output.getvalue()


def get_full_sample_excel():
    """Tạo file Excel đầy đủ 30 KH"""
    df = generate_sample_data()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Danh mục cho vay', index=False)
    
    return output.getvalue()


if __name__ == '__main__':
    df = generate_sample_data()
    print(f"Đã tạo {len(df)} khách hàng mẫu")
    print(f"\nPhân bổ nhóm nợ:")
    for nhom in range(1, 6):
        count = len(df[df['Số ngày quá hạn'].apply(
            lambda x: (nhom == 1 and x < 10) or 
                      (nhom == 2 and 10 <= x <= 90) or
                      (nhom == 3 and 91 <= x <= 180) or
                      (nhom == 4 and 181 <= x <= 360) or
                      (nhom == 5 and x > 360)
        )])
    print(f"\nDữ liệu mẫu:")
    print(df[['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 'Số ngày quá hạn']].to_string(index=False))
