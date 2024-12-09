from tbmail.database import Database
from tbmail.user import User
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from pathlib import Path
import random, json, bcrypt

db = Database()

STATIC = Path(__file__).parents[1] / "static"

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def root():
    # print("root!!")
    with open("static/index.html") as f:
        return f.read()
    
@app.post('/api/link/submit')
async def submit(request: Request):
    try:
        body = await request.json()
        code = str(random.randint(100000, 999999))

        # queue[code] = bcrypt.hashpw(body["password"].encode('utf-8'), bcrypt.gensalt(14))
        db.load()
        db.data["linkcodes"][str(code)] = bcrypt.hashpw(body["password"].encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
        db.write()

        return {"success": True, "code": code}
    except json.decoder.JSONDecodeError:
        return {"success": False, "error": "No JSON provided!"}
    except KeyError as e:
        return {"success": False, "error": f"Missing {e} field."}
    
# @app.get('/api/link/status')
# async def status(request: Request):
#     try:
#         db.load()
#         body = await request.json()
#         while True:
#             data = conn.recv(1024)

#             if not data.startswith(b'LINK/'):
#                 continue

#             data = data.decode('utf-8').split("/")
#             if not str(data[1]) == body["code"]:
#                 conn.send(b"NOT OK")
#                 continue

#             user = User.search(db, home=data[2])
#             if not user:
#                 conn.send(b'NOT OK')
            
#             user.password = queue[body["code"]]
#             del queue['code']

#             idx, raw = user.serialize()
#             db.data["users"][idx] = raw
#             db.write()

#             conn.send(b'OK')

#             return "OK"
#     except json.decoder.JSONDecodeError:
#         return {"success": False, "error": "No JSON provided!"}
#     except KeyError as e:
#         return {"success": False, "error": f"Missing {e} field."}


app.mount("/", StaticFiles(directory=STATIC), name="static")