import json
import os
import subprocess
import shlex

f=open("compile_commands.json")

data = json.load(f)

gcc_output_files = []

gcc_output_dirname = os.getcwd() + '/' + "gcc_analysis_output"
if not os.path.exists(gcc_output_dirname):
    os.mkdir(gcc_output_dirname)
    print(f"created {gcc_output_dirname}.")

for entry in data:
    relative_file_name = os.path.basename(entry['file'])
    absolute_file_name = entry['directory'] + '/' + relative_file_name

    gcc_output_file_path = f"{gcc_output_dirname}/{relative_file_name}.json"

    command = entry['command']

    with open(gcc_output_file_path, "w") as gcc_output_file_stream:
        analysis_command = shlex.split(command) + ["-fanalyzer", "-fdiagnostics-format=json"]

        for idx, arg in enumerate(analysis_command):
            if arg == relative_file_name:
                analysis_command[idx] = absolute_file_name
                break
        print(shlex.join(analysis_command))

        proc = subprocess.Popen(analysis_command, stderr=subprocess.PIPE, universal_newlines=True, cwd=entry['directory'])
        output = ""
        for line in proc.stderr.read().split('\n'):
            if line == '[]' or line == '[][]' or line == '':
                continue
            if line.startswith('distcc'):
                continue
            output = line
            break

        gcc_output_file_stream.write(output)
        gcc_output_files.append(gcc_output_file_path)


report_converter_command = subprocess.Popen(["/home/eumakri/Documents/codechecker/build/CodeChecker/bin/report-converter",
                                             "-t", "gcc",
                                             "-o", "gcc_analysis_output_converted"] + gcc_output_files)
