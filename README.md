# covid-simulation

See [User Guide](https://docs.google.com/document/d/1BJ20ObMTkT_6IOGaUBeb0f9BCu6WbMSWnlLHDlYDGsg/edit?usp=sharing) for more information

### Instructions
1. Clone or download repository
1. Populate input spreadsheet with relevant parameter values `Simulator - Test Sheet.csv`
1. Run the following command in terminal to convert csv to a json file for the Neher Lab simulator
* `python neher-lab/neherlab_inputs.py`
1. Get results from Neher Lab simulator
* Go to https://covid19-scenarios.org/
* Click “Load,” and upload the json file `neher-lab/[country name].json`
* When the simulator finishes running automatically, export the results `c19s.results.summary.tsv`
1. Run centralizing script
1. Open the jupyter notebook `main.ipynb` in the main folder of covid-simulation
1. Run each cell to generate predictions and visualizations of each model
