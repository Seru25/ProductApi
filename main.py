from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
from flask_jwt import JWT,jwt_required
from security import auth, identity
import os
from user import SignUp

app = Flask(__name__)
app.secret_key = '#0#'
api = Api(app)
jwt = JWT(app,auth,identity)#/auth
# app = Flask(__name__)
# app.secret_key='#0#'
# api = Api(app)
# jwt = JWT(app,auth,identity)#/auth

class Products(Resource):
    def __init__(self):
        self.data = pd.read_csv('prices.csv',header=None, index_col=0, squeeze=True)
    @jwt_required()
    def get(self):
        data = self.data
        data = data.to_dict()
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('productId', type=int, required=True , help="Please the product number")
        productId=  parser.parse_args().get("productId", None)
        if productId in data:
            return {"The price is ": data[productId]}, 200  # return data and 200 OK code
        else:
            return jsonify({"message": 'Product not in inventory exist please enter correct code'})

    @jwt_required()
    def put(self):
        data = self.data.to_dict()
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('productId', type=int, required=True, help="Please the product number")
        parser.add_argument('price',type=float, required=True, help="Please the product price")
        productId = parser.parse_args().get("productId", None)
        price = parser.parse_args().get("price",None)
        args = parser.parse_args()
        if productId in data and data[productId]==price:
            return jsonify({"Product price is already": price})
        elif productId in data and data[productId]!=price:
            data[productId]= price
            data=pd.Series(data).to_frame()
            data.to_csv('prices.csv', index=True, header=None)
            return jsonify({"Product price updated to": price})
        else:
            return jsonify({"message":'Product not in inventory exist please enter correct code'})
def load_data():

        data = pd.read_csv('prices.csv', header=None, index_col=0, squeeze=True)
        data = data.to_dict()
        # productmischarge = collections.defaultdict(float)
        productmischarge = {}
        total =0
    # def get(self):
        # parser = reqparse.RequestParser()  # initialize
        # parser.add_argument('productId', type=int, required=True, help="Please the product number")
        arr=[]
        for r, d, f in os.walk("./data"):
            fp=''
            for i in range(len(f)):
                fp = os.path.join(r+"/" +f[i])
                fp= fp.replace("\\","/")
                if os.path.isfile(fp):
                    arr.append(fp)
        for i in arr:
            file = open(i, 'r')

            lines = file.readlines()[1:]
            n = len(lines)
            for i in range(n - 1):
                arr = lines[i].split()
                if arr[-1].isalpha() and "***" not in lines[i + 1] and data[int(arr[-3])] != float(arr[-2]):
                    # product,price = arr[-3], arr[-2]

                    if  int(arr[-3]) in productmischarge:
                        productmischarge[int(arr[-3])] += float(arr[-2])
                    else:
                        productmischarge[int(arr[-3])] = float(arr[-2])
                    # print(productmischarge)
                    total += float(arr[-2])

                elif not arr[-1].isalpha() and "***" not in arr[-1] and "***" not in lines[i + 1] \
                            and data[int(arr[-2])] != float(arr[-1]):
                    # print(productmischarge)
                    if  int(arr[-2]) in productmischarge:
                        productmischarge[int(arr[-2])] += float(arr[-1])
                    else:
                        productmischarge[int(arr[-2])] = float(arr[-1])
                    # productmischarge[int(arr[-2])] += round(float(arr[-1]),2)
                    total +=float(arr[-1])
        # "The total sum of mischarge is:": round(self.total, 2),
        #                         "Total": round(sum(self.productmischarge.values()), 2),
        #                         "The mischarge per product is":
        return {"Mischarge for the product":productmischarge, "Total":total}

class MisCharges(Resource):
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('productId', type=int, required=True, help="Please the product number")
        product = parser.parse_args().get("productId", None)
        productreport= load_data()
        productmischarge=  productreport["Mischarge for the product"][product]
        return {"This is the mischarge for product "+ str(product) : round(productmischarge,2)}


class TotalMischarges(Resource):
    @jwt_required()
    def get(self):
        productreport = load_data()
        productmischarge = productreport["Total"]
        return {"This is the grand total of all mischarges ": round(productmischarge,2)}

api.add_resource(Products, '/products')
api.add_resource(MisCharges,'/mischarges')
api.add_resource(TotalMischarges,'/totalmischarges')
api.add_resource(SignUp,'/signup')
app.run(port=4000,debug=True)
#
# if __name__ == '__main__':
#     app.run()  # run our Flask app