# AUTO DEV SETUP

# check if rye is installed
if ! command -v rye &> /dev/null
then
    echo "rye could not be found"
    echo "Would you like to install via rye or pip? Enter 'rye' or 'pip':"
    read install_method
    clear

    if [ "$install_method" = "rye" ]
    then
        echo "Installing via rye now ..."
        curl -sSf https://rye-up.com/get | bash
        echo "Check the rye docs for more info: https://rye-up.com/"
        source "$HOME/.rye/env"

        echo "SYNC: setup .venv"
        rye sync

        clear

        echo "Run `source \"$HOME/.rye/env\"` and then `rye shell` to activate the virtual environment"


    elif [ "$install_method" = "pip" ]
    then
        echo "Installing via pip now ..."
        if command -v python &> /dev/null
        then
            python -m venv .venv
        else
            python3 -m venv .venv
        fi
        .venv/bin/python -m pip install -e .
        .venv/bin/python -m pip install -r requirements-dev.lock
        
        clear
        
        echo "Run 'source .venv/bin/activate' to activate the virtual environment"
    else
        echo "Invalid option. Please run the script again and enter 'rye' or 'pip'."
        exit 1
    fi
fi

echo "Try 'python examples/simple_chatbot.py' to test your setup."
