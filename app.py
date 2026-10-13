import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

@app.get("/")
def index():
    return render_template("index.html", video_provider=bool(os.getenv("RUNWAY_API_KEY")))

@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "BEVAVE AI Satış Müdürü", "utc": datetime.now(timezone.utc).isoformat()})

@app.post("/api/campaign")
def campaign():
    data = request.get_json(silent=True) or {}
    topic = str(data.get("topic", "")).strip()
    audience = str(data.get("audience", "E-ticarete başlamak isteyen girişimciler")).strip()
    tone = str(data.get("tone", "Güven veren ve satış odaklı")).strip()
    if not topic:
        return jsonify({"error": "Kampanya konusu boş olamaz."}), 400

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                input=(
                    "BEVAVE için Türkçe pazarlama kampanyası oluştur. "
                    "BEVAVE; kırtasiye, ofis, elektronik ve oyuncak kategorilerinde ürün tedariki "
                    "ve XML bayilik modeli sunar. Doğrulanmamış vaat, fiyat veya istatistik uydurma. "
                    "Çıktıyı şu başlıklarla ver: Kampanya fikri, Instagram metni, 20 saniyelik "
                    "dikey video senaryosu (sahne sahne), ekranda yazılar, CTA, hashtagler. "
                    f"Konu: {topic}\nHedef kitle: {audience}\nTon: {tone}\n"
                    "Site: https://www.bevave.com/bev/"
                )
            )
            return jsonify({"result": response.output_text, "mode": "ai"})
        except Exception as exc:
            app.logger.exception("AI request failed")
            return jsonify({"error": "Yapay zekâ isteği başarısız oldu. API anahtarını ve servis ayarlarını kontrol edin.", "detail": str(exc)[:300]}), 502

    result = f"""KAMPANYA FİKRİ
{topic} konusunda BEVAVE'nin ürün tedariki ve XML bayilik modelini anlatan kısa, net bir tanıtım.

INSTAGRAM METNİ
Ürünlerinizi çevrim içi satışa taşımak mı istiyorsunuz? BEVAVE'nin ürün tedarik ve XML bayilik seçeneklerini keşfedin. Ürün kategorilerini ve başvuru koşullarını inceleyin.
{audience} için hazırlanan bu içerik: {tone.lower()}.

20 SANİYELİK DİKEY VİDEO SENARYOSU
0–3 sn: Dikkat çekici ürün kolajı. Ekran yazısı: “Ürün kataloğunuzu büyütün”
3–8 sn: Kırtasiye, ofis, elektronik ve oyuncak kategorilerinden ürünler.
8–14 sn: Bilgisayar veya telefonda çevrim içi mağaza görüntüsü. Ekran yazısı: “XML bayilik modelini keşfedin”
14–20 sn: BEVAVE marka kapanışı. Ekran yazısı: “Bayilik başvurusu: bevave.com/bev/”

ÇAĞRI
Bayilik seçeneklerini ve koşullarını incelemek için https://www.bevave.com/bev/ adresini ziyaret edin.

HASHTAGLER
#BEVAVE #XMLBayilik #ETicaret #ToptanÜrün #OnlineSatış

Not: Bu taslak otomatik şablonla üretildi. OpenAI API anahtarı eklenince AI ile kişiselleştirilebilir. Bu sürüm henüz MP4 video üretmez."""
    return jsonify({"result": result, "mode": "template"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
