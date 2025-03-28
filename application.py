from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)


@app.route("/")
@cross_origin()
def HomePage():
    print("Home Page Fetched")
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"], endpoint="review")
@cross_origin()
def review_page():
    logFile = os.path.join(os.getcwd(), f"Scrapper.log")
    # SAVE ALL THE DATA INTO A FILE USING LOGGING
    logging.basicConfig(filename=logFile, level=logging.INFO, encoding="utf-8")

    if request.method == "POST":
        try:
            # FETCH THE SEARCHED CONTENT
            searchString = request.form["content"].replace(" ", "")

            # CREATE A URL FOR THE SEARCHED CONTENT
            flipcartUrl = "https://www.flipkart.com/search?q=" + searchString

            # OPEN THE URL USING URLOPEN LIBRARY
            uClient = urlopen(flipcartUrl)

            # READ THE DATA AND STORE IN A VARIABLE
            flipcartData = uClient.read()

            # CLOSE THE URLOPEN
            uClient.close()

            # CONVERT THE CONTENT INTO HUMAN READABLE FORMAT
            flipcartHTML = bs(flipcartData, "html.parser")

            # FETCH ALL THE ITEMS PRESENT IN AFTER SEARCH
            dataContainer = flipcartHTML.find_all("div", {"class": "cPHDOP col-12-12"})

            # DELETING THE WASTE DATA FROM THE dataContainer
            del dataContainer[0:2]

            # SAVE THE DATA INTO A CSV FILE
            # FILE NAME WITH SPECIFIC LOCATION
            fileName = os.path.join(os.getcwd(), "ScrapData", f"{searchString}.csv")
            file_exists = os.path.isfile(fileName)

            # DEFINE HEADING FOR THE CSV FILE
            header = "ProductName, Customer Name, Comment, Haeding, Rating\n"

            # OPEN FILE IN WRITE MODE
            with open(fileName, "a", encoding="utf-8") as fw:
                if not file_exists:
                    # CREATING THE HEADING FOR THE CSV FILE
                    fw.write(header)

                # CREATING A EMPTY LIST TO STORE ALL THE FIRST REVIEW OF EACH ITEM
                Review = []

                # FETCHIING ALL THE DETAILS OF THE FIRST RESULTANT DATA

                # GENERATING THE LINK
                link = (
                    "https://www.flipkart.com" + dataContainer[0].div.div.div.a["href"]
                )

                # OPEN THE LINK TO GET THA DATA
                try:
                    reqData = requests.get(link)
                except Exception as e:
                    logging.info(e)
                    # SET THE ENCOADING
                reqData.encoding = "utf-8"

                # CONVERT INTO THE HTML TEXT
                try:
                    reqHTML = bs(reqData.text, "html.parser")
                except Exception as e:
                    logging.info(e)

                    # FETCH THE ALL DATA OF REVIEW
                try:
                    reviewContainer = "No Review"
                    reviewContainer = reqHTML.find_all("div", {"class": "RcXBOT"})
                except Exception as e:
                    logging.info(e)

                    # FETCH THE PRODUCT NAME
                try:
                    ProductName = searchString
                    ProductName = (
                        (reqHTML.find("div", {"class": "DOjaWF gdgoEp col-8-12"})).find(
                            "span", {"class": "VU-ZEz"}
                        )
                    ).text
                except Exception as e:
                    logging.info(e)

                # FETCH ALL THE DATA OF THE REVIEW ONE BY ONE
                for i in reviewContainer:

                    # FETCH NAME WHO GAVE THE REVIEW
                    try:
                        name = "No Name"
                        name = (i.div.div.find("p", {"class": "_2NsDsF AwS1CA"})).text
                    except Exception as e:
                        logging.info(e)

                    # FETCH THE COMMENT OF THE REVIEW
                    try:
                        review = "No Review"
                        review = (
                            i.div.div.find("div", {"class": "ZmyHeo"}).div.div
                        ).text
                    except Exception as e:
                        logging.info(e)

                    # FETCH THE RATING OF THE REVIEW
                    try:
                        rating = "0"
                        rating = (
                            i.div.div.find("div", {"class": "XQDdHH Ga3i8K"})
                        ).text
                    except Exception as e:
                        logging.info(e)

                    # FETCH THE HAED TAG OF THE REVIEW
                    try:
                        headTag = "No HeadTag"
                        headTag = (i.div.div.find("p", {"class": "z9E0IG"})).text
                    except Exception as e:
                        logging.info(e)

                    # CREATE A DICTIONARY AND STORE THE DATA INTO THE DICTIONARY
                    my_dict = {
                        "ProductName": ProductName,
                        "Name": name,
                        "Comment": review,
                        "HeadTag": headTag,
                        "Rating": rating,
                    }
                    # STORE THE FIRST REVIEW AS DICTIONARY IN THE REVIEW LIST
                    Review.append(my_dict)

                    # APPEND THE DATA INTO THE CSV FILE
                    fw.write(f"{ProductName}, {name}, {review}, {headTag}, {rating}\n")

                # SAVE THE DATA INTO THE DATABASE
                try:
                    mongo_url = os.getenv("MONGO_URL")

                    # CONNECT WITH MONGODB
                    Client = pymongo.MongoClient(mongo_url)

                    # CREATING A DATABASE
                    db = Client["Flipcart_WebScrap"]

                    # CREATING A COLLECTION (TABLE IN MYSQL)
                    ReviewCol = db["Review_Data"]
                except pymongo.errors.ConnectionError as e:
                    logging.error("MongoDB connection failed:", e)
                    return (
                        render_template(
                            "error.html",
                            message="Something went wrong. Please try again.",
                        ),
                        500,
                    )
                # INSERTING THE DATA INTO THE DATABASE
                ReviewCol.insert_many(Review)

                # RETURN THE RESULT PAGE
                return render_template(
                    "result.html", Reviews=Review[0 : (len(Review) - 1)]
                )

        except Exception as e:
            logging.info(e)


logging.shutdown()

if __name__ == "__main__":
    app.run()
