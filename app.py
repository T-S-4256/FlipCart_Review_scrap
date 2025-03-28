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


@app.route("/")
def HomePage():
    print("Home Page Fetched")
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
def review():
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
            fileName="D:/LANGUAGE CODE/PW_SKILLS/DATA_SCIENCE/PYTHON/WEB_SCRAPPING/PROJECT/SCRAP_DATA/"+searchString+".csv"
            
            # OPEN FILE IN WRITE MODE 
            fw=open(fileName,"a",encoding="utf-8")
            
            # DEFINE HEADING FOR THE CSV FILE 
            header='ProductName, Customer Name, Comment, Haeding, Rating\n'
            
            # CREATING THE HEADING FOR THE CSV FILE 
            fw.write(header)
            
            # CREATING A EMPTY LIST TO STORE ALL THE FIRST REVIEW OF EACH ITEM
            Review = []
            
            # FETCHIING ALL THE DETAILS OF THE FIRST RESULTANT DATA

            # GENERATING THE LINK
            link = "https://www.flipkart.com" + dataContainer[0].div.div.div.a["href"]
            
            # OPEN THE LINK TO GET THA DATA
            try:
                reqData = requests.get(link)
            except Exception as e:
                print("Invalid Link Generated : ", e)
                # SET THE ENCOADING
            reqData.encoding = "utf-8"
            
            # CONVERT INTO THE HTML TEXT
            try:
                reqHTML = bs(reqData.text, "html.parser")
            except Exception as e:
                print("Unable to Parse the reqData : ", e)
                
                # FETCH THE ALL DATA OF REVIEW
            try:
                reviewContainer = "No Review"
                reviewContainer = reqHTML.find_all("div", {"class": "RcXBOT"})
            except Exception as e:
                print("No Review Found : ", e)

                # FETCH THE PRODUCT NAME
            try:
                ProductName = searchString
                ProductName = (
                    (reqHTML.find("div", {"class": "DOjaWF gdgoEp col-8-12"})).find(
                        "span", {"class": "VU-ZEz"}
                    )
                ).text
            except Exception as e:
                print("No Product Name Found : ", e)
            finally:
                print("Product Name : ", ProductName)
                
            # FETCH ALL THE DATA OF THE REVIEW ONE BY ONE
            for i in reviewContainer:

                # FETCH NAME WHO GAVE THE REVIEW
                try:
                    name = "No Name"
                    name = (i.div.div.find("p", {"class": "_2NsDsF AwS1CA"})).text
                except Exception as e:
                    print("No Reviewer Name : ", e)

                # FETCH THE COMMENT OF THE REVIEW
                try:
                    review = "No Review"
                    review = (i.div.div.find("div", {"class": "ZmyHeo"}).div.div).text
                except Exception as e:
                    print("No Review Written : ", e)

                # FETCH THE RATING OF THE REVIEW
                try:
                    rating = "0"
                    rating = (i.div.div.find("div", {"class": "XQDdHH Ga3i8K"})).text
                except Exception as e:
                    print("No Rating Given : ", e)

                # FETCH THE HAED TAG OF THE REVIEW
                try:
                    headTag = "No HeadTag"
                    headTag = (i.div.div.find("p", {"class": "z9E0IG"})).text
                except Exception as e:
                    print("No HeadTag Found : ", e)

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
                
                # CREATE DATA INTO STRING TO STORE THE DATA INTO THE CSV FILE 
                data=ProductName+", "+name+", "+review+", "+headTag+", "+rating+"\n"
                
                # APPEND THE DATA INTO THE CSV FILE 
                fw.write(data)
                
                # SAVE ALL THE DATA INTO A FILE USING LOGGING
                logging.basicConfig(filename="scrapper.log", level=logging.INFO,encoding="utf-8")
                
                # CREATING THE DATA AS STRING TO STORE IN THE LOG 
                data = "Product_Name : "+ ProductName+ " Name : "+ name+ " Review : "+ review+ " Rating : "+ rating+ " HeadTag : "+ headTag
                
                # STORING THE DATA INTO THE LOG 
                logging.info(data)

            # # OPEN ALL THE ITEMS ONE BY ONE
            """
            for i in dataContainer:
                # GENERATING THE LINK
                link = "https://www.flipkart.com" + i.div.div.div.a["href"]
                # OPEN THE LINK TO GET THA DATA
                try:
                    reqData = requests.get(link)
                except Exception as e:
                    print("Invalid Link Generated : ", e)
                # SET THE ENCOADING
                reqData.encoding = "utf-8"
                # CONVERT INTO THE HTML TEXT
                try:
                    reqHTML = bs(reqData.text, "html.parser")
                except Exception as e:
                    print("Unable to Parse the reqData : ", e)
                # FETCH THE ALL DATA OF REVIEW
                try:
                    reviewContainer = "No Review"
                    reviewContainer = reqHTML.find_all("div", {"class": "RcXBOT"})
                except Exception as e:
                    print("No Review Found : ", e)

                # FETCH NAME WHO GAVE THE REVIEW
                try:
                    name = "No Name"
                    name = (
                        reviewContainer[0].div.div.find(
                            "p", {"class": "_2NsDsF AwS1CA"}
                        )
                    ).text
                except Exception as e:
                    print("No Reviewer Name : ", e)

                # FETCH THE COMMENT OF THE REVIEW
                try:
                    review = "No Review"
                    review = (
                        reviewContainer[0]
                        .div.div.find("div", {"class": "ZmyHeo"})
                        .div.div
                    ).text
                except Exception as e:
                    print("No Review Written : ", e)

                # FETCH THE RATING OF THE REVIEW
                try:
                    rating = "0"
                    rating = (
                        reviewContainer[0].div.div.find(
                            "div", {"class": "XQDdHH Ga3i8K"}
                        )
                    ).text
                except Exception as e:
                    print("No Rating Given : ", e)

                # FETCH THE HAED TAG OF THE REVIEW
                try:
                    headTag = "No HeadTag"
                    headTag = (
                        reviewContainer[0].div.div.find("p", {"class": "z9E0IG"})
                    ).text
                except Exception as e:
                    print("No HeadTag Found : ", e)

                # FETCH THE PRODUCT NAME
                try:
                    ProductName = searchString
                    ProductName = (
                        (reqHTML.find("div", {"class": "cPHDOP col-12-12"})).div.find(
                            "span", {"class": "VU-ZEz"}
                        )
                    ).text
                    print("Product Name : ", ProductName)
                except Exception as e:
                    print("No Product Name Found : ", e)

                # SAVE ALL THE DATA INTO A FILE USING LOGGING
                logging.basicConfig(filename="flipcartData.txt", level=logging.INFO)
                data = (
                    "Product Name : "
                    + ProductName
                    + " Name : "
                    + name
                    + " Review : "
                    + review
                    + " Rating : "
                    + rating
                    + " HeadTag : "
                    + headTag
                )
                logging.info(data)
            
                FIRST ITEM LINK FOR OPEN
                resultLink="https://www.flipkart.com"+dataContainer[0].div.div.div.a['href']
                OPEN THE FIRST ITEM
                resultReq=requests.get(resultLink)
                SET ENCOADING
                resultReq.encoding='urf-8'
                CONVERT INTO HTML TEXT
                result_HTML=bs(resultReq.text,'html.parser')
                FETCHING THE FEEDBACK OF FIRST ITEM
                ReviewContainer = result_HTML.find_all("div", {"class": "RcXBOT"})
                print("The Length Of The Review : ", len(ReviewContainer))
                firstName = (
                    ReviewContainer[0].div.div.find("p", {"class": "_2NsDsF AwS1CA"})
                ).text
                firstReview = (
                    ReviewContainer[0].div.div.find("div", {"class": "ZmyHeo"}).div.div
                ).text
                firstRating = (
                    ReviewContainer[0].div.div.find("div", {"class": "XQDdHH Ga3i8K"})
                ).text
                print("Rating : ", firstRating, " Review : ", firstReview)

                SAVE THE LINK OF ALL THE RESULTANT DATA USING LOGGING
                logging.basicConfig(filename="flipcartData.txt", level=logging.INFO)
                for i in dataContainer:
                resultLink="https://www.flipkart.com"+i.div.div.div.a['href']
                data = (
                    "Name : "
                    + firstName
                    + " Review : "
                    + firstReview
                    + " Rating : "
                    + firstRating
                )
                logging.info(data)
            """
            # SAVE THE DATA INTO THE DATABASE 
            
            mongo_url=os.getenv('MONGO_URL')
            # CONNECT WITH MONGODB
            Client=pymongo.MongoClient(mongo_url)
            
            # CREATING A DATABASE
            db=Client['Flipcart_WebScrap']
            
            # CREATING A COLLECTION (TABLE IN MYSQL) 
            ReviewCol=db['Review_Data']
            
            # INSERTING THE DATA INTO THE DATABASE
            ReviewCol.insert_many(Review)
            
            # RETURN THE RESULT PAGE 
            return render_template("result.html", Reviews=Review[0 : (len(Review) - 1)])

        except Exception as e:
            logging.info(e)
            print("Error Occured : ", e)


logging.shutdown()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
