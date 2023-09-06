REQUIREMENTS='./requeriments.txt' # Sic.
echo "Setting up virtual environment (venv)" 1>&2
python -m venv venv
echo "Activating (venv)" 1>&2
source ./venv/bin/activate
echo "Installing modules in $REQUIREMENTS" 1>&2
pip install -r $REQUIREMENTS
echo "Deactivating (venv)" 1>&2
deactivate
echo 'Use 'source $PWD/venv/bin/activate' to reactivate (venv), or use autovenv.' 1>&2

