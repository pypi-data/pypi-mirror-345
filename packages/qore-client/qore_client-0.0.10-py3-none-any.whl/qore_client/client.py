from io import BytesIO
from typing import Any, Dict, Optional

import pandas as pd
from requests import Response, request

from qore_client.auth import QoreAuth
from qore_client.file_operations import FileOperations
from qore_client.settings import BASE_URL


class QoreClient:
    """
    Qore API Client
    ~~~~~~~~~~~~~~~

    Qore 서비스에 접근할 수 있는 파이썬 Client SDK 예시입니다.
    """

    domain: str = BASE_URL

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None) -> None:
        """
        :param access_key: Qore API 인증에 사용되는 Access Key
        :param secret_key: Qore API 인증에 사용되는 Secret Key
        """
        self.auth = QoreAuth(access_key, secret_key)
        self.file_ops = FileOperations(self._request)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | list[tuple[str, Any]] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        내부적으로 사용하는 공통 요청 메서드

        :param method: HTTP 메서드 (GET, POST, PATCH, DELETE 등)
        :param path: API 엔드포인트 경로 (ex: "/d/12345")
        :param params: query string으로 전송할 딕셔너리
        :param data: 폼데이터(form-data) 등으로 전송할 딕셔너리
        :param json: JSON 형태로 전송할 딕셔너리
        :param files: multipart/form-data 요청 시 사용할 파일(dict)
        :return: 응답 JSON(dict) 또는 raw 데이터
        """
        url = f"{self.domain}{path}"

        # method, path, params를 문자열로 결합하여 서명 생성
        if params is None:
            params = {}

        credential_source = self.auth.get_credential_source(method, path, params)
        headers = self.auth.generate_headers(credential_source=credential_source)

        response: Response = request(
            method=method,
            headers=headers,
            url=url,
            params=params,
            data=data,
            json=json,
            files=files,
        )
        # 에러 발생 시 raise_for_status()가 예외를 던짐
        response.raise_for_status()

        # 일부 DELETE 요청은 204(No Content)일 수 있으므로, 이 경우 JSON 파싱 불가
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    # File operations delegate methods
    def upload_file(self, file_path: str, *, folder_id: str) -> Dict[str, Any]:
        """파일을 업로드합니다."""
        return self.file_ops.upload_file(file_path, folder_id=folder_id)

    def put_file(self, file_content: BytesIO, file_name: str, *, folder_id: str) -> Dict[str, Any]:
        """파일 내용을 직접 메모리에서 업로드합니다."""
        return self.file_ops.put_file(file_content, file_name=file_name, folder_id=folder_id)

    def get_file(self, file_id: str) -> BytesIO:
        """파일을 다운로드합니다."""
        return self.file_ops.get_file(file_id)

    def get_dataframe(self, dataframe_id: str) -> pd.DataFrame:
        """데이터프레임을 다운로드합니다."""
        return self.file_ops.get_dataframe(dataframe_id)

    # def put_dataframe(self, dataframe, dataframe_name: str, folder_id: str) -> Dict[str, Any]:
    #     """데이터프레임을 업로드합니다."""
    #     return self.file_ops.put_dataframe(dataframe, dataframe_name, folder_id)
