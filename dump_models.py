import subprocess

result = subprocess.run(['python', 'manage.py', 'inspectdb'], capture_output=True, text=True, encoding='utf-8')

with open('new_models_dump_utf8.py', 'w', encoding='utf-8') as f:
    f.write(result.stdout)
