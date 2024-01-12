from flask import Flask, request, render_template, send_file
import pandas as pd
import json
import unicodedata
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_date_input = request.form['date_input']
        program_type = request.form['program_type']
        current_year_short = datetime.now().strftime('%y')
        date_str_for_url = user_date_input + current_year_short
        
        # Đọc dữ liệu từ JSON
        with open('data/project_info.json', 'r', encoding='utf-8') as json_file:
            projects_info = json.load(json_file)
        
        # Đọc dữ liệu từ form input
        lines = request.form['input_data'].splitlines()

        datetime_list = []
        program_names = []
        video_links = []

        for line in lines:
            time_part = line[:5].replace('h', ':') + ':00'
            datetime_str = f"{user_date_input}{current_year_short} {time_part}"
            datetime_list.append(datetime_str)
            
            program_name = line[5:].strip().replace(':', '')
            program_names.append(program_name)

            video_link = create_video_link(program_name, projects_info, date_str_for_url)
            video_links.append(video_link)

        output_df = pd.DataFrame({
            'STT': range(1, len(program_names) + 1),
            'Đài truyền hình': [program_type] * len(program_names),
            'Nội dung': program_names,
            'Danh mục': len(program_names),
            'video_link': video_links,
            'ngày_giờ': pd.to_datetime(datetime_list, format='%d%m%y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        })
        
        temp_output_file_path = 'temp_output.xlsx'
        output_df.to_excel(temp_output_file_path, index=False)
        
        return send_file(temp_output_file_path, as_attachment=True)
    
    return render_template('index.html')

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

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
