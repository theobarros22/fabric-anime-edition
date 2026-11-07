"""Paid-job registry + preview lock / Registro de job pago + trava de prévia.

Two rules so you never pay twice nor spend big in the dark / Duas regras:
 1) FINGERPRINT CACHE: every paid step stores a hash of its inputs (text, voice, model, files). Same input = reuse.
 2) PREVIEW FIRST: the full job only runs after a short preview was approved *for that exact fingerprint*.
Never stores API keys, headers or signed URLs. / Nunca grava chave, cabeçalho nem URL assinada.

  from job_estado import Job
  job = Job('work/job-state.json'); imp = job.impressao(text=t, voice=V, model=M)
  r = job.feito('voice_S01', imp)                  # previous result or None
  job.registrar('voice_S01', imp, arquivo='S01.mp3', chars=len(t))
  job.exigir_aprovacao('preview_voice', imp_prev)  # exits if the preview was not approved
CLI: python job_estado.py ver STATE.json | python job_estado.py aprovar STATE.json STEP
"""
import hashlib, json, os, re, sys, threading, time

SECRET = re.compile(r"(api[_-]?key|authorization|token|secret|signature|x-amz-|sig=)", re.I)


def _hash_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


class Job:
    def __init__(self, path):
        self.caminho = path; self._lock = threading.RLock()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.d = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else dict(criado=time.strftime("%Y-%m-%d %H:%M:%S"), etapas={})

    @staticmethod
    def impressao(**inputs):
        norm = {k: ("file:" + _hash_file(v) if isinstance(v, str) and os.path.isfile(v) else v) for k, v in sorted(inputs.items())}
        return hashlib.sha256(json.dumps(norm, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

    def feito(self, etapa, imp):
        e = self.d["etapas"].get(etapa)
        if not e or e.get("impressao") != imp or e.get("estado") != "ok": return None
        arq = e.get("resultado", {}).get("arquivo")
        return None if arq and not os.path.exists(arq) else e["resultado"]

    def registrar(self, etapa, imp, estado="ok", **resultado):
        for k in list(resultado):
            if SECRET.search(k) or (isinstance(resultado[k], str) and SECRET.search(resultado[k])): resultado[k] = "***removed***"
        with self._lock:
            ant = self.d["etapas"].get(etapa, {})
            self.d["etapas"][etapa] = dict(impressao=imp, estado=estado, quando=time.strftime("%Y-%m-%d %H:%M:%S"), resultado=resultado,
                                           aprovado=ant.get("aprovado") if ant.get("impressao") == imp else None, chamadas=ant.get("chamadas", 0) + 1)
            self.salvar()

    def aprovar(self, etapa):
        e = self.d["etapas"].get(etapa)
        if not e or e.get("estado") != "ok": raise SystemExit(f'ERROR: preview "{etapa}" missing or failed.')
        e["aprovado"] = dict(impressao=e["impressao"], quando=time.strftime("%Y-%m-%d %H:%M:%S")); self.salvar()

    def aprovada(self, etapa, imp):
        e = self.d["etapas"].get(etapa) or {}
        return bool(e.get("aprovado")) and e["aprovado"].get("impressao") == imp

    def exigir_aprovacao(self, etapa, imp):
        if not self.aprovada(etapa, imp):
            raise SystemExit(f'LOCKED: preview "{etapa}" for this exact version was not approved. Check it, then: python job_estado.py aprovar {self.caminho} {etapa}')

    def salvar(self):
        with self._lock:
            tmp = f"{self.caminho}.{os.getpid()}.{threading.get_ident()}.tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(self.d, f, ensure_ascii=False, indent=1)
            os.replace(tmp, self.caminho)   # atomic write


if __name__ == "__main__":
    if len(sys.argv) < 3: raise SystemExit(__doc__)
    j = Job(sys.argv[2])
    if sys.argv[1] == "aprovar": j.aprovar(sys.argv[3]); print("APPROVED:", sys.argv[3])
    else:
        for k, e in j.d["etapas"].items(): print(f"{k:24} {e['estado']:6} calls={e.get('chamadas', 0)} approved={'yes' if e.get('aprovado') else '-'} {e['quando']}")
