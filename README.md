# yaslis

**Project for Group Project 2 at AI1030 - Python Programming, MBZUAI**

**Yet Another Smart Library System** (`yaslis` for short) - is a Smart Library Management System built in Python. The project is done as part of `Group Project 2` in `AI1030 - Python Programming` course at MBZUAI.

More information about project requirements can be found in [the assignment brief](files/AI1030_Group_Assignment_2.pdf).

## Setup and Installation

To run the POI management system, you need Python 3.6+ and `pip`.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/murodbecks/yaslis.git
   cd yaslis/
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the project in editable mode:**
   This command installs any dependencies and makes the `yaslis` command available in your terminal.
   ```bash
   pip install -e .
   ```

4. **Prepare data:**
   For testing purposes, we are using [`Goodreads "Best Books Ever" list`](https://www.kaggle.com/datasets/austinreese/goodreads-books/) dataset. This command downloads and processes for the project.
   ```bash
   yaslis prepare_data
   ```

   If you want to get specific number of books and number of users, use this:
   ```bash
   yaslis prepare_data 1000
   ```

## LICENSE

The repository is licensed under [MIT License](LICENSE). The [`Goodreads "Best Books Ever" list`](https://www.kaggle.com/datasets/austinreese/goodreads-books/) is licensed under [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/).

## Team Members
- Eldana Ashirova
- Adam Badr
- Abror Shopulatov