import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import requests


class ApiTestExecutor:
    """Executes API test cases and captures rich diagnostics."""

    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("API base URL is required")
        self.base_url = base_url.rstrip('/')
        self.results: List[Dict[str, Any]] = []
        self.summary = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'execution_time': 0
        }

    def execute_tests(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_suite = time.time()
        self.results = []
        self.summary['total'] = len(test_cases)
        self.summary['passed'] = 0
        self.summary['failed'] = 0

        for case in test_cases:
            start = time.time()
            url = case.get('url') or self._build_url(case.get('path', ''))
            method = (case.get('method') or 'GET').upper()
            headers = case.get('headers') or {}
            payload = case.get('payload')
            params = case.get('query') or {}
            expected_status = int(case.get('expected_status', 200))

            result = {
                'test_id': case.get('test_id'),
                'name': case.get('name'),
                'method': method,
                'url': url,
                'expected_status': expected_status,
                'status': 'SKIPPED',
                'status_code': None,
                'response_time': 0,
                'response_preview': '',
                'error': ''
            }

            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload if payload not in [None, ''] else None,
                    params=params,
                    timeout=30
                )
                duration = round(time.time() - start, 3)
                result['response_time'] = duration
                result['status_code'] = response.status_code
                result['response_preview'] = self._truncate(response.text)

                if response.status_code == expected_status:
                    result['status'] = 'PASS'
                    self.summary['passed'] += 1
                else:
                    result['status'] = 'FAIL'
                    result['error'] = f'Expected {expected_status} but received {response.status_code}'
                    self.summary['failed'] += 1
            except Exception as exc:
                result['status'] = 'FAIL'
                result['error'] = str(exc)
                result['response_time'] = round(time.time() - start, 3)
                self.summary['failed'] += 1

            self.results.append(result)

        self.summary['execution_time'] = round(time.time() - start_suite, 2)
        return {
            'summary': self.summary,
            'tests': self.results
        }

    def save_execution_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"api_execution_report_{timestamp}.json"
        report_path = os.path.join('reports', report_file)
        os.makedirs('reports', exist_ok=True)

        payload = {
            'base_url': self.base_url,
            'executed_at': datetime.utcnow().isoformat(),
            'summary': self.summary,
            'results': self.results
        }

        with open(report_path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

        return report_file

    def _build_url(self, path: str) -> str:
        normalized = path if path.startswith('/') else f'/{path}'
        return f"{self.base_url}{normalized}"

    @staticmethod
    def _truncate(body: str, limit: int = 600) -> str:
        if body is None:
            return ''
        if len(body) <= limit:
            return body
        return body[:limit] + '...'






