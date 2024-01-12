import json
from datetime import datetime
def search_programs(filename, search_term=None, start_date=None, end_date=None, program_type=None):
    try:
        with open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        results = []
        for program in data:
            # Kiểm tra tên chương trình
            if search_term and search_term.lower() not in program['Nội dung'].lower():
                continue

            # Kiểm tra ngày giờ
            program_date = datetime.strptime(program['ngày_giờ'], "%Y-%m-%d %H:%M:%S")
            if start_date and program_date < start_date:
                continue
            if end_date and program_date > end_date:
                continue

            # Kiểm tra thể loại
            if program_type and program_type != program['Đài truyền hình']:
                continue

            results.append(program)

        return results
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []