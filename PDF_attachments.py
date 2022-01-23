import os
from pathlib import Path, PurePath
from PyPDF2 import PdfFileReader, PdfFileWriter
import shutil

BARCLAYS = "Barclays"
DANSKE = "Danske"
DANSKE_COMPANY_CODE = "...."
REPORTS_LOCATION = ".../_Completed"
year_folder: str = ""
processed_pdfs_count = 0
pdf_count = 0
BACKUP_FOLDER_NAME = "generated backup documents"


def select_folder(root):
    dirs = os.listdir(root)
    option = 0
    if len(dirs) == 0:
        print("No options for this folder")
        quit()
    for folder in dirs:
        print(str(option) + ' --> ' + folder)
        option += 1
    while True:
        option = int(input("Select option: "))
        if option < 0 or option > len(dirs) - 1:
            print("Option is not valid")
            continue
        return dirs[option]


def count_pdf_in_folder(folder):
    count = 0
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        dd = str(PurePath(path).suffix)
        if os.path.isfile(path) and dd.lower() == '.pdf':
            count += 1
        elif Path(path).is_dir():
            count += count_pdf_in_folder(path)

    return count


def create_backup_reports_folder(root):
    gbd_path = os.path.join(root, BACKUP_FOLDER_NAME)
    if os.path.exists(gbd_path):
        shutil.rmtree(gbd_path)
    os.mkdir(gbd_path)
    return gbd_path


def generate_backup_documentation(root, is_danske_report):
    gbd_path = create_backup_reports_folder(root)
    global pdf_count
    pdf_count = count_pdf_in_folder(root)
    process_data_report_folders(root, gbd_path, is_danske_report)


def process_data_report_folders(root, gbd_path, is_danske_report):
    dates = os.listdir(root)
    for date in dates:
        date_folder = os.path.join(root, date)
        if date.startswith('.') and os.path.isfile(date_folder):
            continue
        if date == BACKUP_FOLDER_NAME:
            continue
        process_data_folder(date_folder, gbd_path, is_danske_report)


def process_data_folder(date_folder, gbd_path, is_danske_report):
    for document_folder in os.listdir(date_folder):
        dd = os.path.join(date_folder, document_folder)
        if document_folder.startswith('.') and os.path.isfile(dd):
            continue
        if is_danske_report == False and len(Path(dd).name.split("-")) == 1:
            process_data_folder(dd, gbd_path, is_danske_report)
            continue
        else:
            generate_pdf_report(dd, gbd_path)


def generate_pdf_report(path, gbd_path):
    reports = []
    paths = sorted(Path(path).iterdir(), key=os.path.getmtime, reverse=True)
    for p in paths:
        reports.append(str(p))
    merge_pdfs(reports, output=os.path.join(gbd_path, generate_report_name(Path(path).name) + '.pdf'))


def generate_report_name(raw_name):
    elms = raw_name.split("-")
    if len(elms) == 1:
        company_code = DANSKE_COMPANY_CODE
        count: int = max(10 - len(elms[0]), 0)
        document_number = elms[0]
    else:
        company_code = elms[0]
        count: int = max(10 - len(elms[1]), 0)
        document_number = elms[1]

    zero_prefix = ''
    while count != 0:
        zero_prefix += '0'
        count -= 1
    return company_code + zero_prefix + document_number + Path(year_folder).name


def merge_pdfs(paths, output):
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))
        global processed_pdfs_count
        processed_pdfs_count += 1

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)


def main():
    global year_folder
    selected_year = select_folder(REPORTS_LOCATION)
    year_folder = os.path.join(REPORTS_LOCATION, selected_year)

    selected_month = select_folder(year_folder)
    month_folder = os.path.join(year_folder, selected_month)

    selected_bank_folder = select_folder(month_folder)
    bank_folder = os.path.join(month_folder, selected_bank_folder)

    if selected_bank_folder == DANSKE:
        generate_backup_documentation(bank_folder, True)
    else:
        generate_backup_documentation(bank_folder, False)

    print("PDFs found: " + str(pdf_count) + " PDFs processed: " + str(processed_pdfs_count))


if __name__ == "__main__":
    main()
