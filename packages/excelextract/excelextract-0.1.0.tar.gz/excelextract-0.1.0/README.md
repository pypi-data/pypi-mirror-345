# excelextract

**excelextract** is a simple yet powerful command-line tool to extract structured data from Excel spreadsheets using a declarative JSON configuration.  
It’s designed to be accessible to researchers and data collectors working with standardized interview forms and surveys data.

## What It Does

- Parses Excel (`.xlsx`) files from a folder
- Applies looping logic across sheets, rows, and columns
- Uses a JSON configuration to define where and how to extract data
- Outputs clean CSV files for each defined table

## Installation

You can install `excelextract` using `pip`:

```
pip install excelextract
```

Make sure your Python version is 3.8 or higher.

## Example Usage

Given a JSON configuration like:

```json
{
  "exports": [
    {
      "inputFolder": "data",
      "inputRegex": ".*",
      "output": "outputFileName",
      "loops" : [
        {
          "type" : "sheetLoop",
          "token" : "SHEET_NAME",
          "regex" : "Survey (.*)"
        },
        {
          "type": "dynamicRowLoop",
          "token": "ROW",
          "sheet": "%%SHEET_NAME%%",
          "start": 
            {
              "regex": "Participants",
              "column": "C",
              "offset": 3
            },
          "end": 
            {
              "regex": "Total",
              "column": "O",
              "offset": -1
            }
        }
      ],
      "columns": [
        {
          "name": "survey_file",
          "type": "string",
          "value": "%%FILE_NAME%%",
          "doNotInitiate": true
        },
        {
          "name": "survey_name",
          "type": "string",
          "value": "overview!C2",
          "doNotInitiate": true
        },
        {
          "name": "participant",
          "type": "string",
          "value": "%%SHEET_NAME%%!B%%ROW%%"
        },
        {
          "name": "number",
          "type": "number",
          "value": "%%SHEET_NAME%%!I%%ROW%%",
        },
      ]
    }
  ]
}
```

You can run:

```
excelextract config.json
```

And it will generate `outputFileName.csv` in the working directory.

### Features Illustrated in the Example

This configuration is designed for a common research scenario:  
you have **many Excel files**, each containing an **overview sheet** and **multiple survey sheets** (e.g., `Survey A`, `Survey B`, ...).  
Each survey sheet includes a **list of participants**, but the number of rows varies per file and sheet.

The configuration extracts these participant rows dynamically and compiles them into a **single CSV file**, with **one row per participant per sheet**.

It demonstrates:

- **File matching**: Processes all `.xlsx` files in the `data/` folder using a regex.
- **Sheet loop**: Iterates over all sheets matching `"Survey (.*)"`, storing the sheet name as `%%SHEET_NAME%%`.
- **Dynamic row loop**:
  - Starts 3 rows after `"Participants"` in column `C`
  - Ends 1 row before `"Total"` in column `O`
  - Sets the `%%ROW%%` token for use in cell references
- **Token-based cell addressing**: Extracts values like participant name or count using dynamic tokens.
- **Fixed metadata**: Reads values like survey name from static cells (e.g., `overview!C2`) once per file.
- **Selective row inclusion**:
  - `doNotInitiate: true` excludes metadata fields from triggering output
  - `type: "number"` ensures proper numeric conversion and filtering

This setup allows you to turn a folder of semi-structured Excel forms into a single clean dataset with no manual editing.


## Features

- Token-based substitution using `%%SHEET_NAME%%`, `%%ROW%%`, etc.
- Supports sheet loops, row loops, column loops, and regex-based searching
- Dynamically determines start/end positions in Excel
- Cleanly separates config from logic — no programming needed to extract new forms
- UTF-8-BOM output (compatible with Excel and Windows)

## License

MIT License © 2025 Philippe

> This project is not affiliated with or endorsed by Microsoft. "Excel" is a registered trademark of Microsoft Corporation. This tool uses the `.xlsx` format purely as a data source.

## Contributing

This tool is shared in the hope it helps others with structured data collection workflows. Pull requests, feedback, and improvements are welcome!

