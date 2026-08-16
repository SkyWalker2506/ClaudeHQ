"""GPU hakemi — dort hat tek karti paylasiyor.

## Problem

Bu makinede GPU'ya dokunan dort is var ve hepsi ayni RTX 5080'i istiyor:

    video   Wan 2.2 I2V         tepe 15.7 GB   ~112 sn/klip
    resim   SDXL / Qwen-Image   tepe 13.5 GB   ~15-90 sn/gorsel
    ses     Chatterbox TTS      degisken
    soru    Ollama (yerel AI)   2-14 GB modele gore

Kart 16.3 GB. Ikisi ayni anda calisamaz — ve bu teorik degil, olculdu:
GPU paylasilinca uretim **7-90 kat** yavasladi. "Yavas" burada dakikalar
degil saatler demek.

## Cozum ve iki kural

**Kural 1 — Sirayla.** Varsayilan olarak tek hat calisir; oteki hatlar
bekler. `paralel=True` yapilirsa herkes serbest birakilir (kullanicinin
acik tercihi; hakem karismaz).

**Kural 2 — Son istek one gecer (LIFO).** Kullanici o an ne istediyse o
onceliklidir. Calisan hat birakinca, yiginin TEPESI devam eder; en eski
istek en son.

## Yarida kesme IS SINIRINDA olur

Yeni istek geldiginde calisan hat oldurulmez, **birakmasi istenir**
(`birakmasi_isteniyor_mu`). Hat o anki isini bitirir ve birakir.

Sebep olculdu: bir video klibi 112 saniye suruyor ve ortasinda kesilen
uretim tamamen cope gidiyor — dosya yazilmiyor, is `claimed` kaliyor.
Ayni sey ses ve gorselde de gecerli. En kotu bekleme bir is suresi kadar.

## Neden dosya tabanli

Dort hat AYRI surecler, ayri depolarda, ayri venv'lerde, farkli zamanlarda
baslatiliyor. Ortak bellek yok. Dosya, hepsinin gorebildigi tek yer — ve bu
ekosistemde zaten kullanilan kalip (`animation-creator.control.json`,
OzzyVoiceLab `kuyruk/kontrol.json`).

## Cokme dayanikliligi

Bir hat kilidi alip cokerse GPU sonsuza kadar kilitli kalirdi. Her tutucu
bir **zaman damgasi** yeniler; `BAYAT_SN` gecmis bir kilit gecersiz sayilir.
Bu bir kolaylik degil zorunluluk: bu ekosistemde tam da boyle bir sey oldu
(ajan olduruldu, is `claimed` kaldi, kimse almadi).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

#: Taninan hatlar. Serbest metin kabul etmiyoruz: yazim hatasi yeni bir hat
#: uydurur ve kilit sessizce ise yaramaz hale gelir.
HATLAR = ("video", "resim", "ses", "soru")

#: Tutucu bu suredir damgasini yenilemediyse kilit OLU sayilir. Olculen en
#: uzun tek is 370 sn (720p, 81 kare); 15 dakika saglikli hicbir isi kesmez.
BAYAT_SN = 900

#: Damga yenileme araligi — tutucunun `canli()` cagirma sikligi.
NABIZ_SN = 30

def _varsayilan_dosya() -> Path:
    """Durum dosyasinin yeri — DONMUS exe'de `__file__` guvenilmez.

    PyInstaller onefile paketinde bu modul gecici bir dizine (`sys._MEIPASS`)
    acilir; `Path(__file__).parent` her calistirmada BASKA bir klasordur. Yani
    donmus panel kendi ozel durum dosyasini yazar ve hatlarin yazdigini hic
    gormez: panel "bosta" gosterirken hatlar sirayla calisir.

    Bu, tespit edilmesi zor bir hata sinifi — panel calisiyor gorunur, yalniz
    yanlis seyi gosterir. O yuzden donmus surumde `__file__` HIC
    kullanilmiyor; sabit yol ya da ortam degiskeni.
    """
    acik = os.environ.get("GPU_HAKEM_DOSYA")
    if acik:
        return Path(acik)
    if getattr(sys, "frozen", False):
        for dizin in (os.environ.get("GPU_HAKEM_DIZIN"),
                      r"D:\Projects\ClaudeHQ\gpu",
                      os.path.expanduser("~/Projects/ClaudeHQ/gpu")):
            if dizin and Path(dizin).is_dir():
                return Path(dizin) / "hakem-durum.json"
        # Hicbiri yoksa kullanici profilinde ortak bir yer — gecici dizin
        # DEGIL: gecici dizin her calistirmada degisir ve kilit paylasilmaz.
        return Path(os.path.expanduser("~")) / ".gpu-hakem-durum.json"
    return Path(__file__).resolve().parent / "hakem-durum.json"


VARSAYILAN_DOSYA = _varsayilan_dosya()


class Hakem:
    def __init__(self, dosya: Path | str = VARSAYILAN_DOSYA):
        self.dosya = Path(dosya)

    # --- durum okuma/yazma ------------------------------------------------ #

    def _oku(self) -> dict:
        try:
            d = json.loads(self.dosya.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - dosya yok/bozuk: temiz durum
            d = {}
        d.setdefault("paralel", False)
        d.setdefault("tutan", None)
        d.setdefault("damga", 0.0)
        d.setdefault("yigin", [])
        d.setdefault("birak_istegi", False)
        return d

    def _yaz(self, d: dict) -> None:
        """ATOMIK yaz. Dogrudan yazmak, okuyan bir hattin yarim JSON gormesi
        demek; o da 'dosya bozuk' yolundan temiz duruma duser ve kilidi
        sessizce kaybeder."""
        self.dosya.parent.mkdir(parents=True, exist_ok=True)
        gecici = None
        try:
            fd, gecici = tempfile.mkstemp(dir=str(self.dosya.parent),
                                          suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False)
            os.replace(gecici, self.dosya)
            gecici = None
        finally:
            if gecici and os.path.exists(gecici):
                os.unlink(gecici)

    @staticmethod
    def _olu_mu(d: dict, simdi: float) -> bool:
        return bool(d["tutan"]) and (simdi - d.get("damga", 0)) > BAYAT_SN

    # --- kullanicinin ayari ----------------------------------------------- #

    def paralel_ayarla(self, acik: bool) -> None:
        """Paralel modu ac/kapa.

        Acarken kilit durumu TEMIZLENIR. Sebep olculdu: paralel modda `iste()`
        dosyaya hic dokunmadan True donuyor, dolayisiyla o sirada kilidi tutan
        hat onu hic birakmiyor ve `tutan` eski halinde DONUYOR. Paralel geri
        kapatildiginda bu hayalet kilit ortaya cikiyor ve oteki uc hat, damga
        bayatlayana kadar (15 dakika) bosu bosuna bekliyor.

        Temizlemek dogru olan: paralel modda kimse kimseyi beklemiyorsa,
        "kim tutuyor" sorusunun cevabi da yoktur.
        """
        d = self._oku()
        d["paralel"] = bool(acik)
        if acik:
            d.update(tutan=None, damga=0.0, yigin=[], birak_istegi=False)
        self._yaz(d)

    def paralel_mi(self) -> bool:
        return bool(self._oku()["paralel"])

    # --- kilit ------------------------------------------------------------ #

    def iste(self, kim: str) -> bool:
        """GPU'yu iste. True = simdi calisabilirsin.

        False donerse hat yigina konmustur ve BEKLEMELIDIR; ayrica calisan
        hattan birakmasi ISTENIR (LIFO: son istek one gecer).
        """
        if kim not in HATLAR:
            raise ValueError(f"bilinmeyen hat: {kim} ({', '.join(HATLAR)})")
        simdi = time.time()
        d = self._oku()

        if d["paralel"]:
            return True                       # kullanici acik izin verdi

        if self._olu_mu(d, simdi):
            # Tutucu cokmus. Kilidi devral — yoksa GPU sonsuza kadar kilitli.
            d["tutan"], d["birak_istegi"] = None, False

        if d["tutan"] == kim:
            d["damga"] = simdi                # zaten bizde; damgayi tazele
            self._yaz(d)
            return True

        if d["tutan"] is None:
            d.update(tutan=kim, damga=simdi, birak_istegi=False)
            d["yigin"] = [h for h in d["yigin"] if h != kim]
            self._yaz(d)
            return True

        # Baskasinda. Yigina TEPEDEN gir (LIFO) ve birakmasini iste.
        d["yigin"] = [h for h in d["yigin"] if h != kim]
        d["yigin"].append(kim)
        d["birak_istegi"] = True
        self._yaz(d)
        return False

    def canli(self, kim: str) -> None:
        """Damgayi tazele. Uzun bir isin ortasinda periyodik cagrilir; yoksa
        kilit BAYAT_SN sonra olu sayilir ve baskasi devralir."""
        d = self._oku()
        if d["tutan"] == kim:
            d["damga"] = time.time()
            self._yaz(d)

    def birakmasi_isteniyor_mu(self, kim: str) -> bool:
        """Calisan hat bunu IS SINIRINDA sorar. True ise: elindeki isi bitir,
        sonra `birak()`. Uretimin ortasinda kesmek 112 saniyeyi cope atar."""
        d = self._oku()
        return bool(d["tutan"] == kim and d["birak_istegi"])

    def birak(self, kim: str) -> str | None:
        """Kilidi birak. Donen: siradaki hat (yiginin tepesi) ya da None."""
        d = self._oku()
        if d["tutan"] != kim:
            # Bizim degilse dokunma. Baskasinin kilidini acmak, iki hattin
            # ayni anda GPU'ya girmesi demek.
            return d["tutan"]
        siradaki = d["yigin"].pop() if d["yigin"] else None
        d.update(tutan=None, birak_istegi=bool(d["yigin"]), damga=0.0)
        self._yaz(d)
        return siradaki

    # --- panel icin ------------------------------------------------------- #

    def durum(self) -> dict:
        simdi = time.time()
        d = self._oku()
        olu = self._olu_mu(d, simdi)
        return {
            "paralel": d["paralel"],
            "tutan": None if olu else d["tutan"],
            "olu_kilit": olu,
            "tutma_suresi_sn": (round(simdi - d["damga"]) if d["tutan"] and not olu
                                else 0),
            # Yiginin TEPESI once calisacak; kullaniciya o sirayla gosterilir.
            "bekleyenler": list(reversed(d["yigin"])),
            "birak_istegi": d["birak_istegi"],
        }
