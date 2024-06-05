from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasicCredentials, HTTPBasic, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import pybreaker
app = FastAPI()


security: HTTPBasicCredentials = HTTPBasic()
security_bearer = HTTPBearer()

# Create a Circuit Breaker instance
circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=10)


class PackageModel(BaseModel):
    weight: float
    price: float


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


def get_token(credentials: HTTPBasicCredentials):
    try:
        response = circuit_breaker.call(
            requests.get,
            "http://recipients:8080/login",
            auth=(credentials.username, credentials.password)
        )
        if response.status_code >= 500:
            response.raise_for_status()
        print(response.json())
        return response.json()["access_token"]
    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503, detail="User service unavailable due to Circuit Breaker")
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400, detail="Check token and try again")


@app.get("/get_delivery")
def get_report(delivery_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    token = get_token(credentials=credentials)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = circuit_breaker.call(
            requests.get,
            f"http://deliveries:8080/get_info_by_id?delivery_id={delivery_id}",
            headers=headers
        )
        if response.status_code >= 500:
            response.raise_for_status()
        return response.json()
    except pybreaker.CircuitBreakerError:
        raise HTTPException(
            status_code=503, detail="Reports service unavailable due to Circuit Breaker")
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e))
