from typing import Any, Dict, Optional

from requests import Session, Response, RequestException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging

from common.http import HttpMethod

logger = logging.getLogger(__name__)

DEFAULT_RETRY_STRATEGY = Retry(
    total=10,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)


class HttpClient(object):
    def __init__(self,
                 retry_strategy: Retry = None):
        self._retry_strategry = retry_strategy or DEFAULT_RETRY_STRATEGY

    def request(self,
                method: HttpMethod,
                url: str,
                params: Dict[str, str] = None,
                headers: Dict[str, str] = None,
                json: Dict[str, Any] = None,
                data: Any = None,
                stream: bool = False):
        session: Optional[Session] = None
        try:
            session = self._get_http_session()
            response: Response = session.request(method=method.name,
                                                 url=url,
                                                 params=params or dict(),
                                                 headers=headers or dict(),
                                                 json=json or dict(),
                                                 data=data or dict(),
                                                 stream=stream)
            logger.debug(f"Response: [ status = {response.status_code} ]")
            response.raise_for_status()
        except RequestException:
            logger.error(f"Request failed.", exc_info=True)
            raise
        finally:
            if session:
                session.close()
        return response



    def _get_http_session(self) -> Session:
        adapter: HTTPAdapter = HTTPAdapter(max_retries=self._retry_strategry)
        session: Session = Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
