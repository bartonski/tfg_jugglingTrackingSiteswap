REQUIREMENTS='./requeriments.txt' # Sic.
if [ ! -z "$USER" ]; then
    echo "Setting up user paths for $USER." 1>&2
    mkdir -p "users/$USER/dataset/tanda2"
    mkdir -p "users/$USER/results/{videos,excels,mot16}"
    mkdir -p "users/$USER/results/excels/{Tracking,GroundTruth}"
    mkdir -p "users/$USER/results/mot16/{Tracking,GroundTruth/Otros}"
    mkdir -p "users/$USER/results/mot16/Otros/{Optimizer_dist,Optimizer}"
    mkdir -p "users/$USER/results/mot16/Otros/Optimizer_bg_substraction"
    mkdir -p "users/$USER/results/mot16/Otros/Optimizer_Kalman"
fi
echo "Setting up virtual environment (venv)" 1>&2
python -m venv venv
echo "Activating (venv)" 1>&2
source ./venv/bin/activate
echo "Installing modules in $REQUIREMENTS" 1>&2
pip install -r $REQUIREMENTS
echo "Deactivating (venv)" 1>&2
deactivate
echo 'Use 'source $PWD/venv/bin/activate' to reactivate (venv), or use autovenv.' 1>&2

