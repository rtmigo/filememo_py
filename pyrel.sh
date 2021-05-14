# SPDX-FileCopyrightText: (c) 2021 Art Galkin <ortemeo@gmail.com>
# SPDX-License-Identifier: BSD-3-Clause
# See https://github.com/rtmigo/pyrel#pyrel

set -e

TWINE_CHECK=true # should we call `twine check` from `pyrel_test_begin`?
TWINE_CHECK_STRICT=true # works only if TWINE_CHECK is true

####################################################################################################

# without the `realpath` we cannot get the real project directory, so we start with it

function realpath() {
  # emulating realpath for MacOS (10.14 does not have it @2021)
  # refactored code from https://stackoverflow.com/a/18443300
  local original_pwd
  original_pwd=$PWD
  cd "$(dirname "$1")"
  local current_link
  current_link=$(readlink "$(basename "$1")")
  while [ "$current_link" ]; do
    cd "$(dirname "$current_link")"
    current_link=$(readlink "$(basename "$1")")
  done
  local result
  result="$PWD/$(basename "$1")"
  cd "$original_pwd"
  echo "$result"
}

####################################################################################################

if [ ! -f "./setup.py" ]; then
  echo "./setup.py not found. Please run the script python project directory"
  exit 1
fi

echo "OK, we're in the project root"

project_root_dir=$(realpath .)

####################################################################################################

TWINE_CHECK_STRICT=true=true # useful ?

log() { printf '%s\n' "$*"; }
error() { log "ERROR: $*" >&2; }
fatal() { error "$@"; exit 1; }
header() {
  echo
  echo "================================================================================"
  echo "  $1"
  echo "================================================================================"
  echo
}

####################################################################################################

DEFAULT_TRAP_COMMAND="header EXITING"

function trap_add() {
    # slightly modified https://stackoverflow.com/a/30650385
    #
    # Sample:
    #   set -e
    #   trap_add 'echo "in trap A"' EXIT
    #   trap_add 'echo "in trap B"' EXIT
    #   echo "before error"
    #   run_bad_command
    #   echo "after error"
    # Output:
    #   before error
    #   in trap A
    #   in trap B

    [ -z "${DEFAULT_TRAP_COMMAND}" ] && DEFAULT_TRAP_COMMAND="echo Exiting @ $(date)"

    local trap_add_cmd
    local new_cmd
    local trap_add_name
    local existing_cmd

    trap_add_cmd=$1; shift || fatal "${FUNCNAME[0]} usage error"

    new_cmd=
    for trap_add_name in "$@"; do
        # Grab the currently defined trap commands for this trap
        existing_cmd=$(trap -p "${trap_add_name}" |  awk -F"'" '{print $2}')

        # Define default command
        [ -z "${existing_cmd}" ] && existing_cmd="$DEFAULT_TRAP_COMMAND"

        # Generate the new command
        new_cmd="${existing_cmd};${trap_add_cmd}"

        # Assign the test
        # shellcheck disable=SC2064
        trap "${new_cmd}" "${trap_add_name}" || \
          fatal "unable to add to trap ${trap_add_name}"
    done
}

####################################################################################################

function pyrel_venv_begin() {

  log PYREL_VENV_BEGIN

  if [ -n "$temp_venv_dir" ]; then
    fatal "Nesting venvs is not supported"
  fi

  temp_venv_dir=$(mktemp -d -t venv-XXXXXXX)
  log pyrel_venv_begin: creating "$temp_venv_dir"
  python3 -m venv "$temp_venv_dir"
  # shellcheck disable=SC1090
  source "$temp_venv_dir/bin/activate"

  # inserting trap before other cleanup to handle nested venvs
  trap_add "set +e && pyrel_venv_end && set -e" EXIT
}

function pyrel_venv_end() {

  if [ -z "$temp_venv_dir" ]; then
    log pyrel_venv_end: ok: "temp_venv_dir is undefined"
    return
  fi

  if [ -d "$temp_venv_dir" ]; then
    log pyrel_venv_end: removing "$temp_venv_dir"
    deactivate
    python3 -m venv "$temp_venv_dir" --clear
    rm -rf "$temp_venv_dir"
    log pyrel_venv_end: removed "$temp_venv_dir"
  else
    log pyrel_venv_end: ok: temp venv dir "$temp_venv_dir" does not exist.
  fi

  temp_venv_dir=""
}

####################################################################################################

function build_package() {
  cd "$project_root_dir" || return 1
  python3 -m pip install --upgrade pip
  pip3 install setuptools wheel twine --force-reinstall
  python3 setup.py sdist bdist_wheel
}

function check_package() {
  if [ $TWINE_CHECK = true ]; then
    cd "$project_root_dir" || return 1
    if [ $TWINE_CHECK_STRICT = true ]; then
      twine check ./dist/* --strict
    else
      twine check ./dist/*
    fi
  fi
}

function find_latest_file() {
  # usage: find_latest_file *.txt
  local file
  local latest_file
  for file in $1; do
    [[ $file -nt latest_file ]] && latest_file=$file
  done
  echo "$latest_file"
}

function install_package_from_latest_whl() {
  local latest_whl_file
  latest_whl_file=$(find_latest_file "$project_root_dir"/dist/*.whl)
  pip3 install --upgrade pip
  pip3 install "$latest_whl_file" --force-reinstall
}

function cd_project() {
  cd "$project_root_dir" || fatal "Failed to CD to the project dir"
}

function rmdir_with_msg() {
  log "Removing $1"
  # shellcheck disable=SC2086
  rm -rf "$1" #{1}
}

function if_dir_unexisting_remove_on_exit() {
    if ! compgen -G "$1" > /dev/null ; then
      # directory does not exist now, so if we create it, we'll remove it
      log "WILL REMOVE $1 on exit"
      trap_add "rmdir_with_msg $1" EXIT
    else
      log "WILL NOT REMOVE $1 on exit"
    fi
}

function pyrel_test_begin() {

  # we will optionally remove dist, build and egg_info from the project dir
  # if there weren't there before the test

  if_dir_unexisting_remove_on_exit "$project_root_dir/dist"
  if_dir_unexisting_remove_on_exit "$project_root_dir/build"
  if_dir_unexisting_remove_on_exit "$project_root_dir/*.egg-info"

  header "BUILDING PACKAGE"
  pyrel_venv_begin

  cd_project
  python3 -m pip install --upgrade pip
  build_package
  check_package
  pyrel_venv_end

  header "INSTALLING PACKAGE"
  pyrel_venv_begin
  install_package_from_latest_whl

  # move from the current directory to random one
  nowhere_dir=$(mktemp -d -t ci-XXXXXXXXXX)
  cd "$nowhere_dir" || return 1
  trap_add "rmdir_with_msg $nowhere_dir" EXIT

  header "START OF USER COMMANDS BLOCK (after pyrel_test_begin)"
}

function pyrel_test_end() {

  header "END OF OF USER COMMANDS BLOCK (pyrel_test_end)"

  # Python 3.7 sometimes fails when trying to --clear venv while the current
  # directory is created by mktemp. That's why we move to the project before
  # ending the venv
  cd_project
  pyrel_venv_end

  echo "All done."
}
