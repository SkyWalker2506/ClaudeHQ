"""Ortak kontrol paneli — dort hat, tek kart, tek pencere.

Dort ayri exe/pencere vardi ve hangisinin GPU'yu tuttugu hicbir yerde
gorunmuyordu. Kullanicinin yasadigi sey: "video uretimi calisiyor ama ses
baslamiyor" ya da tersi — sebebi gorunmeden.

Bu pencere uc soruyu cevaplar:

    kim calisiyor · kim sirada · neden bekliyor

ve iki dugme verir: **paralel** anahtari ve her hat icin **baslat**.

## Neden Tk

Bu ekosistemde ses ve animasyon panelleri zaten Tk ve exe olarak paketleniyor
(AnimationQueue.exe). Ayni kalibi surdurmek, ayri bir arayuz cercevesi
getirmekten ucuz — ve bagimlilik eklemiyor: Tk Python'la geliyor.

## Panel HICBIR SEYI ZORLAMAZ

Panel kilidi elinden almaz, surec oldurmez. Yalnizca gosterir ve baslatir.
Sebep: kilidi disaridan almak, calisan bir uretimi ortada birakmak demek —
hakem zaten bunun icin "birak istegi" kullaniyor ve hatlar IS SINIRINDA
birakiyor.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hakem as H  # noqa: E402

YENILE_MS = 1000

RENK = {
    "bg": "#12151a", "kart": "#1a1f27", "tx": "#e6e9ef", "mut": "#8b94a3",
    "ok": "#4ade80", "bekle": "#fbbf24", "bos": "#4b5563", "acc": "#60a5fa",
    "bad": "#f87171",
}

#: Hat -> (ekran adi, baslatma komutu). Komut None ise dugme pasif.
HATLAR = {
    "video": ("VIDEO", [r"D:\Projects\animation-creator\AnimationQueue.exe"]),
    "resim": ("RESIM", [r"D:\Projects\bm-sprite-forge\SpriteForge.exe"]),
    "ses":   ("SES",   [r"D:\Projects\OzzyVoiceLab\SesPanel.exe"]),
    # Soru hatti bir uretim kuyrugu degil, etkilesimli bir kabuk. OpenCode
    # TUI'yi kendi penceresinde acmak dogru davranis — hakemde yine gorunur
    # cunku `sor` kart isterken kilide giriyor.
    "soru":  ("SORU",  ["cmd", "/c", "start", "", "cmd", "/k", "opencode"]),
}


class Panel:
    def __init__(self):
        self.h = H.Hakem()
        self.kok = tk.Tk()
        self.kok.title("GPU Kontrol")
        self.kok.configure(bg=RENK["bg"])
        self.kok.attributes("-topmost", True)
        self.kok.geometry("380x290")

        ust = tk.Frame(self.kok, bg=RENK["bg"])
        ust.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(ust, text="GPU", bg=RENK["bg"], fg=RENK["tx"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.l_tutan = tk.Label(ust, text="", bg=RENK["bg"], fg=RENK["mut"],
                                font=("Segoe UI", 9))
        self.l_tutan.pack(side="right")

        self.satirlar = {}
        for hat, (ad, komut) in HATLAR.items():
            self.satirlar[hat] = self._satir(hat, ad, komut)

        alt = tk.Frame(self.kok, bg=RENK["bg"])
        alt.pack(fill="x", padx=12, pady=(8, 4))
        self.paralel = tk.BooleanVar(value=self.h.paralel_mi())
        tk.Checkbutton(
            alt, text="paralel çalışmaya izin ver", variable=self.paralel,
            command=self._paralel_degisti, bg=RENK["bg"], fg=RENK["tx"],
            selectcolor=RENK["kart"], activebackground=RENK["bg"],
            activeforeground=RENK["tx"], font=("Segoe UI", 9),
            highlightthickness=0, bd=0).pack(side="left")

        self.l_ipucu = tk.Label(self.kok, text="", bg=RENK["bg"],
                                fg=RENK["mut"], font=("Segoe UI", 8),
                                anchor="w", justify="left", wraplength=356)
        self.l_ipucu.pack(fill="x", padx=12, pady=(0, 8))

        self._ciz()

    def _satir(self, hat: str, ad: str, komut):
        c = tk.Frame(self.kok, bg=RENK["kart"])
        c.pack(fill="x", padx=12, pady=2)
        nokta = tk.Label(c, text="●", bg=RENK["kart"], fg=RENK["bos"],
                         font=("Segoe UI", 12))
        nokta.pack(side="left", padx=(8, 6))
        tk.Label(c, text=ad, bg=RENK["kart"], fg=RENK["tx"],
                 font=("Segoe UI", 9, "bold"), width=7,
                 anchor="w").pack(side="left")
        durum = tk.Label(c, text="", bg=RENK["kart"], fg=RENK["mut"],
                         font=("Segoe UI", 8), anchor="w")
        durum.pack(side="left", fill="x", expand=True)
        dugme = tk.Button(c, text="▶", width=3, bg=RENK["kart"],
                          fg=RENK["acc"] if komut else RENK["bos"],
                          font=("Segoe UI", 10), bd=0,
                          activebackground=RENK["kart"],
                          state="normal" if komut else "disabled",
                          command=lambda k=komut, h=hat: self._baslat(h, k))
        dugme.pack(side="right", padx=6)
        return {"nokta": nokta, "durum": durum, "dugme": dugme}

    def _paralel_degisti(self):
        self.h.paralel_ayarla(self.paralel.get())

    def _baslat(self, hat: str, komut):
        if not komut:
            return
        hedef = komut[-1]
        if not os.path.exists(hedef) and not os.path.exists(komut[0]):
            self.l_ipucu.config(text=f"bulunamadı: {hedef}", fg=RENK["bad"])
            return
        try:
            subprocess.Popen(komut, cwd=str(Path(hedef).parent),
                             creationflags=(subprocess.CREATE_NO_WINDOW
                                            if os.name == "nt" else 0))
            self.l_ipucu.config(text=f"{hat} başlatıldı", fg=RENK["mut"])
        except Exception as exc:  # noqa: BLE001 - panel olmemeli
            self.l_ipucu.config(text=f"başlatılamadı: {exc}", fg=RENK["bad"])

    def _ciz(self):
        d = self.h.durum()
        tutan, bekleyenler = d["tutan"], d["bekleyenler"]

        if d["paralel"]:
            self.l_tutan.config(text="paralel — hakem karışmıyor",
                                fg=RENK["acc"])
        elif d["olu_kilit"]:
            self.l_tutan.config(text="ölü kilit — devralınacak", fg=RENK["bad"])
        elif tutan:
            self.l_tutan.config(text=f"{tutan} · {d['tutma_suresi_sn']} sn",
                                fg=RENK["ok"])
        else:
            self.l_tutan.config(text="boşta", fg=RENK["mut"])

        for hat, s in self.satirlar.items():
            if d["paralel"]:
                s["nokta"].config(fg=RENK["ok"])
                s["durum"].config(text="serbest")
            elif hat == tutan:
                s["nokta"].config(fg=RENK["ok"])
                metin = f"çalışıyor · {d['tutma_suresi_sn']} sn"
                if d["birak_istegi"]:
                    # Bu tam da kullanicinin gormek istedigi sey: is bitince
                    # devredecek, takilmadi.
                    metin += "  → iş bitince devredecek"
                s["durum"].config(text=metin)
            elif hat in bekleyenler:
                s["nokta"].config(fg=RENK["bekle"])
                s["durum"].config(text=f"sırada ({bekleyenler.index(hat) + 1}.)")
            else:
                s["nokta"].config(fg=RENK["bos"])
                s["durum"].config(text="")

        if not d["paralel"] and bekleyenler:
            # Siranin NEDEN bu sirada oldugunu yaz: LIFO sezgisel degil.
            self.l_ipucu.config(
                text=f"sıra: {' → '.join(bekleyenler)}  (son istek önce)",
                fg=RENK["mut"])
        elif not d["paralel"] and not tutan:
            self.l_ipucu.config(text="kart boşta — bir hat başlatabilirsin",
                                fg=RENK["mut"])

        self.kok.after(YENILE_MS, self._ciz)

    def calistir(self):
        self.kok.mainloop()


if __name__ == "__main__":
    Panel().calistir()
