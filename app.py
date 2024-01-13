from flask import Flask, request, render_template, session, redirect, url_for, jsonify, send_file
import pandas as pd
import json
import unicodedata
from datetime import datetime
import os
import search_module  # Import module tìm kiếm

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'vqk123'  #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
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

            video_link = create_video_link(program_name, projects_info, date_str_for_url, program_type)
            video_links.append(video_link)

        output_df = pd.DataFrame({
            'STT': range(1, len(program_names) + 1),
            'Đài truyền hình': [program_type] * len(program_names),
            'Nội dung': program_names,
            'Danh mục': "",
            'video_link': video_links,
            'ngày_giờ': pd.to_datetime(datetime_list, format='%d%m%y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        })

        # Lưu dữ liệu ra file JSON
        json_output_file_path = 'data/output.json'
        data_to_save = output_df.to_dict(orient='records')

        # Đọc dữ liệu hiện có từ file JSON
        if os.path.exists(json_output_file_path):
            with open(json_output_file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = []

        # Thêm dữ liệu mới vào dữ liệu hiện có
        existing_data.extend(data_to_save)

        # Ghi tất cả dữ liệu vào file JSON
        with open(json_output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
            
        temp_output_file_path = 'temp_output.xlsx'
        output_df.to_excel(temp_output_file_path, index=False)
        
        return send_file(temp_output_file_path, as_attachment=True)
    
    return render_template('index.html')

# Định nghĩa route cho tìm kiếm
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        program_type = request.form.get('program_type')

        # Chuyển đổi chuỗi ngày thành đối tượng datetime
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        # Gọi hàm tìm kiếm với tất cả các tiêu chí
        results = search_module.search_programs(
            'data/output.json', 
            search_term=search_term, 
            start_date=start_date, 
            end_date=end_date, 
            program_type=program_type
        )
        return jsonify(results)  # Trả về kết quả dưới dạng JSON

    return render_template('search.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = validate_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password!'

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Xóa thông tin người dùng khỏi session
    session.pop('username', None)
    return redirect(url_for('login'))
# Hàm để loại bỏ dấu tiếng Việt
def validate_user(username, password):
    try:
        with open('data/user.json', 'r') as file:
            users = json.load(file).get('users', [])
            for user in users:
                if user.get('username') == username and user.get('password') == password:
                    return True
        return False
    except FileNotFoundError:
        print("File user.json not found.")
        return False
    except json.JSONDecodeError:
        print("Error decoding JSON from user.json.")
        return False

def remove_vietnamese_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

# Hàm tạo video link mới
def create_video_link(name, projects_info, date_str_for_url, program_type):
    name_no_accents = remove_vietnamese_accents(name).lower().replace(" ", "")
    for project in projects_info:
        project_name_no_accents = remove_vietnamese_accents(project['name']).lower().replace(" ", "")
        if project_name_no_accents == name_no_accents:
            if program_type == '1':  # Truyền hình
                return f"https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/VIDEO/mp4:{project['shortname']}-{date_str_for_url}.mp4/playlist.m3u8"
            elif program_type == '2':  # Phát thanh
                return f"https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/AUDIO/mp3:{project['shortname']}-{date_str_for_url}.mp3/playlist.m3u8"
    return ""
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    # Mã hóa mật khẩu ở đây trước khi lưu
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return 'User added!'

if __name__ == '__main__':
    app.run(debug=True)