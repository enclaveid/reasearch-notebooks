# enclave-llm

This respository contains the backend code to score psychometrics.

## Installation

- Create and enter to a conda env:

```
conda create -n enclaveid python=3.11 -y
conda activate enclaveid
```

- Install requirements

```
pip install -r requirements.txt
```

## Usage

- Create a `.env` file in the root directory and set your `OPENAI_API_KEY` in it.
- Run the following command to score data either `weekly`, `monthly`, `annually`, or for a `lifetime` period:

```bash
python enclaveid/cli.py -d [root/directory/path] -p [period] -t [conversations/searches]
```

The code will score the data based on the specified period. Below is an example of the output log:

```bash
INFO:__main__:The data in the data directory provided has as the oldest date: 2021-11-27 00:00:00 and as the newest date: 2023-11-15 00:00:00. In total we loaded 593 data items.
INFO:__main__:Processing 593 data items corresponding to the period from 2021-11-27 00:00:00 to 2023-11-15 00:00:00
INFO:core:Split large data items into smaller items
INFO:core:Went from 593 items to 593 items. All of them below a maximum token theshold of 3076
INFO:core:We compressed 593 data items into 15 chunks of data with a maximum size of 3076 tokens.
INFO:core:Classify 15 total chunks of data
INFO:core:Remove low classified chunks
INFO:core:Only 2 out of 15 chunks have at least one trait classified as high.
INFO:core:Scoring 2 high-classified chunks.
INFO:__main__:Obtained score: {'openness': 0.7, 'conscientiousness': 0.6, 'extraversion': 0.75, 'agreeableness': 0.75, 'neuroticism': 0.4}
INFO:__main__:Processed 593 items of data in total.
INFO:__main__:Final score: {'openness': 0.7, 'conscientiousness': 0.6, 'extraversion': 0.75, 'agreeableness': 0.75, 'neuroticism': 0.4} for the period from 2021-11-27 00:00:00 to 2023-11-15 00:00:00.
INFO:__main__:Total cost: 0.2591
```

It will also save the final score, period scores, and intermediate classification results in files located either in the default folder `enclaveid_llm_output/` or in a directory specified through the `save_path` flag option.

> NOTE: The file 'latest.json' contains the average score for all periods and is updated after each run. For example, if you evaluate a set of data for the first time, 'latest.json' will contain the final score, as it was just created. If you evaluate more data subsequently, then 'latest.json' will reflect the average of the initial score it had saved and the final score of this new evaluation.

**Optional flags**:

- `--start-date` (or `-sd`): specify an initial date [YYYY-MM-DD] to start processing the periods.
- `--end-date` (or `-ed`): specify an end date [YYYY-MM-DD] to limit the processing.
- `--save-path`: specify a directory to save the produced data.

## Data

- For the `conversations` type, the names of the CSV files are not important. We expect these CSV files to contain the fields: `sender_name`, `content`, `date`, and `time`.

- For the `searches` type, the names of the CSV files are important; they should follow the format `YYYY-MM-DD.csv`. These files should contain the fields `hour` and `title`.

> NOTE: We do check subfolders within the provided directory path.
