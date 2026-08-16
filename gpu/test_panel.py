"""Ortak panel — EKRANA CIKAN metni olcer.

Sayilari dogru hesaplamak yetmiyor: bu ekosistemde bir sayac dogru
hesaplanip HICBIR YERE yazilmadigi icin aylarca gorunmedi. O yuzden test
widget metnine bakiyor, hakem durumuna degil.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import hakem as H  # noqa: E402
import panel as P  # noqa: E402


class SahteWidget:
    def __init__(self):
        self.metin = ""
        self.renk = ""

    def config(self, **kw):
        if "text" in kw:
            self.metin = kw["text"]
        if "fg" in kw:
            self.renk = kw["fg"]


def panel_kur(h):
    p = P.Panel.__new__(P.Panel)
    p.h = h
    p.l_tutan = SahteWidget()
    p.l_ipucu = SahteWidget()
    p.satirlar = {hat: {"nokta": SahteWidget(), "durum": SahteWidget(),
                        "dugme": SahteWidget()} for hat in P.HATLAR}
    p.kok = mock.Mock()
    return p


class PanelTesti(unittest.TestCase):
    def setUp(self):
        self.dizin = tempfile.mkdtemp()
        self.h = H.Hakem(Path(self.dizin) / "durum.json")
        self.p = panel_kur(self.h)

    def test_bosta_oldugunu_yaziyor(self):
        self.p._ciz()
        self.assertIn("boşta", self.p.l_tutan.metin)

    def test_calisan_hat_gosteriliyor(self):
        self.h.iste("video")
        self.p._ciz()
        self.assertIn("video", self.p.l_tutan.metin)
        self.assertIn("çalışıyor", self.p.satirlar["video"]["durum"].metin)

    def test_bekleyen_hat_SIRASIYLA_gosteriliyor(self):
        self.h.iste("video")
        self.h.iste("ses")
        self.h.iste("resim")            # son istek -> 1. sirada
        self.p._ciz()
        self.assertIn("1.", self.p.satirlar["resim"]["durum"].metin)
        self.assertIn("2.", self.p.satirlar["ses"]["durum"].metin)

    def test_devredecegini_SOYLUYOR(self):
        """Kullanicinin en cok ihtiyaci olan bilgi: takilmadi, devredecek."""
        self.h.iste("video")
        self.h.iste("resim")
        self.p._ciz()
        self.assertIn("devredecek", self.p.satirlar["video"]["durum"].metin)

    def test_istek_yokken_devredecek_YAZMIYOR(self):
        """Ters yon: her zaman 'devredecek' yazan bir panel yalan soyler."""
        self.h.iste("video")
        self.p._ciz()
        self.assertNotIn("devredecek", self.p.satirlar["video"]["durum"].metin)

    def test_lifo_ipucu_yaziliyor(self):
        """LIFO sezgisel degil — panel NEDEN bu sirada oldugunu soylemeli."""
        self.h.iste("video")
        self.h.iste("ses")
        self.p._ciz()
        self.assertIn("son istek önce", self.p.l_ipucu.metin)

    def test_paralel_modda_herkes_serbest(self):
        self.h.paralel_ayarla(True)
        self.h.iste("video")
        self.p._ciz()
        self.assertIn("paralel", self.p.l_tutan.metin)
        for hat in P.HATLAR:
            self.assertEqual(self.p.satirlar[hat]["durum"].metin, "serbest")

    def test_olu_kilit_gorunuyor(self):
        """Olu kilit sessizce gizlenirse kullanici 'neden bekliyor' diye
        saatlerce bakar."""
        import time
        self.h.iste("video")
        d = self.h._oku()
        d["damga"] = time.time() - (H.BAYAT_SN + 60)
        self.h._yaz(d)
        self.p._ciz()
        self.assertIn("ölü kilit", self.p.l_tutan.metin)

    def test_her_hat_icin_satir_var(self):
        """Hakemde tanimli ama panelde gosterilmeyen bir hat, gorunmez
        bekleyen demek."""
        for hat in H.HATLAR:
            self.assertIn(hat, P.HATLAR, f"{hat} panelde yok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
