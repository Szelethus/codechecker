#!/bin/bash

trap '
  trap - INT # restore default INT handler
  kill -s INT "$$"
' INT

print_usage() {
    cat >&2 <<_END_
Analyze a project with CodeChecker.

Usage: $0 -h
       $0 -o output_dir -c clang_bin_dir compile_commands.json

Options:
    -h             This help message.

    -o output dir  Location of the compile_commands.json file

    -c output dir  Location of the clang executable
_END_
}

usage_error() {
    echo "ERROR!"
    print_usage
    exit 2
}

get_source_file() {
    local filename="$1"

    if [ -n "$output_dir" -a -e "${output_dir}/${filename}" ]; then
        echo "${output_dir}/${filename}"
    else
        echo "${script_dir}/${filename}"
    fi
}

run_codechecker() {
  get_options_for_uninit_object $1
  saargs_file=saargs_$1.txt
  output_file=output_$1.txt
  echo $saargs_string > $saargs_file
  CodeChecker analyze --analyzers clangsa --saargs $saargs_file $compile_commands_json -o $output_dir -e optin.cplusplus.UninitializedObject --verbose debug_analyzer &> $output_file
  CodeChecker store $output_dir -n \"$2", UninitObject with "$1\"
}

get_options_for_uninit_object() {
  saargs_string="-Xclang -analyzer-config-compatibility-mode=false "
  for option in $1; do
      saargs_string=$saargs_string"-Xclang -analyzer-config -Xclang optin.cplusplus.UninitializedObject:"$option"=true "
  done
}

# -------- Main body --------

output_dir=
while getopts ":c:u:o::p:" Option; do
    case $Option in
    h)
        print_usage
        exit
        ;;
    o)
        output_dir="$OPTARG"
        ;;
    c)
        clang_bin_dir="$OPTARG"
        ;;
    p)
        project_name="$OPTARG"
        ;;
    *)
        usage_error
        ;;
    esac
done

shift $(($OPTIND - 1))

compile_commands_json="$1"

shift $(($OPTIND - 1))

# Verify input
if [ -z "$compile_commands_json" ]; then
    echo "COMPILE COMMANDS DOESNT EXIST!"
    usage_error
fi

if [ -z "$output_dir" ]; then
    echo "OUTPUT DIR DOESNT EXIST!"
    usage_error
fi

if [ -z "$clang_bin_dir" ]; then
    echo "CLANG EXECUTABLE DOESNT EXIST!"
    usage_error
fi

if [ "$project_name" == "" ]; then
    echo "EMPTY PROJECT NAME"
    usage_error
fi

# Check clang version
clang_version="$clang_bin_dir/clang --version"

eval $clang_version | grep -E "9\.0\.0"

if [ $? -ne 0 ]; then
    echo "CLANG 9 RELEASE REQUIRED"
    usage_error
fi

# Check whether the checker is present
clang_version="$clang_bin_dir/clang -cc1 -analyzer-checker-help"

eval $clang_version | grep -E "optin\.cplusplus\.UninitializedObject"

if [ $? -ne 0 ]; then
    echo "CHECKER ISNT PRESENT"
    usage_error
fi

# Add it to the PATH
export PATH=$clang_bin_dir:$PATH

# Check whether the server is up
CodeChecker server --list | grep 8001

if [ $? -ne 0 ]; then
    echo "CC SERVER ISNT RUNNING!"
    usage_error
fi

run_codechecker "Pedantic" $project_name
run_codechecker "CheckPointeeInitialization" $project_name

exit $error
