# Projelere yapıştırılacak prompt

> Aşağıdaki bloğun tamamını, görsel üretmesini istediğin projenin Claude
> oturumuna yapıştır. `<TOKEN>` yerine gerçek token'ı koy
> (`animation-creator/work/studio-token.txt`), `<PROJE-ADI>` yerine projenin
> adını yaz.

---

Merhaba. PC'deki (RTX 5080) yerel görsel üretim hattı sana açıldı. Bulut yok,
kota yok, ücret yok. Aşağıdakini oku ve **kendi işini bozmadan, paralel
olarak** dene.

## Sen kimsin, ben kimim

Sen `<PROJE-ADI>` tarafısın. Ben PC tarafıyım — üretimi ben yapıyorum ve
sonuçlara göre hattı ben geliştiriyorum. **Aramızdaki iletişim API üzerinden**;
oturum mesajlaşması makineler arası çalışmıyor, o yüzden `/api/feedback`
kullanıyoruz. Yazdığını okuyorum, cevabımı aynı yere yazıyorum.

## Adres

```
http://192.168.0.111:7860
```

Her isteğe `?k=<TOKEN>` ekle (ya da `X-Token: <TOKEN>` başlığı).

Önce ayakta mı diye bak:

```bash
curl "http://192.168.0.111:7860/api/health?k=<TOKEN>"
```

## Senden istenen: 3–5 görsel, REFERANSLA

Bu hattın en pahalı dersi şu: **bir stili metinle tarif etmek işe yaramıyor.**
Dört tur denendi, dördü de ıskaladı. Referans doğrudan verilince tek turda
oturdu.

O yüzden senden istediğim şey düz üretim değil: **kendi projenin mevcut bir
görselini referans ver**, ona benzeyen 3–5 yeni görsel üret.

### 1) Referansını yükle

```bash
curl -X POST "http://192.168.0.111:7860/api/images?k=<TOKEN>" \
  -F "file=@/yol/senin-referans.png"
```

Dönen `id` (`img_...`) senin referansın.

### 2) Üret

```bash
curl -X POST "http://192.168.0.111:7860/api/image-generate?k=<TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "sinif": "karakter",
    "prompt": "ÖZNEYİ AYRINTILI YAZ — stili değil",
    "referanslar": ["img_...."],
    "tohum": 1001
  }'
```

En fazla **3 referans** verebilirsin.

### 3) Bekle ve sonucu al

```bash
curl "http://192.168.0.111:7860/api/image-generate/<is_id>?k=<TOKEN>"
```

`durum` sırayla: `sirada` → `GPU bekleniyor` → `referansli uretim` → `bitti`.
Bittiğinde `gorseller[0].file` gelir; görsel:
`http://192.168.0.111:7860/library/<file>?k=<TOKEN>`

## Prompt nasıl yazılır — ölçülmüş kural

**Stili tarif etme, ÖZNEYİ tarif et.** Boş bıraktığın her şey referanstan
kopyalanır.

Ölçüldü, aynı referans ve aynı model:

| prompt | sonuç |
|---|---|
| `a robed skeletal figure, same art style` | referansın neredeyse **birebir kopyası** |
| `a robed skeletal figure raising a curved sword above its head, both arms up, no lantern` | **aynı stil, yeni poz ve nesne** ✓ |

Yani: pozu, açıyı, nesneyi, ne **olmadığını** (`no lantern`) yaz. Kontur,
palet, ışık yazma — onlar referanstan gelir.

Prompt **İngilizce** olmalı; modeller İngilizce'de belirgin şekilde daha iyi.

## Bilmen gerekenler

- **Görsel başına ~155 saniye.** Prompt uzunluğu süreyi değiştirmiyor.
- **GPU tek.** Dört hat aynı kartı paylaşıyor; sıraya girersin. Son istek öne
  geçer, çalışan iş yarıda kesilmez. `GET /api/gpu` kimin tuttuğunu söyler.
- **Aynı tohum + aynı prompt yeniden çalışmaz** — önbellek eski sonucu döner.
  Yeni bir şey istiyorsan tohumu değiştir.
- **Alfa kanalı yok.** Çıktılar opak.
- `sinif` olarak `karakter` ya da `sahne` kullan. `ikon` ve `yazili` kapalı —
  henüz ölçülmediler, istersen sebebini `GET /api/image-classes` söyler.

## Bana nasıl ulaşırsın

Üretim bittikten sonra — **sonuç iyi olsa da olmasa da** — bana yaz:

```bash
curl -X POST "http://192.168.0.111:7860/api/feedback?k=<TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "kimden": "<PROJE-ADI>",
    "gorsel_id": "img_....",
    "prompt": "kullandığın prompt",
    "beklenen": "ne bekliyordun",
    "gelen": "ne geldi",
    "mesaj": "değerlendirmen"
  }'
```

`beklenen` ve `gelen` alanları en değerlisi. "Kötü" bir şey öğretmiyor;
"kamuflaj filesi istedim, çıplak araç geldi" ölçülebilir bir teste dönüşüyor
ve düzeltiliyor.

### Cevabımı buradan okursun

```bash
curl "http://192.168.0.111:7860/api/feedback?kimden=<PROJE-ADI>&k=<TOKEN>"
```

Her kaydın `cevap` alanına yazarım. Bir şeyi düzelttiysem orada söylerim ve
**tekrar denemeni isterim.**

Döngü şu: sen üret → bana yaz → ben düzeltirim → sana haber veririm → tekrar
üret. İyi sonuç alana kadar sürer. Sonra bu hattı kendi ihtiyaçların için
serbestçe kullanabilirsin.

## Kendi işini bozma

Bu bir yan iş. Kendi sprint'ini durdurma, kendi dosyalarını değiştirme.
Yalnızca:

1. Bir referans görselin yükle
2. 3–5 üretim yap
3. Sonucu bana yaz

Hepsi bu. Üretim PC'de oluyor, senin makineni yormuyor.
