import json
import os
from datetime import datetime

import requests
import pytesseract
import csv


def main():
    # Variables Declare
    url = "https://rpachallengeocr.azurewebsites.net/"
    object = {'lista': 'valor'}
    pytesseract.pytesseract.tesseract_cmd = r'D:\tesseract-ocr\tesseract' # CHANGE THIS TO WORK
    absolute_path = os.path.dirname(__file__)
    relative_path = "invoices/"

    if not os.path.isfile("invoices.csv"):
        with open('invoices.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            field = ["ID", "DueDate", "InvoiceNo", "InvoiceDate", "CompanyName", "TotalDue"]
            writer.writerow(field)


    # Get Text
    x = requests.post(f"{url}/seed", json=object)
    y = json.loads(x.content)
    today_date = datetime.now().strftime("%d-%m-%Y")
    today_datetime = datetime.strptime(today_date, "%d-%m-%Y")

    for item in y["data"]:
        time_date = datetime.strptime(item["duedate"], "%d-%m-%Y")

        id = item["id"]
        duedate = item["duedate"]

        if time_date <= today_datetime:
            print(f"{time_date} / {today_date}")
            image_request = requests.get(f"{url}/{item['invoice']}").content
            file_name = (str(item['invoice'].split("/")[2]))

            with open(f"invoices/{file_name}", 'wb') as handler:
                handler.write(image_request)

            # Invoice Case
            img_to_string = str(
                pytesseract.image_to_string(os.path.join(absolute_path, f"{relative_path}/{file_name}")))
            lista_img_string = img_to_string.splitlines()

            invoice = ""
            company_name = ""
            invoice_date = ""
            total_due = ""

            print(lista_img_string)

            if lista_img_string[0] != "INVOICE":
                company_name = lista_img_string[0][0:lista_img_string[0].index("INVOICE") - 1]
                invoice_date_format = datetime.strptime(lista_img_string[2].split(".")[1].replace(" ", ""), "%Y-%m-%d")
                new_invoice_date = invoice_date_format.strftime("%d-%m-%Y")
                invoice_date = new_invoice_date


            else:
                company_name = lista_img_string[4]
                invoice_date_format = datetime.strptime(
                    lista_img_string[6].split(":")[1].replace(" ", "-").replace("-", "", 1).replace(",", ""),
                    "%b-%d-%Y")
                new_invoice_date = invoice_date_format.strftime("%d-%m-%Y")
                invoice_date = new_invoice_date

            for item_list in lista_img_string:
                if invoice == "":
                    item_novo = item_list.replace(" ", "")
                    index_find = item_novo.find("#")
                    if index_find >= 0:
                        index_invoice = item_novo.index("#")
                        invoice = item_novo[index_invoice:]

                if total_due == "":
                    if item_list.find("Total") >= 0 and item_list.find("(") < 0:
                        total_due = item_list.split(" ")[1].replace(" ", "").replace("$", "")

                else:
                    break

            with open('invoices.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([id, duedate, invoice, invoice_date, company_name, total_due])


if __name__ == "__main__":
    main()
