# Gemini Image MCP Server

Gemini'nin görsel oluşturma yeteneklerini MCP (Model Context Protocol) üzerinden kullanılabilir hale getiren sunucu.

## Araçlar (Tools)

| Tool | Açıklama |
|------|----------|
| `generate_image` | Metin promptundan görsel oluşturur |
| `edit_image` | Mevcut bir görseli metin talimatıyla düzenler |

## Kurulum

### 1. Bağımlılıkları yükle

```bash
cd mcp-servers/gemini-image
npm install
```

### 2. API Key ayarla

[Google AI Studio](https://aistudio.google.com/apikey) üzerinden bir API key al ve ortam değişkeni olarak tanımla:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Veya `.env` dosyasına ekle (gitignored):

```
GEMINI_API_KEY=your-api-key-here
```

### 3. MCP konfigürasyonu

Proje kök dizinindeki `.mcp.json` dosyası zaten yapılandırılmıştır. Claude Code bu sunucuyu otomatik olarak tanır.

## Kullanım

Claude Code oturumunda:

- **Görsel oluştur:** "Bir siberpunk şehir manzarası görseli oluştur"
- **Görsel düzenle:** "Bu görseli düzenle ve arka planı mavi yap"

Görseller `generated-images/` klasörüne kaydedilir.

## Ortam Değişkenleri

| Değişken | Zorunlu | Varsayılan | Açıklama |
|----------|---------|------------|----------|
| `GEMINI_API_KEY` | Evet | — | Google AI Studio API anahtarı |
| `IMAGE_OUTPUT_DIR` | Hayır | `./generated-images` | Görsellerin kaydedileceği dizin |
| `GEMINI_IMAGE_MODEL` | Hayır | `gemini-2.0-flash-exp` | Kullanılacak Gemini modeli |
