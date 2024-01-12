import json
import unicodedata
import pandas as pd
from datetime import datetime

# Đọc tệp tin JSON chứa thông tin về các dự án
json_file_path = 'data/project_info.json'
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    projects_info = json.load(json_file)

# Hàm để loại bỏ dấu tiếng Việt
def remove_vietnamese_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

# Hàm tạo video link mới
def create_video_link(name, projects_info, date_str_for_url):
    name_no_accents = remove_vietnamese_accents(name).lower().replace(" ", "")
    for project in projects_info:
        project_name_no_accents = remove_vietnamese_accents(project['name']).lower().replace(" ", "")
        if project_name_no_accents == name_no_accents:
            return f"https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/VIDEO/mp4:{project['shortname']}-{date_str_for_url}.mp4/playlist.m3u8"
    return ""

# Đường dẫn tới tệp tin txt đã được tải lên
input_txt_path = 'data/input'

# Đường dẫn tới tệp tin Excel output
output_file_path = 'data/output.xlsx'

# Nhận ngày và tháng từ người dùng
user_date_input = input("Vui lòng nhập ngày và tháng (định dạng DDMM): ")
current_year_short = datetime.now().strftime('%y') # Lấy 2 chữ số cuối của năm hiện tại
user_date_str_for_url = user_date_input + current_year_short # Chuỗi ngày dạng ddmmyy cho URL

current_year_full = datetime.now().strftime('%Y') # Lấy năm đầy đủ
user_date_str_for_datetime = user_date_input + current_year_full # Chuỗi ngày dạng ddmmyyyy cho DataFrame

# Đọc tệp tin txt và xử lý dữ liệu
try:
    with open(input_txt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    datetime_list = []
    program_names = []
    video_links = []

    for line in lines:
        # Lấy giờ từ 5 ký tự đầu tiên của mỗi dòng và thay 'h' bằng ':'
        time_part = line[:5].replace('h', ':') + ':00'
        # Tạo chuỗi ngày giờ cho DataFrame
        datetime_str = f"{user_date_str_for_datetime} {time_part}"
        datetime_list.append(datetime_str)
        
        # Lấy tên chương trình từ phần còn lại của mỗi dòng và loại bỏ ':'
        program_name = line[5:].strip().replace(':', '')
        program_names.append(program_name)

        # Tạo video link mới dựa trên tên chương trình và ngày nhập từ người dùng
        video_link = create_video_link(program_name, projects_info, user_date_str_for_url)
        video_links.append(video_link)

    # Tạo DataFrame
    output_df = pd.DataFrame({
        'STT': range(1, len(program_names) + 1),
        'Đài truyền hình': [1] * len(program_names),
        'Nội dung': program_names,
        'Danh mục': ['truyền hình'] * len(program_names),
        'video_link': video_links,
        'ngày_giờ': pd.to_datetime(datetime_list, format='%d%m%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    })

    # Ghi ra tệp Excel
    output_df.to_excel(output_file_path, index=False)
    print("Tệp tin output.xlsx đã được tạo thành công.")
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")