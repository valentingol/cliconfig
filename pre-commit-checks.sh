# Style constants
RED='\033[0;31m'
GREEN='\033[0;32m'
WHITE='\033[0m'
BOLD=$(tput bold)
NORMAL=$(tput sgr0)

# Check output function
check_output() {
    if [ $? -ne 0 ]; then
        echo "${RED}$1 fail!\nExit${WHITE}"
        exit 1
    else
        echo "${GREEN}$1 pass${WHITE}\n"
    fi
}

# Checks
echo "**************** Typing ****************"
mypy .
check_output "Typing checks"

echo "************* Import order *************"
isort --check-only .
check_output "Import order checks"

echo "************** Docstrings **************"
pydocstyle --convention=numpy .
check_output "Docstrings checks"

echo "***************** PEP8 *****************"
flake8 .
check_output "PEP8 checks"

echo "*********** Style evaluation ***********"
score=$(pylint . | sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p')

echo "Pylint score: ${BOLD}$score/10.0${NORMAL} (details by running: pylint .)\nMinimum authorized score: 8.5\n"

echo "************** Integration tests **************"
pytest tests/integration
check_output "Integration tests"

echo "************** Unit tests **************"
pytest --cov-report term-missing --cov=./cliconfig tests/unit
check_output "Unit tests"

printf "\n${GREEN}${BOLD}All checks pass${NORMAL}${WHITE}\n\n"
