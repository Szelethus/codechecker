import json
import os
import subprocess
import shlex

f=open("compile_commands.json")

data = json.load(f)

gcc_output_files = []

for entry in data:
    file_name = os.path.basename(entry['file'])
    dirname = "gcc_analysis_output"
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    gcc_output_file_path = f"{dirname}/{file_name}.json"

    command = entry['command']

    with open(gcc_output_file_path, "w") as file_name:
        analysis_command = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE, universal_newlines=True)
        output = ""
        for line in analysis_command.stderr.read().split('\n'):
            if line == '[]' or line == '[][]' or line == '':
                continue
            output = line

        file_name.write(output)
        gcc_output_files.append(gcc_output_file_path)


report_converter_command = subprocess.Popen(["/home/eumakri/Documents/codechecker/build/CodeChecker/bin/report-converter",
                                             "-t", "gcc",
                                             "-o", "gcc_analysis_output_converted"] + gcc_output_files)
