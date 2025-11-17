import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class SmartApiEngine:
    """Generates API test cases from an OpenAPI/Swagger specification."""

    def __init__(self, base_url: str, spec_source: str):
        if not base_url:
            raise ValueError("API base URL is required")
        if not spec_source:
            raise ValueError("OpenAPI specification is required")

        self.base_url = base_url.rstrip('/')
        self.spec = self._load_spec(spec_source)
        self.test_cases: List[Dict[str, Any]] = []
        self.summary = {
            'total': 0,
            'positive': 0,
            'negative': 0,
            'security': 0
        }

    def _load_spec(self, spec_source: str) -> Dict[str, Any]:
        try:
            return json.loads(spec_source)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON specification provided") from exc

    def generate_tests(self) -> List[Dict[str, Any]]:
        paths = self.spec.get('paths', {})
        if not paths:
            raise ValueError("Specification must include paths")

        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method, details in methods.items():
                if method.upper() not in {'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}:
                    continue
                test_id = self._build_test_id(method, path)
                url = self._build_url(path)
                positive_case = {
                    'test_id': f"{test_id}_POS",
                    'name': details.get('summary') or f"{method.upper()} {path}",
                    'method': method.upper(),
                    'path': path,
                    'url': url,
                    'category': 'positive',
                    'expected_status': self._extract_status(details, success=True),
                    'description': details.get('description', ''),
                    'payload': self._build_payload(details),
                    'headers': self._build_headers(details),
                    'query': self._build_query_params(details),
                }
                self._append_case(positive_case, 'positive')

                if self._has_request_body(details):
                    negative_case = {
                        'test_id': f"{test_id}_NEG",
                        'name': f"{method.upper()} {path} - missing body",
                        'method': method.upper(),
                        'path': path,
                        'url': url,
                        'category': 'negative',
                        'expected_status': self._extract_status(details, success=False),
                        'description': 'Submit request with missing or invalid payload',
                        'payload': {},
                        'headers': self._build_headers(details),
                        'query': self._build_query_params(details),
                    }
                    self._append_case(negative_case, 'negative')

        return self.test_cases

    def _append_case(self, case: Dict[str, Any], bucket: str):
        self.test_cases.append(case)
        self.summary['total'] += 1
        if bucket in self.summary:
            self.summary[bucket] += 1

    def _build_test_id(self, method: str, path: str) -> str:
        safe_path = re.sub(r'[^a-zA-Z0-9]+', '_', path).strip('_')
        return f"API_{method.upper()}_{safe_path or 'ROOT'}"

    def _build_url(self, path: str) -> str:
        if path.startswith('http'):
            return path
        normalized = path if path.startswith('/') else f'/{path}'
        normalized = re.sub(r'\{[^}]+\}', 'sample', normalized)
        return f"{self.base_url}{normalized}"

    def _extract_status(self, details: Dict[str, Any], success: bool = True) -> int:
        responses = details.get('responses', {})
        if not responses:
            return 200 if success else 400
        preferred_prefix = '2' if success else '4'
        for status_code in responses.keys():
            if isinstance(status_code, str) and status_code.startswith(preferred_prefix):
                try:
                    return int(re.sub(r'[^0-9]', '', status_code) or (200 if success else 400))
                except ValueError:
                    continue
        try:
            first_key = next(iter(responses))
            return int(re.sub(r'[^0-9]', '', first_key))
        except StopIteration:
            return 200 if success else 400

    def _build_headers(self, details: Dict[str, Any]) -> Dict[str, str]:
        headers = {}
        consumes = details.get('consumes') or self.spec.get('consumes')
        if consumes:
            headers['Content-Type'] = consumes[0]
        produces = details.get('produces') or self.spec.get('produces')
        if produces:
            headers['Accept'] = produces[0]
        return headers

    def _build_query_params(self, details: Dict[str, Any]) -> Dict[str, Any]:
        params = {}
        for param in details.get('parameters', []):
            if param.get('in') == 'query':
                params[param['name']] = self._sample_value(param.get('schema', {}) or param)
        return params

    def _has_request_body(self, details: Dict[str, Any]) -> bool:
        if details.get('requestBody'):
            return True
        for param in details.get('parameters', []):
            if param.get('in') == 'body':
                return True
        return False

    def _build_payload(self, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        request_body = details.get('requestBody')
        if request_body:
            content = request_body.get('content', {})
            json_content = content.get('application/json')
            if json_content:
                return self._sample_value(json_content.get('schema', {}))

        for param in details.get('parameters', []):
            if param.get('in') == 'body':
                schema = param.get('schema', {})
                return self._sample_value(schema)
        return None

    def _sample_value(self, schema: Dict[str, Any]) -> Any:
        if not schema:
            return {}
        if 'example' in schema:
            return schema['example']
        if 'default' in schema:
            return schema['default']
        if schema.get('enum'):
            return schema['enum'][0]

        schema_type = schema.get('type')
        if schema_type == 'object':
            obj = {}
            for name, prop in (schema.get('properties') or {}).items():
                obj[name] = self._sample_value(prop)
            return obj
        if schema_type == 'array':
            return [self._sample_value(schema.get('items', {}))]
        if schema_type == 'integer':
            return 1
        if schema_type == 'number':
            return 1.0
        if schema_type == 'boolean':
            return True
        if schema_type == 'string':
            fmt = schema.get('format')
            if fmt == 'date':
                return datetime.utcnow().strftime('%Y-%m-%d')
            if fmt == 'date-time':
                return datetime.utcnow().isoformat()
            if fmt == 'email':
                return 'user@example.com'
            if fmt == 'uuid':
                return '00000000-0000-4000-8000-000000000000'
            return schema.get('pattern', 'sample-text')
        return "sample"

    def save_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"api_test_plan_{timestamp}.json"
        report_path = os.path.join('reports', report_file)
        os.makedirs('reports', exist_ok=True)

        payload = {
            'base_url': self.base_url,
            'generated_at': datetime.utcnow().isoformat(),
            'summary': self.summary,
            'test_cases': self.test_cases,
        }

        with open(report_path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

        return report_file

    def get_summary(self) -> Dict[str, int]:
        return self.summary

