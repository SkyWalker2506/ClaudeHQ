Merhaba. Bir AI-ajan ekosisteminin **kalıcı bilgi katmanını** yeniden tasarlamak istiyorum ve
seninle bir mimari tartışması yapmaya geldim. Aşağıdaki sayıların hepsi ölçüldü — tahmin değil.

## Bağlam

Claude Code üzerinde çalışan, ~67 depoya yayılmış bir ajan ekosistemim var. Ajanlar Unity oyun
geliştirme, 3D/2D asset pipeline'ları, UI üretimi gibi işleri yapıyor. Aylardır bilgi
biriktiriyorum ama biriken bilgiye **güvenilir biçimde erişilemiyor**.

## Bugünkü envanter

| Katman | Adet | Fiilen kullanılan |
|---|---|---|
| Agent tanımı | 212 | tarihte **1** tanesi dispatch edilmiş |
| Agent-local knowledge dosyası | 1.124 | tamamı 4 ay önce donmuş |
| Agent `learnings.md` | 205 | **183'ü bayt bayt aynı boilerplate** |
| Skill | 72 | progressive disclosure **çalışıyor** |
| Yapılandırılmış knowledge paketi | 6 repo, 70 madde | doğrulayıcı yalnız 3 repoda |
| Otomatik memory dosyası | **3.171** (~839.000 token) | indekste **233** |

Tüm geçmişte 524 subagent çağrısı yapılmış; %57'si sistemin "kesin yasak" dediği genel amaçlı
ajan. Ajanlar arası paylaşılan öğrenme mekanizmasında tüm ömrü boyunca **1 kayıt** var.

## Ölçtüğüm dört başarısızlık kalıbı

**1. Bilgi var, erişilemiyor — %93.** 3.171 memory dosyası birikmiş; indeks 233'ünü linkliyor.
Alternatif erişim yolu yok: veritabanı yok, embedding yok, vektör indeksi yok. Düz markdown ve
elle yazılmış bir indeks. Her oturumda yalnız indeks yükleniyor (~4.600 token); tekil dosya
ancak model karar verip açınca okunuyor — ve **indekste görünmeyen dosyayı açmayı düşünmesinin
bir yolu yok**. Ayrıca dosyalar arası 915 iç bağlantının 329'u kırık (%36).

**2. "Zorunlu okuma" hiçbir yerde zorunlu değil.** Mimari karar dokümanı bir okuma sırası
tarif ediyor ve 211 ajan tanımının 202'si bunu "zorunlu" diye yazıyor. Zorlayan hiçbir kod yok.
Bunu en net söyleyen, dokümanın kendi reposu: *"Ajanı okumaya zorlayan bir runtime yazılmadı.
Kapı değil, kayıt."* Hangi bilgiye dayandığını **bildiren** ajan tutarlı olmak zorunda;
hiç bildirmeyene hiçbir şey olmuyor. Kritik gözlem: doğrulayıcı script'i olan tek repoda kural
ihlali **sıfır**; olmayan repolarda 70 maddenin 10'unda zorunlu bölüm eksik. Kanıt tam olarak
bu dağılımda.

**3. Aynı kısıtı elle taşıma — tek oturumda 29.000 token.** Bir oturumda 32 ajan açtım,
brief'lerin toplamı 115.566 karakter. Aynı kısıtı ("şu dizine dokunma") **25 kez** elle yazdım.
Ve yazmayı unuttuğum kısıt, ihlal edilen kısıt oldu — bir ajan canlı başka bir ajanın yarım
dosyalarını kendi commit'ine süpürdü. Ayrıca iki ajan **aynı hatayı bağımsız keşfetti**;
birincinin bulgusunun ikinciye ulaşan bir kanalı olsaydı ikinci onu okuyup geçerdi.

**4. Yazma hattı çalışıyor ama boşa akıyor.** Otomatik memory yazan hook 4 ayda 8.681 kez
tetiklenmiş, ama hedef dizin tek bir yola sabit kodlanmış (hangi projede çalışırsan çalış oraya
yazıyor) ve 469 izin hatası var. Haftalık konsolidasyon script'i yazılmış ama hiç kurulmamış.
Temizlik aracı ise "en fazla 15 araç çağrısı" limitiyle 3.171 dosyayı tarayamıyor.

## Bugün gerçekten çalışan üç şey — bunları korumak istiyorum

1. **Progressive disclosure.** Skill'lerde açıklama katmanı 24 KB, gövde katmanı 324 KB (13:1).
   Model açıklamayı görüyor, gövdeyi ancak çağırınca yüklüyor.
2. **"Hangi görevde ne okunur" tablosu.** Her knowledge paketinde var; 15 maddelik bir paketten
   ilgili 1-2 maddeye yönlendiriyor.
3. **İndeks ile karar dosyasının ayrılması.** Bir pakette indeks bir tur boyunca "iki madde aynı
   sonuca vardı" diye yazdı; varmamışlardı. Çözüm: indeks bir *maddeler tablosu*, karar mercii
   değil. Çelişkiler numaralı ayrı bir dosyada, her biri gerekçesiyle. **Madde ile karar farklı
   türler**: madde birikir, karar çelişkiyi kapatır.

## En öğretici olay — bugün, bana oldu

Bir mimari karar dokümanına "bu alan hesaplanamaz, kural tanımsız, bu dokümanın açık borcu"
diye not düştüm. **Yanlıştı.** Kural zaten vardı ve notu yazdığım commit'ten bir öncekinde
eklenmişti — tam bir şema, 12 golden vektörle. İddiayı, o dokümanın kendi şemalar klasörünü
açmadan yazdım.

Buradan çıkardığım sonuç tasarımın merkezinde: **bilgiyi kaydetmek problemin kolay yarısı.**
Zor yarısı, ona danışması gereken şeyin gerçekten danıştığından emin olmak. Bilgi katmanını
kuran taraf olarak ben kendi kayıtlı bilgimi okumadan onun hakkında iddiada bulundum; 212
ajanın bunu yapmayacağını varsaymak için sebep yok.

Aynı örüntü aynı gün beş kez daha çıktı — her seferinde bir kontrol yeşil döndü çünkü **iki
taraflı bir gerçeğin bir tarafına** bakıyordu. Örnek: "spec'te tanımlı eylem üretilen metne
ulaşmış mı" diye soran ama "elemanın eylemi var mı" diye sormayan bir kapı; 73 butonun 68'i
hiçbir şey yapmadan geçti. Ve kapsam raporunun kendisi de yanılttı — 79 odaklanabilir eleman
sayıp sağlıklı göründü. **Bir kuralın uygulanabileceği şeyi saymak, uygulandığı şeyi saymak
değil.** Hepsi mutasyon testiyle yakalandı, hiçbiri kapıyı okuyarak.

## Hedef

Dördü **birden** olan bir bilgi katmanı istiyorum:

1. **Garanti** — her çalışmada okunduğundan emin olunabilsin
2. **Güncel** — yeni bulgu paketi güncellesin
3. **Ucuz** — her oturumda her şey yüklenmesin; sadece gerekeni, gerektiğinde
4. **Göz ardı edilmesin** — "ucuz" olsun diye hiç bakılmayan bir şeye dönüşmesin

3 ile 4 birbirine karşıt ve asıl tasarım problemi bu gerilimde.

## Sana sorularım

**A. Erişim.** 839 bin token'lık bir gövdeden ihtiyaç anında doğru 2 KB'ı getirmenin yolu ne?
Embedding/RAG mı, elle küratörlü hiyerarşik indeks mi, ikisi birden mi? "Memory palace" tarzı
mekânsal/ilişkisel indeksleme bu problemde gerçek bir kazanç mı, yoksa metafor mu?

**B. Garanti.** "Ajan okudu" nasıl **kanıtlanır**? Bugünkü tasarımın cevabı, ajanın hangi
maddelere dayandığını çıktısında bildirmesi — ve bu hiç yazılmıyor. Alternatifler: okumayı
zorunlu kılan bir araç kapısı, brief'e enjekte edilen özet, çıktıyı bilgiye karşı doğrulayan
bir kontrol. Hangisi kotayı en az harcar?

**C. Ucuzluk ile göz ardı etme gerilimi.** Progressive disclosure çalışıyor ama "görünmeyeni
açmayı düşünmeme" riskini de üretiyor — 2.938 dosya tam olarak bu. Bir şeyin **var olduğunu**
ucuza bildirip **içeriğini** pahalıya açmanın doğru granülaritesi ne?

**D. Güncelleme ve terfi.** Bir ajan bulgu ürettiğinde nereye yazılmalı, kim onaylamalı, diğer
ajanlara nasıl ulaşmalı? Bugün ajan→global terfi mekanizması yok.

**E. Çelişki hakemi.** Kaynak güvenilirlik hiyerarşim "ölçüm > resmî doküman > anlatım" ama iki
**resmî doküman** çeliştiğinde sessiz kalıyor; bu bir günde iki kez oldu. Hakem ne olmalı?

**F. Bayatlama.** 1.124 dosya 4 aydır donmuş, 183'ü birbirinin aynısı. Kullanılmayan bilgi ile
**yanlış** bilgi arasındaki farkı ne ölçer?

**G. Ölçek.** 212 ajanın 211'i hiç kullanılmadı. Bilgi tabanını 212 ajan için mi tasarlamalı,
yoksa önce ajan sayısını gerçek kullanıma indirmeli mi?

## Nasıl bir cevap istiyorum

Genel prensip listesi değil, **bu duruma özgü bir mimari öneri**. Somut olarak: hangi katmanlar,
hangi dosya/veri yapıları, hangi tetikleyiciler, ve her mekanizma için **onun çalıştığını nasıl
ölçerim**. Son madde benim için pazarlık dışı — bu ekosistemin tekrar tekrar öğrendiği ders,
ölçmeyen bir kapının er geç yeşil yalan söylediği.

Bir de dürüst ol: yukarıdakilerin hangisi aşırı mühendislik? Ajan sayısını 212'den 15'e indirip
bilgi tabanını basit tutmak daha mı doğru olurdu?
