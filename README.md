# IDA-tool

An offline tool designed to assist with course search, equivalent course mapping, and timetable planning for our newly established collaborative double major program.

## Description

IDA-tool is a lightweight offline program built to streamline academic planning. It allows users to:
- Search for courses and their details.
- Map equivalent courses between institutions.
- Plan timetables efficiently.

The program uses:
- **SQLite**: For managing the database.
- **PyQt6**: For creating the user interface.
- **CSV/XLSX Support**: For reading course and equivalent course data.

## Features

- **Course Search**: Quickly find courses and their relevant details.
- **Equivalent Search**: Identify equivalent courses in collaborative programs.
- **Timetable Planning**: Plan and organize your academic schedule.
- **Data Import**: Support for importing course data in `.csv` and equivalent course data in `.xlsx` formats.

## Download

You can download the latest version of the tool here:  
[IDA-tool v1.0.zip](https://drive.google.com/file/d/1a-DPd9ZtSwDvAcyxDYmmV-EXhrVB0Ww1/view?usp=sharing)

## Installation

1. **Download the ZIP file**:
   - Use the link above to download the `v1.0.zip` file.
2. **Extract the ZIP file**:
   - Extract the contents to your desired location.
3. **Run the Program**:
   - Execute the main Python script or the provided executable file.

## Requirements

To run the program, you will need:
- **Python 3.9+**
- The following Python libraries:
  - `sqlite3`
  - `PyQt6`
  - `pandas` (for CSV handling)
  - `openpyxl` (for XLSX handling)

## How to Use
1. **Import Data**
Open the application.
![image](https://github.com/user-attachments/assets/a17eb034-0709-4b26-a4b2-fcb8cb26ad45)

Navigate to the "Import" section.

For course data:

Select the .csv file containing course details.

Ensure the CSV file has the correct structure (e.g., course code, name, credits, etc.).

For equivalent courses:

Select the .xlsx file containing equivalent course mappings.

Ensure the XLSX file is properly formatted.

Click "Import" to load the data into the application.

2. **Search for Courses**

![image](https://github.com/user-attachments/assets/880fcb0a-8b59-40fa-8793-4c970cb40f67)

Navigate to the "Search" section.

Enter the course code, name, or any relevant keyword in the search bar.

View the relevant details of the courses, such as course name, credits, or equivalent courses.

3. **Plan Timetables**

Add courses by selecting them from the available list or search results by "Add to Cart"

Navigate to the "Shopping Cart" section.

![image](https://github.com/user-attachments/assets/705bbf3e-0d12-472f-9711-93ceed9b6104)


Press "generate timetable" to get your timetable, if there is conflict there will be multiple timetable for you to choose

Press "Previous" or "Next" to navigate around

![image](https://github.com/user-attachments/assets/4bb7f992-6009-43bb-b4c4-185ef97d0e63)


## Contact
For questions or support, please contact:

Email: 1155214522@link.cuhk.edu.hk


