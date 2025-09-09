#!/usr/bin/env bash

# ------------------------- EDIT BELOW AS NEEDED -------------------------

function show_help() {
    echo "Description:"
    echo "  This is a template script for bash scripts. Use this as a starting point for your scripts."
    echo
    echo "Usage: path/to/$(basename $0) [args] [options]" # Keep as it is
    echo
    echo "Arguments:"
    echo "  <dest_dir>              Destination directory to generate template"
    echo
    echo "Options:"
    echo "  -h, --help              Show this help message and exit" # Keep as it is
    echo "  -v, --verbose           Enable verbose mode"
    echo "  --version=<version>     Set the version of Python to install (default: 3.10)"
    echo "  --requirements=<file>    Path to the requirements file (default: requirements.txt)"
    echo
}

MIN_ARGS=0 # Minimum number of arguments
MAX_ARGS=0 # Maximum number of arguments
OPTIONS=("-v=false" "--verbose=false") # Options dictionary with boolean values. Set all to false initially. Exclude -h and --help
SETTER_OPTIONS=("--version=3.10" "--requirements=requirements.txt") # Options array. Set all default values here
TRAP_ERROR=true # Whether to trap any interior error occured, print stack and kill the whole process. Set to false with CAUTION
TELEGRAM_NOTIFICATION=false # Whether to send a telegram notification on trap


function main() {

  VERSION=$(setter_option "--version")
  REQUIREMENTS_FILE=$(setter_option "--requirements")
  REQUIREMENTS_FILE=$(realpath $REQUIREMENTS_FILE)
  if [[ ! -f $REQUIREMENTS_FILE ]]; then
    exit_with_code_and_message 1 "Requirements file not found: $REQUIREMENTS_FILE"
  fi

  # If any virtual environment exists, warn and ask to delete

  if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. (Location: $(realpath ".venv"))\nDelete .venv and recreate? (y/n)"
    read -r response
    if [[ $response == "y" ]]; then
      rm -rf .venv
    else
      exit_with_code_and_message 1 "Virtual environment already exists. Exiting..."
    fi
  fi


  # Check if python version is installed on system for Mac and Linux
  if [[ $(uname) == "Darwin" ]]; then
    if [[ ! $(brew list | grep python@${VERSION}) ]]; then
      print_warning "Python $VERSION not found on system. Install using: brew install python@${VERSION}? (y/n)"
      read -r response
      if [[ $response == "y" ]]; then
        brew install python@${VERSION}
      else
        exit_with_code_and_message 1 "Python $VERSION not found on system. Exiting..."
      fi
    else
      print_info "Using Python $VERSION installed at $(brew --prefix)/opt/python@${VERSION}" 
    fi
  elif [[ $(uname) == "Linux" ]]; then
    if [[ ! $(which python${VERSION}) ]]; then
      print_warning "Python $VERSION not found on system. Install using: sudo apt-get install python${VERSION}? (y/n)"
      read -r response
      if [[ $response == "y" ]]; then
        # Search for repository, if not found add it
        if [[ ! $(apt-cache search python${VERSION}) ]]; then
          print_warning "Python $VERSION not found in repository. Add repository: ppa:deadsnakes/ppa? (y/n)"
          read -r response
          if [[ $response == "y" ]]; then
            sudo add-apt-repository ppa:deadsnakes/ppa
            sudo apt-get update
          else
            exit_with_code_and_message 1 "Python $VERSION not found in repository. Exiting..."
          fi
        fi
        sudo apt-get install python${VERSION}
      else
        exit_with_code_and_message 1 "Python $VERSION not found on system. Exiting..."
      fi
    else
      print_info "Using Python $VERSION found in $(which python${VERSION})"
    fi
  else
    exit_with_code_and_message 1 "Unsupported OS. Use Mac or Linux only."
  fi
    
  # Create a virtual environment
  python${VERSION} -m venv "$(dirname $0)/.venv"
  source "$(dirname $0)/.venv/bin/activate"
  print_success "Python $VERSION venv created"

  # Install requirements
  echo "Installing requirements..."
  pip install -r $REQUIREMENTS_FILE
  print_success "Requirements installed successfully."

  print_success "Setup Successful. Python $VERSION venv created. Path: $(realpath $(dirname $0))/.venv"

}

# Add all cleanup functionality here
function cleanup { 
    : # Add cleanup code here
}
function on_error_cleanup { 
    : # Add additional trap code here
}


# ========================================================================


# ------------- DO NOT EDIT BELOW THIS POINT UNLESS NECESSARY -------------

ARGS=() # Arguments array

# Check if nnmavsh_helpers.sh is in the PATH and seeable
nnmavsh_helpers_path=$(which nnmavsh_helpers.sh)
if [[ ! -f $nnmavsh_helpers_path ]]; then
    echo -e "\033[0;31m[ERROR][$(basename $0)]: nnmavsh_helpers.sh not found\033[0m"
    echo "Ensure that nnmavsh is installed and its scripts have execute permissions"
    echo
    echo "Troubleshooting:"
    echo "  1. Make sure nnmavsh is installed correctly"
    echo "      Installation: "
    echo "        mkdir -p ~/Dev/lib/"
    echo "        cd ~/Dev/lib/"
    echo "        git clone git@github.com:nnmav/nnmavsh.git nnmavsh"
    echo "        sudo chmod +x ./nnmavsh/install_nnmavsh.sh"
    echo "        ./nnmavsh/install_nnmavsh.sh"
    echo "  2. If installed make sure every file in nnmavsh is executable:"
    echo "      chmod +x ~/Dev/lib/nnmav/nnmavsh/src/*.sh"
    echo
    exit 1
else
    source $nnmavsh_helpers_path > /dev/null
fi

# Detect the shell type
SHELL_TYPE=$(ps -p $$ -o comm= | sed 's/^[^a-zA-Z0-9]*//')

# Set options for both bash and zsh
if [ -n "${BASH_VERSION:-}" ]; then
    ORIGINAL_OPTS=$(set +o) # Save the original shell options
    enable_bash_error_opts # From nnmavsh_helpers.sh
elif [ -n "${ZSH_VERSION:-}" ];  then
    ORIGINAL_OPTS=$(setopt)
    setopt ERR_EXIT
    setopt NO_UNSET
    setopt PIPE_FAIL
    setopt ERR_TRAP
    setopt DEBUG_FUNCTIONS
else
    echo "Unsupported shell type. Use in Bash or Zsh only."
    exit 1
fi


function _cleanup() {
  cleanup
  eval $ORIGINAL_OPTS # Reset the shell options
}

function _notify_telegram_trap_bot() {
  if [[ $TELEGRAM_NOTIFICATION == true ]]; then
    local message=$1
    send_telegram_notification "5691340373" "6593194111:AAG9RjOsBkWyt28lObzl4Mzmte9uTwD4ipk" "$message"
  fi  
}

# Trap the script
trap 'on_exit $LINENO $?; _notify_telegram_trap_bot; _cleanup' EXIT INT TERM
if [[ $TRAP_ERROR == true ]]; then
    trap 'on_error $LINENO $?; _notify_telegram_trap_bot; on_error_cleanup;' ERR
fi

# Main script
check_help "$@" # Check if -h or --help is present
parse_args "$@"
main "$@"

# =========================================================================