"""GPU hakemi — IKI YONLU.

Bir kilit iki sekilde bozulur ve ikisi de sessizdir:

  - fazla gevsek: iki hat ayni anda GPU'ya girer, uretim 7-90 kat yavaslar
    ve kimse "kilit bozuk" demez, yalnizca "bugun yavas" der
  - fazla siki: kilit birakilmaz, GPU sonsuza kadar bos bekler ve panelde
    her sey normal gorunur

O yuzden her davranis IKI yonden de olculuyor.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import hakem as H  # noqa: E402


class Temel(unittest.TestCase):
    def setUp(self):
        self.dizin = tempfile.mkdtemp()
        self.h = H.Hakem(Path(self.dizin) / "durum.json")


class KilitTesti(Temel):
    def test_bos_kart_verilir(self):
        self.assertTrue(self.h.iste("video"))

    def test_ikinci_hat_ALAMAZ(self):
        """Asil koruma: iki hat ayni anda GPU'ya girmemeli."""
        self.h.iste("video")
        self.assertFalse(self.h.iste("resim"))

    def test_ayni_hat_tekrar_isteyebilir(self):
        """Ters yon: kendi kilidini kendine kapatan bir hakem de bozuktur."""
        self.h.iste("video")
        self.assertTrue(self.h.iste("video"))

    def test_birakilinca_oteki_alir(self):
        self.h.iste("video")
        self.h.iste("resim")
        self.h.birak("video")
        self.assertTrue(self.h.iste("resim"))

    def test_baskasinin_kilidini_ACAMAZ(self):
        """'resim' video'nun kilidini birakabilseydi ikisi ayni anda
        calisirdi."""
        self.h.iste("video")
        self.h.birak("resim")
        self.assertEqual(self.h.durum()["tutan"], "video")
        self.assertFalse(self.h.iste("ses"))

    def test_bilinmeyen_hat_reddedilir(self):
        with self.assertRaises(ValueError):
            self.h.iste("yazilim")


class LifoTesti(Temel):
    def test_SON_istek_one_gecer(self):
        """Kullanicinin acik istegi: son istek ilk sirada."""
        self.h.iste("video")            # calisiyor
        self.h.iste("ses")              # 1. bekleyen
        self.h.iste("resim")            # 2. bekleyen — SONUNCU
        self.assertEqual(self.h.birak("video"), "resim")

    def test_sonraki_de_lifo(self):
        self.h.iste("video")
        self.h.iste("ses")
        self.h.iste("resim")
        self.h.birak("video")
        self.h.iste("resim")            # resim calisiyor
        # geriye 'ses' kalmali — kesilen istek DEVAM ETMELI, kaybolmamali
        self.assertEqual(self.h.birak("resim"), "ses")

    def test_ayni_hat_yiginda_TEKRARLANMAZ(self):
        """Iki kez isteyen bir hat yiginda iki kez durursa, birakildiginda
        kendi kendine iki tur alir ve oteki hat aclik ceker."""
        self.h.iste("video")
        self.h.iste("ses")
        self.h.iste("ses")
        self.h.iste("resim")
        self.assertEqual(self.h.birak("video"), "resim")
        self.h.iste("resim")
        self.assertEqual(self.h.birak("resim"), "ses")
        self.h.iste("ses")
        self.assertIsNone(self.h.birak("ses"))   # yigin bosaldi

    def test_bekleyenler_calisma_sirasiyla_gosterilir(self):
        self.h.iste("video")
        self.h.iste("ses")
        self.h.iste("resim")
        self.assertEqual(self.h.durum()["bekleyenler"], ["resim", "ses"])


class BirakmaIstegiTesti(Temel):
    def test_yeni_istek_birakmayi_ISTER(self):
        self.h.iste("video")
        self.assertFalse(self.h.birakmasi_isteniyor_mu("video"))
        self.h.iste("resim")
        self.assertTrue(self.h.birakmasi_isteniyor_mu("video"))

    def test_istek_yokken_birakma_ISTENMEZ(self):
        """Ters yon: her zaman 'birak' diyen bir bayrak, hattin hic
        calismamasi demek."""
        self.h.iste("video")
        self.assertFalse(self.h.birakmasi_isteniyor_mu("video"))

    def test_tutmayan_hatta_sorulunca_False(self):
        self.h.iste("video")
        self.h.iste("resim")
        self.assertFalse(self.h.birakmasi_isteniyor_mu("resim"))

    def test_yigin_bosalinca_bayrak_duser(self):
        self.h.iste("video")
        self.h.iste("resim")
        self.h.birak("video")
        self.h.iste("resim")
        self.assertFalse(self.h.birakmasi_isteniyor_mu("resim"))


class ParalelTesti(Temel):
    def test_paralel_acikken_herkes_gecer(self):
        self.h.paralel_ayarla(True)
        self.assertTrue(self.h.iste("video"))
        self.assertTrue(self.h.iste("resim"))
        self.assertTrue(self.h.iste("ses"))

    def test_paralel_kapaninca_tekrar_siraya_girer(self):
        """Ters yon: ayar geri alinabilmeli."""
        self.h.paralel_ayarla(True)
        self.h.iste("video")
        self.h.paralel_ayarla(False)
        self.h.iste("video")
        self.assertFalse(self.h.iste("resim"))

    def test_ayar_kalici(self):
        self.h.paralel_ayarla(True)
        self.assertTrue(H.Hakem(self.h.dosya).paralel_mi())

    def test_paralel_acilinca_HAYALET_KILIT_kalmiyor(self):
        """Olculdu: paralel modda iste() dosyaya dokunmadan True donuyor,
        yani o an kilidi tutan hat onu HIC birakmiyor ve `tutan` donuyor.
        Paralel kapatilinca bu hayalet kilit ortaya cikip oteki hatlari 15
        dakika bekletirdi."""
        self.h.iste("video")
        self.assertEqual(self.h.durum()["tutan"], "video")
        self.h.paralel_ayarla(True)
        self.assertIsNone(self.h.durum()["tutan"])
        # ve paralel kapaninca baska bir hat ANINDA alabilmeli
        self.h.paralel_ayarla(False)
        self.assertTrue(self.h.iste("resim"))

    def test_paralel_acilinca_BEKLEYENLER_de_temizleniyor(self):
        """Yiginda kalan bekleyenler, paralel kapaninca sirasi gelmemis
        hayalet istekler olarak geri donerdi."""
        self.h.iste("video")
        self.h.iste("ses")
        self.h.paralel_ayarla(True)
        self.assertEqual(self.h.durum()["bekleyenler"], [])


class CokmeTesti(Temel):
    def test_olu_kilit_devralinir(self):
        """Bir hat kilidi alip cokerse GPU sonsuza kadar kilitli kalirdi.
        Bu ekosistemde tam da boyle oldu (ajan olduruldu, is claimed kaldi)."""
        self.h.iste("video")
        d = self.h._oku()
        d["damga"] = time.time() - (H.BAYAT_SN + 60)
        self.h._yaz(d)
        self.assertTrue(self.h.durum()["olu_kilit"])
        self.assertTrue(self.h.iste("resim"))

    def test_CANLI_kilit_devralinmaz(self):
        """Ters yon: yasayan bir kilidi devralmak, iki hattin ayni anda
        GPU'ya girmesi demek."""
        self.h.iste("video")
        d = self.h._oku()
        d["damga"] = time.time() - (H.BAYAT_SN - 60)
        self.h._yaz(d)
        self.assertFalse(self.h.durum()["olu_kilit"])
        self.assertFalse(self.h.iste("resim"))

    def test_canli_damgayi_tazeliyor(self):
        self.h.iste("video")
        d = self.h._oku()
        d["damga"] = time.time() - (H.BAYAT_SN - 30)
        self.h._yaz(d)
        self.h.canli("video")
        self.assertFalse(self.h.durum()["olu_kilit"])

    def test_canli_BASKASININ_damgasini_tazelemez(self):
        self.h.iste("video")
        eski = self.h._oku()["damga"]
        time.sleep(0.01)
        self.h.canli("resim")
        self.assertEqual(self.h._oku()["damga"], eski)

    def test_bozuk_dosya_cokertmiyor(self):
        self.h.dosya.parent.mkdir(parents=True, exist_ok=True)
        self.h.dosya.write_text("{yarim json", encoding="utf-8")
        self.assertTrue(self.h.iste("video"))

    def test_dosya_yokken_calisiyor(self):
        self.assertEqual(self.h.durum()["tutan"], None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
