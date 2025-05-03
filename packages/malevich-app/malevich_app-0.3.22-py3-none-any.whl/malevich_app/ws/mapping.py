import base64
from typing import Dict, Optional, List, Callable, Type, Any, Tuple
from pydantic import BaseModel
from fastapi import Response

from malevich_app.export.abstract.abstract import LogsOperation, GetAppInfo, InputCollections, FunMetadata, \
    InitPipeline, InitRun, RunPipeline, Init, Run, Collection, Objects, WSObjectsReq

def __wrapper(fun: Callable, model: Optional[Type[BaseModel]] = None, with_response: bool = True, return_response: bool = False, keys_order: Optional[List[str]] = None, key_body: Optional[str] = None) -> Callable:   # key_body check only if keys_order exists
    async def internal_call(data: Optional[bytes]) -> Tuple[Optional[Any], Response]:
        data = None if model is None else model.model_validate_json(data)
        response = Response() if with_response else None

        args = []
        if data is not None:
            if keys_order is not None:
                data = data.model_dump()
                for key in keys_order:
                    args.append(data.get(key))

                if key_body is not None:
                    body_str = data.get(key_body)
                    response.body = base64.b64decode(body_str).decode('utf-8')
            else:
                args.append(data)
        if with_response:
            args.append(response)
        res = await fun(*args)
        if return_response:
            return None, res
        else:
            return res, response
    return internal_call


operations_mapping: Dict[str, any] = None

def ws_init():
    global operations_mapping
    if operations_mapping is not None:
        return

    import malevich_app.export.api.api as api
    operations_mapping = {
        "ping": __wrapper(api.ping, with_response=False),
        "logs": __wrapper(api.logs, LogsOperation),
        "app_info": __wrapper(api.app_functions_info, GetAppInfo),
        "input": __wrapper(api.input_put, InputCollections),
        "processor": __wrapper(api.processor_put, FunMetadata),
        "output": __wrapper(api.output_put, FunMetadata),
        "init/pipeline": __wrapper(api.init_pipeline, InitPipeline),
        "init_run/pipeline": __wrapper(api.init_run_pipeline, InitRun,False, return_response=True),
        "run/pipeline": __wrapper(api.run_pipeline, RunPipeline),
        "init": __wrapper(api.init_put, Init),
        "init_run": __wrapper(api.init_run, InitRun, False, return_response=True),
        "run": __wrapper(api.run, Run),
        "finish": __wrapper(api.finish, FunMetadata, False, return_response=True),
        "collection": __wrapper(api.put_collection, Collection, False, return_response=True),
        "objects": __wrapper(api.put_objects, WSObjectsReq, return_response=True, keys_order=["operationId", "runId", "asset"], key_body="payload"),
        "objects/reverse": __wrapper(api.get_objects, Objects, False, return_response=True),
    }
