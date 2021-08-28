from server import _init_app
from server.configuration import environment
import uvicorn

if __name__ == '__main__':
    app = _init_app()
    uvicorn.run(app, host=environment.HOST, port=environment.PORT)

