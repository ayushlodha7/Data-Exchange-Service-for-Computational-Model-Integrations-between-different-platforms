from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, Header
import struct
import threading
import asyncio
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.print_sessions_task = asyncio.create_task(print_sessions_every_10_seconds())

@app.on_event("shutdown")
async def shutdown_event():
    task = app.state.print_sessions_task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

async def print_sessions_every_10_seconds():
    while True:
        with session_lock:
            print("Current Sessions and Flags:")
            for session_id, session_info in sessions.items():
                flags = session_info['flags']
                print(f"Session ID: {session_id}, Flags: {flags}")
        await asyncio.sleep(10)

# Define Pydantic models for the request body
class SessionData(BaseModel):
    source_model_ID: int
    destination_model_ID: int
    client_id: str
    initiator_id: int
    inviter_id: int
    input_variables_ID: List[int] = []
    input_variables_size: List[int] = []
    output_variables_ID: List[int] = []
    output_variables_size: List[int] = []

# Session storage
sessions = {}
session_lock = threading.Lock()

@app.post("/create_session/{client_id}")
async def create_session(client_id: str, session_data: SessionData):
    with session_lock:
        # Use data directly from session_data model
        base_session_id = f"{session_data.source_model_ID}_{session_data.destination_model_ID}_{session_data.initiator_id}_{session_data.inviter_id}"
        session_id = base_session_id + "_1"
        i = 1
        while session_id in sessions:
            i += 1
            session_id = f"{base_session_id}_{i}"
        
        var_sizes = {**dict(zip(session_data.input_variables_ID, session_data.input_variables_size)),
                     **dict(zip(session_data.output_variables_ID, session_data.output_variables_size))}
        
        sessions[session_id] = {
            'status': 'created',
            'data': {var: None for var in set(session_data.input_variables_ID) | set(session_data.output_variables_ID)},
            'flags': {var: 0 for var in set(session_data.input_variables_ID) | set(session_data.output_variables_ID)},
            'client_vars': {client_id: list(session_data.input_variables_ID)},
            'end_requests': set(),
            'var_sizes': var_sizes
        }
        
        return {"status": "created", "session_id": session_id}

class JoinSessionData(BaseModel):
    session_id: str
    client_id: str  # Assuming client_id should be part of the body and not a path parameter

@app.post("/join_session")
async def join_session(data: JoinSessionData):
    with session_lock:
        session_id = data.session_id
        joining_client_id = data.client_id

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        if sessions[session_id].get('status') == 'active':
            raise HTTPException(status_code=400, detail="Session is already active")

        session = sessions[session_id]
        initiator_input_vars = session['client_vars'].get(list(session['client_vars'].keys())[0], [])
        all_vars = set(session['data'].keys())
        joining_client_input_vars = list(all_vars - set(initiator_input_vars))

        sessions[session_id]['status'] = 'active'
        sessions[session_id]['client_vars'][joining_client_id] = joining_client_input_vars

        return {"status": "joined and activated", "session_id": session_id}

@app.get("/list_sessions")
async def list_all_session_statuses():
    with session_lock:
        session_statuses = {session_id: session.get('status') for session_id, session in sessions.items()}
        return session_statuses

@app.get("/session_status")
async def session_status(session_id: str):
    with session_lock:
        if session_id in sessions:
            status = 'active' if sessions[session_id]['status'] == 'active' else 'created'
            return {"status": status, "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

@app.get("/get_flags")
async def get_flags(session_id: str):
    with session_lock:
        if session_id in sessions:
            flags = {str(key): value for key, value in sessions[session_id]['flags'].items()}
            return flags
        else:
            raise HTTPException(status_code=404, detail="Session not found")
        
@app.get("/get_variable_flag")
async def get_variable_flag(session_id: str, var_id: int):
    with session_lock:
        if session_id in sessions:
            if var_id in sessions[session_id]['flags']:
                flag_status = sessions[session_id]['flags'][var_id]
                return {"var_id": var_id, "flag_status": flag_status}
            else:
                raise HTTPException(status_code=404, detail="Variable ID not found in session")
        else:
            raise HTTPException(status_code=404, detail="Session not found")

@app.get("/get_variable_size")
async def get_variable_size(session_id: str, var_id: int):
    with session_lock:
        if session_id in sessions and 'var_sizes' in sessions[session_id]:
            var_sizes = sessions[session_id]['var_sizes']
            if var_id in var_sizes:
                return {"var_id": var_id, "size": var_sizes[var_id]}
            else:
                raise HTTPException(status_code=404, detail="Variable ID not found in session")
        else:
            raise HTTPException(status_code=404, detail="Session not found")

        
@app.post("/send_data")
async def send_data(request: Request, session_id: Optional[str] = Header(None), var_id: Optional[int] = Header(None)):
    if session_id is None or var_id is None:
        raise HTTPException(status_code=400, detail="Session-ID or Var-ID header missing")

    binary_data = await request.body()
    array_data = list(struct.unpack('<' + 'd' * (len(binary_data) // 8), binary_data))

    with session_lock:
        if session_id in sessions and var_id in sessions[session_id]['data']:
            sessions[session_id]['data'][var_id] = array_data
            sessions[session_id]['flags'][var_id] = 1  # Data is present
            return {"status": "Binary data received for " + str(var_id)}
        else:
            raise HTTPException(status_code=404, detail="Session or variable not found")

@app.get("/receive_data")
async def receive_data(session_id: str, var_id: int):
    with session_lock:
        if session_id in sessions and var_id in sessions[session_id]['data']:
            data = sessions[session_id]['data'][var_id]
            if data is not None:
                binary_data = struct.pack('<' + 'd' * len(data), *data)
                sessions[session_id]['flags'][var_id] = 0  # Ensure the flag is correctly updated
                return Response(content=binary_data, media_type='application/octet-stream')
            else:
                raise HTTPException(status_code=404, detail="Data not available for variable ID " + str(var_id))
        else:
            raise HTTPException(status_code=404, detail="Session or variable not found")

class EndSessionData(BaseModel):
    session_id: str
    client_id: str

@app.post("/end_session")
async def end_session(data: EndSessionData):
    with session_lock:
        session_id = data.session_id
        client_id = data.client_id

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = sessions[session_id]

        if client_id not in session['client_vars']:
            raise HTTPException(status_code=404, detail="Client not part of the session")

        session['end_requests'].add(client_id)

        if len(session['end_requests']) < len(session['client_vars']):
            session['status'] = 'partial end'
            vars_to_clear = session['client_vars'][client_id]
            for var in vars_to_clear:
                if var in session['data']:
                    session['data'][var] = None
                    session['flags'][var] = 0
            return {"status": "Partial session end for client " + client_id, "session_id": session_id}
        else:
            session['status'] = 'end'
            del sessions[session_id]
            return {"status": "Session ended successfully", "session_id": session_id}

# Start the server with Uvicorn
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(print_sessions_every_10_seconds())
    uvicorn.run(app, host='0.0.0.0', port=8080)