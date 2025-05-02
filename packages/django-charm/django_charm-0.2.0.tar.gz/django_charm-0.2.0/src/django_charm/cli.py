import argparse
import subprocess
import os
import multiprocessing as mp
import sys

def main():
    parser = argparse.ArgumentParser(description="Create Django Project")
    parser.add_argument("-p", type=str, help="project")
    parser.add_argument("-a", type=str, help="app")
    parser.add_argument("--createproject", type=str, help="create-project")
    parser.add_argument("--createapp", type=str, help="create app")

    args = parser.parse_args()
    if args.createproject:
        args.createproject = args.createproject
        if args.createproject is None:
            args.createproject = input("Enter project name: ")

        # command = f"django-admin startproject "
        if args.createproject:
            process = subprocess.Popen([sys.executable, "-m", "django", "startproject", args.createproject],
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # print(f"Command: {command}")
            if stdout:
                print(f"Output:\n{stdout.decode()}")
            if stderr:
                print(f"Errors:\n{stderr.decode()}")

            if process.returncode == 0:
                if args.a is None:
                    args.a = input("Enter app name: ")

                process = subprocess.Popen(
                    [sys.executable, "manage.py", "startapp", args.a],
                    # shell=True,
                    cwd=args.createproject,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )
                stdout, stderr = process.communicate()

                if stderr:
                    print(f"Errors:\n{stderr.decode()}")

                settings_path = os.path.join(args.createproject, args.createproject, "settings.py")

                print("Setting Path: ", settings_path)
                abs_path = os.path.abspath(settings_path)

                print("Full path: ", abs_path)

                add_app_to_installed_apps(args.a, settings_path=settings_path)
                urls_path = os.path.join(args.createproject, args.createproject, "urls.py")
                add_app_to_urls(args.a, urls_path)
                app_path = os.path.join(args.createproject, args.a, )
                create_index_template(app_path, args.a)
                create_views_file(app_path, args.a)
                create_or_update_app_urls(app_path)

    args = parser.parse_args()
    if args.createapp:
        args.a = args.createapp

        if args.p is None:
            args.p = input("Enter parent project: ")

        process = subprocess.Popen(
            [sys.executable, "manage.py", "startapp", args.a],
            # shell=True,
            cwd=args.p,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if stderr:
            print(f"Errors:\n{stderr.decode()}")

        settings_path = os.path.join(args.p, args.p, "settings.py")

        print("Setting Path: ", settings_path)
        abs_path = os.path.abspath(settings_path)

        print("Full path: ", abs_path)

        add_app_to_installed_apps(args.a, settings_path=settings_path)
        urls_path = os.path.join(args.p, args.p, "urls.py")
        add_app_to_urls(args.a, urls_path)
        app_path = os.path.join(args.p, args.a, )
        create_index_template(app_path, args.a)
        create_views_file(app_path, args.a)
        create_or_update_app_urls(app_path)



def create_index_template(app_path, app_name):
    templates_dir = os.path.join(app_path, 'templates', app_name)
    print("Templates_dir:", templates_dir)
    print("Templates_dir_app_name:", app_path)

    os.makedirs(templates_dir, exist_ok=True)

    index_path = os.path.join(templates_dir, 'index.html')

    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Upload Form</title>
</head>
<body>
<h1>Welcome To Django Charm</h1>

<form method="POST" enctype="multipart/form-data">
    {% csrf_token %}



    <label for="text_input">Text input:</label><br>
    <input type="text" name="text_input"><br><br>

    <label for="dropdown">Choose an option:</label><br>
    <select name="dropdown">
        <option value="option1">Option1</option>
        <option value="option2">Option2</option>
    </select><br><br>
    <label for="file">Choose a file:</label><br>
    <input type="file" name="file"><br><br>

    <button type="submit">Submit</button>
</form>

</body>
</html>
'''
    with open(index_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Created index.html at: {index_path}")


def create_views_file(app_path, app_name):
    views_path = os.path.join(app_path, 'views.py')

    view_code = f'''

from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        text_input = request.POST.get("text_input")
        dropdown = request.POST.get("dropdown")

        # Debug: log the inputs
        print("Uploaded File:", uploaded_file)
        print("Text Input:", text_input)
        print("Dropdown Selection:", dropdown)

        return HttpResponse("Form submitted successfully!")

    return render(request, "{app_name}/index.html")
'''

    # If views.py exists, append the function if not already defined
    if os.path.exists(views_path):
        with open(views_path, 'r') as f:
            existing_code = f.read()

        if "def index(" in existing_code:
            print("✅ views.py already has an 'index' view — skipping adding it again.")
        else:
            with open(views_path, 'a') as f:
                f.write(view_code)
            print(f"✅ Appended 'index' view to existing views.py at: {views_path}")
    else:
        with open(views_path, 'w') as f:
            f.write('from django.shortcuts import render\nfrom django.http import HttpResponse\n' + view_code)
        print(f"✅ Created new views.py with 'index' view at: {views_path}")


def create_or_update_app_urls(app_name):
    urls_path = os.path.join(app_name, 'urls.py')

    import_lines = [
        'from django.urls import path\n',
        'from . import views\n'
    ]
    url_pattern_line = "    path('', views.index, name='views_template_urls'),\n"

    if not os.path.exists(urls_path):
        # Create a fresh urls.py with everything
        with open(urls_path, 'w') as f:
            f.writelines(import_lines)
            f.write('\nurlpatterns = [\n')
            f.write(url_pattern_line)
            f.write(']\n')
        print(f"✅ Created new {urls_path} with view path.")
        return

    # If file exists, read its content
    with open(urls_path, 'r') as f:
        lines = f.readlines()

    # Check and add missing imports
    if not any('from django.urls import path' in line for line in lines):
        lines.insert(0, 'from django.urls import path\n')
    if not any('from . import views' in line for line in lines):
        insert_pos = 1 if lines[0].startswith('from django') else 0
        lines.insert(insert_pos, 'from . import views\n')

    # Check if urlpatterns exists
    if not any('urlpatterns' in line for line in lines):
        lines.append('\nurlpatterns = [\n')
        lines.append(url_pattern_line)
        lines.append(']\n')
    else:
        # Insert the path line if it doesn't exist
        if not any('views.index' in line for line in lines):
            for i, line in enumerate(lines):
                if 'urlpatterns' in line:
                    # Insert just after the opening bracket line
                    for j in range(i, len(lines)):
                        if '[' in lines[j]:
                            lines.insert(j + 1, url_pattern_line)
                            break
                    break

    # Write the modified content back
    with open(urls_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ Updated {urls_path} with index view route.")


def add_app_to_urls(app_name, urls_path):
    if not os.path.exists(urls_path):
        print(f"{urls_path} not found.")
        return

    with open(urls_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    include_fixed = False
    app_already_included = any(
        f"include('{app_name}.urls')" in line or f'include("{app_name}.urls")' in line
        for line in lines
    )

    for line in lines:
        # Fix the import line if it exists
        if line.startswith('from django.urls') and 'path' in line:
            if 'include' not in line:
                line = line.strip().rstrip() + ', include\n'
            include_fixed = True
        updated_lines.append(line)

    # If include wasn't imported at all, add a new line
    if not include_fixed:
        # Add after the first django import to keep it organized
        insert_index = 0
        for i, line in enumerate(updated_lines):
            if line.startswith('from django.urls'):
                insert_index = i + 1
                break
        updated_lines.insert(insert_index, 'from django.urls import include\n')

    # Add the app's path only if it's not already included
    if not app_already_included:
        for i, line in enumerate(updated_lines):
            if 'urlpatterns' in line:
                for j in range(i, len(updated_lines)):
                    if ']' in updated_lines[j]:
                        new_path_line = f"    path('', include('{app_name}.urls')),\n"
                        updated_lines.insert(j, new_path_line)
                        print(f"✅ Added path for '{app_name}'")
                        break
                break
    else:
        print(f"'{app_name}' is already included in urlpatterns.")

    with open(urls_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"✅ Ensured 'include' is imported and '{app_name}' is registered in {urls_path}")


def add_app_to_installed_apps(app_name, settings_path):
    with open(settings_path, 'r') as file:
        lines = file.readlines()

    installed_apps_start = None
    installed_apps_end = None

    for i, line in enumerate(lines):
        if 'INSTALLED_APPS' in line and '=' in line:
            installed_apps_start = i
            break

    if installed_apps_start is None:
        print("INSTALLED_APPS not found.")
        return

    for j in range(installed_apps_start, len(lines)):
        if ']' in lines[j]:
            installed_apps_end = j
            break

    if installed_apps_end is None:
        print("Couldn't find the end of INSTALLED_APPS.")
        return

    #  if app is already added
    for line in lines[installed_apps_start:installed_apps_end + 1]:
        if f"'{app_name}'" in line:
            print(f"{app_name} already in INSTALLED_APPS.")
            return

    indent = ' ' * 4  # Adjust if your indent is different
    lines.insert(installed_apps_end, f"{indent}'{app_name}',\n")

    with open(settings_path, 'w') as file:
        file.writelines(lines)

    print(f"Added '{app_name}' to INSTALLED_APPS.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
