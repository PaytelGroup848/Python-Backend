"""
Enterprise QA Test Environment Setup & Fixtures
"""
import os
import sys
import types
import importlib

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Passlib + Bcrypt 4.x / 5.x compatibility patch
try:
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        bcrypt.__about__ = types.SimpleNamespace(__version__=getattr(bcrypt, "__version__", "5.0.0"))
    _orig_hashpw = bcrypt.hashpw
    def _safe_hashpw(password, salt):
        if len(password) > 72:
            password = password[:72]
        return _orig_hashpw(password, salt)
    bcrypt.hashpw = _safe_hashpw
except ImportError:
    pass

# Email validator
try:
    import email_validator
except ImportError:
    ev = types.ModuleType("email_validator")
    def mock_val(email, **kw):
        if not email or "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Invalid email")
        local_part, domain = email.split("@", 1)
        return types.SimpleNamespace(email=email, normalized=email, local_part=local_part, domain=domain)
    ev.validate_email = mock_val
    ev.EmailNotValidError = ValueError
    sys.modules["email_validator"] = ev

# Mock pgvector for local test execution without PostgreSQL pgvector extension
try:
    import pgvector
    import pgvector.sqlalchemy
except ImportError:
    pv = types.ModuleType("pgvector")
    pvs = types.ModuleType("pgvector.sqlalchemy")
    pvs.Vector = lambda *a, **kw: None
    pv.sqlalchemy = pvs
    sys.modules["pgvector"] = pv
    sys.modules["pgvector.sqlalchemy"] = pvs

# Jose / PyJWT
try:
    import jose
    from jose import jwt, JWTError
except ImportError:
    try:
        import jwt as pyjwt
        class JoseShim:
            encode = staticmethod(pyjwt.encode)
            @staticmethod
            def decode(token, key, algorithms=None, **kwargs):
                return pyjwt.decode(token, key, algorithms=algorithms or ["HS256"], **kwargs)
        jose_mod = types.ModuleType("jose")
        jose_mod.jwt = JoseShim
        jose_mod.JWTError = pyjwt.PyJWTError
        sys.modules["jose"] = jose_mod
        sys.modules["jose.jwt"] = JoseShim
    except ImportError:
        pass

# Google Auth & GenAI
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
except ImportError:
    g = sys.modules.get("google", types.ModuleType("google"))
    ga = types.ModuleType("google.auth")
    gat = types.ModuleType("google.auth.transport")
    gatr = types.ModuleType("google.auth.transport.requests")
    gatr.Request = type("Request", (), {})
    go = types.ModuleType("google.oauth2")
    go.id_token = type("id_token", (), {"verify_oauth2_token": staticmethod(lambda *a, **k: {})})
    sys.modules["google"] = g
    sys.modules["google.auth"] = ga
    sys.modules["google.auth.transport"] = gat
    sys.modules["google.auth.transport.requests"] = gatr
    sys.modules["google.oauth2"] = go
    sys.modules["google.oauth2.id_token"] = go.id_token

try:
    from google import genai
except ImportError:
    ggenai = types.ModuleType("google.genai")
    ggenai.Client = lambda *a, **kw: types.SimpleNamespace(models=types.SimpleNamespace(generate_content=lambda *a, **k: None))
    sys.modules["google.genai"] = ggenai
    if "google" in sys.modules:
        setattr(sys.modules["google"], "genai", ggenai)


# APScheduler
try:
    import apscheduler
except ImportError:
    aps = types.ModuleType("apscheduler")
    apss = types.ModuleType("apscheduler.schedulers")
    apssa = types.ModuleType("apscheduler.schedulers.asyncio")
    class MockAsyncIOScheduler:
        def __init__(self):
            self.jobs = []
        def add_job(self, func, trigger=None, **kwargs):
            job = types.SimpleNamespace(func=func, trigger=trigger, kwargs=kwargs)
            self.jobs.append(job)
            return job
        def get_jobs(self):
            return self.jobs
        def start(self): pass
        def shutdown(self): pass
# Document parsing fallbacks for local test runner
for mod_name in ["pandas", "docx", "pptx", "pypdf", "fitz", "paddleocr"]:
    try:
        __import__(mod_name)
    except ImportError:
        m = types.ModuleType(mod_name)
        if mod_name == "pandas":
            m.read_excel = lambda *a, **k: None
            m.read_csv = lambda *a, **k: None
        elif mod_name == "docx":
            m.Document = lambda *a, **k: None
        elif mod_name == "pptx":
            m.Presentation = lambda *a, **k: None
        elif mod_name == "pypdf":
            m.PdfReader = lambda *a, **k: None
        elif mod_name == "fitz":
            m.open = lambda *a, **k: None
        elif mod_name == "paddleocr":
            m.PaddleOCR = lambda *a, **k: None
        sys.modules[mod_name] = m


