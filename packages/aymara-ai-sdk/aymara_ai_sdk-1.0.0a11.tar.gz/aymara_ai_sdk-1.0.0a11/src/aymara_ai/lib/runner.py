"""
EvalRunner & AsyncEvalRunner: Simple orchestrators for Aymara SDK evals (sync and async).

"""

from typing import Any, Dict, List, Union, Callable, Optional, Awaitable
from pathlib import Path

import httpx
import aiofiles

from aymara_ai import AymaraAI, AsyncAymaraAI
from aymara_ai.lib.async_utils import wait_until_complete, async_wait_until_complete
from aymara_ai.types.eval_prompt import EvalPrompt
from aymara_ai.types.shared_params import FileReference
from aymara_ai.types.eval_response_param import EvalResponseParam
from aymara_ai.types.evals.eval_run_result import EvalRunResult


class EvalRunner:
    """
    Orchestrates the evaluation process for Aymara SDK using a user-provided model callable.
    Stores all state internally. For synchronous (blocking) use with AymaraClient.
    """

    def __init__(
        self,
        client: AymaraAI,
        model_callable: Callable[[str], Union[str, Path, None]],
    ):
        """
        Args:
            client: An instance of AymaraClient.
            model_callable: Callable for model inference (prompt) -> str or Path (for image).
        """
        self.client = client
        self.model_callable = model_callable
        self.eval_id: Optional[str] = None
        self.run_id: Optional[str] = None
        self.eval_run_result: Optional[Any] = None

    @staticmethod
    def _default_response_adapter(model_output: Union[str, Path], prompt: EvalPrompt) -> EvalResponseParam:
        """
        Adapts model output to EvalResponseParam or FileReferenceParam based on type.
        """

        if isinstance(model_output, (str, bytes)):
            return EvalResponseParam(content=model_output, prompt_uuid=prompt.prompt_uuid)
        elif isinstance(model_output, Path):  # type: ignore
            # For image, wrap in FileReferenceParam
            return EvalResponseParam(
                content=FileReference(remote_file_path=str(model_output.absolute)),
                prompt_uuid=prompt.prompt_uuid,
                content_type="image",
            )
        else:
            raise ValueError("Unsupported model output type for response adapter.")

    def run_eval(
        self,
        eval_params: Dict[str, Any],
    ) -> EvalRunResult:
        """
        Orchestrate the full eval flow (sync).
        """
        # 1. Create eval
        eval_obj = self.client.evals.create(**eval_params)
        self.eval_id = eval_obj.eval_uuid

        # 2. Wait for eval readiness

        eval_obj = wait_until_complete(self.client.evals.get, resource_id=str(self.eval_id))

        # 3. Fetch prompts
        prompts_response = self.client.evals.list_prompts(str(self.eval_id))
        prompts = prompts_response.items

        # 4. Model inference and response adaptation
        responses: List[EvalResponseParam] = []
        with httpx.Client() as client:
            for prompt in prompts:
                model_output = self.model_callable(prompt.content)
                # Allow model_callable to return None, str, or Path
                if model_output is None:
                    # Model refused to answer
                    response = EvalResponseParam(prompt_uuid=prompt.prompt_uuid, ai_refused=True)
                    responses.append(response)
                    continue
                if isinstance(model_output, str):
                    response = EvalResponseParam(content=model_output, prompt_uuid=prompt.prompt_uuid)
                    responses.append(response)
                    continue
                if isinstance(model_output, Path):  # type: ignore
                    # Upload the image file and use remote path
                    model_output = str(model_output)
                    upload_resp = self.client.files.create(files=[{"local_file_path": model_output}])
                    file_info = upload_resp.files[0]
                    if not file_info.file_url:
                        raise RuntimeError("No presigned file_url returned for upload.")
                    # Upload to presigned URL
                    with open(model_output, "rb") as f:
                        put_resp = client.put(file_info.file_url, content=f)
                        put_resp.raise_for_status()
                    response = EvalResponseParam(
                        content=FileReference(remote_file_path=file_info.remote_file_path),
                        prompt_uuid=prompt.prompt_uuid,
                        content_type="image",
                    )
                    # Optionally include local_file_path for downstream use
                    response["local_file_path"] = model_output  # type: ignore
                    responses.append(response)
                    continue
                raise ValueError("Unsupported model output type for response adapter.")

        # 5. Create eval run
        eval_run = self.client.evals.runs.create(eval_uuid=str(self.eval_id), responses=responses)
        self.run_id = eval_run.eval_run_uuid

        # 6. Wait for eval run completion
        eval_run = wait_until_complete(self.client.evals.runs.get, resource_id=str(self.run_id))
        self.eval_run_result = eval_run
        return eval_run


class AsyncEvalRunner:
    """
    Orchestrates the evaluation process for Aymara SDK using a user-provided async model callable.
    Stores all state internally. For asynchronous use with AsyncAymaraClient.
    """

    def __init__(
        self,
        client: AsyncAymaraAI,
        model_callable: Callable[[str], Awaitable[Union[str, Path, None]]],
    ):
        """
        Args:
            client: An instance of AsyncAymaraClient.
            model_callable: Async callable for model inference (prompt) -> str or Path (for image).
        """
        self.client = client
        self.model_callable = model_callable
        self.eval_id: Optional[str] = None
        self.run_id: Optional[str] = None
        self.eval_run_result: Optional[Any] = None

    @staticmethod
    def _default_response_adapter(model_output: Union[str, Path], prompt: EvalPrompt) -> Any:
        """
        Adapts model output to EvalResponseParam or FileReferenceParam based on type.
        """

        if isinstance(model_output, str):
            return EvalResponseParam(content=model_output, prompt_uuid=prompt.prompt_uuid)
        elif isinstance(model_output, Path):  # type: ignore
            # For image, wrap in FileReference
            # Try both possible FileReference imports for compatibility
            file_ref = FileReference(remote_file_path=str(model_output))
            return EvalResponseParam(content=file_ref, prompt_uuid=prompt.prompt_uuid, content_type="image")
        else:
            raise ValueError("Unsupported model output type for response adapter.")

    async def run_eval(
        self,
        eval_params: Dict[str, Any],
        timeout: int = 30,
        poll_interval: int = 5,
    ) -> EvalRunResult:
        """
        Orchestrate the full eval flow (async).
        """
        # 1. Create eval
        eval_obj = await self.client.evals.create(**eval_params)
        self.eval_id = eval_obj.eval_uuid

        # 2. Wait for eval readiness
        eval_obj = await async_wait_until_complete(
            self.client.evals.get, resource_id=str(self.eval_id), interval=poll_interval, timeout=timeout
        )

        # 3. Fetch prompts
        prompts_response = await self.client.evals.list_prompts(str(self.eval_id))
        prompts = prompts_response.items

        # 4. Model inference and response adaptation

        responses: List[EvalResponseParam] = []

        async with httpx.AsyncClient() as client:
            for prompt in prompts:
                model_output = await self.model_callable(prompt.content)
                if model_output is None:
                    response = EvalResponseParam(prompt_uuid=prompt.prompt_uuid, ai_refused=True)
                    responses.append(response)
                    continue
                if isinstance(model_output, str):
                    response = EvalResponseParam(content=model_output, prompt_uuid=prompt.prompt_uuid)
                    responses.append(response)
                    continue
                if isinstance(model_output, Path):  # type: ignore
                    # Upload the image file and use remote path
                    model_output = str(model_output)
                    upload_resp = await self.client.files.create(files=[{"local_file_path": model_output}])
                    file_info = upload_resp.files[0]
                    if not file_info.file_url:
                        raise RuntimeError("No presigned file_url returned for upload.")
                        # Upload to presigned URL (async)
                    async with aiofiles.open(model_output, mode="rb") as f:
                        put_resp = await client.put(file_info.file_url, content=f)
                        if put_resp.status_code != 200:
                            raise RuntimeError(f"Failed to upload file: {put_resp.status_code}")
                    response = EvalResponseParam(
                        content=FileReference(remote_file_path=file_info.remote_file_path),
                        prompt_uuid=prompt.prompt_uuid,
                        content_type="image",
                    )
                    response["local_file_path"] = model_output  # type: ignore
                    responses.append(response)
                    continue
                raise ValueError("Unsupported model output type for response adapter.")

        # 5. Create eval run
        eval_run = await self.client.evals.runs.create(eval_uuid=str(self.eval_id), responses=responses)
        self.run_id = eval_run.eval_run_uuid

        # 6. Wait for eval run completion
        eval_run = await async_wait_until_complete(
            self.client.evals.runs.get, resource_id=str(self.run_id), interval=poll_interval, timeout=timeout
        )
        self.eval_run_result = eval_run
        return eval_run
