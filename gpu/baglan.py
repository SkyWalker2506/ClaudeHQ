"""Hakemi BASKA DEPOLARDAN yuklemenin tek yolu.

Dort hat ayri depolarda ve ayri venv'lerde calisiyor. `hakem.py`'yi her
depoya kopyalamak en kolay yol olurdu ve en kotusu: dort kopya zamanla dort
farkli kurala doner, sonra da iki hat ayni anda GPU'ya girer.

Bunun yerine her depo bu dosyayi ISTER; dosya hakemi bulur.

Kullanim (kopyalanacak tek satir):

    from gpu_baglan import hakem_yukle          # bkz. asagidaki kisayol
    h = hakem_yukle()
    if h and not h.iste("video"): ...

Hakem BULUNAMAZSA None doner ve cagiran hat NORMAL calisir. Sebep: hakemin
yoklugu uretimi durdurmamali. Tek kartli bir makinede hakem faydali; onu
bulamamak bir hata mesaji hak eder ama uretimi kilitlemeyi hak etmez.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

#: Aranacak yerler, sirayla. Ortam degiskeni her zaman kazanir — makine
#: degisirse tek bir degisken yeter.
ADAYLAR = [
    os.environ.get("GPU_HAKEM_DIZIN"),
    r"D:\Projects\ClaudeHQ\gpu",
    os.path.expanduser("~/Projects/ClaudeHQ/gpu"),
]

_ONBELLEK = None


def hakem_yukle(sessiz: bool = False):
    """Hakem nesnesini dondur; bulunamazsa None.

    None donmesi 'hakem yok, serbest calis' demektir — cagiran taraf bunu
    ELE ALMALI, cunku hakemsiz calismak GPU'yu paylasma riski demek.
    """
    global _ONBELLEK
    if _ONBELLEK is not None:
        return _ONBELLEK
    for dizin in ADAYLAR:
        if not dizin:
            continue
        yol = Path(dizin) / "hakem.py"
        if not yol.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("gpu_hakem", yol)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["gpu_hakem"] = mod
            spec.loader.exec_module(mod)
            _ONBELLEK = mod.Hakem()
            return _ONBELLEK
        except Exception as exc:  # noqa: BLE001 - hakem uretimi durdurmaz
            if not sessiz:
                print(f"hakem yuklenemedi ({yol}): {exc}", file=sys.stderr)
            return None
    if not sessiz:
        print("hakem bulunamadi — hatlar birbirini beklemeden calisacak "
              "(GPU_HAKEM_DIZIN ayarlanabilir)", file=sys.stderr)
    return None
