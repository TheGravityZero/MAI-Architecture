

from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
import jwt

app = FastAPI()

collection = MongoClient(
    f"mongodb://root:root@mongo:27017/").get_database("arch").get_collection("deliveries")

security = HTTPBearer()


class DeliveryModel(BaseModel):
    from_address: str
    to_address: str
    sender: int
    recipient: int
    state: str
    package_id: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    modified_details = []
    for error in details:
        if error["msg"] == "Field required" or error["msg"] == "missing":
            modified_details.append(
                {
                    "message": f"The field {error["loc"][1]} absent in your request",
                }
            )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": modified_details}),
    )


def auth(token: str):
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        current_user = payload["user_id"]
    except:
        raise HTTPException(
            status_code=401, detail="Invalid user data")
    return current_user


@app.get("/get_all")
def get_all_deliveries():
    try:
        result = []
        for i in collection.find():
            i["_id"] = str(i["_id"])
            i["package_id"] = str(i["package_id"])
            result.append(i)
        return result
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Что-то пошло не так")


@app.get("/get_info_by_id")
def get_all_deliveries(delivery_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        result = collection.find_one({"_id": ObjectId(delivery_id)})
        if result:
            result["_id"] = str(result["_id"])
            result["package_id"] = str(result["package_id"])
            jwt_id = int(auth(credentials.credentials))
            print(jwt_id, result["sender"], result["recipient"])
            if jwt_id != result["sender"] and jwt_id != result["recipient"]:
                raise HTTPException(
                    status_code=401, detail=f"У данного пользователя нет доступа к этой информации")
            return result
        else:
            raise HTTPException(
                status_code=404, detail=f"Посылка не найдена")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail=f"Что-то пошло не так, проверьте корректность id")


@app.post("/create_delivery")
def create_delivery(delivery: DeliveryModel):
    try:
        delivery_dict = delivery.model_dump()
        delivery_dict["package_id"] = ObjectId(delivery_dict["package_id"])
        return f"Delivery was successfully created with id {str(collection.insert_one(delivery_dict).inserted_id)}"
    except InvalidId as e:
        raise HTTPException(
            status_code=400, detail=f"Вы ввели неккоректный id посылки")
    except Exception as e:
        print(type(e))
        raise HTTPException(
            status_code=400, detail=f"Что-то пошло не так, проверьте корректность введенных данных")


@app.put("/update_delivery")
def update_delivery(delivery_id: str, delivery: DeliveryModel, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth(credentials.credentials, delivery_id)
        delivery_dict = delivery.model_dump()
        delivery_dict["_id"] = ObjectId(delivery_id)
        delivery_dict["package_id"] = ObjectId(delivery_dict["package_id"])
        collection.update_one(filter={"_id": ObjectId(
            delivery_id)}, update={"$set": delivery_dict})
        return f"Delivery was successfully updated with id {delivery_id}"
    except HTTPException as e:
        raise e
    except InvalidId as e:
        raise HTTPException(
            status_code=400, detail=f"Вы ввели неккоректный id посылки или доставки")
    except Exception as e:
        print(type(e))
        raise HTTPException(
            status_code=400, detail=f"Что-то пошло не так, проверьте корректность введенных данных")


@app.delete("/delete_delivery")
def delete_delivery(delivery_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        auth(credentials.credentials, delivery_id)
        collection.delete_one(
            filter={"_id": ObjectId(delivery_id)}).deleted_count
        return f"Delivery was successfully deleted with id {delivery_id}"
    except HTTPException as e:
        raise e
    except InvalidId as e:
        raise HTTPException(
            status_code=400, detail=f"Вы ввели неккоректный id доставки")
    except Exception as e:
        print(type(e))
        raise HTTPException(
            status_code=400, detail=f"Что-то пошло не так, проверьте корректность введенных данных")
